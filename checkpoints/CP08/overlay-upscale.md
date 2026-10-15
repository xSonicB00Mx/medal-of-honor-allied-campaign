# High-resolution single-player optical overlays

Six textures replace the generic sniper mask, KAR98 upper/lower masks, binocular mask, camera mask and gas-mask frame. Five geometric masks use 2048x2048 pixels; the gas-mask texture uses 2048x1024. Original zoom settings, aiming center, reticle widths/gaps and existing widescreen layout are preserved. Multiplayer assets are excluded.

## Construction and integration

The optical masks contain constant RGB and geometric alpha, so tools/package_overlay_art.py reconstructs their elliptical boundaries and original soft falloff mathematically. It does not invent lens details with AI. Downsampling to the original 256x256 gives mean alpha differences of 0.14-0.50 out of 255. The native shader blend modes are retained. Package generation asserts a bounded mask difference and a transparent central aiming region in the gas mask.

The camera previously fell through to the generic sniper texture despite selecting zoomType 2. cgame now registers cameraoverlay and selects it explicitly. Its original brown mask has no sniper crosshair. Only cgame.dll changes; engine and server game DLL remain unchanged.

The gas mask uses the built-in Imagegen tool in edit mode with transparent output. Original rubber frame served as the source reference. Rejected variants had opaque lens blotches or a center bar blocking aim; the selected version has a continuous clear viewing opening and detailed brown rubber rim. The generated alpha is preserved, with only texture-size conversion for packaging.

## Imagegen prompt and saved paths

Final corrective prompt, applied to the preceding generated gas-mask frame:

> Edit target: this gas mask overlay. REMOVE THE ENTIRE VERTICAL CENTER BRIDGE, including its metal/rubber outlines. The two transparent eye holes must MERGE into ONE continuous wide transparent opening. At the center leave a wide transparent connection occupying the middle 20% of canvas width and middle 40% of canvas height. There must be absolutely NO rubber, nose bar, line, object or opacity at the center. This is an inside view game overlay, not an external portrait of a mask. Keep outer dark brown rubber material frame, top and bottom frame and rest of lens boundaries unchanged. Transparent eye opening, opaque outer frame extending to image edges. Same 2:1 aspect. No new objects.

Selected output exec-7a986fa2-0db6-41bf-8944-e432f90307b2.png is copied to generated-local/hud-upscale/overlays/generated/gasmask_overlay.png. All six final texture PNGs are in generated-local/hud-upscale/overlays/prepared. Local packages are in generated-local/hud-upscale/overlays/packages/{main,mainta,maintt}/zzzzzzzz_AC_Overlays.pk3. No image, original asset or binary is committed to Git.

## Verification and delivery

cgame RelWithDebInfo build passed (existing unrelated VectorCopy warning in cg_parsemsg.cpp). Metadata, campaign and weapon-policy validators passed. Package CRC and alpha/geometry checks passed.

tools/test_overlay_art.py equips actual Springfield, KAR98 sniper, binoculars and Spy Camera, toggles native zoom, invokes the same gas-mask huddraw commands used in m6l3d, then clears the overlay. Native isolated AA and SH tests at 3840x2160 with HUD 1.66 passed; AA 1280x960 passed. Visually checked centered reticles, optical contours, camera without crosshair, clear gas-mask center and clean removal. These are rendering/equipment fixtures, not full mission completions or combat-accuracy acceptance.

Installed batch overlays-r1 from d580996f. Integrity checks: 9072 original files, 9000 runtime-base files, eight Max Payne inputs and 80 active-profile files unchanged. Rollback: generated-local/widescreen/backups/overlays-r1. Update archive: artifacts-local/CP08-r1-overlays-r1-update.zip. Personal acceptance and merge remain open.

Final BT test bt-installed-r1 passed at UHD/HUD 1.66 using the installed runtime without candidate packages or DLL overrides; all overlay types and clearing visually checked. Post-test runtime hashes and all 80 active-profile files verified unchanged. Machine-readable evidence: overlay-tests.json. Fifteen full-resolution screenshots: artifacts-local/CP08-Overlays-UHD-Screenshots.zip.
