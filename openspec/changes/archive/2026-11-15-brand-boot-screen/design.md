## Context

Evidence is in `openspec/observations/qidi-platform.md` under Boot logo and boot animation, from the project Plus 5 (`01.01.02.01`) and the test Max 4 (`01.01.06.05`). In short:

- The boot partition (`/dev/block/by-name/boot`) holds an Android boot image, header version 0, page 2048, with the kernel and a Rockchip resource image (`RSCE`) as its second stage. The resource image holds `rk-kernel.dtb`, `logo.bmp`, and `logo_kernel.bmp`; both logos are the same top-down 24-bit BMP: 480x800, turned for the portrait panel as the framebuffer is, on the Plus 5, and 800x480 upright on the Max 4. Its entries carry no hash.
- The header's id is the SHA-1 over the kernel, ramdisk, and second stage with their sizes. The bootloader's strings show hash checks for FIT images and the device tree, and none for the Android image id.
- `bootanim.service` runs `/usr/bin/bootanim`, which has no hooks on QIDI's image. The kernel logs `Freeing drm_logo memory` about 13 s into the boot. QIDI's SOC package writes neither the boot partition nor `/etc/bootanim.d`.
- `/dev/fb0` is `root:video` 0660, and `qidi` is in `video`.

## Goals / Non-Goals

**Goals:**

- The touchscreen shows Valve Oil from power-on until the touchscreen app draws.
- A boot partition write never leaves a printer that can't boot, and uninstall returns QIDI's partition byte for byte.

**Non-Goals:**

- Changing the kernel, the device tree, or the bootloader.
- An animation before Linux starts.

## Decisions

**D1. Patch the logos in place, by structure.** Any boot image of the layout above, whose id matches its parts, has both logo BMPs replaced with the same-size BMP rendered from `boot-logo.png` and turned to the stored geometry, and its id recomputed. Any other image is left alone with the reason. Accepting by structure rather than a list of partition hashes covers each firmware's kernel, since only the logo bytes, which the structure check pins down, change.

**D2. Write order and verification.** The whole partition is saved under `printer_data` first and its copy verified. The changed 512-byte blocks are written with `dd conv=notrunc,fsync`, logos first and the header's block last, and the partition is read back; a mismatch writes QIDI's bytes back. A write cut short leaves damaged logo pixels or a stale id, neither of which the bootloader checks, so the printer still boots.

**D3. The record outlives QIDI's package.** `printer_data/.tltg_boot_logo.json` names the original and written SHA-256s and the backup. Uninstall writes the backup's differing blocks back only while the partition holds what Valve Oil wrote; a partition changed since is left as it is.

**D4. Our own unit, not QIDI's bootanim hook.** `bootanim` kills its hooks after 5 s. `tltg-boot-animation.service` starts after `local-fs.target`, runs as `qidi` at nice 10, and plays until a `qidiclient` process exists, at most 2 minutes, then puts the changed area back to the first frame. It draws nothing while a firmware update record or the install screen marker exists.

**D5. Frames are stored as changed rectangles.** The animation file holds the first frame whole and only the rectangles that change after it, and the player converts pixels by byte slicing on 24- and 32-bit framebuffers: on the Plus 5 the first frame takes about 0.12 s and later frames about 20 ms at 15 frames per second.

## Risks / Trade-offs

- [The bootloader of another firmware checks the id] → The id is recomputed and written last, and the partition is read back.
- [A firmware with another boot image layout] → Left alone; the animation still plays.

## Open Questions

- Whether the framebuffer still holds the boot logo when the player starts; the player draws the first frame whole either way.
