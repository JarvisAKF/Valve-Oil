## Why

QIDI's touchscreen app writes `box.cfg` and restarts Klipper whenever the USB Boxes it finds change. It compares against its own last result instead of the file, so a Box board reset that briefly drops the Boxes off USB restarts Klipper again for an unchanged file. That happens after every Klipper start that resets the Box boards and after every Valve Oil Box flash, so Klipper started five times within two minutes of the test Max 4's firmware update. The app's startup write restarts Klipper without checking for a print, and its restart zeroes the heaters. It numbers Boxes by USB port, so moving a Box to another port renumbers the Boxes and moves their slots. After a QIDI firmware package resets `box.cfg`, the Boxes are back only once the app has started, after Valve Oil's board step, so a firmware update can't flash them.

## What Changes

- Patch the reviewed touchscreen builds so the app's Box detection never reports a change: it no longer writes `box.cfg`, saves `box_count` on hotplug, or restarts Klipper for the Boxes. Detection itself, the Box firmware notices, and the app's `MCU_ID.cfg` update keep working.
- Add Valve Oil's Box monitor: a udev rule starts a service when a USB Box connects or disconnects. Once the Boxes have stayed the same for a few seconds, it writes `box.cfg` in QIDI's layout only when the file would change, and restarts Klipper only while no print runs or is paused and no heater is on, waiting until then otherwise. It stays out of the way of Valve Oil's own board operations.
- Number each Box by its own ID, recorded by Valve Oil and seeded from the current `box.cfg`, so a Box keeps its number and slots when it moves to another port.
- Make a QIDI firmware update write `box.cfg` itself after QIDI's package resets it, so the board step flashes the USB Boxes in the same update.
- Redraw the firmware update's touchscreen message as a branded image, like the install screen.
- Uninstall puts QIDI's app back unchanged, which rebuilds `box.cfg` at its next start, and removes the monitor.

## Capabilities

### New Capabilities

- `qidi-box-config`: Valve Oil owns `box.cfg` for USB Boxes: detection, stable numbering, writes, and Klipper restarts.

### Modified Capabilities

- `qidi-firmware-updates`: the update writes `box.cfg` and flashes the USB Boxes in its board step; the update screen is a branded image.

## Impact

- `installer/runtime/qidiclient_firmware_popup.py` (a third patch site and new reviewed-build hashes for both printers), a new Box monitor under `installer/runtime/` and `installer/system/` with its udev rule and unit, `firmware_update.py`, `board_firmware.py`, `update_screen.py`, `scripts/render_touchscreen_images.py`, uninstall.
- `docs/qidi-box.md`, `docs/install.md`, `docs/under-the-hood.md`, `docs/troubleshooting.md`, `CHANGELOG.md`, `openspec/observations/qidi-box/topology-and-control.md`.
- RS-485 Boxes and printers without a USB Box keep QIDI's behavior; `box.cfg` stays `# No Box Config` without a USB Box.
- Existing printers keep their current Box numbering.
