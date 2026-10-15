# High-resolution ammunition HUD artwork

18 separate transparent Imagegen restorations provide 19 sprites, including the smaller pistol-cartridge variant. Prepared canvases and alpha bounds are eight times the original size. Existing HUD rectangles, ammo stats, weapon scripts and gameplay remain unchanged. The two mine-counter pairs are excluded from this pass. Unused magazine artwork referenced only in commented-out HUD definitions is not replaced.

Local inputs: generated-local/hud-upscale/ammo/source. Selected built-in Imagegen masters: generated-local/hud-upscale/ammo/generated. Aligned PNGs: generated-local/hud-upscale/ammo/prepared. Campaign packages and hash/bounds reports: generated-local/hud-upscale/ammo/packages. All raster assets remain local and excluded from GitHub.

## Rendering

The first isolated capture exposed an engine convention: statbar_tileshader divides UV extents by uploaded texture dimensions. Merely increasing resolution therefore magnified the cartridge and lost repetition. The package preserves each effective original shader and adds tcMod scale 8 8 to compensate for the eightfold resolution. Existing alpha semantics are retained; mip filtering is enabled without picmip reduction. Implicit shaders use the renderer's equivalent global color/alpha blend. The AA-gun and detector graphics use fixed rectangles and do not receive the tile correction. No engine rebuild or code change is required.

## Generation prompt set

Built-in Imagegen, one original sprite as edit target per call, transparent_background=true. Shared instructions: faithful high-resolution restoration; preserve source silhouette, proportions, orientation and muted WWII material palette; crisp restrained detail; genuine transparent alpha; no text, background, shadow, extra objects or redesign. Per-asset subjects:

- clip_rifle: horizontal copper pointed bullet left, bottleneck brass casing and rim right.
- clip_pistol: short horizontal rounded copper bullet left, straight brass case and rim right; reused for clip_pistol_small.
- clip_shotgun: horizontal deep-red paper shell, flat crimped end left, brass base right.
- clip_bazooka: olive rocket, broad pointed warhead left, narrow shaft and fins right.
- clip_panzerschreck: olive-grey stepped projectile left, tapered rear shaft and circular flange right.
- clip_fraggrenade: dark olive segmented pineapple grenade, original top fuse/lever and tilt.
- clip_steilhandgranate: metal head upper left, slender wooden handle lower right.
- clip_cangrenade: upright slightly tilted pale olive smoke can and original top lever.
- clip_flak: very narrow vertical shell, black pointed projectile top, long brass case below.
- clip_mortar: vertical dark-red teardrop head, slender shaft and fins below.
- clip_nebelwerfer: thin horizontal grey rocket, blunt cone left, banded body, flat right base.
- clip_pzb41: horizontal dark olive pointed projectile left, long grey metallic case right.
- clip_riflegrenade: horizontal dark pointed nose left, golden brass body and flat right base.
- clip_piat: broad rounded silver-grey head left with red band, shaft/fins right.
- it_w_bomba: compact diagonal segmented silver-grey grenade with muted red lower portion.
- it_w_bombabreda: compact diagonal segmented silver-grey grenade with ochre yellow lower portion.
- clip_aa_gun: original compact olive antiaircraft gun silhouette, barrels upper left, shield right.
- clip_mine_detector: circular detector disk lower left, long olive shaft/handle upper right.

## Verification scope

tools/test_ammo_art.py uses isolated profiles and actual weapon selection, firing and reload commands at 3840x2160 with ac_hud_scale=1.66. Native captures cover AA m2l1, SH t1l3 and BT e3l1. This is HUD visual smoke coverage, not exhaustive gameplay acceptance of every weapon or mounted emplacement. Special artillery sprites are packaged but not all are exercised at an actual emplacement. User acceptance and merge remain open.

AA aa-r2 visually verified Garand 8 -> 7 rounds, pistol, shotgun, launchers and grenades. SH sh-r2 verified the staggered SMG counter 30/120 -> 26/120 -> 30/116 after reload, plus smoke grenades. The earlier +reload diagnostic command was invalid; corrected to the native reload command before the successful run. BT captures verify PIAT and the shared ammunition counters. Source/policy validators and git diff --check passed.

Installed batch ammo-r1 from source 967cc389. Deployment verified 9072 original files, 9000 runtime-base files, eight MP1 input files and all 80 active-profile files unchanged. Existing compass/font packages and binaries are retained. Rollback metadata: generated-local/widescreen/backups/ammo-r1. Delivery: artifacts-local/CP08-r1-ammo-r1-update.zip.

Final installed BT capture bt-installed-r1 also verified both Italian grenade variants after allowing the weapon-give event to finish before selection. No test package overlay was used. Selected full-resolution captures are bundled in artifacts-local/CP08-Ammo-UHD-Screenshots.zip.
