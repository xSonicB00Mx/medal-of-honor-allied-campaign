# Allied Campaign 1.0.1 - consolidated packages

This maintenance release consolidates the 68 Allied Campaign PK3 files into **three packages**, one in each game folder (`main`, `mainta`, `maintt`). Effective file contents and enumeration order are preserved, including shader precedence. The engine, gameplay and save format are unchanged from 1.0.0.

## Installation / upgrade

Install the original War Chest games and War Chest Restored for all three games first. Close the game and back up your installation. Extract **Medal-of-Honor-Allied-Campaign-1.0.1-Windows-x64.zip** into the game folder, allowing replacement of included files. Start **Start-Allied-Campaign.cmd**.

For an existing 1.0.0 installation, the launcher verifies the new packages and removes the 68 known obsolete AC packages automatically. It preserves original game/WCR packages and all saves/settings. Modified or unrecognized legacy AC packages stop cleanup for manual review; nothing is removed during a failed preflight. Custom-launcher users should run **Update-Allied-Campaign.cmd** once first. Both fresh installation and repeated update are supported. Windows PowerShell is required for the updater; no administrator rights or execution-policy changes are needed.

Keep `AlliedCampaign-User` in place to continue your campaign. Original games and WCR are prerequisites and are not bundled. Download the named release ZIP, not GitHub's automatic source archive. English instructions, credits, matching engine source and SHA-256 checksums are included/provided.
