# Medal of Honor: Allied Campaign

**Allied Assault, Spearhead and Breakthrough in one chronological single-player campaign.**

Allied Campaign is a single-player mod and customized [OpenMoHAA](https://github.com/openmoh/openmohaa) fork. It connects the three games through shared progression, an Operations map, unified options and a refreshed widescreen interface. The current content baseline includes **War Chest Restored (WCR)**.

## What changes

- **One campaign:** 15 operations arranged chronologically, ending in Berlin. Completed operations remain available for replay without resetting campaign progress. Credits play at the end of the combined campaign.
- **Operations map:** two regions, selectable difficulty, Roman mission numbers and grouped markers for overlapping locations.
- **Mission List:** replay completed individual levels with standard equipment and score tracking. Kills, headshots, grenade multikills, accuracy and friendly fire contribute to the result. Each level records difficulty-specific best scores and its latest score. Saving and loading are disabled during score runs.
- **Briefing Room:** revisit briefings as they unlock through campaign progress.
- **LOADOUT:** choose portable weapons from all three games for completed Operations replays. New campaign missions and Mission List score runs retain their normal equipment. The former multiplayer entrance opens LOADOUT.
- **Shared presentation:** campaign-wide settings, widescreen menu and briefing artwork, Courier New Bold text, higher-resolution HUD elements, adjustable HUD size and a separate menu font-size control.
- **Combat feedback:** dynamic spread-based crosshairs, blood mist, drops, surface stains and persistent character wounds, including visual corpse-hit effects. A mortar impact guide helps with aiming.
- **Model shadows:** filtered dynamic shadows for NPCs and pickups, with a shared live toggle. The environment receives shadows; new environment shadow casting is outside the current scope.
- **Allied Campaign Options:** organized display, HUD and blood settings; hit flinch adjustable from 0% to 100% in 10% steps; optional original Breakthrough drop restrictions.

Multiplayer is outside this mod's scope. Upstream networking and server code remain in the source tree, but they are not an Allied Campaign feature or a tested release target.

## Project status

The planned feature set is complete. Work is now focused on bug fixes, regression testing and release preparation under **Checkpoint 9 (CP09)**.

A local Windows x64 / OpenGL 1 candidate is available in the development workspace. Technical checks and selected native game tests have passed, but the complete campaign playthrough and remaining performance/long-duration checks are still open. This is **not yet a generally installable public release**.

See [current status](STATUS.md), the [CP09 report](checkpoints/CP09/REPORT.md) and the [player test guide](checkpoints/CP09/PLAYER-TEST.md) for evidence and outstanding work. A passing source build is not a full campaign acceptance test.

## Requirements and installation

The currently tested setup uses:

- Medal of Honor: Allied Assault **and both expansions**, Spearhead and Breakthrough;
- the WCR content baseline recorded in [third_party/wcr](third_party/wcr/);
- Allied Campaign's matching `openmohaa.exe`, `game.dll`, `cgame.dll` and mod packages;
- Windows x64 with the tested OpenGL 1 renderer.

The mod packages alone are not sufficient with an unmodified OpenMoHAA executable. Compatibility without WCR, with other WCR revisions, with other platforms or with the OpenGL 2 renderer has not been established for this project.

**Cloning this repository does not provide a playable installation.** Original game data, imported third-party assets, generated artwork packages and personal profiles are excluded. The local candidate workflow operates on an already imported and verified installation; it is not a universal installer for arbitrary game folders.

For an already prepared development workspace, follow [local installation and launch instructions](checkpoints/CP09/INSTALLATION.md). Its workspace launcher can use the existing personal profile; its standalone runtime launcher creates a separate profile. Keep these paths distinct and back up saves before changing builds.

A public release still needs a separately prepared distribution package and documented handling of externally supplied content. Do not upload the complete local runtime or assume that a package containing `AC` in its name contains only original project assets.

## Source and development

| Location | Purpose |
| --- | --- |
| `code/` | Customized engine, game and client-game code |
| `mod/` | Allied Campaign definitions, UI sources and project scripts |
| `tools/` | Build, packaging, validation and isolated test tools |
| `tests/ac_visual/` | Asset-independent C++ visual-system tests |
| `checkpoints/` | Implementation reports, test evidence and acceptance limits |
| `third_party/` | Content provenance and integration metadata |
| `docs/` | Inherited OpenMoHAA technical documentation; not all features described there are supported by Allied Campaign |

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change. The [Windows build helper](tools/build-cp00.ps1) and [validation workflow](.github/workflows/cp00-validation.yml) describe the current source-only build. Building the binaries does not import or package the required game assets.

## Reporting problems

Report Allied Campaign issues in [this repository](https://github.com/xSonicB00Mx/medal-of-honor-allied-campaign/issues), rather than assuming they are OpenMoHAA bugs. Include the build/commit, campaign and map, how the mission was started, reproduction steps and relevant logs or screenshots. See the [bug-report checklist](CONTRIBUTING.md#reporting-a-bug).

## Credits and licenses

Allied Campaign builds on OpenMoHAA and its contributors, with the engine heritage and third-party components retained in this repository. WCR remains part of the tested content baseline. Asset provenance and integration records are kept under [third_party/](third_party/) and in the checkpoint reports; map attribution is documented in [GEOGRAPHY.md](mod/campaign/GEOGRAPHY.md).

The engine source retains its existing GPL licensing; see [COPYING.txt](COPYING.txt), source-file notices and component-specific licenses. These source-code licenses do not establish redistribution permission for original game data, WCR, Max Payne resources, fonts or other imported artwork. Preserve the applicable notices and review content provenance when preparing a release.

This is an independent fan project, not an official Electronic Arts release. OpenMoHAA is the upstream engine project, not the maintainer of this fork's features or test results.
