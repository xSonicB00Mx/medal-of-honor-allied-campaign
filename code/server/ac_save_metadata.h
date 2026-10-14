#include "../qcommon/ac_content.h"

static int ac_loadedOperation = -1, ac_loadedReplay;
static char ac_loadedMap[MAX_QPATH];

static qboolean AC_CheckSaveMetadata(const char *name)
{
    void *data = NULL;
    char fingerprint[65] = "", map[MAX_QPATH] = "", magic[8] = "";
    int game = -1, patch = -1, op = -1, replay = 0;
    int size = FS_ReadFileEx(Com_GetArchiveFileName(name, "acmeta"), &data, qtrue);
    ac_loadedOperation=-1;ac_loadedReplay=0;ac_loadedMap[0]=0;
    if (size < 0) {
        if (!Cvar_VariableIntegerValue("ac_campaign_mode")) return qtrue;
        Com_Printf("AC_SAVE_REJECT no supported campaign metadata: %s\n", name);
        return qfalse;
    }
    int fields = sscanf((const char *)data, "%7s %d %64s %d %63s %d %d", magic, &game, fingerprint, &patch, map, &op, &replay);
    qboolean valid = size < 512 && ((!strcmp(magic,"ACM1") && fields==5) || (!strcmp(magic,"ACM2") && fields==7))
        && game == com_target_game->integer && game >= 0 && game < 3
        && !strcmp(fingerprint, ac_content_fingerprints[game]) && patch == (game == 2 ? 1 : 0);
    FS_FreeFile(data);
    if (!valid) Com_Printf("AC_SAVE_REJECT incompatible content or game: %s\n", name);
    else {ac_loadedOperation=op;ac_loadedReplay=replay;Q_strncpyz(ac_loadedMap,map,sizeof(ac_loadedMap));Com_Printf("AC_SAVE_ACCEPT context=%d map=%s\n", game, map);}
    return valid;
}

static void AC_WriteSaveMetadata(const char *name)
{
    char text[256];
    int game = com_target_game->integer;
    if (game < 0 || game > 2) return;
    Com_sprintf(text,sizeof(text),"ACM2 %d %s %d %s %d %d\n",game,ac_content_fingerprints[game],game==2?1:0,svs.mapName,Cvar_VariableIntegerValue("ac_operation"),Cvar_VariableIntegerValue("ac_replay"));
    if (!FS_WriteFile(Com_GetArchiveFileName(name,"acmeta"),text,strlen(text)))
        Com_Printf("AC_SAVE_METADATA_FAILED %s\n",name);
    else AC_CampaignSaved(name,svs.mapName);
}
