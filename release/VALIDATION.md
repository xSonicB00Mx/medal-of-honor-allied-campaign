# Allied Campaign 1.0.0 release validation

Release acceptance: the creator completed personal playtesting and requested distribution on November 11, 2026. Public publication in the existing repository was explicitly approved.

## Artifact

- File: `Medal-of-Honor-Allied-Campaign-1.0.0-Windows-x64.zip`
- Size: 471,749,160 bytes
- SHA-256: `3a765240ab40a311d23543f1a81133f063a5b589da27e6628ef056f34db78e9c`
- Packaged source: `c4d476e7d180a2a92a88850c85cf759f405b36f7`

## Checks completed

- Archive CRC and all 94 manifest-listed file hashes verified.
- Actual ZIP extracted over a separate copy of the tested WCR installation; all 9,000 base-file hashes remained unchanged.
- Native launches and rendered screenshots verified for Allied Assault `m1l1`, Spearhead `t1l1`, and Breakthrough `e2l2`. All three exited successfully.
- The shipped directory-relative CMD launcher independently reached the main menu and completed its diagnostic exit marker using the separate `AlliedCampaign-User` profile.
- All 867 files in the creator's personal profile remained unchanged during the package tests.
- Local checkpoint/campaign validators passed. GitHub Windows CI passed for the packaged source commit (run 42928694039).
- GitHub's uploaded ZIP digest matches the local archive digest.

Tests used separate profiles, windowed rendering and diagnostic console scripts. Intro fades were cleared in the campaign smoke tests; early paused/blank diagnostic captures were excluded. These checks establish installation and rendering viability for the tested WCR base, not compatibility with every hardware configuration or other mod combination. Gameplay acceptance is the creator's independent playtest.
