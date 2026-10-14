#include "../qcommon/ac_missions.h"

static void AC_UIItem(fileHandle_t f,const char *name,const char *title,int x,int y,int w,int h,const char *command,const char *color="0.95 0.89 0.7 1")
{
    FS_Printf(f,"resource\n%s\n{\nname \"%s\"\ndontlocalize\ntitle \"%s\"\nrect %d %d %d %d\nfont facfont-20\nfgcolor %s\nbgcolor 0.07 0.085 0.06 0.95\nborderstyle NONE\n",command?"Button":"Label",name,title,x,y,w,h,color);
    if(command) FS_Printf(f,"stuffcommand \"%s\"\n",command);
    FS_Printf(f,"}\n");
}

static void AC_ShowOperations(void)
{
    int selected=Cmd_Argc()>1?atoi(Cmd_Argv(1)):-1;
    const char *menuName="ac_campaign_operations";
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_campaign_operations.urc");
    if(!f) return;
    if(selected<0||selected>=AC_MISSION_COUNT) {
        selected=0;for(int i=0;i<AC_MISSION_COUNT;i++) if(AC_MissionState(i)==3){selected=i;break;}
    }
    FS_Printf(f,"menu \"%s\" 960 540 NONE 0\nvirtualres 1\nfullscreen 1\nbgcolor 0.07 0.085 0.06 1\nborderstyle NONE\n",menuName);
    AC_UIItem(f,"heading","Allied Campaign",32,18,896,40,NULL);
    AC_UIItem(f,"continue","Continue Campaign",32,66,360,32,"ac_continue");
    AC_UIItem(f,"options","Allied Campaign Options",570,66,358,32,"ac_ui_options");
    for(int i=0;i<AC_MISSION_COUNT;i++) {
        int state=AC_MissionState(i);char title[180],cmd[64],name[32];
        Com_sprintf(title,sizeof(title),"%02d  [%s] %s",i+1,state==2?"DONE":state==3?"NEXT":state==1?"OPEN":"LOCKED",ac_missions[i].title);
        Com_sprintf(cmd,sizeof(cmd),"ac_campaign %d",i);Com_sprintf(name,sizeof(name),"mission_%d",i);
        AC_UIItem(f,name,title,32+(i/8)*452,112+(i%8)*36,436,32,cmd,state==0?"0.55 0.57 0.5 1":state==3?"1 0.82 0.3 1":"0.95 0.89 0.7 1");
    }
    const acMission_t &m=ac_missions[selected];
    AC_UIItem(f,"details",m.title,32,410,640,28,NULL);
    AC_UIItem(f,"date",m.date,32,440,640,24,NULL);
    char line[180],cmd[64];
    Com_sprintf(line,sizeof(line),"%s | %s | %s",m.place,m.game==0?"Allied Assault":m.game==1?"Spearhead":"Breakthrough",m.hero);
    AC_UIItem(f,"location",line,32,468,896,24,NULL);
    if(AC_MissionState(selected)) {
        Com_sprintf(cmd,sizeof(cmd),"ac_mission %d",selected);
        AC_UIItem(f,"start",AC_MissionState(selected)==2?"Replay":"Start Mission",700,420,228,40,cmd);
    }
    AC_UIItem(f,"back","Main Menu",32,502,180,28,"popmenu 0; pushmenu main");
    for(int i=0;i<3;i++) {
        Com_sprintf(cmd,sizeof(cmd),"ac_context %d saves",i);
        AC_UIItem(f,va("saves_%d",i),i==0?"AA saves":i==1?"SH saves":"BT saves",370+i*190,502,178,28,cmd);
    }
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
