# Dynamic single-player crosshairs

Four separate white arms and a center dot replace the standard raster crosshair. A dark outline maintains contrast; friendly targets turn the geometry green using the existing ally trace. Native rectangles remain sharp at UHD. Stroke size follows HUD size; the angular opening does not. The inner white arm tips indicate the spread boundary. For an opening too small to separate the arms cleanly from the dot, only the dot is drawn. No generated bitmap is needed.

## Ballistic analysis and meaning

`Weapon::Shoot` interpolates `bulletspread` and `bulletspreadmax` with `min(length(player velocity)/sv_runspeed, 1)`, then multiplies by `1 + fireSpreadMult`. A zoom-capable weapon additionally applies `1 + (1-moving)*(zoomSpreadMult-1)` while zoomed. There is no independent universal crouch or jump penalty; movement contributes exactly as in the firing implementation. The multiplier decays immediately before a shot, respecting the existing time cap and positive/negative clamping; the shot then adds the weapon's configured amount. Some rifles and shotguns have no sustained-fire multiplier and therefore should not exhibit invented firing bloom.

`BulletAttack` and `FakeBulletAttack` construct the ray from `forward*range + right*grandom()*spread.x + up*grandom()*spread.y`. `grandom` is a standard Gaussian. Consequently there is **no finite maximum hit radius**. The displayed boundary is the 95% circle: `slope = sqrt(-2*ln(0.05))*max(abs(sigmaX),abs(sigmaY))/range`. It contains 95% for symmetric spread and at least 95% for unequal axes. Bullets can land outside it. It describes the next shot's random spread around the current aim, not damage, guaranteed hits, recoil prediction, or a projectile trajectory. Distance changes the world footprint but not its angular projection.

The firing path and HUD now share the original interpolation and pre-shot decay functions. HUD queries do not mutate multiplier/timestamps or consume random numbers. Weapon data, damage, shot cadence, recoil and actual dispersion remain unchanged. Actual values come from the equipped runtime weapon, including WCR and campaign-specific models, not a manually maintained table.

## Integration

- Server computes the next-shot angular radius in the formerly unused player-stat slot 31. A 16-bit angle encoding survives signed-short transport; the existing 32-slot playerstate and save structures do not grow. Code 0 means no Gaussian bullet model, code 1 means zero spread.
- Client projects the decoded slope with actual viewport width/height and FOV: `pixels = slope * dimension / (2*tan(FOV/2))`. HUD scaling changes only line/dot dimensions. No decorative smoothing delays the real spread change or its existing recovery-time cutoff.
- Existing crosshair visibility, cinematics, intermission, HUD toggle and scope rules remain in force. No normal crosshair is drawn over the fully engaged sniper scope.
- Projectiles and melee use a fixed small cross with dot. Vehicles without an exposed turret do not borrow the holstered handheld weapon's spread. Mounted weapons use their actual turret weapon when available; barrel/view parallax and scripted aim offsets are not represented by this centered angular indicator.
- `ac_dynamic_crosshair 1` is the default; `0` restores legacy texture rendering. `ac_crosshair_debug 1` logs projection and actual bullet samples for isolated tests; default 0. Multiplayer keeps its existing rendering.

## Verification

`tools/tests/dynamic_crosshair_math.cpp` compiles the shared production header. It verifies 270 positive/negative/zero multiplier decay cases against the previous algorithm, signed-short transport, zero spread, resolution/FOV/aspect projection and seeded Gaussian coverage (200,000 samples: 95.00% symmetric, 98.31% conservative anisotropic circle).

Reproduce with `cmake -S tools/tests -B build-local/crosshair-math`, `cmake --build build-local/crosshair-math --config Release`, then `ctest --test-dir build-local/crosshair-math -C Release --output-on-failure`.

`tools/test_dynamic_crosshair.py` launches isolated native profiles and records real shots, movement, recovery, HUD sizes 1/1.66, FOV 80/90, rifle fire without artificial bloom, scope entry/exit, grenade fallback, save/load, crosshair hiding and legacy mode. `tools/verify_dynamic_crosshair.py` checks the logs against actual first-shot sigma and the projection formula, with a maximum 0.01 pixel tolerance for rounded diagnostics. It rejects fixtures where movement was blocked. Screenshots are native framebuffer captures.

Initial AA `aa-r2` at 3840x2160 verified firing/movement/projection: Thompson standing 47.276 px, firing up to 106.346 px within the sampled firing phase (112.706 immediately after the final shot), moving 78.581 px, recovered 47.276 px. HUD 1 and 1.66 retain the same radius. FOV 90 yields 39.669 px versus 47.276 at FOV 80. KAR98 remains 8.392 px before/after firing. This initial build still had the transient load issue corrected below. The FOV setting is the game's 4:3-reference setting; the actual 16:9 horizontal projections are approximately 96.418 and 106.260 degrees.

Initial SH fixtures are not movement acceptance: `sh-r1` starts on a boat and `sh-r2` is still in an intro cinematic. Final expansion probes use copies of previously validated on-foot saves, also exercising loading saves from before this change. Personal acceptance and merge remain open.

Those old expansion fixtures require `ac_campaign_mode 0` at process startup (they predate campaign sidecar metadata) and `developer 1` before loading to preserve test-script access. Rejected/no-script runs are not accepted evidence. Normal AA tests use campaign mode 1. User profiles are never used by the fixture.

The SH save/load probe exposed a one-frame visual spike while restored weapon timestamps preceded restoration of the level clock. `GetCrosshairSpread` now returns an unavailable sentinel for that temporary negative elapsed time; the player retains the archived HUD value until the clock is valid. Merely clamping time to zero was insufficient because the stored multiplier itself had not decayed. The firing path is unchanged. The native verifier additionally rejects a radius spike anywhere in the load phase.

## Final installed result

Batch `dynamic-crosshair-r1`, source `433e760e873aaa3e0afd49000d12de62da828caf`, replaces only game.dll and cgame.dll. Engine and all artwork remain as installed. Final native reports `aa-installed-1080`, `sh-r8`, and `bt-installed-r1` pass every verifier assertion and use identical DLL hashes. AA and BT launch directly from the installed runtime; SH uses an isolated runner with those same binaries. AA at 1920x1080 has exactly half the UHD resting radius (23.638 px); SH and BT at UHD give 47.276 px. No load-phase spikes remain. Standing/firing screenshots were visually reviewed in all campaigns; scope and movement examples were also inspected.

Metadata, campaign and weapon-policy validators pass. CTest passes. Final integrity checks preserve 9072 original files, 9000 runtime-base files, eight Max Payne inputs and all 80 user-profile files. All 56 owned runtime hashes match. Rollback: `generated-local/widescreen/backups/dynamic-crosshair-r1`. Local update: `artifacts-local/CP08-r1-dynamic-crosshair-r1-update.zip`. Eight native screenshots: `artifacts-local/CP08-Dynamic-Crosshairs-Screenshots.zip`. Machine-readable final evidence: `dynamic-crosshair-tests.json`.

These are focused weapon/HUD/save-load tests, not playthroughs of all missions or every scripted vehicle/turret. The mounted-weapon path is implemented and source-reviewed; no claim of universal turret/parallax calibration is made.
