# Natural Courier New Bold for UI and HUD

Courier New Bold now uses its genuine monospaced advances and natural outlines. The local Windows font is rasterized at 8x resolution without resizing glyphs horizontally or vertically. Fresh RitualFont metrics describe the actual cells; existing character mappings, runtime colors and the small black shadow remain. Mip filtering supports smaller HUD text. Marlett symbols and lettering baked into artwork remain unchanged.

The packages contain 18 text sizes for AA and 19 for each add-on, including eight uniformly sized menu fonts. Generated Allied Campaign controls select a fitting size from measured text width and height; Mission List columns use consistent smaller text. Numeric fields accommodate six decimals. Ammo panels provide 100 extra virtual pixels for long weapon names while retaining the other HUD elements' positions. The binding table inherits its layout font into child labels and buttons, fixing the clipped Alternate heading. Commands, cvars and HUD stat bindings are asserted unchanged when packaging.

## Validation

RelWithDebInfo engine build, CP00 and campaign validators pass. Isolated native captures cover AA gameplay HUD, objectives/subtitles, settings, controls, all five Mission List pages, both Operations regions and Briefing Room. AA 1024x768 checks supplement Full HD; SH/BT captures check their menus and text fixtures, although their initial scenes are dark/cinematic and do not establish normal gameplay HUD coverage. A native scripted level completion checks the score summary and save/load explanation. No exhaustive menu, language or hardware matrix is claimed.

Early natural-font captures revealed clipping in weapon names, numeric fields, controls and score columns. These drove the targeted layout fixes. natural-aa-r4 verifies the final binding-table inheritance; earlier r1-r3 runs must not be cited as final controls acceptance. Machine-readable evidence is in courier-natural-tests.json; full local reports and screenshots remain under generated-local/courier and profiles-local/courier. User files are never used as test profiles.

## Build and delivery

Run tools/package_courier_fonts.py with --runtime runtime-local/CP08-r1, --font C:/Windows/Fonts/courbd.ttf and --output generated-local/courier/packages. Inspect with tools/test_courier_fonts.py --built --extended. Deploy the reviewed packages and engine together using tools/deploy_widescreen_art.py --font-packages generated-local/courier/packages/package-report.json --with-engine, a fresh batch name and the existing MP1 path. Deployment hashes protected inputs and user-profile files and retains rollback copies.

Generated graphics, font files, runtime packages and screenshots remain local and are excluded from GitHub. This replaces the compressed font-only courier-r1 delivery; its historical tests are retained in courier-fonts-tests.json. No merge or personal acceptance is implied.

Installed source: 1129fcadebf8a9a29317bc7f2df1a2899e03df6e, batch courier-natural-r1. Engine and three font packages replaced; game DLLs and other artwork packages unchanged. Integrity check verified 9072 original files, 9000 runtime-base files, 8 MP1 inputs and all 80 active profile files unchanged. Isolated natural-installed-r1 passed using the installed files without test overlays (--original denotes this harness mode). Source push verified by fresh remote SHA. Cloud CI was still pending at delivery; local build and validators passed. Screenshots: artifacts-local/CP08-Courier-Natural-Screenshots.zip.
