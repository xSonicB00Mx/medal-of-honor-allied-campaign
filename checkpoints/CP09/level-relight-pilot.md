# CP09 - level-lighting pilot withdrawn

The user rejected the overall lighting change on 2026-10-31 because it altered
the game's appearance too much. The explicit request is to roll it back and
wait before exploring further changes.

- Implementation commit `e29b1d533ffd3dd57bd6c159e590d284958edac8` is reverted.
  Renderer, CMake and tools match pre-pilot commit `69b26086` exactly.
- Regular CP08-r1 and CP09-r1 runtimes were never modified by the pilot.
  Both retain executable SHA-256
  `f567924a3a3dbb671056a6136dc7a3d43bd6744e058622be269cf7f1eed1ee47`.
- The local build executable is restored from that same verified regular
  executable. No recompilation or fresh gameplay test is claimed.
- The isolated pilot runtime and both Before/After launchers are archived in
  `generated-local/CP09/relight-withdrawn`; no active pilot starter remains.
  Existing isolated test profiles, screenshots and bake data are historical
  reference only. Nothing was deleted from the personal profile.
- Personal files are hashed before/after rollback and remain unchanged.
  No game process was running at rollback.
- Positive feedback: the shadow beneath the vehicle reduced its previously
  flat appearance. This is recorded for future discussion only; no separate
  vehicle-shadow feature was requested or implemented in this rollback.

The original implementation/validation report remains in Git history and in
the ignored rollback archive. Returning to the ordinary launcher needs no
additional restoration. No merge or user acceptance is implied.
