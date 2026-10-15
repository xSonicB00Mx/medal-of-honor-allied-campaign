# Smaller menu type, working hover labels and HD cursor

Menu text uses separate ac-menu font aliases at exactly 0.66 of the existing Courier New Bold metrics. The same HD glyph atlases are sampled through reciprocal UV scaling; proportions, colors and shadows remain intact. Widget context selects the alias for menus and their child controls/column headers. HUD containers retain the original fonts. Generated-menu fit calculations still use the original sizes, preventing an auto-fit step from enlarging the reduced text again. Lettering baked into pictures is unchanged.

Quit and Back to Game now have actual transparent gold hover images in addition to their shader definitions. The former shader-only hover material displayed an opaque grey missing-material rectangle during actual mouse hover. Both buttons were reproduced with the native mouse and checked after the fix; text stays visible. Button commands and rectangles are unchanged.

The bronze cursor was regenerated with built-in Imagegen using the extracted 32x32 original as reference. Master: generated-local/menu-polish/cursor-master.png (exec-88eb3c87-bbcc-490f-bdf5-25b063cf384d). Transparent bounds are registered to a 256x256 sprite with the upper-left tip at the click origin. Prompt: faithfully restore the small WWII pointer as a crisp high-resolution transparent sprite, slender upper-left arrow, angular aged-brass/bronze head and short diagonal shaft, dark inset bevel and warm highlights, original silhouette, no text/circle/background/external shadow, orthographic UI asset.

Software cursor size is 24 logical pixels at 480p (54 at 1080p, 108 at 2160p), independent of texture dimensions and menu/HUD sliders. The SDL hardware cursor is linearly resampled to the equivalent window-pixel size, handling drawable/window DPI differences. Refreshing renderer materials also refreshes the cursor. Raw image and SDL allocations are released on success and failure; cursor pointers are cleared on destruction.

## Checks

RelWithDebInfo engine build passed. Isolated AA Full HD captures cover the settings menu, control binding table, Mission List and gameplay HUD. Actual native mouse hover verified both main-menu buttons and the final correctly sized hardware cursor. Earlier baseline/aa-r1 scripted hover captures did not establish hover acceptance (actual mouse state superseded the synthetic event); the final native observations are the evidence. An initial oversized hardware cursor exposed the separate SDL path and was corrected before delivery.

Local masters, packages and screenshots are ignored; no original artwork/font or profile data is committed. Personal acceptance and merge remain open.
