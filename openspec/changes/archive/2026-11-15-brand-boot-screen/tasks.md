## 1. Boot logo

- [x] 1.1 Render the boot logo and write it into both logos of a boot image of the reviewed layout, with the id recomputed, verified by readback, and restored on uninstall.
- [x] 1.2 Read the Max 4's boot image and check its layout and logo geometry.
- [x] 1.3 Write the logo on a test printer, reboot, and record what the screen shows in `openspec/observations/qidi-platform.md`.

## 2. Boot animation

- [x] 2.1 Render the animation and play it from `tltg-boot-animation.service` until the touchscreen app runs.
- [x] 2.2 Time the boot with the animation on both printers and check that it ends when the app draws.

## 3. Release

- [x] 3.1 Update the docs and the changelog.
