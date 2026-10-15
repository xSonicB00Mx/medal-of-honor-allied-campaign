# Mission List highscore runs

This supersedes the save/load and completion behavior in level-replay.md. Normal campaign play and the briefing catalogue retain their existing behavior.

## Scoring, version 1

- Every enemy actor killed by the player: 100 points. A lethal firearm head/helmet hit adds 50 points. Dying actors and corpses cannot generate another kill or headshot bonus.
- For each individual grenade explosion killing n enemies: add 100 × n × (n − 1) bonus points. Together with ordinary kill points this is 100 × n²: two enemies = 400, three = 900. Separate grenades never share their multiplier. The counter belongs to the explosion instance, not its recyclable entity number or an arbitrary time window.
- Firearm accuracy A = successful discharges / total discharges. One shotgun discharge counts once; multiple pellets or penetrated targets cannot push accuracy above 100%. Only actual damage to a living enemy actor qualifies. Objects, friends and corpses do not. Grenades and melee are excluded from firearm accuracy.
- Positive subtotal B = 100 × kills + 50 × headshot kills + grenade bonuses. Accuracy bonus = floor(B × A / 2). With no firearm shots the bonus is zero.
- Friendly-fire penalty = 2 × rounded-up damage per friendly hit, capped at that actor's remaining health. This measures validated attempted damage after hit-location scaling, even though native single-player friendly-fire immunity prevents the health loss. It does not change friendly AI damage rules.
- Final score = max(0, B + accuracy bonus − friendly-fire penalty). Penalties are subtracted after bonuses. Integer arithmetic and bounded counters keep calculation deterministic and avoid overflow. Difficulty needs no artificial multiplier because each difficulty has its own record.

## Run and record lifecycle

Selecting an unlocked level and difficulty starts a fresh in-memory attempt. The common engine owns the counters; the native game module reports actual combat events through its import API. Successful native intermission must identify the selected map and its known successor. Results are committed once, then the player sees a breakdown using the existing Gemini soldiers group photo. A first completion establishes a record, including a zero score. A tied score does not trigger NEW HIGH SCORE.

Death, failure, restart, disconnect and leaving an unfinished run do not update records. Successful runs update exactly one difficulty's best and the level's difficulty-independent last score, with its difficulty displayed as E/M/H. Other levels and difficulties are preserved. Campaign progress is never updated by this mode.

All campaigns share ac_scores.dat at the profile root. The versioned format contains 53 indexed records, each with three played/best pairs and one last-run entry. Writes use a validated temporary file and atomic replacement; a valid previous file is backed up. Corruption falls back to the backup. If neither is valid, existing files are preserved and results explicitly report that the score could not be saved. Opening menus does not create or rewrite records. Reset Progress resets unlocks as before and keeps personal score records.

Manual save, quicksave, load, quickload, the cross-campaign load command and the save/load menu are blocked during the attempt. A visible English message explains the restriction and offers Resume Run or Exit Run (No Score). Autosaves are suppressed silently. Legacy level-replay saves can be loaded outside an active attempt as unranked operation replays; they cannot restore scoring counters or establish records.

Local records are not a competitive online anti-cheat system. Natural full playthroughs of all 53 levels are outside the scripted verification scope.

## Validation

RelWithDebInfo engine/game builds, campaign validator and 12 compiled C formula cases passed. Native isolated tests cover a real pistol kill/headshot, misses and corpse hits, friendly-fire attempts, two separate grenade explosions with two/three kills, exact 1,315-point breakdown, Medium/Hard records, lower scores, ties, first zero records on Easy/Hard, restart, death, abandonment, atomic persistence, corruption refusal, backup recovery, and ordinary unranked save/load. All active progress/sentinel saves remained unchanged. The Hard run restored the regular campaign's Medium preference.

AA and SH checks had no script errors. BT e1l3 completed and stored its score; its 28 script diagnostics were reproduced identically with the previous installed engine/game, with zero new diagnostics. This is recorded separately from a clean native test. Full-HD result, table and lock-dialog previews and a 4:3 table were visually checked. Fresh locked levels and the first-only briefing catalogue remain intact. Evidence: highscore-tests.json and highscore-bt-baseline.json; detailed local reports are generated-local/highscore-*.json.

The deterministic combat fixture produced six kills (one lethal native head hit), five firearm discharges with one successful discharge, five grenade kills in groups of two and three, and 140 attempted friendly damage: B=1,450, accuracy bonus=145, penalty=280, total=1,315. Diagnostic setup attempts that did not execute their scripts are not counted as successful runs. Native intermissions are deliberately scripted and do not prove a complete natural playthrough.

Installation: source bcf0560429cd25f57579b6ac7a103d8c6e7840b1 deployed to the existing CP08-r1 starter, including the matching engine/game DLL. Original input files (9072), runtime base (9000), MP1 inputs (8) and all 80 active user-profile files were verified unchanged. The installed BT smoke test passed the score/store/menu/lock checks with no diagnostics beyond the exact historical baseline. Rollback: generated-local/widescreen/backups/highscore-r1. Local screenshots: artifacts-local/CP08-Highscore-Screenshots.zip. Private source push verified; CI was still running at installation. No merge or personal acceptance is claimed.
