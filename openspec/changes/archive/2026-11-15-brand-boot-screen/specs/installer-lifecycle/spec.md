## ADDED Requirements

### Requirement: Valve Oil's boot screen
An install SHALL replace QIDI's boot logo with Valve Oil's in a boot partition of the reviewed layout, and SHALL play Valve Oil's boot animation from early in the boot until QIDI's touchscreen app runs. Uninstall SHALL put QIDI's boot logo back.

#### Scenario: A boot partition of the reviewed layout
- **WHEN** an install finds an Android boot image whose id matches its parts and whose resource image holds `logo.bmp` and `logo_kernel.bmp` as full-screen 24-bit BMPs
- **THEN** the partition is saved and its copy verified, both logos are replaced with Valve Oil's in their stored geometry, the id is recomputed, only those blocks are written, logos before the header, and the partition is read back
- **AND** the kernel, the device tree, and every other byte are unchanged
- **AND** a readback that doesn't match writes QIDI's bytes back and the install goes on

#### Scenario: Any other boot partition
- **WHEN** the boot partition doesn't hold such an image
- **THEN** nothing is written, and the install says it kept QIDI's boot logo and why

#### Scenario: Uninstall
- **WHEN** Valve Oil is uninstalled and the partition holds what Valve Oil wrote
- **THEN** QIDI's bytes are written back from the saved partition and verified, and the record and the saved partition are removed
- **AND** a partition changed since Valve Oil wrote it is left as it is

#### Scenario: The boot animation
- **WHEN** the printer boots with the animation installed
- **THEN** it plays from shortly after local file systems are mounted until a touchscreen app process exists, at most 2 minutes, and ends on its first frame, which is the boot logo
- **AND** it draws nothing while a QIDI firmware update or an install shows its own screen, or when the touchscreen app already runs
