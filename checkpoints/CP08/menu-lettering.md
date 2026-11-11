# Matching main-menu lettering

Eight transparent assets were generated individually with the built-in image generator, using the accepted OPERATIONS asset as the style reference: OPTIONS, WAR RECORDS, BRIEFING ROOM, MAP LIST, CREDITS, LOAD / SAVE, QUIT and BACK TO GAME. Sources are local in generated-local/menu-lettering/*.png. The accepted Operations source and placement remain unchanged. No multiplayer lettering was generated.

Hover signs use the existing measured centered UV shear; main-menu Quit and Back to Game use horizontal alpha lettering and a green button background, with a gold hover state. Packaging audits that the main-menu commands remain identical. The mapping also supports the expansion-specific shader names. The original menus and all artwork remain local; only source and documentation are tracked.

## Exact prompt template

Create a transparent game UI lettering asset matching the provided OPERATIONS reference exactly in typography: bold classic roman/slab serif capitals, warm ivory-white, subtle bevel, short dark olive drop shadow. Replace its wording with exactly TEXT. Single straight horizontal line, no tilt, no perspective. Preserve style and letter weight, natural spacing. Only lettering and its short shadow on genuine alpha transparency. No background, signboard, border, decorations or extra words. Large crisp centered lettering with transparent padding; wide canvas.

TEXT was replaced with each quoted label listed above. Reference: generated-local/operations-sign/operations.png. Transparent background was enabled for every request. The original generated PNGs and alpha channels are retained; game packaging performs size normalization and glyph-bound measurement.

## Validation

Local RelWithDebInfo engine build passed. Native menu-signs-aa-r1, menu-signs-sh-r1 and menu-signs-bt-r1 each captured seven Full HD frames without resource/script errors. All eighteen hover-sign views were visually inspected in a contact sheet, with full-frame checks for long text and Quit. Back to Game retains its original visibility conditions; its new asset is packaged without changing its action. No player profile or campaign progress was used for these isolated previews. Personal acceptance and merge remain open.
Installed in CP08-r1 with engine f8bcb1b3. The installed AA main-menu sign smoke test passed. All 80 active player-profile files, 9072 original inputs, 9000 runtime-base files and eight MP1 inputs remain hash-identical. Rollback: generated-local/widescreen/backups/menu-lettering-r1. Screenshot and alpha-asset ZIPs are in artifacts-local.
