## MODIFIED Requirements

### Requirement: A firmware update survives its own side effects
A firmware update SHALL run independently of the session that started it, SHALL keep its working files where QIDI's package does not delete them, and SHALL record enough to finish after an interruption.

#### Scenario: Started over SSH
- **WHEN** an operator starts an install that includes a firmware update from an SSH session and the session ends
- **THEN** the update continues to completion and its progress and result can be read afterwards
- **AND** the next install from a terminal follows an update still running, or reports the result of one no session saw finish, instead of starting another

#### Scenario: An interactive install
- **WHEN** an interactive install finds a firmware update it can start
- **THEN** it says which firmware it installs, which boards it flashes, that the printer can't be used and must not be powered off while it runs, and roughly how long it takes, and starts the update without asking
- **AND** the operator cannot decline it and install Valve Oil for the older firmware instead
- **AND** an install with `--dry-run` reports the same plan without downloading, stopping, or changing anything

#### Scenario: The touchscreen app is stopped
- **WHEN** the update has stopped the touchscreen app
- **THEN** the screen shows a Valve Oil image saying the firmware is updating and not to power the printer off, upright on each printer's screen, until the app starts again, or the same message as text when the image can't be shown
- **AND** a screen the app had put to sleep is lit for the message

#### Scenario: Power is lost during the update
- **WHEN** the printer restarts with a firmware update unfinished
- **THEN** the update resumes without operator action, and no other installer operation runs until it finishes, except a board's rescue
- **AND** once QIDI's package is installed, the resumed update stops Klipper, the touchscreen, and Moonraker again and flashes the boards without waiting for Klipper, finding the mainboard at its USB position when its new firmware has renamed it
- **AND** while QIDI's update folder still describes the firmware being replaced, it holds no SOC package the touchscreen app's own board update could install
- **AND** a board transfer that cannot be verified keeps that board's rescue record and instructions
- **AND** after a few boots that each stopped partway, the update is recorded as failed and the printer is left running

#### Scenario: A step fails after the printer changed
- **WHEN** installing QIDI's package or flashing a board fails
- **THEN** the update is recorded as failed at that step with what to do next, and a printer warning and the Valve Oil section show it
- **AND** it is continued by the next install or update now rather than at every boot, and only while nothing prints and no heater has a target
- **AND** the screen says the update did not finish while the touchscreen app stays stopped
- **AND** a board's rescue may run only once the update has stopped with that failure
- **AND** after a board write that cannot be verified only Moonraker is started again; after a failure that wrote nothing to a board, Klipper and Moonraker are started again too
- **AND** when the mainboard is left on a version the target firmware's Klipper can't use, the touchscreen is started as well and the result says to update the mainboard from the touchscreen's firmware page before running the installer again

#### Scenario: A recorded update this release cannot continue
- **WHEN** an install or update finds a firmware update recorded by another release, for another target firmware or in a newer format
- **THEN** a record of which nothing was installed yet is dropped and the release plans its own update, and any other is kept with the command that installs the release that can finish it
- **AND** the installer bundle that release left is not replaced

#### Scenario: The operator's saved calibration
- **WHEN** a firmware update installs QIDI's package, which replaces `printer.cfg` and may reset `saved_variables.cfg`
- **THEN** the `SAVE_CONFIG` block from before the update is back in the new `printer.cfg` before the boards are flashed and Valve Oil is installed, with the operator's values over QIDI's and the body changed only as Klipper's `SAVE_CONFIG` would change it, and saved variables QIDI's package reset are back
- **AND** a saved section the new firmware's config no longer has, or an option Valve Oil's install sets, is not carried, and the result names it with the path of the config backup
- **AND** an update resumed after a power loss puts back the calibration captured before QIDI's package first ran, never QIDI's
- **AND** a calibration that can't be restored is reported the same way and doesn't fail the update

#### Scenario: Uninstall after a firmware update
- **WHEN** a firmware update installs QIDI's package, which deletes Valve Oil's installed state with the config folder
- **THEN** the install that follows still holds what the earlier install recorded about the host before it changed it, for every host change that is still as that install left it, and keeps the operator's earlier choices about the optional OS optimizations and AI detection
- **AND** a later uninstall undoes those host changes as it would have before the update
- **AND** a host file QIDI's package replaced is recorded as it is after the package, so uninstall puts back the new firmware's file

#### Scenario: Valve Oil's install for the new firmware fails
- **WHEN** QIDI's package and the boards are done but installing Valve Oil for the target firmware fails
- **THEN** the update ends, every service is started again, and the installer's own recovery and the next install or automatic update apply

### Requirement: Boards receive this project's firmware
A firmware update, an install, and an automatic update SHALL bring the THR and every USB Box on both printers, and the mainboard on the Max 4, to this project's build for the target firmware, without a question and without a per-run option. A board with no build of this project SHALL receive QIDI's image for the target firmware when its version changes. A board already on its pinned image MUST NOT be flashed.

#### Scenario: Board on QIDI's firmware or an earlier build
- **WHEN** a run finds an admitted board on QIDI's firmware or an earlier build of this project
- **THEN** the board is backed up, flashed with the pinned image, and verified by readback, under the same idle, heater, and service-ownership rules as the board scripts

#### Scenario: The THR was flashed
- **WHEN** a run has flashed the THR
- **THEN** the saved input shaper calibration stays in effect and a printer warning says to run input shaper calibration, until the operator has

#### Scenario: USB Boxes during a firmware update
- **WHEN** a firmware update's board step runs after QIDI's package has reset `box.cfg`
- **THEN** the update has written `box.cfg` for the USB Boxes connected, and the board step flashes and verifies each of them like the THR and the mainboard

#### Scenario: Automatic update
- **WHEN** an enrolled printer's automatic update finds boards that need their pinned image and the printer passes the update checks
- **THEN** those boards are flashed unattended

#### Scenario: Closed-loop motor drivers
- **WHEN** a Max 4 firmware update's target package carries another closed-loop driver version than the installed firmware's, and both drivers report the installed firmware's driver version (or already the target), the expected hardware, and idle
- **THEN** before QIDI's package is installed, with the touchscreen and Moonraker stopped and the motors off, the run sends each driver not on the target QIDI's image, checked against its pinned size and SHA-256, through QIDI's `UPGRADE_MOTOR`, X then Y
- **AND** a driver counts as updated only once it reports the target version and idle

#### Scenario: Closed-loop drivers not as expected
- **WHEN** either driver reports another version or hardware, or is not idle, before anything was sent
- **THEN** neither driver is sent an image, the rest of the update goes on, and the update's result and the Valve Oil section name the driver and say to update the drivers from the touchscreen's firmware page

#### Scenario: A closed-loop driver update fails
- **WHEN** a driver isn't verified after three transfers
- **THEN** the bus is reset with `FIRMWARE_RESTART`, the other driver is not touched, QIDI's package is not installed, every service is started again, and the result gives what to do and a prefilled support issue
- **AND** the next install or "update now" continues the update, sending the image again to a driver the run admitted, even when it no longer reports a version

#### Scenario: Closed-loop drivers in the status
- **WHEN** an update check runs on a Max 4 that is on the release's QIDI firmware
- **THEN** the status lists the closed-loop drivers with the version Klipper reports, up to date on the target package's version and otherwise to be updated from the touchscreen's firmware page
- **AND** the check sends the drivers nothing
