# Inventory artwork restoration

The single-player inventory pass targets the real texture/shader references in the effective AA, SH and BT packages, including War Chest Restored additions. Fifteen object restorations and 32 counter variants use 512x512 RGBA canvases, eight times the original 64x64 resolution. Multiplayer artwork is excluded.

## Retained originals and limits

The built-in provider refused the grey-green identification booklet and two officer-uniform requests. Both booklet variants and all three uniform variants are retained unchanged; no censored/modified substitute or unapproved API fallback is used. These five objects are not claimed as upscaled. The unused item_binoculars label texture is not replaced: the live item_binoculars shader samples binoc3. Empty-slot and highlight frame textures remain unchanged. Existing shader references to radar/uboat/STG44 documents without matching source textures are outside this restoration pass.

## Packaging

tools/package_inventory_art.py uniformly fits each generated sprite within eightfold original alpha bounds, preserving proportions and the original center. No per-axis stretching. Fixed native HUD rectangles, scripts, inventory slots, item behavior and fade timing remain unchanged. Effective original shaders, including oneMinusVertex alpha, are retained with mip filtering enabled. Implicit shaders use the renderer's global color/alpha blend. Unlike tiled ammunition bars, inventory sprites require no UV scaling.

Counters are typeset locally in natural Courier New Bold with yellow fill and dark outline/shadow. Twelve number overlays (0-9, 9+, !?) plus ten demolition-charge and ten sticky-charge composites share the same restored base sprites. Composite counters fit their original bright-yellow glyph bounds; sticky-charge numbers keep their smaller size near the bottom. This makes count transitions visually consistent. No font file is redistributed in Git.

## Saved local assets and generation mode

Built-in Imagegen edit mode, one source sprite per request, transparent_background=true. No external API/CLI generation. All raster assets and packages stay local and excluded from Git:

- Original extracted sprites: generated-local/hud-upscale/items/source.
- Selected masters: generated-local/hud-upscale/items/generated.
- Registered 512x512 sprites: generated-local/hud-upscale/items/prepared.
- Campaign packages and hashes: generated-local/hud-upscale/items/packages/package-report.json.
- Asset inventory and reference audit: generated-local/hud-upscale/items/inventory.json and references.json.

## Prompt set

Shared prompt: faithful high-resolution restoration of the supplied low-resolution WWII inventory sprite; preserve silhouette, relative proportions, viewing angle and muted vintage material colors; restrained material detail/edge highlights; one isolated icon on genuine transparent alpha; square canvas with clear padding; no cast shadow, scene, extra objects, modern redesign or new labels.

- binoc3: black two-barrel field binoculars, original diagonal three-quarter orientation.
- bangalores: three parallel narrow olive tubes, diagonally lower left to upper right.
- battery: upright olive radio battery, two black top terminals, small dark data plates.
- clipboard: brown board, pale paper manifest, columns and silver clip, original clockwise tilt.
- explosives: yellow demolition-charge bundle in black carrier/straps, small top wire loop; no count.
- gasmask: dark grey-green front-facing rubber mask, brown round eyepieces and lower cylindrical filter.
- item_camera: narrow horizontal silver/beige spy camera with black left recess and two right circular features.
- item_radio_explosive: olive box with left antenna, front dial, black top controls and pale right inset.
- radio1: narrow diagonal olive handset, two circular front features and short black antenna.
- wirecutters: steel cutting head upper right and burgundy handles lower left.
- item_tigerii_manual: worn horizontal beige booklet with original small monochrome panel and tiny red title.
- item_battleplans: overlapping monochrome reconnaissance photographs with off-white borders.
- item_stickybomb: mottled blue/olive cloth-wrapped charge and one long pale curved fuse; no count.
- item_keys: two antique slender keys on a thin circular ring, original spread and transparent gaps.
- plunger: tan wooden detonator box, vertical shaft, reddish T handle and lid terminals.

## Verification

tools/test_inventory_art.py uses fresh isolated profiles at 3840x2160 and HUD scale 1.66. Baseline captures exercise the original inventory scripts before replacement: adding up to six items, removing an item and showing count changes in AA m2l1, SH t1l3 and BT e3l1. These scripted visual fixtures do not constitute complete mission playthroughs or personal acceptance.

Candidate AA captures visually verify all common restored items, six-slot spacing, removal, counts 3/9+/0 and coexistence with the five retained original objects. SH captures verify the sticky-charge sprite and the native demolition 3-to-2 and sticky 9-to-8 transitions. Archive CRC, all 512x512 RGBA texture dimensions, alpha extrema and shader conventions passed. Metadata/campaign/weapon-policy validators and git diff --check passed. No engine rebuild is required for this artwork-only change.

BT candidate captures verify keys, wooden plunger, sticky charge, shared inventory objects and item removal. Its original count fixture incorrectly called SH's absent democharge helper. The corrected fixture uses BT's own charges3/charges2 inventory entries; the resulting x2 icon was visually verified. Additional trial assertions on script debug messages failed despite correct captures, so those logging assertions were removed. Native game processes exited normally; failed postprocessing runs are not presented as passing harness runs. The installed smoke test below checks the corrected harness. Machine-readable evidence is inventory-tests.json.
