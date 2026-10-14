#include "../qcommon/ac_missions.h"
#include "ac_map.h"

static const char *AC_StateColor(int state)
{return state==0?"1 0.30 0.25 1":state==2?"0.57 0.80 0.61 1":state==3?"1 0.82 0.32 1":"0.72 0.87 1 1";}
static const char *AC_StateName(int state)
{return state==0?"LOCKED":state==2?"COMPLETE":state==3?"NEXT":"AVAILABLE";}
static void AC_UIItem(fileHandle_t f,const char *name,const char *title,int x,int y,int w,int h,const char *command,const char *color="0.95 0.89 0.7 1")
{
    FS_Printf(f,"resource\n%s\n{\nname \"%s\"\ndontlocalize\ntitle \"%s\"\nrect %d %d %d %d\nfont facfont-20\nfgcolor %s\nbgcolor 0.075 0.095 0.075 0.96\nborderstyle NONE\n",command?"Button":"Label",name,title,x,y,w,h,color);
    if(command) FS_Printf(f,"stuffcommand \"%s\"\n",command);
    FS_Printf(f,"}\n");
}
static void AC_ShowOperations(void)
{
    int selected=Cmd_Argc()>1?atoi(Cmd_Argv(1)):-1;
    int region=Cmd_Argc()>2?atoi(Cmd_Argv(2)):0;
    if(region<0||region>5) region=0;
    const char *menuName="ac_campaign_operations";
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_campaign_operations.urc");if(!f) return;
    if(selected<0||selected>=AC_MISSION_COUNT) {
        selected=0;for(int i=0;i<AC_MISSION_COUNT;i++) if(AC_MissionState(i)==3||AC_MissionState(i)==1){selected=i;break;}
    }
    const acMission_t &m=ac_missions[selected];int state=AC_MissionState(selected);
    FS_Printf(f,"menu \"%s\" 960 540 NONE 0\nvirtualres 1\nfullscreen 1\nbgfill 0 0 0 1\nbgcolor 0.055 0.07 0.055 1\nborderstyle NONE\n",menuName);
    FS_Printf(f,"resource\nLabel\n{\nname canvas\nrect 0 0 960 540\nbgcolor 0.055 0.07 0.055 1\nborderstyle NONE\n}\n");
    AC_UIItem(f,"heading","ALLIED CAMPAIGN / OPERATIONS",24,16,640,34,NULL);
    AC_UIItem(f,"previous","Previous",724,20,100,28,va("ac_campaign %d %d",(selected+14)%15,ac_mapMarkers[0][(selected+14)%15].region));
    AC_UIItem(f,"next","Next",836,20,100,28,va("ac_campaign %d %d",(selected+1)%15,ac_mapMarkers[0][(selected+1)%15].region));
    for(int r=0;r<6;r++) {
        int first=selected;if(r && ac_mapMarkers[0][first].region!=r) for(int i=0;i<15;i++) if(ac_mapMarkers[0][i].region==r){first=i;break;}
        AC_UIItem(f,va("region_%d",r),ac_mapRegions[r].name,24+r*154,62,142,30,va("ac_campaign %d %d",first,r),r==region?"1 0.82 0.32 1":"0.85 0.85 0.72 1");
    }
    FS_Printf(f,"resource\nLabel\n{\nname map_surface\nrect 24 110 560 330\nfgcolor 1 1 1 1\nbgcolor 0 0 0 0\nborderstyle NONE\nshader ac_map_%d\n}\n",region);
    if(!region) {
        for(int r=1;r<6;r++) {
            int first=-1,count=0,groupState=0,done=0;
            for(int i=0;i<15;i++) if(ac_mapMarkers[0][i].region==r){if(first<0)first=i;count++;int s=AC_MissionState(i);if(s==3||s==1)groupState=s;if(s==2)done++;}
            if(!groupState && done)groupState=done==count?2:1;
            const acMapMarker_t &p=ac_mapMarkers[0][first];int x=(int)p.x+24,y=(int)p.y+110;
            const char *codes[]={"","NA","IT","WE","NO","BE"};
            AC_UIItem(f,va("area_%d",r),codes[r],x-16,y-12,32,24,va("ac_campaign %d %d",first,r),AC_StateColor(groupState));
        }
    } else {
        for(int i=0;i<15;i++) if(ac_mapMarkers[0][i].region==region) {
            // Coincident regional anchors form one expandable group, never displaced fake coordinates.
            int first=i,count=0;for(int j=0;j<15;j++) if(ac_mapMarkers[0][j].region==region && ac_mapMarkers[region][j].x==ac_mapMarkers[region][i].x && ac_mapMarkers[region][j].y==ac_mapMarkers[region][i].y){if(j<first)first=j;count++;}
            if(first!=i) continue;
            int target=i;if(count>1){target=first;for(int j=first;j<15;j++) if(j==selected && ac_mapMarkers[region][j].x==ac_mapMarkers[region][i].x){target=j+1;if(target>=15 || ac_mapMarkers[region][target].x!=ac_mapMarkers[region][i].x)target=first;break;}}
            const acMapMarker_t &p=ac_mapMarkers[region][i];int x=24+(int)p.x,y=110+(int)p.y;
            int markerState=AC_MissionState(i);
            if(count>1)for(int j=i;j<i+count;j++)if(AC_MissionState(j)==3||AC_MissionState(j)==1)markerState=AC_MissionState(j);
            AC_UIItem(f,va("marker_%d",i),count>1?"3":markerState==0?"L":markerState==2?"C":markerState==3?"N":"A",x-10,y-10,20,20,va("ac_campaign %d %d",target,region),AC_StateColor(markerState));
            // Only the selected marker gets a label; the region's complete list stays beside the map.
            if(i==selected || (count>1 && selected>=i && selected<i+count)) {
                int lx=x+14;if(lx+192>580)lx=x-204;int ly=y-12;
                AC_UIItem(f,"selected_marker",count>1?"Normandy / 3 operations":m.place,lx,ly,192,24,NULL,"1 0.85 0.4 1");
            }
        }
    }
    AC_UIItem(f,"title",m.title,608,110,328,30,NULL,"1 0.85 0.4 1");
    AC_UIItem(f,"date",strstr(m.date,"unspecified")?"1945 / exact date unspecified":m.date,608,146,328,24,NULL);
    AC_UIItem(f,"place",m.place,608,176,328,24,NULL);
    AC_UIItem(f,"hero",va("%s / %s",m.game==0?"Allied Assault":m.game==1?"Spearhead":"Breakthrough",m.hero),608,206,328,24,NULL);
    AC_UIItem(f,"precision","Approximate mission area",608,236,328,20,NULL,"0.68 0.71 0.61 1");
    AC_UIItem(f,"status",AC_StateName(state),608,268,144,30,NULL,AC_StateColor(state));
    if(state) AC_UIItem(f,"start",state==2?"Replay Mission":"Start Mission",764,268,172,30,va("ac_mission %d",selected),AC_StateColor(state));
    int listRegion=region?region:ac_mapMarkers[0][selected].region,row=0;
    AC_UIItem(f,"region_list",va("%s / operations",ac_mapRegions[listRegion].name),608,308,328,22,NULL);
    for(int i=0;i<15;i++) if(ac_mapMarkers[0][i].region==listRegion) {
        AC_UIItem(f,va("mission_%d",i),va("%02d %s%s",i+1,i==selected?"> ":"",ac_missions[i].title),608,338+row*24,328,22,va("ac_campaign %d %d",i,listRegion),AC_StateColor(AC_MissionState(i)));row++;
    }
    AC_UIItem(f,"locked_key","Locked",24,450,128,22,NULL,AC_StateColor(0));
    AC_UIItem(f,"open_key","Available",164,450,128,22,NULL,AC_StateColor(1));
    AC_UIItem(f,"done_key","Complete",304,450,128,22,NULL,AC_StateColor(2));
    AC_UIItem(f,"next_key","Next",444,450,140,22,NULL,AC_StateColor(3));
    AC_UIItem(f,"back","Original Menu",24,508,140,26,"popmenu 0; pushmenu main");
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
