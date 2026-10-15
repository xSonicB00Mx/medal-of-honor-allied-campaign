# Briefing Room and single-level replay

Main-menu Briefing Room now uses the regular campaign resume operation, independent of the last replay. AA uses its six original narrated briefing scenes with saving disabled and their outgoing spmap intercepted. SH/BT use the native cinematic player directly, returning through its end/skip callback to the main menu. Their original PlayMovie script path has a malformed command/continuation problem; the new replay route does not depend on it. The 15 operations map to 12 distinct briefings: six AA slideshows, three SH videos, three BT chapter videos. Bizerte shares the first BT chapter; Anzio and Monte Battaglia share the third. After campaign completion the final SH briefing remains available.

Mission List contains the 53 main playable sections, with original BSP level names; repeated SH region names have part numbers. Optional/helper maps are excluded. Only completed levels appear, eleven per page. Selecting a row requires an explicit Easy/Medium/Hard choice before Start Replay becomes available. The 960x540 canvas is proportional at 16:9 and 4:3. The main-menu alpha sign now says MISSION LIST in the accepted lettering style.

A successful native level intermission records that section in ACPROG2 (two 32-bit masks). Existing ACPROG1 records remain readable: completed operations imply their completed sections; compatible resume metadata identifies preceding sections in the current operation. Merely reading legacy progress never modifies it. Atomic writes, previous-record backup, corruption recovery and Reset Progress cover both masks. Reset retains saved games and preferences.

Single-level replay uses a distinct persisted replay mode, also preserved in save metadata. Its first successful native level completion disconnects to the main menu rather than following the campaign chain. The main campaign record and resume slot are unchanged. Existing campaign saves cannot be overwritten from this mode; new replay saves are supported and retain their replay status on load. Briefing replay creates no saves. Replay difficulty is applied with the native difficulty command after initialization, while the regular campaign difficulty is retained in shared preferences and restored when leaving replay. Campaign initialization no longer unconditionally resets difficulty to Medium.

## Validation

Local RelWithDebInfo build and campaign/CP00 validators passed. Native isolated tests cover AA/SH/BT replay, all three difficulties, non-default campaign difficulty restoration, replay save/load, existing-save protection, blocked locked levels, legacy current-save migration, all 53 levels and pagination, 1920x1080 and 1024x768 rendering, normal native section unlocks below and above bit 31, ACPROG2 restart, malformed primary plus legacy backup, invalid mask rejection, and Reset Progress confirmation/cancel/restart. Original AA briefing skip returns without starting gameplay. SH first briefing (92.77 seconds) and BT first chapter (48.9 seconds, selected through Bizerte progress) ran to their natural video ends and returned without modifying progress. Resource audit verifies every one of the 15 mappings, all six video files and matching audio. Exact results and engine hashes: level-replay-tests.json.

Level completion tests trigger the real intermission path with isolated script fixtures; they are not natural playthroughs. Every level and every full briefing has not been played end to end in this revision. No personal acceptance or merge is claimed. Tests never use the active user profile.

## Generated sign

The built-in image generator used generated-local/operations-sign/operations.png as the style reference with alpha enabled. Exact prompt:

Create a transparent game UI lettering asset matching the provided OPERATIONS reference exactly in typography: bold classic roman/slab serif capitals, warm ivory-white, subtle bevel, short dark olive drop shadow. Replace its wording with exactly MISSION LIST. Single straight horizontal line, no tilt, no perspective. Preserve style and letter weight, natural spacing. Only lettering and its short shadow on genuine alpha transparency. No background, signboard, border, decorations or extra words. Large crisp centered lettering with transparent padding; wide canvas. This is a style reference, the output is a new label.

The generated source is local at generated-local/menu-lettering/mission_list.png; original Map List art is retained for rollback. Packaging retains the established sign transform. No original or generated artwork enters Git. Local preview ZIP: artifacts-local/CP08-Mission-List-Screenshots.zip.

## Installation

Installed in CP08-r1 through the existing Start-CP08-r1.cmd, source ca01a239. The installed menu and BT Hard replay tests passed; BT returned to the preserved Easy campaign preference and kept campaign progress and save sentinels unchanged. Integrity verification preserved all 80 active player-profile files, 9072 original inputs, 9000 runtime-base files and eight MP1 inputs. Rollback copy: generated-local/widescreen/backups/level-replay-r1. No user save or progress reset was performed. The local update archive is artifacts-local/CP08-r1-level-replay-r1-update.zip.
