## Why

From power-on until QIDI's touchscreen app starts, about 20 to 30 seconds, the touchscreen shows QIDI's logo, so a printer running Valve Oil looks like a stock one until the app is up. Valve Oil already shows its own screens while it installs and updates.

## What Changes

- Replace QIDI's boot logo, which the bootloader shows from the boot partition and the kernel keeps until Linux draws, with the Valve Oil logo. Only the two logo images in the boot image's resource image and the image's SHA-1 id change. QIDI's partition is saved before the first write, and uninstall writes QIDI's logo back while the partition holds Valve Oil's.
- Play a boot animation from early in the boot until the touchscreen app starts: an oil drop falls from the logo's canister and spreads along a line. Its first frame is the boot logo.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `installer-lifecycle`: Valve Oil's boot logo and boot animation.

## Impact

- `installer/runtime/boot_logo.py`, `installer/runtime/boot_screen.py`, `installer/system/tltg_boot_animation.py`, the images under `installer/system/touchscreen/`, and `scripts/render_touchscreen_images.py`.
- `runner.py`, `uninstall.py`, and the guarded host files in `system_optimizations.py`.
- `docs/install.md`, `docs/under-the-hood.md`, `CHANGELOG.md`, `openspec/observations/qidi-platform.md`.
