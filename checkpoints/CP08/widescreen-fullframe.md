# Full-frame widescreen artwork

User instruction supersedes the earlier original-center invariant. All 45 selected backgrounds now use the complete supplied 16:9 image. No original central tile is drawn over it. The three user-supplied files map by briefing title to m4l1 (09_00_06), m4l2 (09_00_18) and m5l2 (09_00_24). These files were copied without alteration into ignored local storage; packaged texture pixels match the supplied full images after the standard size normalization.

The renderer draws the entire texture across the centered 16:9 canvas. The packager removes only inventoried static background Label tiles and their legacy Voodoo copies, including tiles in shared briefing includes. Interactive widgets, text, hover effects, commands and loading indicators retain their existing layout. Narrow displays crop the image; ultrawide displays retain a centered 16:9 canvas. SH/BT original-art loading zoom and the single-player restriction remain intact.

Build and metadata/campaign validators passed. Native probes passed in AA, SH and BT at 1920x1080, plus AA at 1024x768 and 2560x1080. The initial AA probe used the incorrect menu name m5l2; the actual resource is m5l2a and the corrected run passed. It is recorded as a diagnostic, not a successful test. The full images expose AI changes previously covered by original pixels: notably the SH main background says Breakthrough. This and possible menu/hotspot artwork offsets remain for the user's requested visual review; no seamless alignment claim is made.

Screenshots: artifacts-local/CP08-r1-Fullframe-Screenshots.zip. Start: Start-CP08-r1.cmd. The three user files and generated artwork remain excluded from Git. No personal acceptance or merge is implied.

Installed delivery: `widescreen-fullframe-r1`. Input verification preserved 9,072 original files, 9,000 runtime-base files, eight MP1 inputs and all 80 user-profile files. The installed three loading screens and video options passed an isolated native retest. Rollback is under generated-local/widescreen/backups/widescreen-fullframe-r1. Machine-readable evidence: [widescreen-fullframe-verification.json](widescreen-fullframe-verification.json).
