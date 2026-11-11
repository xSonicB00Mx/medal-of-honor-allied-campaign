#include <vector>
#include <algorithm>
#include <ctime>

struct acSavedGame_t {
    int game, timestamp;
    str slot, title, path;
};
static std::vector<acSavedGame_t> ac_savedGames;
static int ac_selectedSave=-1, ac_savePage=0;
static const char *ac_saveFolders[]={"main","mainta","maintt"};
static const char *ac_saveCampaigns[]={"Allied Assault","Spearhead","Breakthrough"};
static const int ac_savesPerPage=10;

static bool AC_SaveSlotValid(const char *slot)
{
    if(!*slot || strlen(slot)>=64)return false;
    for(const char *p=slot;*p;++p)
        if(!((*p>='a'&&*p<='z')||(*p>='A'&&*p<='Z')||(*p>='0'&&*p<='9')||*p=='_'||*p=='-'))return false;
    return true;
}

static bool AC_ReadSaveHeader(const char *path,int game,savegamestruct_t &save)
{
    FILE *file=Sys_FOpen(path,"rb");if(!file)return false;
    const size_t count=fread(&save,1,sizeof(save),file);fclose(file);
    if(count!=sizeof(save))return false;
    Com_SwapSaveStruct(&save);
    if(save.version!=SAVEGAME_STRUCT_VERSION || save.type!=game)return false;
    char archive[MAX_OSPATH];COM_StripExtension(path,archive,sizeof(archive));Q_strcat(archive,sizeof(archive),".sav");
    file=Sys_FOpen(archive,"rb");if(!file)return false;fclose(file);
    return true;
}

static void AC_ScanSavedGames(void)
{
    ac_savedGames.clear();ac_selectedSave=-1;ac_savePage=0;
    // Same home-first precedence as native loading; identical slots from
    // different campaigns are separate entries. Never move or rewrite saves.
    const char *roots[]={Cvar_VariableString("fs_homedatapath"),Cvar_VariableString("fs_basepath")};
    for(int root=0;root<2;++root)for(int game=0;game<3;++game) {
        char directory[MAX_OSPATH];
        Q_strncpyz(directory,FS_BuildOSPath(roots[root],ac_saveFolders[game],Com_GetArchiveFolder()),sizeof(directory));
        int count=0;char **files=Sys_ListFiles(directory,".ssv",NULL,&count,qfalse);
        for(int i=0;i<count;++i) {
            char slot[64],path[MAX_OSPATH];
            if(strlen(files[i])>=sizeof(slot)+4)continue;
            COM_StripExtension(files[i],slot,sizeof(slot));if(!AC_SaveSlotValid(slot))continue;
            if(root) {
                const str home=FS_BuildOSPath(roots[0],ac_saveFolders[game],Com_GetArchiveFolder());
                FILE *shadow=Sys_FOpen(va("%s/%s.sav",home.c_str(),slot),"rb");
                if(shadow){fclose(shadow);continue;}
                shadow=Sys_FOpen(va("%s/%s.ssv",home.c_str(),slot),"rb");
                if(shadow){fclose(shadow);continue;}
            }
            bool duplicate=false;
            for(const auto &entry:ac_savedGames)if(entry.game==game && !Q_stricmp(entry.slot,slot)){duplicate=true;break;}
            if(duplicate)continue;
            Com_sprintf(path,sizeof(path),"%s/%s",directory,files[i]);
            savegamestruct_t save={};if(!AC_ReadSaveHeader(path,game,save))continue;
            // Header strings are untrusted data, never URC syntax or commands.
            save.comment[sizeof(save.comment)-1]=0;
            for(char *p=save.comment;*p;++p)if((unsigned char)*p<32 || *p=='"' || *p=='\\')*p=' ';
            acSavedGame_t entry;entry.game=game;entry.timestamp=save.time;
            entry.slot=slot;entry.title=*save.comment?save.comment:slot;entry.path=path;
            ac_savedGames.push_back(entry);
        }
        Sys_FreeFileList(files);
    }
    std::sort(ac_savedGames.begin(),ac_savedGames.end(),[](const acSavedGame_t &a,const acSavedGame_t &b){
        if(a.timestamp!=b.timestamp)return a.timestamp>b.timestamp;
        if(a.game!=b.game)return a.game<b.game;
        return Q_stricmp(a.slot,b.slot)<0;
    });
    if(!ac_savedGames.empty())ac_selectedSave=0;
}

static void AC_ShowSavedGames(void)
{
    if(AC_ScoreSaveBlocked(qtrue))return;
    const char *action=Cmd_Argv(1);
    if(!strcmp(action,"select") && Cmd_Argc()==3) {
        const int index=atoi(Cmd_Argv(2));
        if(index>=0 && index<(int)ac_savedGames.size())ac_selectedSave=index;
    } else if(!strcmp(action,"page") && Cmd_Argc()==3)ac_savePage=atoi(Cmd_Argv(2));
    else AC_ScanSavedGames();
    const int pages=std::max(1,((int)ac_savedGames.size()+ac_savesPerPage-1)/ac_savesPerPage);
    ac_savePage=std::max(0,std::min(ac_savePage,pages-1));
    if(!strcmp(action,"page") && !ac_savedGames.empty())ac_selectedSave=ac_savePage*ac_savesPerPage;
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_saved_games.urc");if(!f)return;
    FS_Printf(f,"menu ac_saved_games 960 540 NONE 0\nvirtualres 1\nwidecanvas\nfullscreen 1\nbgfill 0 0 0 1\nwidescreenbackground \"textures/ac/menu_background\"\n");
    AC_UIItem(f,"heading","SAVED GAMES",24,16,912,34,NULL,"1 0.85 0.4 1");
    AC_UIItem(f,"date_header","Date and time",24,98,200,25,NULL);
    AC_UIItem(f,"campaign_header","Campaign",232,98,176,25,NULL);
    AC_UIItem(f,"save_header","Saved game",416,98,520,25,NULL);
    for(int row=0;row<ac_savesPerPage;++row) {
        const int index=ac_savePage*ac_savesPerPage+row;if(index>=(int)ac_savedGames.size())break;
        const auto &save=ac_savedGames[index];
        char date[64]="Unknown date";time_t timestamp=save.timestamp;struct tm *local=localtime(&timestamp);
        if(local)strftime(date,sizeof(date),"%Y-%m-%d %H:%M:%S",local);
        const char *color=index==ac_selectedSave?"1 0.85 0.3 1":"0.85 0.9 0.8 1";
        const str command=va("ac_saves select %d",index);const int y=130+row*31;
        AC_UIItem(f,va("date_%d",row),date,24,y,200,28,command.c_str(),color,14);
        AC_UIItem(f,va("campaign_%d",row),ac_saveCampaigns[save.game],232,y,176,28,command.c_str(),color,14);
        AC_UIItem(f,va("save_%d",row),va("%s%s",index==ac_selectedSave?"> ":"",save.title.c_str()),416,y,520,28,command.c_str(),color,15);
        Com_DPrintf("AC_SAVE_LIST index=%d game=%d time=%d slot=%s\n",index,save.game,save.timestamp,save.slot.c_str());
    }
    if(ac_savedGames.empty())AC_UIItem(f,"empty","No saved games found.",24,220,912,32,NULL);
    if(ac_selectedSave>=0)AC_UIItem(f,"selected",va("Selected: %s / %s",ac_saveCampaigns[ac_savedGames[ac_selectedSave].game],ac_savedGames[ac_selectedSave].slot.c_str()),24,446,912,24,NULL);
    if(ac_savePage>0)AC_UIItem(f,"previous","Previous",24,478,140,24,va("ac_saves page %d",ac_savePage-1));
    AC_UIItem(f,"page",va("Page %d / %d (%d saves)",ac_savePage+1,pages,(int)ac_savedGames.size()),176,478,400,24,NULL);
    if(ac_savePage+1<pages)AC_UIItem(f,"next","Next",588,478,140,24,va("ac_saves page %d",ac_savePage+1));
    AC_UIItem(f,"back","Operations",24,510,180,26,"ac_campaign");
    AC_UIItem(f,"refresh","Refresh",216,510,160,26,"ac_saves");
    if(ac_selectedSave>=0)AC_UIItem(f,"load","Load Selected Game",700,510,236,26,"ac_saves_load","1 0.85 0.4 1");
    FS_Printf(f,"end.\n");FS_FCloseFile(f);AC_OpenGeneratedMenu("ac_saved_games");
}

static void AC_LoadSelectedSave_f(void)
{
    if(AC_ScoreSaveBlocked(qtrue) || ac_selectedSave<0 || ac_selectedSave>=(int)ac_savedGames.size())return;
    const auto &save=ac_savedGames[ac_selectedSave];savegamestruct_t header={};
    if(!AC_ReadSaveHeader(save.path,save.game,header)) {
        Com_Printf("Saved game is no longer available. Refresh the list.\n");return;
    }
    Com_Printf("AC_SAVE_LIST_LOAD game=%d slot=%s\n",save.game,save.slot.c_str());
    if(save.game==Cvar_VariableIntegerValue("com_target_game"))Cbuf_ExecuteText(EXEC_INSERT,va("loadgame %s\n",save.slot.c_str()));
    else Cbuf_ExecuteText(EXEC_INSERT,va("ac_load %d %s\n",save.game,save.slot.c_str()));
}
