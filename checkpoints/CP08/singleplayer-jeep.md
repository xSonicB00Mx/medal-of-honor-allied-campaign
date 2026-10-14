# Single-player restriction and Jeep blood effects

The AA m1l3a/m1l3b Jeep uses `models/vehicles/jeep_30cal.tik`. This exact model was missing from the visual weapon policy. Version 4 adds it to the existing machine-gun group. Damage, fire rate, spread, ammunition and mission scripts are unchanged.

Multiplayer main-menu widgets are disabled, including keyboard activation. Menu manager and menu-level guards reject multiplayer menus, including direct `showmenu`. Connect/reconnect, deathmatch startup and multiplayer map prefixes are blocked; server mode and client capacity are fixed to single player. All messages remain English. Art inventory and packaging exclude multiplayer resources.

## Validation

- RelWithDebInfo build passed. Weapon policy generation/check passed with 38 exact model IDs. Existing visual C++ test suite passed; CP00 and campaign validators passed.
- Isolated native menu probes `mp-aa-r2`, `mp-sh-r2`, `mp-bt-r2` passed. Each retained the main menu through nine reports, showed the multiplayer entry disabled, and rejected alternate entry commands. The first AA probe exposed a direct-show bypass; menu-level guards fixed it before the successful r2 tests.
- Native `jeep-r1` loaded m1l3a, obtained the mission Jeep's actual turret and fired it at a controlled human target. It logged 13 confirmed MG-group entries, 13 authorized mist events, 22 emitted wounds, 21 received wounds, 132 drop diagnostics and 76 created marks. Firing-phase server snapshot intervals remained 50 ms. The test saved 16 wounds. Screenshots show red mist, drops, wounds and world stains.
- This is a controlled actual-turret test, not a complete natural Jeep mission playthrough. It does not establish that every emitted wound is displayed, or test corpse shots after the target leaves the ray. Personal acceptance and merge remain open.

Gemini generation continues serially, using a fresh chat for each image with 3.8 Flash / High. Approved artwork remains local and retains the original central game image and UI bindings. SH/BT loading zoom from the preceding delivery remains intact.
