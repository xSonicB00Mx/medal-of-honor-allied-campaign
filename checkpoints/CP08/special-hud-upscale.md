# Direction marker, special indicator and objective panel artwork

Four built-in Imagegen masters replace the red/brass directional triangle, empty and completed objective boxes (256x256), and objective backdrop (1024x1024). The panel is deliberately quiet: pale fine-grain texture receives the existing dark translucent tint. Native rectangles, text wrapping, current-yellow/completed-grey colors, fade timing and shader definitions remain unchanged. No engine/gameplay changes or rebuild.

SH/BT red_mask is a technical layer of the AA-gun indicator, not multiplayer artwork. Its red coverage is now derived exactly from the installed 1024x1024 clip_aa_gun alpha. Green/blue remain zero and alpha opaque, as required by the existing additive shader. This prevents the old mask from protruding beyond the renewed gun silhouette. Artillery team icons and lock_icon are multiplayer-only and excluded. The directional-arrow asset has no confirmed active SP caller; it is prepared and tested using an explicit diagnostic HUD element, without adding gameplay behavior.

## Local assets and reproducibility

Masters: generated-local/hud-upscale/special/generated/{directional_arrow,emptybox,filledbox,objectives_backdrop}.png. Prepared textures: sibling prepared directory, including red_mask.png. tools/package_special_hud.py trims generated margins, registers sprites to original normalized rectangles, validates the installed gun dependency byte-for-byte and writes three campaign packages. PNG masters, TGA payloads and PK3s stay local/ignored.

Built-in Imagegen prompts (one call per asset, no CLI):

- Direction: faithfully restore the original upward red-enamel triangle with thin aged-brass rim and dark inset; orthographic, crisp geometry, original palette, transparent outside, no text/glow/external shadow.
- Empty box: restore original square with very thin straight aged-brass beveled rim, dark charcoal-olive empty inset, restrained texture, no marks/text/perspective, transparent outside.
- Completed box: edit the generated empty box, preserving frame and materials; add two thin diagonal aged-brass strips forming X inside the frame, small endpoint gaps, no checkmark.
- Backdrop: flat evenly lit pale neutral-grey matte paper surface with extremely subtle fine grain; opaque, no text/borders/seams/stains/objects/vignette/folds; quiet nondirectional texture to tint dark behind readable objectives.

Selected outputs: exec-cc876c1b-54bd-4a16-8fed-ac58d48c0845, exec-f46e4cd0-1ca6-4702-a515-29abd39b0805, exec-7ec13669-5b21-4784-a941-192f82d76f45, exec-39661164-a75d-4dc5-98de-098ebf318c98. Copied from Imagegen storage into the workspace. Original references were the extracted AA assets. Package report records master and package hashes.

## Verification

tools/test_special_hud.py uses isolated profiles at UHD, HUD 1.66 and 1.0. Native addobjective/+scores exercise completed, current, additional open, hidden and wrapped-text states. The diagnostic shader gallery shows the triangle and three alpha levels of the SH/BT gun overlay. This is visual/registration verification, not a full mission or actual-emplacement heat-cycle test. AA aa-r1 and SH sh-r2 passed; screenshots visually reviewed. The first fixture's low-alpha marker was invisible, so the fixture was corrected to show it at alpha 1 and keep all indicators within the scaled viewport. No production shader change was needed.

Installed batch special-hud-r1 from 563f43ca. Installed BT bt-installed-r1 passed, with native objective panel and all three diagnostic overlay levels visually reviewed. Results: special-hud-tests.json. Integrity verification preserved 9072 original files, 9000 runtime-base files, eight Max Payne input files and 80 personal-profile files; all 59 owned runtime hashes match after installation. Rollback: generated-local/widescreen/backups/special-hud-r1. Local update: artifacts-local/CP08-r1-special-hud-r1-update.zip. Eight UHD captures and a fixture explanation: artifacts-local/CP08-SpecialHUD-UHD-Screenshots.zip.

Personal acceptance and merge remain open.
