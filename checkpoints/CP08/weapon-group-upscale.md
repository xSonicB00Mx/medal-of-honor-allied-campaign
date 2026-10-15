# High-resolution weapon-group HUD

Six matching three-state badge sheets provide 18 textures at 512x256: pistol, rifle, SMG, automatic rifle/MG, grenade and heavy weapons (launcher plus shotgun). Available is pewter silver, equipped is warm bronze, unavailable is dark blue steel. The original 64x32 UI rectangles, six-slot order, inventory conditions and equipped pulse remain intact. No engine or gameplay code changes and no binary rebuild.

Only the 18 shaders referenced by hud_weapons.urc are replaced. Legacy weap_empty and weap_selected images are not consumed by this six-slot bar and remain untouched. Multiplayer artwork is excluded.

## Artwork and prompts

Built-in Imagegen edit mode with transparent output; one matching three-state sheet per group. The extracted original contact sheet supplied shapes and state colors; the new pistol sheet supplied the consistent plaque style for the remaining groups. No CLI/API fallback. No raster assets are committed.

Prompt set: Restore only the indicated weapon-group row from the original contact sheet as a high-resolution three-state sprite sheet. Three identical front-facing 2:1 clipped-corner metal plaques stacked vertically with transparent gutters. Top available cool pewter silver; middle equipped muted warm bronze; bottom unavailable dark blue-black steel with subdued highlights. Same weapon geometry and position in all three; crisp metallic bas-relief, restrained aged-metal grain, clear silhouette at small HUD sizes; no text, numbers or extra symbols. Transparent outside plaques. Each subsequent prompt uses the pistol sheet as the plaque style reference.

Subject constraints per sheet:

- pistol: left-facing period semi-automatic pistol matching original first row.
- rifle: long left-facing bolt-action rifle, horizontal barrel, shoulder stock right, no scope.
- smg: left-facing WWII Thompson, stick magazine down, pistol grip and stock right.
- mg: left-facing BAR automatic rifle, thin barrel left, small box magazine below, shoulder stock right; no tripod or belt.
- grenade: slightly tilted WWII pineapple grenade with right-side safety lever.
- heavy: two distinct horizontal silhouettes, bazooka above and pump shotgun below; both muzzle left, rear/stock right.

Selected outputs: pistol exec-ddddae7d-2acc-42ce-864c-3241c0c1faef.png; rifle exec-a74eecdf-4ddd-4afc-912f-042086c40eb5.png; smg exec-164a7954-2b25-43ef-afef-9993f07e4c16.png; mg exec-318a7a4c-1caa-44c4-8016-4b6876e62d65.png; grenade exec-86087a95-f5b4-4fa6-8054-caabf13cb7f4.png; heavy exec-21c42ebf-46c1-46d5-a37b-14545c3780c3.png.

Workspace masters: generated-local/hud-upscale/weapons/generated/{pistol,rifle,smg,mg,grenade,heavy}.png. Final sprites: generated-local/hud-upscale/weapons/prepared/weap_*.png. tools/package_weapon_group_art.py finds the three opaque plaque spans, trims transparent gutters and registers each state to the native 2:1 rectangle. Generated alpha is preserved. Effective campaign shader blending and wave timing are retained; mip filtering enabled for small HUD scales. Packages: generated-local/hud-upscale/weapons/packages/{main,mainta,maintt}/zzzzzzzz_AC_WeaponGroups.pk3.

## Verification

tools/test_weapon_group_art.py uses isolated profiles at 3840x2160 and HUD 1.66. It removes inventory, gives and equips one weapon per group sequentially, cycles all six equipped states with all weapons owned, then removes inventory again. Fourteen screenshots per campaign capture actual native state changes, not a manually painted state gallery. AA aa-r1 passed and all 14 bar crops were visually reviewed: correct availability/selection changes, stable layout, readable shapes, no clipping. This is HUD/inventory-fixture verification, not full mission or combat acceptance.

Metadata, campaign and weapon-policy validators passed. All three package CRCs, 18 RGBA payloads per package and 512x256 dimensions verified. Personal acceptance and merge remain open.

SH sh-r1 and installed BT bt-installed-r1 passed the same 14-step native fixture. All 42 state-bar crops across AA/SH/BT were visually reviewed. BT used installed runtime packages without a candidate override. Machine-readable results: weapon-group-tests.json.

Installed batch weapon-groups-r1 from db8e9442. Integrity checks preserved 9072 original files, 9000 runtime-base files, eight Max Payne inputs and 80 active-profile files. Post-test checks confirm all 56 owned runtime hashes and all 80 profile files. Rollback: generated-local/widescreen/backups/weapon-groups-r1. Local update: artifacts-local/CP08-r1-weapon-groups-r1-update.zip. Fourteen native UHD screenshots plus a texture-state overview: artifacts-local/CP08-WeaponGroups-UHD-Screenshots.zip.
