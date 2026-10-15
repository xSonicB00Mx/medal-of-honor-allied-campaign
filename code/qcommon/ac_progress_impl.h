#include "ac_missions.h"
#include "ac_content.h"

typedef struct { unsigned completed; int resume; char slot[64]; unsigned levels[2]; } acProgress_t;
static acProgress_t ac_progress;
static qboolean ac_progressLoaded;
static qboolean ac_progressValid = qtrue;
static void AC_EndReplay(void);

static int AC_LevelIndex(int op, const char *map)
{
    int i;
    for(i=0;i<AC_LEVEL_COUNT;i++) if(ac_levels[i].operation==op && !strcmp(ac_levels[i].map,map)) return i;
    return -1;
}

static void AC_MarkLevel(acProgress_t *p, int i)
{ if(i>=0 && i<AC_LEVEL_COUNT) p->levels[i/32] |= 1u<<(i%32); }

// Read legacy saves only to recover sections already passed in the current operation.
// Opening a menu never rewrites the user's progress or save files.
static void AC_ImportLegacyLevels(acProgress_t *p)
{
    int i, game, patch, op, replay, current=-1;
    char relative[MAX_OSPATH], path[MAX_OSPATH], magic[8], fingerprint[65], map[MAX_QPATH];
    static const char *folders[]={"main","mainta","maintt"};
    FILE *f;
    for(i=0;i<AC_LEVEL_COUNT;i++) if(p->completed&(1u<<ac_levels[i].operation)) AC_MarkLevel(p,i);
    if(p->resume>=AC_MISSION_COUNT || !strcmp(p->slot,"-")) return;
    game=ac_missions[p->resume].game;
    Com_sprintf(relative,sizeof(relative),"%s/%s",folders[game],Com_GetArchiveFileName(p->slot,"acmeta"));
    Q_strncpyz(path,FS_BaseDir_BuildOSPath(Cvar_VariableString("fs_homedatapath"),relative),sizeof(path));
    f=Sys_FOpen(path,"rb");if(!f)return;
    if(fscanf(f,"%7s %d %64s %d %63s %d %d",magic,&game,fingerprint,&patch,map,&op,&replay)==7
        && !strcmp(magic,"ACM2") && game==ac_missions[p->resume].game
        && !strcmp(fingerprint,ac_content_fingerprints[game]) && patch==(game==2?1:0)
        && op==p->resume && !replay) current=AC_LevelIndex(op,map);
    fclose(f);
    for(i=0;i<current;i++) if(ac_levels[i].operation==p->resume) AC_MarkLevel(p,i);
}

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
    memset(p,0,sizeof(*p));
    n=fscanf(f,"%15s %u %d %63s",magic,&p->completed,&p->resume,p->slot);
    if(n==4 && !strcmp(magic,"ACPROG2")) n+=fscanf(f,"%u %u",&p->levels[0],&p->levels[1]);
    fclose(f);
    if(!((n==4 && !strcmp(magic,"ACPROG1")) || (n==6 && !strcmp(magic,"ACPROG2")))
        || p->completed >= (1u<<AC_MISSION_COUNT) || p->resume<0 || p->resume>AC_MISSION_COUNT
        || p->completed!=((1u<<p->resume)-1) || !AC_SafeSlot(p->slot)
        || p->levels[1] >= (1u<<(AC_LEVEL_COUNT-32))) return qfalse;
    if(!strcmp(magic,"ACPROG1")) AC_ImportLegacyLevels(p);
    return qtrue;
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
    Com_sprintf(text,sizeof(text),"ACPROG2 %u %d %s %u %u\n",p->completed,p->resume,p->slot,p->levels[0],p->levels[1]);
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

qboolean AC_ResetCampaignProgress(void)
{
    acProgress_t fresh;
    AC_LoadProgress();
    memset(&fresh, 0, sizeof(fresh));
    strcpy(fresh.slot, "-");
    if (!AC_StoreProgress(&fresh)) return qfalse;
    AC_EndReplay();
    Cvar_Set("ac_operation", "-1");
    Cvar_Set("ac_replay", "0");
    Cvar_Set("ac_expected_map", "");
    Cvar_Set("ac_native_transition", "");
    Com_Printf("AC_PROGRESS_RESET saves and preferences preserved\n");
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

qboolean AC_LevelCompleted(int index)
{
    AC_LoadProgress();
    return ac_progressValid && index>=0 && index<AC_LEVEL_COUNT
        && (ac_progress.levels[index/32]&(1u<<(index%32)))!=0;
}

static void AC_EndReplay(void)
{
    if(Cvar_VariableIntegerValue("ac_replay")==2) {
        Cvar_Set("skill",Cvar_VariableString("ac_campaign_skill"));
        Cvar_Set("g_skill",Cvar_VariableString("ac_campaign_g_skill"));
        Cvar_Set("g_maxplayerhealth",Cvar_VariableIntegerValue("skill")==0?"1500":Cvar_VariableIntegerValue("skill")==2?"250":"750");
    }
    Cvar_Set("ac_replay","0");Cvar_Set("ac_operation","-1");
    Cvar_Set("ac_expected_map","");Cvar_Set("ac_native_transition","");
}

static void AC_ReturnMain_f(void)
{
    AC_EndReplay();
    Cbuf_AddText("disconnect\npopmenu 0\npushmenu main\n");
    Com_Printf("AC_REPLAY_RETURN_MAIN skill=%s\n",Cvar_VariableString("skill"));
}

static void AC_LevelReplay_f(void)
{
    int index, difficulty, op;
    if(!Cvar_VariableIntegerValue("ac_campaign_mode") || Cmd_Argc()!=3) return;
    if(!*Cmd_Argv(1) || strspn(Cmd_Argv(1),"0123456789")!=strlen(Cmd_Argv(1))
        || strlen(Cmd_Argv(2))!=1 || Cmd_Argv(2)[0]<'0' || Cmd_Argv(2)[0]>'2') return;
    index=atoi(Cmd_Argv(1));difficulty=atoi(Cmd_Argv(2));
    if(!AC_LevelCompleted(index)) {Com_Printf("AC_LEVEL_LOCKED\n");return;}
    AC_EndReplay();op=ac_levels[index].operation;
    Cvar_Set("ac_campaign_skill",*Cvar_VariableString("skill")?Cvar_VariableString("skill"):"1");
    Cvar_Set("ac_campaign_g_skill",*Cvar_VariableString("g_skill")?Cvar_VariableString("g_skill"):"1");
    Cvar_Set("ac_level_skill",va("%d",difficulty));
    Cvar_Set("ac_operation",va("%d",op));Cvar_Set("ac_replay","2");
    Cvar_Set("ac_expected_map",ac_levels[index].map);
    Cbuf_AddText(va("ac_context %d %s\n",ac_missions[op].game,ac_levels[index].map));
    Com_Printf("AC_LEVEL_REPLAY %s difficulty=%d\n",ac_levels[index].map,difficulty);
}

static void AC_Briefing_f(void)
{
    int op;
    AC_LoadProgress();
    if(!ac_progressValid || !Cvar_VariableIntegerValue("ac_campaign_mode")) return;
    if(Cmd_Argc()!=2 || !*Cmd_Argv(1) || strspn(Cmd_Argv(1),"0123456789")!=strlen(Cmd_Argv(1))) return;
    op=atoi(Cmd_Argv(1));
    if(!AC_MissionState(op)) {Com_Printf("AC_BRIEFING_LOCKED\n");return;}
    AC_EndReplay();
    Cvar_Set("ac_operation",va("%d",op));Cvar_Set("ac_replay","3");
    Cvar_Set("ac_expected_map",ac_missions[op].briefing);
    Cbuf_AddText(va("ac_context %d %s\n",ac_missions[op].game,ac_missions[op].game?"briefing":ac_missions[op].briefing));
    Com_Printf("AC_BRIEFING_REPLAY %s %s\n",ac_missions[op].id,ac_missions[op].briefing);
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
    AC_EndReplay();
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
    AC_EndReplay();
    if(ac_progress.resume>=AC_MISSION_COUNT) {Cbuf_AddText("ac_campaign\n");return;}
    if(strcmp(ac_progress.slot,"-")) Cbuf_AddText(va("ac_load %d %s\n",ac_missions[ac_progress.resume].game,ac_progress.slot));
    else Cbuf_AddText(va("ac_mission %d\n",ac_progress.resume));
}

qboolean AC_CampaignMapCommand(const char *map)
{
    int op=Cvar_VariableIntegerValue("ac_operation");
    const char *expected=Cvar_VariableString("ac_expected_map");
    if(!Cvar_VariableIntegerValue("ac_campaign_mode")) return qfalse;
    if(Cvar_VariableIntegerValue("ac_replay")==3 && op>=0 && op<AC_MISSION_COUNT) {
        if(*expected && !strcmp(map,expected) && !strcmp(map,ac_missions[op].briefing)) {
            Cvar_Set("ac_expected_map","");Com_Printf("AC_BRIEFING_STARTED %s\n",map);return qfalse;
        }
        Com_Printf("AC_BRIEFING_COMPLETE\n");Cbuf_AddText("ac_return_main\n");return qtrue;
    }
    if(op>=0 && op<AC_MISSION_COUNT && ac_missions[op].game==com_target_game->integer
        && *expected && !strcmp(expected,map) && AC_MapInMission(op,map)) {
        if(!strcmp(map,ac_missions[op].entry) && strcmp(map,ac_missions[op].first)) Cvar_Set("ac_expected_map",ac_missions[op].first);
        else Cvar_Set("ac_expected_map", "");
        Com_Printf("AC_MISSION_ENTRY %s %s\n",ac_missions[op].id,map);
    } else {
        AC_EndReplay();
        Cvar_Set("ac_operation","-1");Cvar_Set("ac_expected_map","");
        Com_Printf("AC_MISSION_DETACHED console or optional map\n");
    }
    return qfalse;
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
    if(Cvar_VariableIntegerValue("ac_replay")==2) {
        Com_Printf("AC_LEVEL_REPLAY_COMPLETE %s\n",current);
        Cbuf_AddText("ac_return_main\n");return qtrue;
    }
    AC_LoadProgress();
    if(!Cvar_VariableIntegerValue("ac_replay")) {
        int level=AC_LevelIndex(op,current);
        if(level>=0 && !strcmp(nextMap,ac_levels[level].next) && AC_MissionState(op)) {
            next=ac_progress;AC_MarkLevel(&next,level);
            if(!AC_StoreProgress(&next)) return qtrue;
            Com_Printf("AC_LEVEL_COMPLETE %s\n",current);
        }
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
    if(Cvar_VariableIntegerValue("ac_campaign_mode") && Cvar_VariableIntegerValue("ac_replay")==3) {
        Com_Printf("AC_SAVE_PROTECTED briefing replay\n");return qfalse;
    }
    if(Cvar_VariableIntegerValue("ac_campaign_mode") && Cvar_VariableIntegerValue("ac_replay")==2
        && FS_ReadFileEx(Com_GetArchiveFileName(slot,"sav"),NULL,qtrue)>=0) {
        void *data=NULL;char magic[8],hash[65],map[MAX_QPATH];int game,patch,op,replay;
        int size=FS_ReadFileEx(Com_GetArchiveFileName(slot,"acmeta"),&data,qtrue);
        qboolean own=size>0 && size<512
            && sscanf((const char *)data,"%7s %d %64s %d %63s %d %d",magic,&game,hash,&patch,map,&op,&replay)==7
            && !strcmp(magic,"ACM2") && replay==2;
        if(data)FS_FreeFile(data);
        if(!own) {Com_Printf("AC_SAVE_PROTECTED campaign save; choose another save name\n");return qfalse;}
    }
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
    Cvar_Set("ac_replay",replay==2 && op>=0?"2":(replay || (op>=0 && (ac_progress.completed&(1u<<op))))?"1":"0");
    Cvar_Set("ac_expected_map",op>=0 && !strcmp(map,ac_missions[op].entry) && strcmp(map,ac_missions[op].first)?ac_missions[op].first:"");
}

static void AC_ProgressReport_f(void)
{
    AC_LoadProgress();
    Com_Printf("AC_PROGRESS valid=%d completed=%u resume=%d slot=%s operation=%s replay=%s\n",ac_progressValid,ac_progress.completed,ac_progress.resume,ac_progress.slot,Cvar_VariableString("ac_operation"),Cvar_VariableString("ac_replay"));
    Com_Printf("AC_LEVEL_PROGRESS %u %u skill=%s\n",ac_progress.levels[0],ac_progress.levels[1],Cvar_VariableString("skill"));
}
