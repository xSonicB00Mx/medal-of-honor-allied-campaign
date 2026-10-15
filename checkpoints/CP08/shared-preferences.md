# Shared campaign preferences

The previous implementation shared only 18 named values and omitted modifier bindings. The common preference file now includes archived rendering, audio, input, terrain, visual-effects and HUD preferences, plus player-facing miscellaneous options. Mission progress, save pointers, statistics and networking are excluded. Latched values are saved, so pending graphics changes survive context restart. Existing legacy shared preferences load first for migration; main/ac_preferences.cfg then overrides each campaign config. Normal, Alt and Ctrl bindings (including unbound keys) and aliases are retained. The Ctrl binding cvar registration now correctly uses cl_ctrlbindings rather than cl_altbindings.

Native isolated test shared-r1 passed the actual AA -> SH -> BT -> AA process chain, conflicting target configs, modifier controls, deleted bindings, latched r_picmip and separate fresh startup of all three campaigns. Mission-state exclusion was checked. The active user profile is not edited during installation; the new shared file is initialized on the next normal configuration save. Source graphics assets are unchanged by this correction. Personal acceptance and merge remain open.

Installed in CP08-r1; CI run 38700782117 passed. All 80 active user-profile files were preserved byte-for-byte. Combined delivery is recorded in shared-options-art-delivery.json.

