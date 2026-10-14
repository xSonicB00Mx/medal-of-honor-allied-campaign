/* Allied Campaign: explicit, single-player content-context lifecycle. */
static void AC_Context_f(void)
{
    char targetText[8], map[MAX_QPATH];
    int target, i;
    static const char *sharedNames[] = {
        "ac_ui_auto", "ac_menu_scale", "ac_hud_scale", "ac_hud_safe",
        "ac_blood_mist", "ac_world_blood", "ac_body_wounds", "ac_corpse_effects",
        "cg_fov", "s_volume", "s_musicvolume", "sensitivity", "skill",
        "r_mode", "r_customwidth", "r_customheight", "r_fullscreen",
        "cl_playintro", "developer", "logfile", "com_maxfps", "com_maxfpsUnfocused", "ac_campaign_mode"
    };
    
    if (Cmd_Argc() != 3 || strlen(Cmd_Argv(1)) != 1 || Cmd_Argv(1)[0] < '0' || Cmd_Argv(1)[0] > '2') {
        Com_Printf("AC_CONTEXT_REJECT usage: ac_context <0|1|2> <map|menu>\n");
        return;
    }
    if (com_dedicated->integer || Cvar_VariableIntegerValue("g_gametype") != 0) {
        Com_Printf("AC_CONTEXT_REJECT single player only\n");
        return;
    }
    Q_strncpyz(targetText, Cmd_Argv(1), sizeof(targetText));
    Q_strncpyz(map, Cmd_Argv(2), sizeof(map));
    if (strlen(Cmd_Argv(2)) >= sizeof(map) || !map[0]) return;
    for (i=0; map[i]; i++) {
        if (!((map[i]>='a' && map[i]<='z') || (map[i]>='0' && map[i]<='9') || map[i]=='_')) {
            Com_Printf("AC_CONTEXT_REJECT invalid map\n"); return;
        }
    }
    target = targetText[0]-'0';
#ifdef _WIN32
    {
        STARTUPINFOA si;
        PROCESS_INFORMATION pi;
        char exe[MAX_OSPATH], args[16384], part[2048];
        const char *pathNames[] = {"fs_basepath", "fs_homepath", "fs_steampath", "fs_gogpath", "fs_microsoftstorepath"};
        if (!GetModuleFileNameA(NULL, exe, sizeof(exe))) return;
        Com_sprintf(args, sizeof(args), "\"%s\" +set com_target_game %d +set ac_parent_pid %lu +set net_enabled 0 +set cl_playintro 0", exe, target, GetCurrentProcessId());
        for (i=0; i<ARRAY_LEN(pathNames); i++) {
            const char *value = Cvar_VariableString(pathNames[i]);
            if (strchr(value, '\"') || strchr(value, '\n') || strchr(value, '\r')) return;
            Com_sprintf(part, sizeof(part), " +set %s \"%s\"", pathNames[i], value);
            Q_strcat(args, sizeof(args), part);
        }
        for (i=0; i<ARRAY_LEN(sharedNames); i++) {
            const char *value = Cvar_VariableString(sharedNames[i]);
            if (strchr(value, '\"') || strchr(value, '\n') || strchr(value, '\r')) return;
            Com_sprintf(part, sizeof(part), " +set %s \"%s\"", sharedNames[i], value);
            Q_strcat(args, sizeof(args), part);
        }
        {
            fileHandle_t controls = FS_BaseDir_FOpenFileWrite_HomeConfig("main/ac_controls.cfg");
            if (!controls) { Com_Printf("AC_CONTEXT_FAILED cannot preserve controls\n"); return; }
            Key_WriteBindings(controls);
            FS_FCloseFile(controls);
        }
        Q_strcat(args, sizeof(args), " +exec ac_controls.cfg");
        Com_sprintf(part, sizeof(part), " +set ac_context_start %s", map);
        Q_strcat(args, sizeof(args), part);
        if (!strcmp(map, "saves")) Q_strcat(args, sizeof(args), " +ac_saves");
        else if (strcmp(map, "menu")) {
            Com_sprintf(part, sizeof(part), " +%s %s", !strcmp(Cmd_Argv(0), "ac_load") ? "loadgame" : "map", map);
            Q_strcat(args, sizeof(args), part);
        } else Q_strcat(args, sizeof(args), " +ac_campaign");
        Q_strcat(args, sizeof(args), " +exec ac_context_ready.cfg");
        Com_Memset(&si,0,sizeof(si));si.cb=sizeof(si);
        Com_Memset(&pi,0,sizeof(pi));
        Com_WriteConfiguration();
        if (!CreateProcessA(exe,args,NULL,NULL,FALSE,0,NULL,NULL,&si,&pi)) {
            Com_Printf("AC_CONTEXT_FAILED create process: %lu\n",GetLastError()); return;
        }
        CloseHandle(pi.hThread);CloseHandle(pi.hProcess);
        Com_Printf("AC_CONTEXT_RESTART %d -> %d %s child=%lu\n",com_target_game->integer,target,map,pi.dwProcessId);
        Com_Quit_f();
    }
#else
    Com_Printf("AC_CONTEXT_REJECT internal restart currently supported on Windows only\n");
#endif
}

static void AC_WaitForPreviousContext(void)
{
#ifdef _WIN32
    const char *pidText = Cvar_VariableString("ac_parent_pid");
    if (*pidText) {
        DWORD pid = (DWORD)strtoul(pidText, NULL, 10);
        HANDLE parent;
        if (pid == GetCurrentProcessId()) Com_Error(ERR_FATAL,"Invalid campaign parent");
        parent = OpenProcess(SYNCHRONIZE,FALSE,pid);
        if (parent) {
            DWORD result = WaitForSingleObject(parent,30000);
            CloseHandle(parent);
            if (result != WAIT_OBJECT_0) Com_Error(ERR_FATAL,"Previous campaign context did not stop");
        }
        Cvar_Set("ac_parent_pid", "");
    }
#endif
}
