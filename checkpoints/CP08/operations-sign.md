# Operations lettering and header layout

Reset Progress is now in the upper-right corner at 756,20 on the 960x540 canvas. Previous and Next were removed; mission selection remains available through map markers, regional tabs and mission rows. Confirmation behavior is unchanged.

The built-in image generation tool generated transparent OPERATIONS lettering using local NEW GAME and OPTIONS textures as style references. The output is kept locally at generated-local/operations-sign/operations.png, copied from the generator output. Packaging preserves RGBA, measures visible glyph bounds to exclude near-invisible alpha specks, fits the lettering into a 256x64 transparent sign texture and includes it in all three campaign packages. No generated artwork or original texture is committed.

## Generation prompt

Create a game UI lettering asset. Reference images show the exact lettering style to match: original Medal of Honor menu signs NEW GAME and OPTIONS. Generate ONLY the word "OPERATIONS" in ALL CAPITAL LETTERS, in the same bold classic slab/roman serif lettering, warm ivory-white face, subtle dark olive/black short drop shadow and slight old videogame bevel. Match the original letter shapes, weight, spacing and restrained texture closely. One single straight horizontal line, no perspective or rotation. No signboard, no wood, no green background, no border, no other text or ornaments. Genuine transparent RGBA background including around the short shadow. Wide landscape canvas; lettering large and centered with generous transparent padding. This will be placed onto an existing green wooden menu sign, so only typography must be visible. Exact text OPERATIONS, spelled correctly.

## Validation

RelWithDebInfo engine build passed. Native menu rendering and isolated reset/cancel/restart tests are run with generated packages, leaving the active user profile untouched. Screenshots remain local. Personal visual acceptance and merge remain open.
