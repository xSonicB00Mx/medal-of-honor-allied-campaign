#include "../qcommon/ac_missions.h"
#include "ac_map.h"
#include "../qcommon/ac_loadout.h"

static void AC_OpenGeneratedMenu(const char *name)
{
    menuManager.Unlock(NULL);menuManager.ClearMenus(true);
    Menu *old=menuManager.FindMenu(name);
    if(old) {
        UIWidgetContainer *root=(UIWidgetContainer *)old->GetContainerWidget();menuManager.DeleteMenu(old);
        while(root->getFirstChild())delete root->getFirstChild();
        delete root->m_layout;delete root;delete old;
    }
    new UILayout(va("ui/%s.urc",name));
    UIWidgetContainer *root=(UIWidgetContainer *)uWinMan.FindWidget(name);
    if(root) {
        Menu *menu=new Menu(name);menu->setFullscreen(root->isFullscreen());
        menu->setVidMode(root->getVidMode());menu->AddMenuItem(root);UI_ForceMenu(name);UI_CloseConsole();
    }
}

static const char *AC_StateColor(int state)
{return state==2?"0.57 0.80 0.61 1":"1 0.58 0.45 1";}

static void AC_MainMenu_f(void)
{
    // PopMenu locks the stack until the next UI event pass. A pop/push command
    // pair therefore loses its push and exposes gameplay (or restarts intro music).
    menuManager.Unlock(NULL);
    menuManager.ClearMenus(true);
    UI_ForceMenu("main");
    UI_MainMenuWidgetsUpdate();
    UI_CloseConsole();
    Com_Printf("AC_MAIN_MENU context=%d active=%d\n", Cvar_VariableIntegerValue("com_target_game"), clc.state);
}
static const char *AC_StateName(int state)
{return state==2?"COMPLETE":"CURRENT";}
struct AC_UICommand {
    str text;
    AC_UICommand(const char *value):text(value?value:"") {}
};
static void AC_UIItem(fileHandle_t f,const str name,const str title,int x,int y,int w,int h,const AC_UICommand command,const char *color="0.95 0.89 0.7 1",int maxFontHeight=17)
{
    // Own va() arguments before font lookup reuses the rotating format buffers.
    const str commandText=command.text;
    // Choose a uniformly smaller font where needed, never stretch glyph axes.
    char fontName[32]="facfont-20";
    for(int size=maxFontHeight>17?17:maxFontHeight;size>=10;--size) {
        char candidate[32];Com_sprintf(candidate,sizeof(candidate),"ac-courier-%d",size);
        UIFont font(candidate);
        const int width=font.getWidth(title,-1);
        if(width>0 && width<=w-(w<=48?2:12) && font.getHeight()<=h-2) {
            Q_strncpyz(fontName,candidate,sizeof(fontName));break;
        }
    }
    FS_Printf(f,"resource\n%s\n{\nname \"%s\"\ndontlocalize\ntitle \"%s\"\nrect %d %d %d %d\nfont %s\nfgcolor %s\nbgcolor 0.075 0.095 0.075 0.96\nborderstyle NONE\n",commandText.length()?"Button":"Label",name.c_str(),title.c_str(),x,y,w,h,fontName,color);
    if(commandText.length()) FS_Printf(f,"stuffcommand \"%s\"\n",commandText.c_str());
    FS_Printf(f,"}\n");
}

static void AC_ScoreLocked_f(void)
{
    if(!AC_ScoreSaveBlocked(qfalse))return;
    const char *name="ac_score_lock";
    if(!menuManager.FindMenu(name)) {
        fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_score_lock.urc");if(!f)return;
        FS_Printf(f,"menu \"%s\" 960 540 NONE 0\nvirtualres 1\nwidecanvas\nfullscreen 0\nbgfill 0 0 0 0.7\nborderstyle NONE\n",name);
        AC_UIItem(f,"heading","HIGHSCORE RUN",180,170,600,40,NULL,"1 0.85 0.4 1");
        AC_UIItem(f,"locked","Saving and loading are disabled during this run.",180,224,600,30,NULL);
        AC_UIItem(f,"rule","Finish this level to record a score. Exiting discards the run.",180,264,600,30,NULL);
        AC_UIItem(f,"resume","Resume Run",240,332,210,36,"popmenu 0");
        AC_UIItem(f,"exit","Exit Run (No Score)",500,332,240,36,"ac_return_main","1 0.58 0.45 1");
        FS_Printf(f,"end.\n");FS_FCloseFile(f);UI_LoadMenu(name);
    }
    UI_PushMenu(name);UI_CloseConsole();
}

static void AC_ScoreFailed_f(void)
{
    AC_CancelLevelReplay();Cbuf_ExecuteText(EXEC_INSERT,"disconnect\nac_score_failure_menu\n");
}

static void AC_ScoreFailureMenu_f(void)
{
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_score_failure.urc");if(!f)return;
    FS_Printf(f,"menu \"ac_score_failure\" 960 540 NONE 0\nvirtualres 1\nwidecanvas\nfullscreen 1\nbgfill 0.055 0.07 0.055 1\n");
    AC_UIItem(f,"heading","RUN NOT COMPLETED",180,160,600,40,NULL,"1 0.58 0.45 1");
    AC_UIItem(f,"message","No score recorded. Your previous records are unchanged.",180,224,600,30,NULL);
    AC_UIItem(f,"list","Mission List",240,332,210,36,"ac_level_list");
    AC_UIItem(f,"main","Main Menu",500,332,210,36,"ac_main_menu");
    FS_Printf(f,"end.\n");FS_FCloseFile(f);AC_OpenGeneratedMenu("ac_score_failure");
}

static void AC_ScoreResults_f(void)
{
    const acScoreResult_t *r=AC_GetScoreResult();if(!r->valid)return;
    const acScoreStats_t &s=r->stats;
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_score_results.urc");if(!f)return;
    FS_Printf(f,"menu \"ac_score_results\" 960 540 NONE 0\nvirtualres 1\nwidecanvas\nfullscreen 1\nbgfill 0 0 0 1\nwidescreenbackground \"textures/ac/widescreen/aa-statsscreen_failed\"\n");
    AC_UIItem(f,"heading","LEVEL COMPLETE",24,20,912,38,NULL,"1 0.85 0.4 1");
    AC_UIItem(f,"level",va("%s / %s",ac_levels[r->level].title,r->skill==0?"Easy":r->skill==1?"Medium":"Hard"),24,66,912,30,NULL);
    AC_UIItem(f,"record",!r->saved?"SCORE NOT SAVED - RECORD FILE ERROR":r->newBest?"NEW HIGH SCORE!":"RUN COMPLETED",24,112,456,38,NULL,r->saved && r->newBest?"1 0.85 0.25 1":"0.95 0.89 0.7 1");
    AC_UIItem(f,"kills",va("Enemy kills: %d    +%d",s.kills,100*s.kills),24,160,456,26,NULL);
    AC_UIItem(f,"heads",va("Headshot kills: %d    +%d",s.heads,50*s.heads),24,190,456,26,NULL);
    AC_UIItem(f,"grenades",va("Grenade kills: %d | Best: %d    +%d bonus",s.grenadeKills,s.bestGrenade,s.grenadeBonus),24,220,456,26,NULL);
    AC_UIItem(f,"accuracy",va("Accuracy: %d / %d (%.1f%%)",s.hits,s.shots,s.shots?100.0*s.hits/s.shots:0.0),24,250,456,26,NULL);
    AC_UIItem(f,"accuracy_bonus",va("Accuracy bonus (up to 50%%): +%d",r->accuracyBonus),24,280,456,26,NULL);
    AC_UIItem(f,"friendly",va("Friendly hits: %d | Damage: %d    -%d",s.friendlyHits,s.friendlyDamage,r->penalty),24,310,456,26,NULL,"1 0.65 0.55 1");
    AC_UIItem(f,"total",va("FINAL SCORE: %d",r->total),24,350,456,40,NULL,"1 0.85 0.25 1");
    AC_UIItem(f,"previous",va("Previous best on this difficulty: %d",r->previous),24,400,456,26,NULL);
    AC_UIItem(f,"rules","Kills + headshots + grenade bonus + accuracy - friendly fire",24,452,912,26,NULL);
    AC_UIItem(f,"list","Mission List",24,500,220,30,"ac_level_list");
    AC_UIItem(f,"main","Main Menu",716,500,220,30,"ac_main_menu");
    FS_Printf(f,"end.\n");FS_FCloseFile(f);AC_OpenGeneratedMenu("ac_score_results");
}
static const char *AC_OperationNumber(int index)
{
    static const char *numbers[] = {
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
        "XI", "XII", "XIII", "XIV", "XV"
    };
    static_assert(sizeof(numbers)/sizeof(numbers[0]) == AC_MISSION_COUNT,
                  "Add Roman labels when the operation count changes");
    return index>=0 && index<AC_MISSION_COUNT ? numbers[index] : "";
}

static void AC_ShowOperations(void)
{
    int selected=Cmd_Argc()>1?atoi(Cmd_Argv(1)):-1;
    int region=Cmd_Argc()>2?atoi(Cmd_Argv(2)):-1;
    if(Cmd_Argc()>3 && strlen(Cmd_Argv(3))==1 && Cmd_Argv(3)[0]>='0' && Cmd_Argv(3)[0]<='2')
        Cvar_Set("ac_next_skill",Cmd_Argv(3));
    int difficulty=Cvar_VariableIntegerValue("ac_next_skill");
    if(selected<0||selected>=AC_MISSION_COUNT||!AC_MissionState(selected)) {
        selected=-1;
        for(int i=0;i<AC_MISSION_COUNT;i++) if(AC_MissionState(i)) {
            selected=i;if(AC_MissionState(i)!=2)break;
        }
    }
    if(region<0||region>1)region=selected>=0?ac_mapMarkers[0][selected].region:0;
    if(selected>=0&&ac_mapMarkers[0][selected].region!=region)selected=-1;
    if(selected<0)for(int i=0;i<AC_MISSION_COUNT;i++)
        if(AC_MissionState(i)&&ac_mapMarkers[0][i].region==region){selected=i;break;}
    const char *menuName="ac_campaign_operations";
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_campaign_operations.urc");if(!f)return;
    FS_Printf(f,"menu \"%s\" 960 540 NONE 0\nvirtualres 1\nfullscreen 1\nbgfill 0 0 0 1\nbgcolor 0.055 0.07 0.055 1\nborderstyle NONE\n",menuName);
    FS_Printf(f,"widescreenbackground \"textures/ac/menu_background\"\n");
    AC_UIItem(f,"heading","ALLIED CAMPAIGN / OPERATIONS",24,16,640,34,NULL);
    AC_UIItem(f,"reset_progress","Reset Progress",756,20,180,28,"ac_reset_progress","1 0.58 0.45 1");
    for(int r=0;r<2;r++)
        AC_UIItem(f,va("region_%d",r),ac_mapRegions[r].name,24+r*462,62,450,30,va("ac_campaign -1 %d",r),r==region?"1 0.82 0.32 1":"0.85 0.85 0.72 1");
    FS_Printf(f,"resource\nLabel\n{\nname map_surface\nrect 24 110 560 330\nfgcolor 1 1 1 1\nbgcolor 0 0 0 0\nborderstyle NONE\nshader ac_map_%d\n}\n",region);
    int leaders[AC_MISSION_COUNT];for(int i=0;i<AC_MISSION_COUNT;i++)leaders[i]=-1;
    for(int i=0;i<AC_MISSION_COUNT;i++)if(AC_MissionState(i)&&ac_mapMarkers[0][i].region==region&&leaders[i]<0) {
        leaders[i]=i;
        for(int j=i+1;j<AC_MISSION_COUNT;j++)if(AC_MissionState(j)&&ac_mapMarkers[0][j].region==region&&leaders[j]<0
            &&fabs(ac_mapMarkers[region][j].x-ac_mapMarkers[region][i].x)<28
            &&fabs(ac_mapMarkers[region][j].y-ac_mapMarkers[region][i].y)<22)leaders[j]=i;
    }
    for(int i=0;i<AC_MISSION_COUNT;i++)if(leaders[i]==i) {
        int members[AC_MISSION_COUNT],n=0,chosen=0;
        for(int j=0;j<AC_MISSION_COUNT;j++)if(leaders[j]==i) {
            if(j==selected)chosen=n;members[n++]=j;
        }
        if(members[0]!=i)continue;
        int target=n>1?members[(chosen+1)%n]:i,state=AC_MissionState(i);
        for(int j=0;j<n;j++)if(AC_MissionState(members[j])!=2)state=AC_MissionState(members[j]);
        const acMapMarker_t &p=ac_mapMarkers[region][i];int x=24+(int)p.x,y=110+(int)p.y;
        const str label=n>1?va("%d",n):AC_OperationNumber(i);
        // Keep cluster counts Arabic; wider Roman labels stay centered on the location.
        const int width=label.length()>2?label.length()*10+4:24;
        AC_UIItem(f,va("marker_%d",i),label,x-width/2,y-10,width,20,va("ac_campaign %d %d",target,region),AC_StateColor(state));
    }
    if(selected>=0) {
        const acMission_t &m=ac_missions[selected];int state=AC_MissionState(selected);
        AC_UIItem(f,"title",m.title,608,110,328,30,NULL,"1 0.85 0.4 1");
        AC_UIItem(f,"date",strstr(m.date,"unspecified")?"1945 / exact date unspecified":m.date,608,146,328,24,NULL);
        AC_UIItem(f,"place",m.place,608,176,328,24,NULL);
        AC_UIItem(f,"hero",va("%s / %s",m.game==0?"Allied Assault":m.game==1?"Spearhead":"Breakthrough",m.hero),608,206,328,24,NULL);
        bool custom=false;
        for(int s=0;s<AC_LOADOUT_SLOTS;s++) {
            const int i=Cvar_VariableIntegerValue(va("ac_loadout_%d",s))-1;
            if(i>=0 && i<AC_LOADOUT_COUNT && ac_loadoutWeapons[i].selectable && ac_loadoutWeapons[i].slot==s)custom=true;
        }
        AC_UIItem(f,"loadout",state==2?(custom?"Loadout: CUSTOM / Change":"Loadout: DEFAULT / Change"):"Loadout: mission equipment",608,236,328,24,state==2?"ac_loadout":NULL,"0.7 0.85 0.7 1",14);
        AC_UIItem(f,"status",AC_StateName(state),608,268,144,30,NULL,AC_StateColor(state));
        AC_UIItem(f,"start",state==2?"Replay Mission":"Start Mission",764,268,172,30,va("ac_mission %d",selected),AC_StateColor(state));
    } else AC_UIItem(f,"empty","No operations unlocked in this region",608,146,328,30,NULL);
    int row=0;
    for(int i=0;i<AC_MISSION_COUNT;i++)if(AC_MissionState(i)&&ac_mapMarkers[0][i].region==region) {
        AC_UIItem(f,va("mission_%d",i),va("%s %s%s",AC_OperationNumber(i),i==selected?"> ":"",ac_missions[i].title),608,316+row*22,328,21,va("ac_campaign %d %d",i,region),i==selected?"1 0.85 0.3 1":AC_StateColor(AC_MissionState(i)));row++;
    }
    AC_UIItem(f,"difficulty_label","Next mission difficulty",24,446,560,24,NULL);
    for(int i=0;i<3;i++)
        AC_UIItem(f,va("difficulty_%d",i),i==0?"Easy":i==1?"Medium":"Hard",24+i*190,474,180,26,
            va("ac_campaign %d %d %d",selected,region,i),i==difficulty?"1 0.85 0.3 1":"0.85 0.9 0.8 1");
    AC_UIItem(f,"back","Main Menu",24,508,140,26,"ac_main_menu");
    AC_UIItem(f,"continue","Continue Campaign",176,508,192,26,"ac_continue");
    AC_UIItem(f,"options","Allied Campaign Options",380,508,260,26,"ac_ui_options");
    for(int i=0;i<3;i++)AC_UIItem(f,va("saves_%d",i),i==0?"AA saves":i==1?"SH saves":"BT saves",656+i*96,508,88,26,va("ac_context %d saves",i));
    FS_Printf(f,"end.\n");FS_FCloseFile(f);
    menuManager.Unlock(NULL);menuManager.ClearMenus(true);
    Menu *old=menuManager.FindMenu(menuName);
    if(old) {
        UIWidgetContainer *root=(UIWidgetContainer *)old->GetContainerWidget();
        menuManager.DeleteMenu(old);
        while(root->getFirstChild()) delete root->getFirstChild();
        delete root->m_layout;delete root;delete old;
    }
    new UILayout("ui/ac_campaign_operations.urc");
    UIWidgetContainer *root=(UIWidgetContainer *)uWinMan.FindWidget(menuName);
    if(root) {
        Menu *menu=new Menu(menuName);menu->setFullscreen(root->isFullscreen());
        menu->setVidMode(root->getVidMode());menu->AddMenuItem(root);
        UI_ForceMenu(menuName);UI_CloseConsole();
    }
}

static void AC_ResetProgressMenu_f(void)
{
    const char *name = "ac_campaign_reset";
    if (Cmd_Argc() > 1 && !strcmp(Cmd_Argv(1), "confirm")) {
        Menu *current = menuManager.CurrentMenu();
        if (!current || current->m_name != name) {
            Com_Printf("AC_RESET_REQUIRES_CONFIRMATION\n");
            return;
        }
        if (AC_ResetCampaignProgress()) Cbuf_AddText("disconnect\nac_campaign\n");
        else Com_Printf("AC_PROGRESS_ERROR reset failed; progress retained\n");
        return;
    }
    if (!menuManager.FindMenu(name)) {
        fileHandle_t f = FS_FOpenFileWrite_HomeData("ui/ac_campaign_reset.urc");
        if (!f) return;
        FS_Printf(f,"menu \"%s\" 960 540 NONE 0\nvirtualres 1\nfullscreen 1\nbgfill 0.055 0.07 0.055 1\nborderstyle NONE\n",name);
        AC_UIItem(f,"heading","RESET CAMPAIGN PROGRESS?",180,142,600,40,NULL,"1 0.58 0.45 1");
        AC_UIItem(f,"warning","Completed operations and mission unlocks will be reset.",180,202,600,30,NULL);
        AC_UIItem(f,"restart","Continue Campaign will start from the first operation.",180,242,600,30,NULL);
        AC_UIItem(f,"preserved","Your saved games and options will NOT be deleted.",180,282,600,30,NULL);
        AC_UIItem(f,"cancel","Cancel",240,358,200,36,"popmenu 0");
        AC_UIItem(f,"confirm","Reset Progress",520,358,200,36,"ac_reset_progress confirm","1 0.58 0.45 1");
        FS_Printf(f,"end.\n"); FS_FCloseFile(f);
        UI_LoadMenu(name);
    }
    UI_PushMenu(name);
}

static void AC_BriefingPlay_f(void)
{
    int op=Cvar_VariableIntegerValue("ac_operation");
    if(!Cvar_VariableIntegerValue("ac_campaign_mode") || Cvar_VariableIntegerValue("ac_replay")!=3
        || op<0 || op>=AC_MISSION_COUNT || ac_missions[op].game!=com_target_game->integer || !ac_missions[op].game) return;
    const char *file=strrchr(ac_missions[op].briefing,'/');if(!file)return;
    if(FS_ReadFile(va("video/%s.roq",file+1),NULL)<0) {
        Com_Printf("AC_BRIEFING_ERROR missing video\n");Cbuf_AddText("ac_return_main\n");return;
    }
    menuManager.Unlock(NULL);menuManager.ClearMenus(true);UI_CloseConsole();
    Cvar_Set("nextmap","ac_return_main");
    Cbuf_AddText(va("cinematic %s.roq\n",file+1));
    Com_Printf("AC_BRIEFING_VIDEO %s.roq\n",file+1);
}

static void AC_LevelList_f(void)
{
    int page=Cmd_Argc()>1?atoi(Cmd_Argv(1)):0;
    int selected=Cmd_Argc()>2?atoi(Cmd_Argv(2)):-1;
    int difficulty=Cmd_Argc()>3?atoi(Cmd_Argv(3)):-1;
    int count=AC_LEVEL_COUNT,unlocked=0;
    const int rows=11;
    const char *name="ac_level_list";
    for(int i=0;i<AC_LEVEL_COUNT;i++)if(AC_LevelCompleted(i))unlocked++;
    int pages=count?(count+rows-1)/rows:1;
    if(page<0)page=0;if(page>=pages)page=pages-1;
    if(!AC_LevelCompleted(selected))selected=-1;
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_level_list.urc");if(!f)return;
    FS_Printf(f,"menu \"%s\" 960 540 NONE 0\nvirtualres 1\nfullscreen 1\nbgfill 0.055 0.07 0.055 1\nborderstyle NONE\n",name);
    FS_Printf(f,"widecanvas\nwidescreenbackground \"textures/ac/menu_background\"\n");
    AC_UIItem(f,"heading","MISSION LIST",24,16,912,34,NULL,"1 0.85 0.4 1");
    AC_UIItem(f,"description","Highscore runs: complete the level in one attempt. No saving or loading.",24,58,912,28,NULL);
    const char *columns[]={"Easy best","Medium best","Hard best","Last run"};
    for(int c=0;c<4;c++)AC_UIItem(f,va("column_%d",c),columns[c],500+c*108,90,c==3?112:104,24,NULL,"0.95 0.89 0.7 1",12);
    for(int row=0;row<rows && page*rows+row<count;row++) {
        int index=page*rows+row;const acLevel_t &level=ac_levels[index];
        const acMission_t &op=ac_missions[level.operation];
        char item[32],title[256],command[64];
        Com_sprintf(item,sizeof(item),"level_%d",index);
        Com_sprintf(title,sizeof(title),"%s %s / %s",selected==index?">":" ",op.game==0?"AA":op.game==1?"SH":"BT",AC_LevelCompleted(index)?level.title:"LOCKED");
        Com_sprintf(command,sizeof(command),"ac_level_list %d %d -1",page,index);
        AC_UIItem(f,item,title,24,120+row*25,464,24,AC_LevelCompleted(index)?command:NULL,
            !AC_LevelCompleted(index)?"1 0.25 0.2 1":selected==index?"1 0.85 0.4 1":"0.85 0.9 0.8 1",12);
        acScoreRecord_t record;AC_GetScoreRecord(index,&record);
        for(int c=0;c<4;c++) {
            Com_sprintf(item,sizeof(item),"score_%d_%d",index,c);
            if(c<3)Com_sprintf(title,sizeof(title),record.played[c]?"%d":"--",record.best[c]);
            else if(record.hasLast)Com_sprintf(title,sizeof(title),"%d (%s)",record.last,record.lastSkill==0?"E":record.lastSkill==1?"M":"H");
            else Q_strncpyz(title,"--",sizeof(title));
            AC_UIItem(f,item,title,500+c*108,120+row*25,c==3?112:104,24,NULL,"0.95 0.89 0.7 1",12);
        }

    }
    AC_UIItem(f,"page",va("Page %d / %d   |   %d / %d levels unlocked",page+1,pages,unlocked,count),24,409,536,26,NULL);
    if(page>0)AC_UIItem(f,"previous","Previous",696,409,112,26,va("ac_level_list %d",page-1));
    if(page+1<pages)AC_UIItem(f,"next","Next",824,409,112,26,va("ac_level_list %d",page+1));
    if(selected>=0) {
        AC_UIItem(f,"choose","Choose difficulty:",24,451,216,30,NULL);
        for(int i=0;i<3;i++)AC_UIItem(f,va("difficulty_%d",i),i==0?"Easy":i==1?"Medium":"Hard",252+i*148,451,132,30,
            va("ac_level_list %d %d %d",page,selected,i),difficulty==i?"1 0.85 0.4 1":"0.85 0.9 0.8 1");
        if(difficulty>=0 && difficulty<=2)AC_UIItem(f,"play","Start Score Run",712,451,224,30,va("ac_level_replay %d %d",selected,difficulty),"1 0.85 0.4 1");
    }
    AC_UIItem(f,"back","Main Menu",24,504,180,28,"ac_main_menu");
    AC_UIItem(f,"return_hint","Finish to record a score. Abandoning awards no score.",252,504,684,28,NULL);
    FS_Printf(f,"end.\n");FS_FCloseFile(f);
    menuManager.Unlock(NULL);menuManager.ClearMenus(true);
    Menu *old=menuManager.FindMenu(name);
    if(old) {
        UIWidgetContainer *root=(UIWidgetContainer *)old->GetContainerWidget();menuManager.DeleteMenu(old);
        while(root->getFirstChild())delete root->getFirstChild();
        delete root->m_layout;delete root;delete old;
    }
    new UILayout("ui/ac_level_list.urc");
    UIWidgetContainer *root=(UIWidgetContainer *)uWinMan.FindWidget(name);
    if(root) {
        Menu *menu=new Menu(name);menu->setFullscreen(root->isFullscreen());
        menu->setVidMode(root->getVidMode());menu->AddMenuItem(root);UI_ForceMenu(name);UI_CloseConsole();
    }
}

static void AC_BriefingMenu_f(void)
{
    const char *name="ac_briefing_room";
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_briefing_room.urc");if(!f)return;
    FS_Printf(f,"menu \"%s\" 960 540 NONE 0\nvirtualres 1\nwidecanvas\nfullscreen 1\nbgfill 0.055 0.07 0.055 1\nborderstyle NONE\n",name);
    FS_Printf(f,"widescreenbackground \"textures/ac/menu_background\"\n");
    AC_UIItem(f,"heading","BRIEFING ROOM",24,16,912,34,NULL,"1 0.85 0.4 1");
    AC_UIItem(f,"description","Select a briefing. More unlock as you advance through Operations.",24,58,912,28,NULL);
    int row=0;
    for(int i=0;i<AC_MISSION_COUNT;i++) {
        if(!AC_MissionState(i))continue;
        bool duplicate=false;
        for(int j=0;j<i;j++)if(AC_MissionState(j) && !strcmp(ac_missions[i].briefing,ac_missions[j].briefing))duplicate=true;
        if(duplicate)continue;
        const acMission_t &op=ac_missions[i];
        char item[32],title[256],command[64];
        Com_sprintf(item,sizeof(item),"briefing_%d",i);
        Com_sprintf(title,sizeof(title),"%s / %s",op.game==0?"AA":op.game==1?"SH":"BT",op.title);
        Com_sprintf(command,sizeof(command),"ac_briefing_replay %d",i);
        AC_UIItem(f,item,title,24,104+row*30,912,28,command);row++;
    }
    if(!row)AC_UIItem(f,"empty","No briefings available.",24,104,912,28,NULL);
    AC_UIItem(f,"back","Main Menu",24,504,180,28,"ac_main_menu");
    AC_UIItem(f,"count",va("%d briefings unlocked",row),252,504,684,28,NULL);
    FS_Printf(f,"end.\n");FS_FCloseFile(f);
    menuManager.Unlock(NULL);menuManager.ClearMenus(true);
    Menu *old=menuManager.FindMenu(name);
    if(old) {
        UIWidgetContainer *root=(UIWidgetContainer *)old->GetContainerWidget();menuManager.DeleteMenu(old);
        while(root->getFirstChild())delete root->getFirstChild();
        delete root->m_layout;delete root;delete old;
    }
    new UILayout("ui/ac_briefing_room.urc");
    UIWidgetContainer *root=(UIWidgetContainer *)uWinMan.FindWidget(name);
    if(root) {
        Menu *menu=new Menu(name);menu->setFullscreen(root->isFullscreen());
        menu->setVidMode(root->getVidMode());menu->AddMenuItem(root);UI_ForceMenu(name);UI_CloseConsole();
    }
}
