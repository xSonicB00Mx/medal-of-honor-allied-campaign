## Font-only scaling update

The latest request supersedes the fixed 66% reduction below. Menu aliases now retain the full Courier New Bold metrics and atlas coordinates. UIFont applies ac_menu_scale to glyph rendering, measurement, justification and field width limits, keeping the text origin anchored. The existing slider offers 65-100%; 1.0 is the unchanged default and now means full size. Existing saved values remain valid and shared across campaigns. Manual values up to 150% retain the prior engine limit and may exceed tightly fitted labels.

Widget layout and virtual scales no longer consume ac_menu_scale; changing it does not trigger a resolution/layout rebuild. The option is named Menu font size. HUD fonts, picture lettering, cursor and hover assets are unaffected. Native tests cycle 100%, 65%, 150%, 100% in campaign options and legacy controls, assert identical root/child rectangles and capture the gameplay HUD. Personal profiles are not used for testing.

## Previous menu polish delivery

# Smaller menu type, working hover labels and HD cursor

Menu text uses separate ac-menu font aliases at exactly 0.66 of the existing Courier New Bold metrics. The same HD glyph atlases are sampled through reciprocal UV scaling; proportions, colors and shadows remain intact. Widget context selects the alias for menus and their child controls/column headers. HUD containers retain the original fonts. Generated-menu fit calculations still use the original sizes, preventing an auto-fit step from enlarging the reduced text again. Lettering baked into pictures is unchanged.

Quit and Back to Game now have actual transparent gold hover images in addition to their shader definitions. The former shader-only hover material displayed an opaque grey missing-material rectangle during actual mouse hover. Both buttons were reproduced with the native mouse and checked after the fix; text stays visible. Button commands and rectangles are unchanged.

The bronze cursor was regenerated with built-in Imagegen using the extracted 32x32 original as reference. Master: generated-local/menu-polish/cursor-master.png (exec-88eb3c87-bbcc-490f-bdf5-25b063cf384d). Transparent bounds are registered to a 256x256 sprite with the upper-left tip at the click origin. Prompt: faithfully restore the small WWII pointer as a crisp high-resolution transparent sprite, slender upper-left arrow, angular aged-brass/bronze head and short diagonal shaft, dark inset bevel and warm highlights, original silhouette, no text/circle/background/external shadow, orthographic UI asset.

Software cursor size is 24 logical pixels at 480p (54 at 1080p, 108 at 2160p), independent of texture dimensions and menu/HUD sliders. The SDL hardware cursor is linearly resampled to the equivalent window-pixel size, handling drawable/window DPI differences. Refreshing renderer materials also refreshes the cursor. Raw image and SDL allocations are released on success and failure; cursor pointers are cleared on destruction.

## Checks

RelWithDebInfo engine build passed. Isolated AA Full HD captures cover the settings menu, control binding table, Mission List and gameplay HUD. Actual native mouse hover verified both main-menu buttons and the final correctly sized hardware cursor. Earlier baseline/aa-r1 scripted hover captures did not establish hover acceptance (actual mouse state superseded the synthetic event); the final native observations are the evidence. An initial oversized hardware cursor exposed the separate SDL path and was corrected before delivery.

Spearhead sh-uhd-r1 passed at 3840x2160, with the options screenshot visually checked. Exact metric checks cover all 18 AA and 19 SH/BT text fonts, including every glyph's advance and atlas rectangle. All package CRCs passed. Breakthrough's initial direct e2l2 start emitted map-script prespawn errors; the test harness now copies the previously validated on-foot save into its isolated profile instead. No player save is used.

Breakthrough then exposed a real lazy-menu-loading use-after-free: a local crash dump identified UI_Update calling Menu::ForceHide through the cached hud_ammo pointer after UI_LoadMenu called CreateMenus, which deleted every Menu. Lazy loading now preserves existing Menu objects and skips already loaded layouts; full initialization retains the original rebuild behavior. The exact failing sequence passes with the fix (bt-r4), including returning to the gameplay HUD. Validators for protected inputs/metadata and campaign structure pass.

Initial batch menu-polish-r1 from 0d25e551 was superseded by the lazy-menu correction. Installation verified 9072 original files, 9000 runtime-base files, eight Max Payne input files and the current 95 personal-profile files unchanged. All 62 owned runtime hashes match. Existing font/HUD packages and game/cgame DLLs are preserved; the engine and three new menu packages are installed.

Final installed batch: menu-polish-r2, source cf4993de. Installed engine hash equals the passing bt-r4 candidate. Installed AA aa-installed-final also passes; all 62 runtime hashes match and deployment again preserved 95 profile files. Rollback: generated-local/widescreen/backups/menu-polish-r2. Delivery: artifacts-local/CP08-r1-menu-polish-r2-update.zip. Screenshot bundle (nine menu captures, two actual-mouse hover captures and the cursor sprite): artifacts-local/CP08-MenuPolish-Screenshots.zip. Evidence: menu-polish-tests.json. No exhaustive display/DPI/localization matrix is claimed.

Local masters, packages and screenshots are ignored; no original artwork/font or profile data is committed. Personal acceptance and merge remain open.
