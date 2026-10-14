#include "../qcommon/ac_missions.h"
#include "ac_map.h"

static const char *AC_StateColor(int state)
{return state==2?"0.57 0.80 0.61 1":"1 0.82 0.32 1";}
static const char *AC_StateName(int state)
{return state==2?"COMPLETE":"CURRENT";}
static void AC_UIItem(fileHandle_t f,const char *name,const char *title,int x,int y,int w,int h,const char *command,const char *color="0.95 0.89 0.7 1")
{
    FS_Printf(f,"resource\n%s\n{\nname \"%s\"\ndontlocalize\ntitle \"%s\"\nrect %d %d %d %d\nfont facfont-20\nfgcolor %s\nbgcolor 0.075 0.095 0.075 0.96\nborderstyle NONE\n",command?"Button":"Label",name,title,x,y,w,h,color);
    if(command) FS_Printf(f,"stuffcommand \"%s\"\n",command);
    FS_Printf(f,"}\n");
}
static void AC_ShowOperations(void)
{
    int selected=Cmd_Argc()>1?atoi(Cmd_Argv(1)):-1;
    int region=Cmd_Argc()>2?atoi(Cmd_Argv(2)):-1;
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
    FS_Printf(f,"resource\nLabel\n{\nname canvas\nrect 0 0 960 540\nbgcolor 0.055 0.07 0.055 1\nborderstyle NONE\n}\n");
    AC_UIItem(f,"heading","ALLIED CAMPAIGN / OPERATIONS",24,16,640,34,NULL);
    int visible[AC_MISSION_COUNT],count=0,index=0;
    for(int i=0;i<AC_MISSION_COUNT;i++)if(AC_MissionState(i)) {
        if(i==selected)index=count;visible[count++]=i;
    }
    if(count>1) {
        int previous=visible[(index+count-1)%count],next=visible[(index+1)%count];
        AC_UIItem(f,"previous","Previous",724,20,100,28,va("ac_campaign %d %d",previous,ac_mapMarkers[0][previous].region));
        AC_UIItem(f,"next","Next",836,20,100,28,va("ac_campaign %d %d",next,ac_mapMarkers[0][next].region));
    }
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
        AC_UIItem(f,va("marker_%d",i),n>1?va("%d",n):va("%02d",i+1),x-12,y-10,24,20,va("ac_campaign %d %d",target,region),AC_StateColor(state));
    }
    if(selected>=0) {
        const acMission_t &m=ac_missions[selected];int state=AC_MissionState(selected);
        AC_UIItem(f,"title",m.title,608,110,328,30,NULL,"1 0.85 0.4 1");
        AC_UIItem(f,"date",strstr(m.date,"unspecified")?"1945 / exact date unspecified":m.date,608,146,328,24,NULL);
        AC_UIItem(f,"place",m.place,608,176,328,24,NULL);
        AC_UIItem(f,"hero",va("%s / %s",m.game==0?"Allied Assault":m.game==1?"Spearhead":"Breakthrough",m.hero),608,206,328,24,NULL);
        AC_UIItem(f,"precision","Approximate mission area",608,236,328,20,NULL,"0.68 0.71 0.61 1");
        AC_UIItem(f,"status",AC_StateName(state),608,268,144,30,NULL,AC_StateColor(state));
        AC_UIItem(f,"start",state==2?"Replay Mission":"Start Mission",764,268,172,30,va("ac_mission %d",selected),AC_StateColor(state));
    } else AC_UIItem(f,"empty","No operations unlocked in this region",608,146,328,30,NULL);
    int row=0;
    for(int i=0;i<AC_MISSION_COUNT;i++)if(AC_MissionState(i)&&ac_mapMarkers[0][i].region==region) {
        AC_UIItem(f,va("mission_%d",i),va("%02d %s%s",i+1,i==selected?"> ":"",ac_missions[i].title),608,316+row*22,328,21,va("ac_campaign %d %d",i,region),AC_StateColor(AC_MissionState(i)));row++;
    }
    AC_UIItem(f,"current_key","Current operation",24,450,270,24,NULL,AC_StateColor(1));
    AC_UIItem(f,"done_key","Completed",310,450,274,24,NULL,AC_StateColor(2));
    AC_UIItem(f,"back","Main Menu",24,508,140,26,"popmenu 0; pushmenu main");
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
