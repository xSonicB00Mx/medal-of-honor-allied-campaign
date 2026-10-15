# High-resolution stopwatch and fuse HUD

Five restored sprites: stopwatch case/dial and separate rotating hand (1024x1024), normal and shootable/wet fuse bases (1024x512), repeating cord (256x512). Original HUD layout, countdown events, expiry behavior and gameplay are preserved. The original 24-frame sparks and 24-frame smoke animations remain unchanged, including 48/12 fps timing and native marker size. Legacy static fusespark/fusesmoke textures are unused by these widgets and excluded.

## Imagegen assets and prompts

Built-in Imagegen edit mode, transparent background, using extracted originals as references. Final masters are in generated-local/hud-upscale/timers/generated; source textures in timers/source; registered sprites in timers/prepared. No raster artwork is committed to Git.

- stopwatchbase.png: faithful front-facing silver period stopwatch with ivory dial, red 60 at top and black 5 through 55 clockwise, original crown and upper-left side button, small subdial, no baked-in main hands. Output exec-34cd3e0b-4a21-48f8-90e6-611dca62e3b0.png.
- stopwatchhand.png: single slender vertical gunmetal needle, circular hub, short lower counterweight, transparent canvas, no dial or backdrop. Output exec-de9b52b2-ee75-4bf4-a38f-2ece800aaabc.png.
- fuse-pair.png: matching original dark mottled blue/olive fabric charge and short rightward ochre cord; second copy includes original thin red targeting reticle; transparent two-sprite sheet. Output exec-acc34f48-8c61-4693-a041-d2b02a282f81.png.
- fusetile.png: straight horizontal ochre braided cord, seamless left/right continuation, transparent above/below, no ends or additional effects. Output exec-b4b1e2f3-cc00-48f7-ab2a-c6a012694df8.png.

## Integration and verification

tools/package_timer_art.py explicitly registers dial and hand pivots to 512,512 (the original 64,64 at 8x); fixed circular radius and needle length retain native rotation. Effective original shaders keep alpha semantics; mip filtering enabled. The repeating fuse receives tcMod scale 8 8 to compensate for the renderer's texture-dimension-based tiling. The first SH preview exposed a cord thickness step at the charge; corrected tile thickness and socket registration before installation.

tools/test_timer_art.py drives actual player stopwatch events in isolated profiles at UHD and HUD 1.66. AA aa-r1 verified distinct 45/30/15-second positions, near-zero and expiry. Expansion fixtures additionally exercise shortening lit fuse, original animated spark, wet reticle/smoke and fixed wet length, then expiry. These are native HUD-event fixtures, not full mission/detonation gameplay acceptance. Package CRC, alpha/texture scope and metadata/campaign/weapon policy validators passed. No engine changes or rebuild.

Final SH sh-r2 verifies corrected cord thickness and continuous join. Installed batch timers-r1 from 16a94a06; BT bt-installed-r1 passed without a test overlay and wet fuse visually verified. Installed hashes match tested packages. Integrity: 9072 original files, 9000 runtime-base files, eight MP1 inputs and 80 active-profile files unchanged; profile checked again after final test. Rollback: generated-local/widescreen/backups/timers-r1. Local update: artifacts-local/CP08-r1-timers-r1-update.zip. Screenshots: artifacts-local/CP08-Timers-UHD-Screenshots.zip. Machine-readable tests: timer-tests.json. User acceptance and merge remain open.

## Fuse join correction, timers-r2

User screenshot exposed a hard material change and metal ferrule between the short cord and tiled cord. Built-in Imagegen edit used the existing fuse-pair as target and fusetile as material reference. Prompt: replace only both short cords with straight, constant-thickness golden tan twisted hemp matching the repeating texture; remove metal cap, dark ring, mottled knots and terminal cut face; preserve charge bodies, layout, transparency and right-hand reticle. Output exec-1f1843c2-548c-4fcc-90c8-68b91dcf611d.png is selected as generated-local/hud-upscale/timers/generated/fuse-pair.png; prior master retained in timers/revisions-r1.

sh-join-r3 passed the native UHD/HUD 1.66 harness. Normal and wet variants visually inspected in artifacts-local/HUD-Fuse-Join-r3.png: matching material and no metal band, substantially softer join. Exact package payload comparison confirms only fusebase and fusebase_shoot changed in SH/BT; AA payloads, stopwatch, tile, shaders and original animations remain byte-identical. Evidence: generated-local/hud-upscale/timers/join-r3-scope.json and sh-join-r3-test.json.
