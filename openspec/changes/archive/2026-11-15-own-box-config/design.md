## Context

Evidence is static analysis of the Max 4 `01.01.07.01` touchscreen app (`qidiclient` `b5285d1a…`) and the Plus 5 `01.01.02.01` app (`6c09a58a…`), with the app's log and `klippy.log` from the test Max 4's firmware update on 2026-11-13; see `openspec/observations/qidi-box/topology-and-control.md`. In short:

- **Only the app writes `box.cfg`.** Klipper imports `box_detect.so`, but its calls are commented out.
- **Two write paths, one detector.** At startup the app compares its generated config with the file and, when they differ, writes it and runs `systemctl restart klipper` with no print check. On a udev tty event for a Box it runs the detector, and if the result differs from its own last result and Klipper's idle state is `Ready` or `Idle`, it saves `box_count` and, 4 s after the last event, writes and restarts, without checking again.
- **The detector** lists `usb-Klipper_*` serial devices, keeps Boxes by USB model, compares their versions with `~/update`, publishes serials and versions for the firmware page, and returns "changed" from one instruction (`mov w20, #1`). When a Box needs QIDI's firmware update it reports 0 Boxes and writes nothing.
- **The restart** sets extruder, bed, and chamber targets to 0 and waits up to about 30 s first. Other app paths use the same routine.
- **Numbering** follows udev's syspath order, reversed: port position, not serial.
- **`box_count`** is also saved from the detected count after each Moonraker subscribe and Klippy state change.

## Goals / Non-Goals

**Goals:**

- Klipper restarts for the Boxes only when the set of Boxes really changed, and never during a print or with a heater on.
- A Box keeps its number, and so its slots and tool mappings, wherever it is plugged in.
- A QIDI firmware update ends with every USB Box flashed.

**Non-Goals:**

- RS-485 Boxes, which `box.cfg` doesn't list.
- Changing what the app shows about Boxes or its Box firmware notices.
- More than the app's five USB Boxes.

## Decisions

**D1. Patch the detector's "changed" result, not the writer or the restart.** One instruction (Max 4 file offset `0x264288`, Plus 5 `0x263438`, `mov w20, #1` → `mov w20, #0`) stops the startup write and restart, the hotplug `box_count` save, and the delayed write and restart, while detection, serials, versions, and notices still run. The restart routine is shared with other app paths and stays. The site joins the reviewed-build patch in both its forms, with and without QIDI's package updates blocked, so unreviewed builds keep QIDI's behavior. The earlier patched forms become other forms of each build, which the next install finishes, and the earlier blocked form stays blocked. The installed monitor carries each reviewed build's size and detector site, and reads those 4 bytes of the app before it does anything, so it stands down when the app isn't patched, for example after a QIDI package replaced it.

**D2. udev starts the monitor; it doesn't poll USB.** A rule for tty add and remove events of a Klipper device whose USB model is a QIDI Box, by the app's own test, runs `systemctl --no-block start` on the monitor's service; `SYSTEMD_WANTS` acts on add events only. The service is `Type=simple`, so starting it while it runs does nothing, and it reads the Box list again before every write. It also runs once at boot, for a Box removed while the printer was off, and doesn't act in the first 30 s after boot, while USB devices still appear. The monitor settles first: it waits until the Box list from `/dev/serial/by-id` has been the same for 5 s, which outlasts a Box board reset's drop-off (about 4 s on the test Max 4), and compares its config with the file on disk, so a list that returns to where it was writes nothing and restarts nothing. It is a standalone Python file in `/usr/local/lib`, like the status service, with the reviewed builds filled in at install; the installer loads the bundled copy for D7.

**D3. Number Boxes by serial, with a record.** A record in `printer_data` maps each Box's `/dev/serial/by-id` path, which carries its serial, to its number. On first run it is seeded from the `[mcu mcu_box<n>]` sections of the current `box.cfg`, in any layout an app has written, so existing numbering stays. A new Box gets the lowest number no connected Box has, taking it from a disconnected Box that held it. `box.cfg` itself never has gaps, since Klipper's Box objects index slots from Box 0: it lists the connected Boxes in number order, so the Boxes after a disconnected one move up until it returns. The record is sensitive like `box.cfg`, mode 600, and never leaves the printer.

**D3a. Write only what the app would write.** The monitor rewrites `box.cfg` only when the file is in the app's current layout (it regenerates byte for byte from its own Box list) or lists no Box (only comments, such as the file QIDI's package installs, or `# No Box Config`). A file in any other layout, such as one edited by hand or the `01.01.06` app's layout with tool macros, is left alone. It writes atomically and keeps the previous file beside the record.

**D4. Restart only when idle.** The monitor writes `box.cfg` and restarts the Klipper service through Moonraker only with no print running or paused and every heater target 0; a Klipper that isn't ready, other than starting, can't print, so it counts as idle. Otherwise it writes a small status file that Klipper's printer warnings read, keeps running, and checks again every 10 s until the printer is idle. It never sets a heater target. Waiting in the monitor, rather than in the status service, keeps the Box logic in one place and needs no other service to know about it.

**D5. Board operations own the Boxes while they run.** Valve Oil's Box, mainboard, and THR tools reset boards that re-enumerate. The monitor does nothing while the installer lock is held (it tests the lock with a shared, non-blocking `flock`), a firmware update's record exists, or a board recovery record exists, and waits for them to end, so it runs once when the operation ends. It checks again just before it writes. An install restarts the monitor's service when its files change, and the monitor then waits for that install.

**D6. `box_count` follows the file.** The app still saves its detected count after subscribe and Klippy state changes. Valve Oil's `box.cfg` lists the same Boxes, so the counts agree; the case of a Box the app thinks needs QIDI's firmware (count 0) is checked on the printer before release.

**D7. The firmware update writes `box.cfg` before its board step.** Before QIDI's package first runs, the update seeds the Box record from the current `box.cfg`, so numbering survives even where the monitor never ran, such as on Max 4 `01.01.06.05`, whose app isn't reviewed. After the package resets `box.cfg`, the board step writes it from the record and the Boxes connected, without restarting Klipper, which is stopped, so the board step finds and flashes them under the names the board admission read before the update.

**D8. The update screen is an image.** Like the install screen, the firmware update's message is a rendered 800×480 PNG with the Valve Oil logo, decoded with zlib only, with the text screen as fallback.

## Risks / Trade-offs

- [The patch is a byte change in a closed binary] → Applied only to reviewed builds by exact SHA-256, restored on uninstall, and tested on both printers before release.
- [A wrong `box.cfg` stops Klipper from starting] → Written atomically in QIDI's exact layout, checked against QIDI's generator output for the same Boxes in tests, and the previous file kept for one restart.
- [A Box connected during a print isn't usable until the print ends] → QIDI's hotplug path also waits for idle; the warning says the Box is added once the printer is idle.

## Migration Plan

The next install applies the patch and starts the monitor, which seeds its record from the current `box.cfg` without restarting Klipper. Uninstall removes both and restores QIDI's app.

## Open Questions

- What the app shows and saves when a Box runs Valve Oil's Box firmware and the detector reports 0 Boxes for a needed QIDI update.
- Whether the app's firmware page still lists Boxes correctly with the patch.
