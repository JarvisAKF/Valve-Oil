#!/usr/bin/env python3
"""Render the images Valve Oil shows on the printer's touchscreen while QIDI's touchscreen app is stopped or not yet
running, and the boot animation.

Each image is drawn as SVG around the Valve Oil logo, rasterized with rsvg-convert, flattened with ImageMagick, and
saved as an 800x480 8-bit RGB PNG whose rows all use PNG filter 0, so the printer decodes it with zlib alone
(installer/runtime/update_screen.py). The boot animation's frames are drawn the same way and saved as
boot-animation.bin (installer/runtime/boot_screen.py); its first frame is the boot logo. The files are committed; run
this after changing a screen or the logo:

    python3 scripts/render_touchscreen_images.py
"""
from __future__ import annotations

import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from installer.runtime import boot_screen, update_screen  # noqa: E402

LOGO = REPO_ROOT / ".github/images/valve-oil-logo-dark.svg"
WIDTH, HEIGHT = update_screen.IMAGE_SIZE
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"


def _hex(color) -> str:
    return "#" + "".join(f"{component:02X}" for component in color)


def _logo(x: float, y: float, width: float, *, drop=None) -> str:
    """The logo at (x, y), `width` wide; `drop`, if given, replaces its oil drop (see _drop)."""
    source = LOGO.read_text(encoding="utf-8")
    view_box = re.search(r'viewBox="([^"]+)"', source).group(1)
    _, _, box_width, box_height = (float(value) for value in view_box.split())
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", source, flags=re.S)
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    if drop is not None:
        inner = inner.replace(_drop_path(inner), drop)
    height = width * box_height / box_width
    return (f'<svg x="{x}" y="{y}" width="{width}" height="{height}" viewBox="{view_box}" overflow="visible">'
            f'{inner}</svg>')


def _drop_path(inner: str) -> str:
    """The logo's oil drop under the canister, which hangs from (150, 392) in logo units."""
    return re.search(r'<path d="M150,392 .*?/>', inner).group(0)


def _screen_svg(title: str, warning: str, note: str) -> str:
    """Valve Oil's layout for a screen shown while QIDI's touchscreen app is stopped: the logo, a title with the brand
    accent under it, a warning in amber, and a quieter note."""
    logo_width = 400
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{_hex(update_screen.BACKGROUND)}"/>
{_logo((WIDTH - logo_width) / 2, 48, logo_width)}
<text x="{WIDTH / 2}" y="268" text-anchor="middle" font-family="{FONT}" font-weight="bold" font-size="46"
      fill="{_hex(update_screen.TEXT)}">{title}</text>
<rect x="{WIDTH / 2 - 60}" y="294" width="120" height="4" rx="2" fill="#F2B05A"/>
<text x="{WIDTH / 2}" y="356" text-anchor="middle" font-family="{FONT}" font-weight="bold" font-size="30"
      fill="{_hex(update_screen.WARNING)}">{warning}</text>
<text x="{WIDTH / 2}" y="404" text-anchor="middle" font-family="{FONT}" font-size="22"
      fill="#9AA0AA">{note}</text>
</svg>
"""


def installing_svg() -> str:
    return _screen_svg("Installing Valve Oil", "Don't turn the printer off.",
                       "The touchscreen comes back when the install is done.")


def updating_svg() -> str:
    return _screen_svg("Updating Firmware", "Don't turn the printer off.",
                       "The printer restarts by itself when the update is done.")


# The boot logo and the boot animation: the logo large, slightly above center, with room below for the line the oil
# drop lands on.
BOOT_LOGO_WIDTH = 660
BOOT_LOGO_HEIGHT = BOOT_LOGO_WIDTH * 530 / 1500  # the logo's viewBox
BOOT_LINE_GAP = 22
BOOT_LOGO_X = (WIDTH - BOOT_LOGO_WIDTH) / 2
BOOT_LOGO_Y = (HEIGHT - (BOOT_LOGO_HEIGHT + BOOT_LINE_GAP + 4)) / 2
BOOT_LINE_Y = BOOT_LOGO_Y + BOOT_LOGO_HEIGHT + BOOT_LINE_GAP
BOOT_SCALE = BOOT_LOGO_WIDTH / 1500
BOOT_FPS = 15
BOOT_FRAMES = 48  # 3.2 s


def _drop(dy: float, scale: float, opacity: float, inner: str) -> str:
    return (f'<g opacity="{opacity:.3f}" transform="translate(150,392) translate(0,{dy:.2f}) scale({scale:.3f}) '
            f'translate(-150,-392)">{_drop_path(inner)}</g>')


def boot_frame_svg(t: float) -> str:
    """The boot animation at t in [0, 1): the drop hangs under the canister, falls onto a line, the oil spreads along
    the line and fades, and a new drop forms. t = 0 is the boot logo."""
    inner = LOGO.read_text(encoding="utf-8")
    drop_x = BOOT_LOGO_X + (150 + 30) * BOOT_SCALE  # the logo's viewBox starts at -30
    nozzle_y = BOOT_LOGO_Y + (392 + 30) * BOOT_SCALE
    fall = (BOOT_LINE_Y - nozzle_y - 10) / BOOT_SCALE
    if t < 0.15:
        drop = _drop(0, 1, 1, inner)
    elif t < 0.35:
        progress = (t - 0.15) / 0.2
        drop = _drop(fall * progress * progress, 1, 1, inner)
    elif t < 0.6:
        drop = _drop(0, 0, 0, inner)
    else:
        grow = (t - 0.6) / 0.4
        drop = _drop(0, 0.15 + 0.85 * (1 - (1 - grow) ** 2), min(1.0, grow * 3), inner)
    left_end, right_end = BOOT_LOGO_X + 10, BOOT_LOGO_X + BOOT_LOGO_WIDTH - 10
    extras = ""
    if t >= 0.35:
        spread = min(1.0, (t - 0.35) / 0.25)
        ease = 1 - (1 - spread) ** 3
        left = drop_x - (drop_x - left_end) * ease
        right = drop_x + (right_end - drop_x) * ease
        fade = 1.0 if t < 0.7 else max(0.0, 1 - (t - 0.7) / 0.25)
        if fade > 0:
            extras += (f'<rect x="{left:.2f}" y="{BOOT_LINE_Y:.2f}" width="{max(0.1, right - left):.2f}" height="4" '
                       f'rx="2" fill="#F2B05A" opacity="{fade:.3f}"/>')
        if t < 0.5:
            ring = (t - 0.35) / 0.15
            radius = 4 + 40 * ring
            extras += (f'<ellipse cx="{drop_x:.2f}" cy="{BOOT_LINE_Y + 2:.2f}" rx="{radius:.2f}" ry="{radius / 5:.2f}" '
                       f'fill="none" stroke="#F2B05A" stroke-width="2" opacity="{1 - ring:.3f}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{_hex(update_screen.BACKGROUND)}"/>
{extras}{_logo(BOOT_LOGO_X, BOOT_LOGO_Y, BOOT_LOGO_WIDTH, drop=drop)}
</svg>
"""


def boot_logo_svg() -> str:
    return boot_frame_svg(0.0)


IMAGES = {update_screen.INSTALLING_IMAGE: installing_svg, update_screen.UPDATING_IMAGE: updating_svg,
          boot_screen.BOOT_LOGO_IMAGE: boot_logo_svg}


def rasterize(svg: str) -> bytes:
    """The SVG as WIDTH x HEIGHT rows of RGB."""
    with tempfile.TemporaryDirectory() as directory:
        source, raster = Path(directory) / "screen.svg", Path(directory) / "screen.png"
        source.write_text(svg, encoding="utf-8")
        subprocess.run(["rsvg-convert", "-w", str(WIDTH), "-h", str(HEIGHT), "-o", str(raster), str(source)],
                       check=True)
        return subprocess.run(["magick", str(raster), "-background", _hex(update_screen.BACKGROUND), "-flatten",
                               "-depth", "8", "rgb:-"], check=True, capture_output=True).stdout


def render(svg: str, destination: Path) -> None:
    rgb = rasterize(svg)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(_png(rgb))
    update_screen.decode_png(destination.read_bytes())  # the printer must be able to read it


def render_animation(destination: Path) -> None:
    frames = [rasterize(boot_frame_svg(index / BOOT_FRAMES)) for index in range(BOOT_FRAMES)]
    first = boot_screen.Rectangle(0, 0, WIDTH, HEIGHT, frames[0])
    # Each later frame holds what changed since the one before; the last brings the screen back to the first, so the
    # player loops from frame 1.
    encoded = [(first,)] + [_changes(before, after) for before, after in zip(frames, frames[1:] + frames[:1])]
    animation = boot_screen.Animation(BOOT_FPS, WIDTH, HEIGHT, tuple(encoded))
    data = boot_screen.encode(animation)
    boot_screen.decode(data)  # the printer must be able to read it
    destination.write_bytes(data)


def _changes(before: bytes, after: bytes) -> tuple:
    """The rectangles of `after` that differ from `before`: one per band of changed rows."""
    stride = 3 * WIDTH
    changed_rows = [y for y in range(HEIGHT) if before[y * stride:(y + 1) * stride] != after[y * stride:(y + 1) * stride]]
    bands, rectangles = [], []
    for y in changed_rows:
        if bands and y - bands[-1][1] <= 8:
            bands[-1][1] = y
        else:
            bands.append([y, y])
    for top, bottom in bands:
        columns = [x for x in range(WIDTH) if any(
            before[(y * WIDTH + x) * 3:(y * WIDTH + x) * 3 + 3] != after[(y * WIDTH + x) * 3:(y * WIDTH + x) * 3 + 3]
            for y in range(top, bottom + 1))]
        left, right = min(columns), max(columns) + 1
        rows = b"".join(after[(y * WIDTH + left) * 3:(y * WIDTH + right) * 3] for y in range(top, bottom + 1))
        rectangles.append(boot_screen.Rectangle(left, top, right - left, bottom + 1 - top, rows))
    return tuple(rectangles)


def _png(rgb: bytes) -> bytes:
    """An 8-bit RGB PNG with every row unfiltered, which zlib alone decodes."""
    stride = 3 * WIDTH
    if len(rgb) != stride * HEIGHT:
        raise ValueError(f"expected {stride * HEIGHT} bytes of RGB, got {len(rgb)}")
    raw = b"".join(b"\x00" + rgb[start:start + stride] for start in range(0, len(rgb), stride))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main() -> int:
    for path, svg in IMAGES.items():
        render(svg(), path)
        print(path.relative_to(REPO_ROOT))
    render_animation(boot_screen.ANIMATION_FILE)
    print(boot_screen.ANIMATION_FILE.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
