#include "ac_missions.h"

typedef struct { unsigned completed; int resume; char slot[64]; } acProgress_t;
static acProgress_t ac_progress;
static qboolean ac_progressLoaded;
static qboolean ac_progressValid = qtrue;

static qboolean AC_SafeSlot(const char *s)
{
    int i;
    if (!*s || strlen(s)>=64) return qfalse;
    for(i=0;s[i];i++) if(!((s[i]>='a'&&s[i]<='z')||(s[i]>='A'&&s[i]<='Z')||(s[i]>='0'&&s[i]<='9')||s[i]=='_'||s[i]=='-')) return qfalse;
    return qtrue;
}

static qboolean AC_ReadProgress(const char *path, acProgress_t *p)
{
    FILE *f=Sys_FOpen(path,"rb");
    char magic[16]; int n;
    if(!f) return qfalse;
    n=fscanf(f,"%15s %u %d %63s",magic,&p->completed,&p->resume,p->slot);
    fclose(f);
    return n==4 && !strcmp(magic,"ACPROG1") && p->completed < (1u<<AC_MISSION_COUNT)
        && p->resume>=0 && p->resume<=AC_MISSION_COUNT && p->completed==((1u<<p->resume)-1) && AC_SafeSlot(p->slot);
}

static void AC_LoadProgress(void)
{
    char path[MAX_OSPATH], backup[MAX_OSPATH]; FILE *f;
    if(ac_progressLoaded) return;
    ac_progressLoaded=qtrue; memset(&ac_progress,0,sizeof(ac_progress));strcpy(ac_progress.slot,"-");
    Q_strncpyz(path,FS_BaseDir_BuildOSPath(Cvar_VariableString("fs_homedatapath"),"ac_progress.dat"),sizeof(path));
    Com_sprintf(backup,sizeof(backup),"%s.bak",path);
    f=Sys_FOpen(path,"rb");
    if(!f) {
        f=Sys_FOpen(backup,"rb");
        if(!f) return;
    }
    fclose(f);
    if(!AC_ReadProgress(path,&ac_progress)) {
        if(AC_ReadProgress(backup,&ac_progress)) Com_Printf("AC_PROGRESS_RECOVERED backup\n");
        else {ac_progressValid=qfalse;Com_Printf("AC_PROGRESS_ERROR corrupt progress; preserved for recovery\n");}
    }
}

static qboolean AC_StoreProgress(const acProgress_t *p)
{
    char path[MAX_OSPATH], temp[MAX_OSPATH], backup[MAX_OSPATH], text[256];
    fileHandle_t f; size_t n;
    if(!ac_progressValid) return qfalse;
    Com_sprintf(text,sizeof(text),"ACPROG1 %u %d %s\n",p->completed,p->resume,p->slot);
    f=FS_BaseDir_FOpenFileWrite_HomeData("ac_progress.dat.tmp");
    if(!f) return qfalse;
    n=FS_Write(text,strlen(text),f);FS_Flush(f);FS_FCloseFile(f);
    if(n!=strlen(text)) return qfalse;
    Q_strncpyz(path,FS_BaseDir_BuildOSPath(Cvar_VariableString("fs_homedatapath"),"ac_progress.dat"),sizeof(path));
    Q_strncpyz(temp,FS_BaseDir_BuildOSPath(Cvar_VariableString("fs_homedatapath"),"ac_progress.dat.tmp"),sizeof(temp));
    Com_sprintf(backup,sizeof(backup),"%s.bak",path);
#ifdef _WIN32
    { acProgress_t previous; if(AC_ReadProgress(path,&previous)) CopyFileA(path,backup,FALSE); }
    if(!MoveFileExA(temp,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)) {
        Com_Printf("AC_PROGRESS_ERROR atomic replacement failed\n");return qfalse;
    }
#else
    if(rename(temp,path)) return qfalse;
#endif
    ac_progress=*p;
    Com_Printf("AC_PROGRESS_COMMIT completed=%u resume=%d slot=%s\n",p->completed,p->resume,p->slot);
    return qtrue;
}

int AC_MissionState(int index)
{
    AC_LoadProgress();
    if(index<0||index>=AC_MISSION_COUNT||!ac_progressValid) return 0;
    if(ac_progress.completed&(1u<<index)) return 2;
    if(!index || (ac_progress.completed&(1u<<(index-1)))) return ac_progress.resume==index && strcmp(ac_progress.slot,"-")?1:3;
    return 0;
}

static qboolean AC_MapInMission(int op, const char *map)
{
    char key[MAX_QPATH+3];
    if(op<0||op>=AC_MISSION_COUNT) return qfalse;
    Com_sprintf(key,sizeof(key),"|%s|",map);
    return strstr(ac_missions[op].chain,key)!=NULL || !strcmp(map,ac_missions[op].entry);
}

static void AC_Mission_f(void)
{
    int op; qboolean replay; acProgress_t next;
    AC_LoadProgress();
    if(Cmd_Argc()!=2 || !ac_progressValid) return;
    if(!Cmd_Argv(1)[0] || strspn(Cmd_Argv(1),"0123456789")!=strlen(Cmd_Argv(1))) return;
    op=atoi(Cmd_Argv(1));
    if(op<0||op>=AC_MISSION_COUNT||!AC_MissionState(op)) {Com_Printf("AC_MISSION_LOCKED\n");return;}
    replay=(ac_progress.completed&(1u<<op))!=0;
    if(!replay) {next=ac_progress;next.resume=op;if(!AC_StoreProgress(&next)) return;}
    Cvar_Set("ac_operation",va("%d",op));
    Cvar_Set("ac_replay",replay?"1":"0");
    Cvar_Set("ac_expected_map",ac_missions[op].entry);
    Cbuf_AddText(va("ac_context %d %s\n",ac_missions[op].game,ac_missions[op].entry));
}

static void AC_Continue_f(void)
{
    AC_LoadProgress();
    if(!ac_progressValid) return;
    if(ac_progress.resume>=AC_MISSION_COUNT) {Cbuf_AddText("ac_campaign\n");return;}
    if(strcmp(ac_progress.slot,"-")) Cbuf_AddText(va("ac_load %d %s\n",ac_missions[ac_progress.resume].game,ac_progress.slot));
    else Cbuf_AddText(va("ac_mission %d\n",ac_progress.resume));
}

void AC_CampaignMapCommand(const char *map)
{
    int op=Cvar_VariableIntegerValue("ac_operation");
    const char *expected=Cvar_VariableString("ac_expected_map");
    if(!Cvar_VariableIntegerValue("ac_campaign_mode")) return;
    if(op>=0 && op<AC_MISSION_COUNT && ac_missions[op].game==com_target_game->integer
        && *expected && !strcmp(expected,map) && AC_MapInMission(op,map)) {
        if(!strcmp(map,ac_missions[op].entry) && strcmp(map,ac_missions[op].first)) Cvar_Set("ac_expected_map",ac_missions[op].first);
        else Cvar_Set("ac_expected_map", "");
        Com_Printf("AC_MISSION_ENTRY %s %s\n",ac_missions[op].id,map);
    } else {
        Cvar_Set("ac_operation","-1");Cvar_Set("ac_expected_map","");
        Com_Printf("AC_MISSION_DETACHED console or optional map\n");
    }
}

qboolean AC_CampaignTransition(const char *current, const char *nextMap)
{
    int op=Cvar_VariableIntegerValue("ac_operation");char proof[MAX_QPATH*2+4];acProgress_t next;
    qboolean native;
    Com_sprintf(proof,sizeof(proof),"%s|%s",current,nextMap);
    native=!strcmp(proof,Cvar_VariableString("ac_native_transition"));
    Cvar_Set("ac_native_transition","");
    if(!Cvar_VariableIntegerValue("ac_campaign_mode")||op<0||op>=AC_MISSION_COUNT) return qfalse;
    if(!native||ac_missions[op].game!=com_target_game->integer||!AC_MapInMission(op,current)) {
        Cvar_Set("ac_operation","-1");return qfalse;
    }
    if(strcmp(current,ac_missions[op].last)||strcmp(nextMap,ac_missions[op].next)) {
        if(!AC_MapInMission(op,nextMap)) Cvar_Set("ac_operation","-1");
        return qfalse;
    }
    AC_LoadProgress();
    if(Cvar_VariableIntegerValue("ac_replay")) {
        Cvar_Set("ac_operation","-1");Cbuf_AddText("disconnect\nac_campaign\n");
        Com_Printf("AC_REPLAY_COMPLETE %s\n",ac_missions[op].id);return qtrue;
    }
    if(!AC_MissionState(op)) return qtrue;
    next=ac_progress;next.completed|=1u<<op;next.resume=op+1;strcpy(next.slot,"-");
    if(!AC_StoreProgress(&next)) return qtrue;
    Cvar_Set("ac_operation","-1");
    Com_Printf("AC_MISSION_COMPLETE %s\n",ac_missions[op].id);
    if(op+1==AC_MISSION_COUNT) return qfalse; // Preserve the final SH debriefing and credits.
    Cbuf_AddText(va("ac_mission %d\n",op+1));return qtrue;
}

void AC_CampaignSaved(const char *slot, const char *map)
{
    int op=Cvar_VariableIntegerValue("ac_operation"); acProgress_t next;
    if(!Cvar_VariableIntegerValue("ac_campaign_mode")||Cvar_VariableIntegerValue("ac_replay")||!AC_MapInMission(op,map)||!AC_SafeSlot(slot)) return;
    AC_LoadProgress();next=ac_progress;next.resume=op;Q_strncpyz(next.slot,slot,sizeof(next.slot));AC_StoreProgress(&next);
}

qboolean AC_CampaignCanSave(const char *slot)
{
    AC_LoadProgress();
    if(!Cvar_VariableIntegerValue("ac_campaign_mode") || ac_progress.resume>=AC_MISSION_COUNT) return qtrue;
    if(!strcmp(slot,ac_progress.slot) && ac_missions[ac_progress.resume].game==com_target_game->integer
        && (Cvar_VariableIntegerValue("ac_replay") || Cvar_VariableIntegerValue("ac_operation")!=ac_progress.resume)) {
        Com_Printf("AC_SAVE_PROTECTED main campaign resume point; choose another save name\n");return qfalse;
    }
    return qtrue;
}

void AC_CampaignRestore(int op, int replay, const char *map)
{
    AC_LoadProgress();
    if(op<0||op>=AC_MISSION_COUNT||!AC_MapInMission(op,map)||!AC_MissionState(op)||ac_missions[op].game!=com_target_game->integer) op=-1;
    Cvar_Set("ac_operation",va("%d",op));
    Cvar_Set("ac_replay",(replay || (op>=0 && (ac_progress.completed&(1u<<op))))?"1":"0");
    Cvar_Set("ac_expected_map",op>=0 && !strcmp(map,ac_missions[op].entry) && strcmp(map,ac_missions[op].first)?ac_missions[op].first:"");
}

static void AC_ProgressReport_f(void)
{
    AC_LoadProgress();
    Com_Printf("AC_PROGRESS valid=%d completed=%u resume=%d slot=%s operation=%s replay=%s\n",ac_progressValid,ac_progress.completed,ac_progress.resume,ac_progress.slot,Cvar_VariableString("ac_operation"),Cvar_VariableString("ac_replay"));
}
