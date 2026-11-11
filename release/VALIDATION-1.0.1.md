# Allied Campaign 1.0.1 validation

Packaging-only maintenance release, November 11, 2026.

- ZIP: `Medal-of-Honor-Allied-Campaign-1.0.1-Windows-x64.zip`
- Size: 460,175,862 bytes
- SHA-256: `156b236d2fe98433acfe64edf6e39e219ff9b6261474fd0eac045d099d0d6fbb`
- Packaged source: `f148d3106f17d248c7823a6a650b32818989fef3`
- Engine/game/cgame binaries and save format are unchanged from 1.0.0.

## Package equivalence

The 24 AA, 21 SH and 23 BT archives became one `zz_AlliedCampaign.pk3` in each game folder. For every folder, the full effective archive view, including the original game and WCR packages, has identical file hashes and identical enumeration order before/after consolidation. This covers 18,262 AA, 7,676 SH and 7,831 BT resolved paths. The three new archives contain 1,165, 810 and 509 winning AC members respectively.

Member order deliberately follows the old descending package priority and central-directory order. Alphabetically sorting merged members would change shader enumeration. Native startup logs independently confirmed identical shader ordering for all three game contexts.

## Installation and gameplay checks

- CRC and all 30 manifest-listed file hashes passed for the final ZIP.
- Fresh extraction over an independent WCR copy passed.
- A real 1.0.0 upgrade removed exactly 68 known legacy AC packages. Running the updater again succeeded without further changes.
- All 9,000 original/WCR files remained unchanged.
- Native AA `m1l1`, SH `t1l1` and BT `e2l2` launches completed, with rendered screenshots reviewed.
- A separate copy of the creator's current `t2l30000` save was accepted and rendered the `t2l3` scene after its loading screen/intro transition. The original 867 personal-profile files remained unchanged.
- The exact shipped CMD launcher completed its startup/exit marker.
- Seven synthetic updater cases passed: fresh, upgrade, modified old package, unknown old package, missing replacement, corrupt replacement and unsafe path. Failed preflight cases left all files unchanged; successful cases preserved original/WCR fixtures and profile data. Repeat runs were safe.
- Source unit tests and metadata/campaign validators passed. Windows CI passed for the packaged source (run 42933572882).

The initial save-test invocation used an invalid console command; it was rejected as a test-harness failure. The final verification uses `loadgame`, requires `AC_SAVE_ACCEPT context=1 map=t2l3`, and checks the actual scene after the diagnostic loading screen is closed. Menu/loading-screen captures were excluded. No game code or shipped gameplay assets were changed during this correction.

These checks cover the tested WCR baseline and the packaging migration. They do not claim universal compatibility with unrelated mods or modified legacy packages; the updater intentionally stops for manual review in those cases.
