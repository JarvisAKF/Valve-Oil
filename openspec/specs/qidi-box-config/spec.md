# qidi-box-config Specification

## Purpose
Keep `box.cfg` matching the USB QIDI Boxes connected, with each Box keeping its number by serial number, without QIDI's touchscreen app rewriting it or restarting Klipper during a print.

## Requirements

### Requirement: Valve Oil writes box.cfg for USB Boxes
On a printer whose touchscreen app is a reviewed build, Valve Oil SHALL stop the app from writing `box.cfg` or restarting Klipper for the Boxes, and SHALL write `box.cfg` itself in QIDI's layout for the USB Boxes connected.

#### Scenario: The touchscreen app starts or sees a Box
- **WHEN** the patched app starts, or a USB Box connects or disconnects
- **THEN** the app writes no `box.cfg`, saves no `box_count` for the hotplug, and restarts no Klipper for the Boxes
- **AND** it still shows the Boxes' firmware versions and notices and updates `MCU_ID.cfg` when the mainboard reconnects

#### Scenario: The set of Boxes changes
- **WHEN** a USB Box connects or disconnects and the Box list then stays the same for 5 seconds
- **THEN** Valve Oil writes `box.cfg` atomically in QIDI's layout, with `# No Box Config` for no Box, only when the file would change
- **AND** a list that returns to what the file already holds, as after a Box board reset, writes nothing and restarts nothing

#### Scenario: box.cfg in another layout
- **WHEN** `box.cfg` is neither in the layout the patched app writes nor lists no Box, such as a file edited by hand
- **THEN** Valve Oil leaves it as it is and restarts nothing

#### Scenario: Unreviewed touchscreen app
- **WHEN** the touchscreen app is not a reviewed build
- **THEN** the app keeps managing `box.cfg` and Valve Oil's monitor writes nothing

### Requirement: Box numbers stay with each Box
Each USB Box SHALL keep its number, and so its slots, wherever it is plugged in, from a record Valve Oil keeps on the printer.

#### Scenario: Existing printer
- **WHEN** the monitor first runs on a printer
- **THEN** its record takes each Box's number from the current `box.cfg`, and nothing is rewritten or restarted

#### Scenario: A Box moves to another port
- **WHEN** a recorded Box is connected to another USB port
- **THEN** it keeps its number

#### Scenario: A new Box
- **WHEN** a Box the record doesn't hold connects
- **THEN** it gets the lowest number no connected Box uses, and `box.cfg` numbers the Boxes without gaps

### Requirement: Klipper restarts for the Boxes only when idle
Valve Oil SHALL restart Klipper for a Box change only while no print runs or is paused and every heater target is 0, and SHALL never change a heater target to do so.

#### Scenario: The printer is idle
- **WHEN** `box.cfg` changed and the printer is idle
- **THEN** the Klipper service is restarted once

#### Scenario: A print runs or a heater is on
- **WHEN** a Box change waits while a print runs or a heater is on
- **THEN** `box.cfg` and Klipper are left as they are and a printer warning says the Box change applies once the printer is idle
- **AND** the change is written and Klipper restarted once the printer is idle

#### Scenario: A board operation runs
- **WHEN** Valve Oil holds the installer lock or a board recovery record exists
- **THEN** the monitor changes nothing, and it runs once after the operation ends

### Requirement: Uninstall gives box.cfg back to QIDI
Uninstall SHALL remove the monitor and its record and restore the touchscreen app's original bytes.

#### Scenario: Uninstall
- **WHEN** Valve Oil is uninstalled
- **THEN** the app is QIDI's original build again, the monitor's rule and service are gone, and the app rebuilds `box.cfg` at its next start
