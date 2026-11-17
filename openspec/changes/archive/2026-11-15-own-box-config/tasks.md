## 1. Patch

- [x] 1.1 Add the detector site to the reviewed-build patch for both printers, with the combined hashes for every form, and restore QIDI's bytes on uninstall.
- [x] 1.2 On the test Max 4, check startup, Box connect and disconnect, the firmware page, and `box_count` with the patch, and record the results in `openspec/observations/qidi-box/topology-and-control.md`.

## 2. Box monitor

- [x] 2.1 Generate `box.cfg` in QIDI's layout from a numbered Box list, matching QIDI's output byte for byte.
- [x] 2.2 Keep the Box record, seeded from the current `box.cfg`, and number new Boxes.
- [x] 2.3 Add the udev rule and service: settle, compare with the file, write atomically, and restart Klipper only when idle; defer otherwise and run again once idle.
- [x] 2.4 Skip while the installer lock or a board recovery record exists, and run once when a board operation ends.
- [x] 2.5 Install and remove the rule, service, and record with the other host changes.

## 3. Firmware update

- [x] 3.1 Write `box.cfg` after QIDI's package and before the board step, and flash the USB Boxes there.
- [x] 3.2 Render the update screen as a branded image, with the text screen as fallback.

## 4. Release

- [x] 4.1 Update the docs, the changelog, and the observations.
- [x] 4.2 Run a full firmware update from stock `01.01.06.05` on the test Max 4 and check that both Boxes are flashed and Klipper starts once for them.
