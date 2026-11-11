MEDAL OF HONOR: ALLIED CAMPAIGN 1.0.1
Windows x64 - War Chest Restored edition
Released November 11, 2026

INSTALLATION
1. Install Medal of Honor: Allied Assault and BOTH expansions, Spearhead and
   Breakthrough. Install War Chest Restored (WCR) for all three campaigns.
2. Close the game. Back up the installation, or make a separate copy for this
   mod. Remove unrelated third-party mods from that copy to avoid conflicts.
3. Extract the ENTIRE ZIP directly into the game folder containing main,
   mainta and maintt. Merge these folders and allow replacement of the engine
   and runtime DLLs. Do not extract into main or into an extra subfolder.
4. Run Start-Allied-Campaign.cmd. Use this launcher for every normal session.
   On an existing 1.0.0 installation, it automatically removes the 68 known
   legacy AC packages after checking both their hashes and the three new
   packages. Original game/WCR packages, saves and settings are never removed.
   No installer, Python, compiler, separate Max Payne installation or developer
   workspace is required. The matching engine, DLLs, artwork, HUD and effects
   packages are included. Original games and WCR are not included.

The folder must be writable. A location outside Program Files is recommended.
Windows 10/11 x64 and a recent graphics driver are recommended. The tested
renderer is OpenGL 1. Advanced graphics features require appropriate GPU
support; the name OpenGL 1 does not mean they run on legacy OpenGL-only cards.
Compatibility with other WCR revisions and unrelated mods is not guaranteed.
WCR-BASELINE.json records the exact package hashes used for testing.

WHAT CHANGED IN 1.0.1
The 68 separate AC packages are consolidated into exactly three:
  main/zz_AlliedCampaign.pk3
  mainta/zz_AlliedCampaign.pk3
  maintt/zz_AlliedCampaign.pk3
Their effective file contents AND enumeration order match 1.0.0. The engine,
gameplay and save format are unchanged. This is a packaging maintenance release.

UPDATING FROM 1.0.0
Close the game, back up the installation and extract the entire 1.0.1 ZIP over
it. Then use Start-Allied-Campaign.cmd, or run Update-Allied-Campaign.cmd once
before using a custom launcher. Windows PowerShell is used for the one-time
cleanup; no administrator rights or execution-policy changes are required.
If an old AC package has been modified, an unknown old AC package is found,
or a replacement is missing/damaged, cleanup stops before removing files.
Follow the displayed message; do not delete original game or WCR packages.
The updater only removes the exact 1.0.0 AC files listed in the manifest.
Running it again is safe. Keep the AlliedCampaign-User folder in place.

SAVES, SETTINGS AND UPGRADES
A fresh profile is created in AlliedCampaign-User next to the launcher.
Your existing game saves and settings are not included, erased or imported.
Back up the ENTIRE AlliedCampaign-User folder to preserve progress, scores,
bindings and shared preferences. Never delete it during an upgrade.
Original-game saves are not guaranteed compatible with the customized engine.
To move an existing Allied Campaign profile, copy its entire contents into
AlliedCampaign-User while the game is closed; keep the original backup.
Start a new campaign if migrating from an unsupported build.

WHAT THE MOD DOES
- Combines Allied Assault, Spearhead and Breakthrough into 15 chronological
  operations, ending with Spearhead's Berlin finale.
- Operations map with two regions, difficulty selection, Roman numerals and
  progress-safe replays. Reset Progress requires confirmation.
- Mission List replays completed individual levels with their standard gear.
  Score runs track kills, headshots, grenade multikills, accuracy and friendly
  fire. Best scores are stored separately for each difficulty, plus last score.
  Saving/loading is disabled during score runs; abandoning a run awards no score.
- Unlockable Briefing Room and a combined, date-sorted saved-game browser.
- LOADOUT replaces the multiplayer entrance: select one portable weapon per
  group from all three games for completed Operations replays. DEFAULT restores
  normal equipment. New missions and Mission List runs use their standard gear.
- Settings shared across campaigns; unified menus, widescreen artwork, sharper
  HUD artwork, Courier New Bold text, independent HUD and menu-font scaling.
- Dynamic spread-based crosshairs and a mortar impact guide.
- Blood mist, drops, surface stains and character wounds, including visual
  hits on corpses and dying enemies. Blood options are individually adjustable.
- Dynamic NPC/pickup shadows, ambient occlusion, temporal anti-aliasing and
  adjustable per-object motion blur. These are engine features, not ReShade.
- Adjustable hit flinch in 10% steps and live Breakthrough drop-rule selection.
- Restored detailed skies and spatial thunder flashes, including exterior
  lighting visible through windows while enclosed interiors stay sheltered.
- Campaign/script fixes, cross-campaign weapon compatibility and preserved
  War Chest Restored integration. This is a single-player mod, not multiplayer.

OPTIONS AND PERFORMANCE
Use Allied Campaign Options for Interface & Gameplay and Graphics & Effects.
Start with default settings, then adjust resolution and HUD/font size to taste.
TAA, ambient occlusion, shadows and object motion blur have performance costs.
If performance is low, lower resolution or disable the expensive effects first.
Simplified skies are a player option; weather scripts no longer force them on.

TROUBLESHOOTING / REMOVAL
If launch reports missing content, check the extraction location and WCR setup.
Use the supplied engine and matching DLLs together, not stock OpenMoHAA binaries.
Do not retain earlier AC packages alongside the three consolidated packages.
The supplied launcher performs the supported 1.0.0 cleanup automatically.
If Windows blocks a downloaded archive, review its Properties/Unblock option
and extract it again. Do not disable antivirus or firewall protection.
For a clean rollback, restore your installation backup or remove the separate
modded game-folder copy. Keep AlliedCampaign-User if you want to retain progress.
The manifest lists supplied files; it is not an automatic uninstaller.

Source, releases and bug reports:
https://github.com/xSonicB00Mx/medal-of-honor-allied-campaign
Include the version, campaign/map, launch method and reproduction steps when
reporting a problem. Logs may contain local paths; review them before sharing.

The creator accepted the playtested mod for release. Targeted native AA/SH/BT,
save/load, widescreen, UHD and graphics regressions accompany that acceptance;
this does not guarantee compatibility with every hardware/mod combination.
See CREDITS-Allied-Campaign.txt and the supplied license notices. Corresponding
engine source is included in Allied-Campaign-Source.zip. This is an independent,
free fan modification and is not endorsed by Electronic Arts.
