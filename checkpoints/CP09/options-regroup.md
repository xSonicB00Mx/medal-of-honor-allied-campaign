# CP09 - options regrouping, 2026-11-03

The growing options menu mixed rendering controls with gameplay and kept TAA
and object motion blur on a separate page. The user requested a clearer layout
with graphics options together.

## Result

Two consistently styled category tabs with a highlighted current page:

- **Interface & Gameplay**: automatic scaling, menu font size, HUD size/safe
  area/outline, hit flinch and Breakthrough drop restrictions. The existing
  uppercase ADDITIONAL OPTIONS heading remains for the gameplay section.
- **Graphics & Effects**: TAA, ambient occlusion, dynamic model shadows and
  object motion blur in the left column; all four blood effects in the right.

Both pages use the same title, background, margins, footer and visual grouping.
Short descriptions explain effects. The old extra AA & Motion button is gone.
Internal ac_scaling/ac_temporal names and existing cvar bindings remain for
compatibility. No renderer/gameplay behavior or saved preference is migrated.
Page defaults resets only that page; moving to another page never resets it.
Hit flinch and object blur retain their exclusive 10-percent steps.

## Validation

`generated-local/CP09/options-regroup-r2/result.json`:

- Real native checkbox, slider, tab, Defaults and Back callbacks in AA 1920x1080,
  SH 1280x960, BT 3440x1440 and AA 3840x2160.
- Both pages at full/reduced menu font size, invariant frame geometry and no
  overlapping/clipped widget rectangles. Native screenshots visually inspected.
- All 15 settings change and persist; navigation preserves the chosen values.
  Graphics defaults preserve interface/gameplay settings; both page defaults
  together restore the established defaults. Both percentage sliders visit
  precisely 0,10,...,100 during dragging.
- Six captures per case. The initial r1 harness clicked a slider arrow rather
  than its track; corrected test drag initialization. No game-code workaround.
- Existing temporal lifecycle test passes with updated menu coordinates in
  `generated-local/CP09/options-regroup-ingame`: in-game navigation, graphics
  restart, map switch, FOV, 4:3/16:9 and unchanged temporal rendering.
- All 683 personal profile files, including saves and settings, are hash-identical.

Only menu resources and packaging/test/deployment helpers changed. The packaging
helper now includes both pages. The deployment helper supports options-only
updates while preserving executable/DLL contents and engine provenance.

## Delivery

Source commit: `4a44de98`. Exact tested three campaign packages share SHA-256
`d07415458825d3c80d55c5ec50524eb36112e91dcb56ec8f47aa4f9670f7107d`.
Installed in CP08-r1 and CP09-r1: only the three options packages per runtime
were replaced. Deployment verified 9,086/9,090 runtime files, 9,072 original
inputs and all 683 unchanged personal files. Engine remains f567924a; game,
cgame and artwork are unchanged. Evidence:
`generated-local/CP09/options-regroup-r2/deployment.json`.
Previous packages/manifests are backed up under that folder's `rollback`.
No campaign playthrough or user visual acceptance is claimed.
