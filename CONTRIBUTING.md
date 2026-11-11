# Contributing to Medal of Honor: Allied Campaign

Allied Campaign combines Allied Assault, Spearhead and Breakthrough into one single-player experience using a customized OpenMoHAA engine and a verified WCR content baseline.

The planned feature set is complete. Current work focuses on **bug fixes, regression testing, documentation and release preparation**. Discuss new features or changes to gameplay balance with the maintainer before implementing them.

These guidelines apply to this fork. Contributions submitted to OpenMoHAA itself must follow that project's own rules.

## Reporting a bug

Use [this repository's issues](https://github.com/xSonicB00Mx/medal-of-honor-allied-campaign/issues). Check existing reports first, then include:

- Allied Campaign build ID or commit, plus the engine version from the log;
- campaign (AA, SH or BT), mission and map name;
- launch mode: campaign progression, Operations replay, custom LOADOUT, Mission List score run or loaded save;
- difficulty, relevant options and any additional modifications;
- expected behavior, actual behavior and repeatable steps;
- whether a fresh level start and a loaded save behave differently;
- operating system, GPU, resolution and HUD/menu font scaling for display problems;
- a relevant `qconsole.log` excerpt, crash information and screenshots where useful.

Remove sensitive local paths or other personal information from shared logs. Do not commit save files or complete profiles. If a save is needed to reproduce a bug, arrange a separate test copy with the maintainer.

Use the matching Allied Campaign binaries and packages when reproducing an issue. Replacing only the executable with an upstream development build is not a valid compatibility test for the fork.

## Protect the campaign and the player's data

- Test in independent, ignored runtimes and profiles. Never run destructive tests against a personal save, progress file or score record.
- Keep original installations and imported sources read-only. Do not use hardlinks or junctions that allow tests to modify the source installation.
- Preserve the pinned WCR integration. Do not silently remove, replace or update WCR or restore its scripts to vanilla versions.
- Operations replays must not roll back campaign progress. Custom LOADOUTs belong only to completed Operations replays; Mission List runs retain standard equipment.
- Preserve save compatibility where possible. Any unavoidable migration or incompatibility must be documented and reviewed before deployment.
- Visual hit effects must not accidentally change damage, bullet penetration, death behavior, random gameplay outcomes or item drops.
- Keep UI text in English. Existing project discussion and checkpoint reports may be in German; English is preferred for shared technical documentation and code comments.

## Preparing a change

1. Read [STATUS.md](STATUS.md), the relevant checkpoint report and any applicable [AGENTS.md](AGENTS.md) instructions. [PLAN.md](PLAN.md) records the original scope; later user decisions and checkpoint reports explain subsequent changes.
2. Confirm the appropriate base branch with the maintainer. Active checkpoint work may be ahead of `main`. Use a focused topic branch; do not push directly to `main` or rewrite shared history.
3. Match the surrounding code style and keep the patch limited to the problem. Preserve copyright headers, licenses and attribution.
4. Update the canonical source or generator when changing packaged data. Do not fix only an ignored runtime copy. Keep original/generated asset packages out of Git.
5. Record what you tested, what passed and what remains untested. Keep documentation consistent with the delivered behavior.

## Build and validation

The tested development target is Windows x64 with Visual Studio 2022 and OpenGL 1. See the [build helper](tools/build-cp00.ps1) and [CI workflow](.github/workflows/cp00-validation.yml) for configuration and parser-tool requirements. The inherited [compilation reference](docs/markdown/04-coding/01-compiling.md) provides engine background; its broader platform claims are not an Allied Campaign acceptance matrix.

Source and metadata checks, run from the repository root with Python 3:

```text
python tools/validate_cp00.py
python tools/validate_campaign.py
python tools/generate_weapon_policy.py --check
```

Asset-independent visual tests, with CMake and the Visual Studio generator available:

```text
cmake -S tests/ac_visual -B build-local/ac-visual-tests -A x64
cmake --build build-local/ac-visual-tests --config Release
ctest --test-dir build-local/ac-visual-tests -C Release --output-on-failure
```

Run checks appropriate to the change. Documentation-only edits need link and diff checks, not a full game rebuild. Engine or gameplay changes require the affected binaries to be rebuilt and relevant tests to run. Shared behavior should be checked in AA, SH and BT; UI changes should cover relevant aspect ratios and scaling settings.

Native test scripts often require a prepared local runtime, external assets and particular fixtures. Read their inputs and output paths before running them; they are not all usable from a fresh clone. Use isolated profiles and compare protected data before and after testing. Known diagnostics must be identified explicitly, not silently counted as an error-free run.

Keep source validation, compilation, native tests, natural playthrough acceptance and merge approval separate. Refer to the [CP09 report](checkpoints/CP09/REPORT.md) for the current limits.

## What belongs in Git

Commit project source, build/test tools, documentation and suitable metadata. Review staged paths explicitly before committing.

Do not commit original game files, WCR archives, Max Payne resources, generated game/artwork packages, compiled binaries, local toolchains, personal configurations, saves, credentials or runtime backups. Keep these in the ignored local work areas. A generated package's project filename is not evidence that all of its contents may be redistributed.

Changes involving artwork or imported resources must document their origin and how they are packaged. Preserve third-party notices and consult the maintainer before adding external content to a distribution.

## AI-assisted contributions

This project is developed with AI assistance, so AI-assisted code and documentation are permitted here. Contributors remain responsible for understanding, reviewing and testing their changes, checking provenance and describing important limitations. Disclose material AI assistance in the pull request; do not invent test results, approvals or authorship claims.

This does not override the contribution policies of OpenMoHAA or any other upstream project.

## Pull requests and review

A pull request should explain the concrete problem, resulting behavior, affected campaigns, relevant validation and any save/content compatibility risks. Include a screenshot for meaningful UI changes when it can be shared appropriately. Link the issue or checkpoint report where applicable.

Keep changes reviewable and avoid unrelated refactors. Do not claim a clean playthrough based only on scripted fixtures, or a successful runtime deployment based only on a source build. Merging requires the maintainer's approval for that change; a successful test run alone is not merge authorization.

Contributions must retain the applicable project and component licenses. See [COPYING.txt](COPYING.txt) and the notices in the files you modify.
