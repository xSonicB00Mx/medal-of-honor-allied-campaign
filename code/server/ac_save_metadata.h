#include "../qcommon/ac_content.h"

static qboolean AC_CheckSaveMetadata(const char *name)
{
    void *data = NULL;
    char fingerprint[65], map[MAX_QPATH], magic[8];
    int game = -1, patch = -1;
    int size = FS_ReadFileEx(Com_GetArchiveFileName(name, "acmeta"), &data, qtrue);
    if (size < 0) {
        if (!Cvar_VariableIntegerValue("ac_campaign_mode")) return qtrue;
        Com_Printf("AC_SAVE_REJECT no supported campaign metadata: %s\n", name);
        return qfalse;
    }
    qboolean valid = size < 512 && sscanf((const char *)data, "%7s %d %64s %d %63s", magic, &game, fingerprint, &patch, map) == 5
        && !strcmp(magic, "ACM1") && game == com_target_game->integer && game >= 0 && game < 3
        && !strcmp(fingerprint, ac_content_fingerprints[game]) && patch == (game == 2 ? 1 : 0);
    FS_FreeFile(data);
    if (!valid) Com_Printf("AC_SAVE_REJECT incompatible content or game: %s\n", name);
    else Com_Printf("AC_SAVE_ACCEPT context=%d map=%s\n", game, map);
    return valid;
}

static void AC_WriteSaveMetadata(const char *name)
{
    char text[256];
    int game = com_target_game->integer;
    if (game < 0 || game > 2) return;
    Com_sprintf(text,sizeof(text),"ACM1 %d %s %d %s\n",game,ac_content_fingerprints[game],game==2?1:0,svs.mapName);
    if (!FS_WriteFile(Com_GetArchiveFileName(name,"acmeta"),text,strlen(text)))
        Com_Printf("AC_SAVE_METADATA_FAILED %s\n",name);
}
