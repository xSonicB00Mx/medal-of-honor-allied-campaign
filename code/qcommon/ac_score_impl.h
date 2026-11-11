/* Included by common.c after the campaign helpers. Never stored in savegames. */
static acScoreResult_t ac_scoreRun, ac_scoreResult;
static qboolean ac_scoreActive;

static qboolean AC_ReadScores(const char *path, acScoreRecord_t *records)
{
    FILE *f=Sys_FOpen(path,"rb");int i,j,n,version,count;char magic[16],extra;
    if(!f)return qfalse;
    n=fscanf(f,"%15s %d %d",magic,&version,&count);
    if(n!=3 || strcmp(magic,"ACSCORE") || version!=1 || count!=AC_LEVEL_COUNT){fclose(f);return qfalse;}
    for(i=0;i<AC_LEVEL_COUNT;i++) {
        acScoreRecord_t *r=&records[i];int index;
        n=fscanf(f,"%d %d %d %d %d %d %d %d %d %d",&index,&r->played[0],&r->best[0],&r->played[1],&r->best[1],&r->played[2],&r->best[2],&r->hasLast,&r->lastSkill,&r->last);
        if(n!=10 || index!=i || r->hasLast<0 || r->hasLast>1 || r->lastSkill<0 || r->lastSkill>2 || r->last<0 || r->last>2000000000){fclose(f);return qfalse;}
        for(j=0;j<3;j++)if(r->played[j]<0 || r->played[j]>1 || r->best[j]<0 || r->best[j]>2000000000 || (!r->played[j] && r->best[j])){fclose(f);return qfalse;}
        if(r->hasLast && (!r->played[r->lastSkill] || r->last>r->best[r->lastSkill])){fclose(f);return qfalse;}
    }
    n=fscanf(f," %c",&extra);fclose(f);return n==EOF;
}

static void AC_ScorePath(char *path, int size)
{Q_strncpyz(path,FS_BaseDir_BuildOSPath(Cvar_VariableString("fs_homedatapath"),"ac_scores.dat"),size);}

static qboolean AC_LoadScores(acScoreRecord_t *records)
{
    char path[MAX_OSPATH],backup[MAX_OSPATH];FILE *f;
    memset(records,0,sizeof(*records)*AC_LEVEL_COUNT);AC_ScorePath(path,sizeof(path));
    Com_sprintf(backup,sizeof(backup),"%s.bak",path);
    if(AC_ReadScores(path,records))return qtrue;
    if(AC_ReadScores(backup,records)){Com_Printf("AC_SCORE_RECOVERED backup\n");return qtrue;}
    memset(records,0,sizeof(*records)*AC_LEVEL_COUNT);
    f=Sys_FOpen(path,"rb");if(f){fclose(f);return qfalse;}
    f=Sys_FOpen(backup,"rb");if(f){fclose(f);return qfalse;}
    return qtrue;
}

void AC_GetScoreRecord(int level, acScoreRecord_t *record)
{
    acScoreRecord_t records[AC_LEVEL_COUNT];memset(record,0,sizeof(*record));
    if(level>=0 && level<AC_LEVEL_COUNT && AC_LoadScores(records))*record=records[level];
}

static qboolean AC_StoreScores(const acScoreRecord_t *records)
{
    char path[MAX_OSPATH],temp[MAX_OSPATH],backup[MAX_OSPATH];int i;
    acScoreRecord_t check[AC_LEVEL_COUNT];fileHandle_t f=FS_BaseDir_FOpenFileWrite_HomeData("ac_scores.dat.tmp");
    if(!f)return qfalse;
    FS_Printf(f,"ACSCORE 1 %d\n",AC_LEVEL_COUNT);
    for(i=0;i<AC_LEVEL_COUNT;i++) {
        const acScoreRecord_t *r=&records[i];
        FS_Printf(f,"%d %d %d %d %d %d %d %d %d %d\n",i,r->played[0],r->best[0],r->played[1],r->best[1],r->played[2],r->best[2],r->hasLast,r->lastSkill,r->last);
    }
    FS_Flush(f);FS_FCloseFile(f);AC_ScorePath(path,sizeof(path));
    Com_sprintf(temp,sizeof(temp),"%s.tmp",path);Com_sprintf(backup,sizeof(backup),"%s.bak",path);
    if(!AC_ReadScores(temp,check) || memcmp(check,records,sizeof(check)))return qfalse;
#ifdef _WIN32
    if(AC_ReadScores(path,check) && !CopyFileA(path,backup,FALSE))return qfalse;
    return MoveFileExA(temp,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
    return rename(temp,path)==0;
#endif
}

static void AC_ScoreBegin(int index)
{
    memset(&ac_scoreRun,0,sizeof(ac_scoreRun));memset(&ac_scoreResult,0,sizeof(ac_scoreResult));
    ac_scoreRun.level=index;ac_scoreRun.skill=Cvar_VariableIntegerValue("ac_level_skill");
    ac_scoreActive=index>=0 && index<AC_LEVEL_COUNT && ac_scoreRun.skill>=0 && ac_scoreRun.skill<=2;
    Com_Printf("AC_SCORE_BEGIN level=%d skill=%d\n",index,ac_scoreRun.skill);
}

void AC_ScoreEvent(int event, int value)
{
    acScoreStats_t *s=&ac_scoreRun.stats;
    if(!ac_scoreActive || Cvar_VariableIntegerValue("ac_replay")!=2)return;
    /* Bounded counters avoid overflow even in artificially prolonged sessions. */
    switch(event) {
    case AC_SCORE_SHOT: if(s->shots<1000000){s->shots++;if(value)s->hits++;}break;
    case AC_SCORE_KILL: if(s->kills<100000){s->kills++;if(value)s->heads++;}break;
    case AC_SCORE_GRENADE_KILL:
        if(value<1 || value>1024 || s->kills>=100000)break;
        s->kills++;s->grenadeKills++;
        if(s->grenadeBonus<100000000)s->grenadeBonus+=200*(value-1);
        if(value>s->bestGrenade)s->bestGrenade=value;
        break;
    case AC_SCORE_FRIENDLY:
        if(value>0 && value<=100000 && s->friendlyDamage<100000000){s->friendlyHits++;s->friendlyDamage+=value;}break;
    case AC_SCORE_DEATH:
        ac_scoreActive=qfalse;Cbuf_ExecuteText(EXEC_INSERT,"ac_score_failed\n");break;
    }
}

static qboolean AC_ScoreFinish(const char *map,const char *nextMap)
{
    acScoreRecord_t records[AC_LEVEL_COUNT],*r;int index=ac_scoreRun.level;
    if(!ac_scoreActive || index<0 || index>=AC_LEVEL_COUNT || strcmp(map,ac_levels[index].map)
        || strcmp(nextMap,ac_levels[index].next))return qfalse;
    ac_scoreActive=qfalse;ac_scoreResult=ac_scoreRun;ac_scoreResult.valid=1;
    AC_ScoreCalculate(&ac_scoreResult);
    if(AC_LoadScores(records)) {
        r=&records[index];ac_scoreResult.previous=r->best[ac_scoreResult.skill];
        ac_scoreResult.newBest=!r->played[ac_scoreResult.skill] || ac_scoreResult.total>r->best[ac_scoreResult.skill];
        if(ac_scoreResult.newBest)r->best[ac_scoreResult.skill]=ac_scoreResult.total;
        r->played[ac_scoreResult.skill]=1;r->hasLast=1;r->last=ac_scoreResult.total;r->lastSkill=ac_scoreResult.skill;
        ac_scoreResult.saved=AC_StoreScores(records);
    }
    Com_Printf("AC_SCORE_COMPLETE level=%d skill=%d kills=%d heads=%d shots=%d hits=%d grenadeBonus=%d friendlyDamage=%d score=%d newBest=%d saved=%d\n",
        index,ac_scoreResult.skill,ac_scoreResult.stats.kills,ac_scoreResult.stats.heads,ac_scoreResult.stats.shots,ac_scoreResult.stats.hits,
        ac_scoreResult.stats.grenadeBonus,ac_scoreResult.stats.friendlyDamage,ac_scoreResult.total,ac_scoreResult.newBest,ac_scoreResult.saved);
    return qtrue;
}

const acScoreResult_t *AC_GetScoreResult(void){return &ac_scoreResult;}

qboolean AC_ScoreSaveBlocked(qboolean notify)
{
    if(!Cvar_VariableIntegerValue("ac_campaign_mode") || Cvar_VariableIntegerValue("ac_replay")!=2)return qfalse;
    if(notify){Com_Printf("AC_SCORE_SAVE_LOAD_BLOCKED\n");Cbuf_ExecuteText(EXEC_INSERT,"ac_score_locked\n");}
    return qtrue;
}

void AC_CancelLevelReplay(void)
{
    if(Cvar_VariableIntegerValue("ac_replay")!=2)return;
    ac_scoreActive=qfalse;AC_EndReplay();Com_Printf("AC_SCORE_ABANDONED no record written\n");
}

static void AC_ScoreReport_f(void)
{
    acScoreResult_t r=ac_scoreRun;AC_ScoreCalculate(&r);
    Com_Printf("AC_SCORE_RUN active=%d level=%d skill=%d kills=%d heads=%d shots=%d hits=%d grenadeKills=%d grenadeBonus=%d bestGrenade=%d friendlyHits=%d friendlyDamage=%d score=%d\n",
        ac_scoreActive,r.level,r.skill,r.stats.kills,r.stats.heads,r.stats.shots,r.stats.hits,r.stats.grenadeKills,r.stats.grenadeBonus,r.stats.bestGrenade,r.stats.friendlyHits,r.stats.friendlyDamage,r.total);
}

qboolean AC_ScoreIntermission(const char *map,const char *nextMap,qboolean success)
{
    if(!AC_ScoreSaveBlocked(qfalse))return qfalse;
    if(success && AC_ScoreFinish(map,nextMap)) {
        AC_EndReplay();Cbuf_ExecuteText(EXEC_INSERT,"disconnect\nac_score_results\n");
    } else {
        ac_scoreActive=qfalse;Cbuf_ExecuteText(EXEC_INSERT,"ac_score_failed\n");
    }
    return qtrue;
}
