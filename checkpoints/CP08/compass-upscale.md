# Compass artwork restoration

## Correction after visual feedback

The first restoration was visually wrong: compassface's original alpha contains mostly markings and a faint texture, while the generated master included a complete opaque brass disk and another rim. Fitting that disk to the sparse original alpha bounds (91x106) made it oval; rotation exposed the unrelated underlying housing. The previous two-view smoke check missed this defect.

Revision 2 uses a separate transparent rose/lettering overlay with no disk, rim, ticks or second center rivet. It is uniformly scaled by 0.61 and registered by its actual rose intersection (625,630) to the native canvas pivot (512,512). The housing uses a circular 864x864 placement centered on the same pivot. Needle, objective arc/beads, damage effects, native rotation logic and HUD rectangles remain unchanged.

Built-in Imagegen edit prompt: correct the previous face into only a transparent eight-point charcoal engraved rose with narrow aged-brass edge highlights and labels N, NE, E, SE, S, SW, W, NW; delete the whole brass disk, outer rings/ticks and central rivet; genuine transparency between all elements and within letters; equal cardinal rays, shorter diagonal rays, symmetric placement, orthographic view, no perspective/oval distortion, no shadow or background. Inputs: previous generated face as edit target and original face as reference. Selected master: generated-local/hud-upscale/compass/generated/compassface-r2.png. Prepared artwork and packages remain in the paths below.

tools/test_compass_art.py captures isolated native UHD/HUD 1.66 views at yaw 0/90/180/270 and pitched diagonal views in AA, plus opposite headings in SH/BT. This checks actual compositing and common pivots, not just each layer's bounds. The original revision is documented below for history; its face registration is superseded.

Revision 2 installed from source 6e164137 as batch compass-r2. AA six views, SH two views and installed BT two views visually inspected: common center, stable circular housing and unobscured housing texture between the rotating markings. Evidence: compass-r2-tests.json. Deployment preserved all 80 active-profile files, 9072 original files, 9000 runtime-base files and eight MP1 inputs. Rollback: generated-local/widescreen/backups/compass-r2. Screenshots: artifacts-local/CP08-Compass-Corrected-UHD.zip. No merge or personal acceptance claimed.

## Original revision

Five separate compass sprites restored with the built-in Imagegen tool: compassback, compassface, compassneedle, compassobjarrow and compassobjball. Sources are the effective local AA HUD textures shared by the add-ons. Generated masters are retained under generated-local/hud-upscale/compass/generated. Package preparation aligns each alpha silhouette to its original source bounds at 8x resolution: four 1024-square textures and one 128-square target dot. Near-invisible generated alpha speckles are excluded from bounds measurement. The disk keeps its original asymmetric silhouette and all existing runtime pivots.

No HUD layout, rotation logic, mission-direction stats, damage timing or gameplay code changes. Original compasspain and compasspainblank shader effects remain. The unused compass.tga sheet and multiplayer radar graphics are not replaced. Existing alpha shader semantics are preserved; high-resolution textures allow mip filtering. Each campaign receives the same five assets in a separate local zzzzzzzz_AC_Compass.pk3. Original packages are untouched.

## Generation prompts

Built-in tool, transparent_background=true, one image per call, original matching layer as edit target. Prompts requested faithful restoration, genuine alpha, original framing/orientation and aged brass colors:

1. Face: faithful high-resolution restoration; N top, E right, S bottom, W left and diagonal NE/SE/SW/NW; exact original silhouette, compass-rose geometry and lettering placement; source bounds x18..109 y10..116 on 128 grid, center (64,64); fine engraving and subtle aged metal; no redesign, extra lettering, additional needle or background.
2. Back: dull aged bronze/brass, fine rim tick marks and blank mottled metal center; source bounds x10..118 y9..118; no rose, letters, needles or new features; original center, orientation and margins; flat orthographic sprite, no cast shadow.
3. Needle: slim vertical shaft, small lance-shaped top tip, circular pivot and rounded lower counterweight; source bounds x59..69 y27..99, pivot (64,64); roughly seven times taller than wide; worn beige brass; no disk, lettering, extra needles or background.
4. Objective arc: thin inverted-U aged bronze arc with rounded ends and a small upright beige brass arrow and round stud at top midpoint; source bounds x21..108 y10..48, center x64; bottom three fifths transparent; original curvature and symmetry, no disk, letters or other objects.
5. Objective bead: small round polished amber/brass bead, dark warm rim, cream upper-left highlight and darker lower edge; original simple circle and palette; source bounds1..15 in16square; no ornate jewel, letters, background, shadow or extra shapes.

Exact source/target bounds and generated-master SHA256 values are recorded in generated-local/hud-upscale/compass/packages/package-report.json. Raster masters and game assets remain local, excluded from GitHub.

## Verification

Isolated native screenshots at 3840x2160 and ac_hud_scale=1.66; AA m2l1, SH t1l3 and BT e3l1 (after a 30-second intro wait). Add-on capture commands turn the view between screenshots. Inspect compass overlap, direction change and transparent edges. This is visual smoke coverage, not exhaustive mission/objective/damage-state acceptance. Package deployment uses --hud-packages and preserves engine, fonts, existing artwork and active player profile, with rollback metadata.

Installed source 4bf9f1aed064eb67a068567fa4bf231079e06b9c, batch compass-r1. Deployment verified 9072 original files, 9000 runtime-base files, eight MP1 files and all 80 active-profile files unchanged. Rollback: generated-local/widescreen/backups/compass-r1. Installed no-overlay UHD capture: compass-installed-r1. Source push verified; no merge or personal acceptance claimed.
