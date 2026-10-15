# Operations title and confirmed campaign reset

The main-menu sign formerly displaying New Game now renders Operations when its map action is highlighted. Other signs retain their existing shaders.

The Operations screen includes Reset Progress below the map legend, outside both regional mission lists. It opens an English warning with Cancel and Reset Progress. Confirmation is accepted only while that warning is the active menu. Cancel changes no progress.

Confirmation atomically stores a fresh campaign record (completed=0, resume=0, slot=-), clears the active operation context and returns to the first-operation map. Existing save files and preferences are retained. The previous valid progress record is backed up by the existing progress writer. Medal awards are not deleted by this operations-progress reset. Corrupt progress is preserved rather than silently overwritten if the writer refuses the change.

Native isolated tests exercise a seeded completed-operation record, direct-confirm rejection, cancel, confirmed reset, backup contents, hidden locked missions and persistence after process restart. Save sentinels in AA/SH/BT are byte-identical afterwards. Warning and map layouts were visually inspected. No reset was performed in the user's active profile.

Local RelWithDebInfo build passed. Test script: tools/test_operations_reset.py. Original assets and native screenshots remain local. Personal acceptance and merge are open.
Installed in CP08-r1 (engine 4149a5bb). The installed executable passed the complete isolated reset test again. Installation verified all 80 active user-profile files unchanged, including the real progress and saves; 9072 original inputs, 9000 runtime-base files and eight MP1 inputs also remain unchanged. See operations-reset-integrity.json and operations-reset-installed-test.json.
