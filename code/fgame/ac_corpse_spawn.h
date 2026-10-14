// Preserve BSP artwork/collision; invisible non-solid skeletal adapters only.
#include "../qcommon/qfiles.h"
#include "../qcommon/ac_corpse_models.h"
#include <cmath>
#include "g_phys.h"
void ACSpawnStaticCorpses() {
    if(g_gametype->integer!=GT_SINGLE_PLAYER)return;
    void *buffer=nullptr;str path="maps/"+level.mapname+".bsp";
    int bytes=gi.FS_ReadFile(path.c_str(),&buffer,qfalse);
    if(bytes<(int)sizeof(dheader_t)){if(buffer)gi.FS_FreeFile(buffer);return;}
    const auto *header=(const dheader_t*)buffer;
    if(header->ident!=BSP_IDENT || header->version<17 || header->version>21){gi.FS_FreeFile(buffer);return;}
    int index=LUMP_STATICMODELDEF+(header->version<=18?1:0);
    const auto& lump=header->lumps[index];
    if(lump.fileofs<0 || lump.filelen<0 || lump.fileofs>bytes || lump.filelen>bytes-lump.fileofs || lump.filelen%sizeof(cStaticModel_t)) {
        gi.FS_FreeFile(buffer);return;
    }
    const auto *models=(const cStaticModel_t*)((byte*)buffer+lump.fileofs);int added=0;
    for(int i=0;i<lump.filelen/(int)sizeof(cStaticModel_t);++i) {
        const auto& m=models[i];if(!memchr(m.model,0,sizeof(m.model)))continue;
        char name[160];Com_sprintf(name,sizeof(name),!strnicmp(m.model,"models/",7)?"%s":"models/%s",m.model);
        int write=0;for(int read=0;name[read];++read) {
            char c=name[read]=='\\' ? '/' : name[read];
            if(c=='/' && write && name[write-1]=='/')continue;name[write++]=c;
        }name[write]=0;
        bool allowed=false;for(const char *known:acCorpseModels)if(!Q_stricmp(name,known)){allowed=true;break;}
        if(!allowed || !std::isfinite(m.scale) || m.scale<=0 || m.scale>8)continue;
        bool finite=true;for(int k=0;k<3;++k)if(!std::isfinite(m.origin[k]) || !std::isfinite(m.angles[k]))finite=false;
        if(!finite)continue;
        bool exists=false;
        for(int e=0;e<globals.num_entities;++e) {
            const auto& ent=g_entities[e];
            if(ent.inuse && ent.entity && (ent.s.renderfx&RF_AC_CORPSE_PROXY) &&
                !Q_stricmp(ent.entity->model.c_str(),name) && VectorCompare(ent.entity->origin,m.origin)){exists=true;break;}
        }
        if(exists)continue;
        if(globals.num_entities>=MAX_GENTITIES-128){gi.Printf("AC_STATIC_CORPSE capacity reached\n");break;}
        auto *proxy=new Animate();proxy->setModel(name);proxy->setOrigin(m.origin);proxy->setAngles(m.angles);proxy->setScale(m.scale);
        proxy->setSolidType(SOLID_NOT);proxy->setMoveType(MOVETYPE_NONE);proxy->takedamage=DAMAGE_NO;
        proxy->health=0;proxy->deadflag=DEAD_DEAD;proxy->NewAnim("idle");
        proxy->edict->s.renderfx=RF_DONTDRAW|RF_AC_CORPSE_PROXY;
        proxy->edict->r.svFlags&=~SVF_NOCLIENT;
        ++added;
    }
    gi.FS_FreeFile(buffer);
    if(gi.Cvar_Get("ac_fx_debug","0",0)->integer)gi.Printf("AC_STATIC_CORPSES map=%s added=%d\n",level.mapname.c_str(),added);
}
