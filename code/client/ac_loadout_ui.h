#include "../qcommon/ac_loadout.h"

static int AC_LoadoutChoice(int slot)
{
    const int i=Cvar_VariableIntegerValue(va("ac_loadout_%d",slot))-1;
    return i>=0 && i<AC_LOADOUT_COUNT && ac_loadoutWeapons[i].selectable && ac_loadoutWeapons[i].slot==slot?i:-1;
}

static void AC_Loadout_f(void)
{
    int slot=Cmd_Argc()>2?atoi(Cmd_Argv(2)):0;
    if(slot<0 || slot>=6)slot=0;
    bool changed=false;
    // Removed catalogue entries fall back to DEFAULT; other saved indices stay stable.
    for(int s=0;s<AC_LOADOUT_SLOTS;s++) {
        if(Cvar_VariableIntegerValue(va("ac_loadout_%d",s)) && AC_LoadoutChoice(s)<0) {
            Cvar_Set(va("ac_loadout_%d",s),"0");changed=true;
        }
    }
    if(Cmd_Argc()>1 && !strcmp(Cmd_Argv(1),"default")) {
        for(int s=0;s<AC_LOADOUT_SLOTS;s++)Cvar_Set(va("ac_loadout_%d",s),"0");
        changed=true;
    } else if(Cmd_Argc()>3 && !strcmp(Cmd_Argv(1),"select")) {
        const int n=atoi(Cmd_Argv(3));
        if(n>=0 && n<=AC_LOADOUT_COUNT && (!n || (ac_loadoutWeapons[n-1].selectable && ac_loadoutWeapons[n-1].slot==slot))) {
            const str key=va("ac_loadout_%d",slot);
            Cvar_Set(key,va("%d",n));changed=true;
        }
    } else if(Cmd_Argc()>1 && !strcmp(Cmd_Argv(1),"shuffle")) {
        for(int s=0;s<AC_LOADOUT_SLOTS;s++) {
            int pool[AC_LOADOUT_COUNT],count=0;
            for(int i=0;i<AC_LOADOUT_COUNT;i++)if(ac_loadoutWeapons[i].selectable && ac_loadoutWeapons[i].slot==s)pool[count++]=i+1;
            if(count){const str key=va("ac_loadout_%d",s);Cvar_Set(key,va("%d",pool[rand()%count]));}
        }
        changed=true;
    }
    if(changed)Com_WriteConfiguration();
    const int selected=AC_LoadoutChoice(slot);
    int custom=0;for(int s=0;s<AC_LOADOUT_SLOTS;s++)if(AC_LoadoutChoice(s)>=0)custom++;
    fileHandle_t f=FS_FOpenFileWrite_HomeData("ui/ac_loadout.urc");if(!f)return;
    FS_Printf(f,"menu ac_loadout 960 540 NONE 0\nvirtualres 1\nwidecanvas\nfullscreen 1\nbgfill 0 0 0 1\nwidescreenbackground \"textures/ac/menu_background\"\n");
    AC_UIItem(f,"heading","LOADOUT / FIELD ARMORY",24,16,560,36,NULL,"1 0.85 0.4 1",24);
    AC_UIItem(f,"default_all","DEFAULT",760,20,176,30,"ac_loadout default","1 0.58 0.45 1");
    AC_UIItem(f,"rules","Completed Operations only. New missions and Mission List use standard equipment.",24,62,912,25,NULL,"0.8 0.85 0.78 1",14);
    for(int s=0;s<AC_LOADOUT_SLOTS;s++) {
        if(s==6)continue;
        int c=AC_LoadoutChoice(s);
        AC_UIItem(f,va("slot_%d",s),ac_loadoutSlots[s],24,106+s*48,224,23,va("ac_loadout view %d",s),s==slot?"1 0.85 0.4 1":"0.85 0.9 0.8 1",16);
        AC_UIItem(f,va("equipped_%d",s),c<0?"DEFAULT":ac_loadoutWeapons[c].name,24,129+s*48,224,21,va("ac_loadout view %d",s),"0.65 0.75 0.65 1",12);
    }
    AC_UIItem(f,"choose",ac_loadoutSlots[slot],268,106,292,28,NULL,"1 0.85 0.4 1",20);
    AC_UIItem(f,"slot_default",selected<0?"> DEFAULT":"DEFAULT",268,142,292,23,va("ac_loadout select %d 0",slot),selected<0?"1 0.85 0.4 1":"0.85 0.9 0.8 1",14);
    int row=0;
    for(int i=0;i<AC_LOADOUT_COUNT;i++)if(ac_loadoutWeapons[i].selectable && ac_loadoutWeapons[i].slot==slot) {
        const acLoadoutWeapon_t &w=ac_loadoutWeapons[i];
        AC_UIItem(f,va("weapon_%d",i),va("%s%s",selected==i?"> ":"",w.name),268,171+row*22,292,21,va("ac_loadout select %d %d",slot,i+1),selected==i?"1 0.85 0.4 1":"0.85 0.9 0.8 1",13);
        row++;
    }
    if(selected>=0) {
        const acLoadoutWeapon_t &w=ac_loadoutWeapons[selected];
        Cvar_Set("ac_loadout_preview",w.model);
        AC_UIItem(f,"model_name",w.name,584,106,352,30,NULL,"1 0.85 0.4 1",18);
        FS_Printf(f,"resource\nLabel\n{\nname weapon_preview\nrect 620 145 280 280\nbgcolor 0 0 0 0\nborderstyle NONE\nlinkcvar ac_loadout_preview\nrendermodel 1\nmodelangles \"0 90 180\"\nmodelscale 1.25\nmodelanim idle\n}\n");
        AC_UIItem(f,"origin",w.game==0?"ALLIED ASSAULT":w.game==1?"SPEARHEAD":"BREAKTHROUGH",584,432,352,24,NULL,"0.65 0.75 0.65 1",14);
    } else {
        AC_UIItem(f,"default_title","MISSION EQUIPMENT",584,188,352,34,NULL,"1 0.85 0.4 1",20);
        AC_UIItem(f,"default_hint","Original gear for this slot.",584,244,352,26,NULL);
        AC_UIItem(f,"default_note","Select a weapon to inspect it.",584,280,352,26,NULL);
    }
    AC_UIItem(f,"saved",custom?va("%d custom slots / selection saved",custom):"DEFAULT / original mission equipment",24,462,536,26,NULL,"0.6 0.85 0.65 1",14);
    AC_UIItem(f,"shuffle","SHUFFLE LOADOUT",584,466,352,26,"ac_loadout shuffle","1 0.85 0.4 1",15);
    AC_UIItem(f,"back","Main Menu",24,506,180,26,"ac_main_menu");
    AC_UIItem(f,"hint","Pickups stay available. Press a weapon-class key again to cycle.",220,506,510,26,NULL,"0.8 0.85 0.78 1",12);
    AC_UIItem(f,"operations","Operations",752,506,184,26,"ac_campaign");
    FS_Printf(f,"end.\n");FS_FCloseFile(f);AC_OpenGeneratedMenu("ac_loadout");
    Com_Printf("AC_LOADOUT_MENU slot=%d selected=%d custom=%d\n",slot,selected+1,custom);
}
