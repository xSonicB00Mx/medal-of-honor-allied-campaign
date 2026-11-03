# CP09 - options regrouping, 2026-11-03

The growing options menu mixed rendering controls with gameplay and kept TAA
and object motion blur on a separate page. The user requested a clearer layout
with graphics options together.

## Result

A full-width page navigation bar, clearly separate from the content columns,
shows PAGE 1 OF 2 / PAGE 2 OF 2, a centered current-page title and previous/next
arrows. Unavailable directions are dim and non-interactive:

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

## Follow-up: separate navigation from content

The user found that the two wide category tabs looked like headings for the
columns underneath. Replaced them with one unified page navigation strip.
Only the current page name is shown, centered between arrows; the explicit
page counter establishes that the controls switch whole pages. All options,
column contents, cvars, scoped defaults and menu-stack behavior are retained.

Source `a8bdf3ec`; shared package SHA-256
`0c79f800e8c2c403d68ebf904e67c036a42358abe9210447bf26893efa12a428`.
`generated-local/CP09/options-page-navigation/result.json` passes the same
four native layout/control/navigation cases (AA 1080p/UHD, SH 4:3, BT ultrawide),
including both font sizes, discrete sliders and defaults. Both pages visually
inspected. All 683 personal files remain unchanged. Deployment evidence:
`generated-local/CP09/options-page-navigation/deployment.json`.
The previous delivery paths and hashes above describe the initial layout.
