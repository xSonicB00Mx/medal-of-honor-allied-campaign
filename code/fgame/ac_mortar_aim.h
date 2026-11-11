#include "../corepp/tiki.h"

// Prediction does not spawn entities, change archive layouts or consume gameplay RNG.
static void ACMortarAim(Weapon *weapon, Entity *viewer, Entity *base, const str& projectile)
{
    if(g_gametype->integer!=GT_SINGLE_PLAYER || !viewer || !viewer->client
        || !Q_stristr(projectile.c_str(),"granatwerferproj"))return;
    auto *tiki=gi.modeltiki(CanonicalTikiName(projectile));
    if(!tiki)return;
    float speed=0,gravity=0,life=0;Vector mins(0,0,0),maxs(0,0,0),added(0,0,0);bool inherit=false;
    for(int i=0;i<tiki->a->num_server_initcmds;++i) {
        const auto& c=tiki->a->server_initcmds[i];if(c.num_args<2)continue;
        const char *key=c.args[0],*value=c.args[1];
        if(!Q_stricmp(key,"speed"))speed=atof(value);
        else if(!Q_stricmp(key,"gravity"))gravity=atof(value);
        else if(!Q_stricmp(key,"life"))life=atof(value);
        else if(!Q_stricmp(key,"addownervelocity"))inherit=atoi(value)!=0;
        else if(!Q_stricmp(key,"setsize") && c.num_args>=3) {sscanf(value,"%f %f %f",&mins.x,&mins.y,&mins.z);sscanf(c.args[2],"%f %f %f",&maxs.x,&maxs.y,&maxs.z);}
        else if(!Q_stricmp(key,"addvelocity") && c.num_args>=4)added=Vector(atof(c.args[1]),atof(c.args[2]),atof(c.args[3]));
    }
    if(speed<=0 || life<=0)return;
    // Fixed-turret bases become solid again during their Think; their own shells
    // must be able to leave the barrel. Hide only our assembly for this query.
    struct IgnoreAssembly {
        Entity *weapon,*base,*legacy=nullptr;int wc,bc,lc=0;
        IgnoreAssembly(Entity *w,Entity *b):weapon(w),base(b),wc(w->edict->r.contents),bc(b?b->edict->r.contents:0){w->edict->r.contents=0;if(b)b->edict->r.contents=0;}
        ~IgnoreAssembly(){weapon->edict->r.contents=wc;if(base)base->edict->r.contents=bc;if(legacy)legacy->edict->r.contents=lc;}
    } ignore(weapon,base==weapon?nullptr:base);
    Vector pos,dir;weapon->GetMuzzlePosition(pos,NULL,dir,NULL,NULL);
    Vector velocity=dir*(speed+(inherit?fmaxf(0,DotProduct(viewer->velocity,dir)):0))+added;
    // Match MOVETYPE_BOUNCE: clamp, apply gravity, then sweep the projectile box.
    const float dt=level.frametime;if(dt<=0)return;
    for(int step=0;step<1024 && step*dt<life;++step) {
        for(int k=0;k<3;++k)velocity[k]=Q_clamp_float(velocity[k],-sv_maxvelocity->value,sv_maxvelocity->value);
        velocity.z-=gravity*sv_gravity->value*dt;
        Vector end=pos+velocity*dt;
        trace_t tr=G_Trace(pos,mins,maxs,end,viewer,MASK_PROJECTILE,true,"AC mortar prediction");
        if(step==0 && tr.startsolid && tr.ent && tr.ent->entity && !ignore.legacy
            && Q_stristr(tr.ent->entity->model.c_str(),"granatwerfer_base")) {
            ignore.legacy=tr.ent->entity;ignore.lc=tr.ent->r.contents;tr.ent->r.contents=0;
            tr=G_Trace(pos,mins,maxs,end,viewer,MASK_PROJECTILE,true,"AC mortar prediction");
        }
        if(tr.startsolid || tr.allsolid){if(gi.Cvar_Get("ac_mortar_debug","0",0)->integer)gi.Printf("AC_MORTAR_BLOCK step=%d entity=%d model=%s turret=%d viewer=%d start=%.1f,%.1f,%.1f\n",step,tr.entityNum,tr.ent && tr.ent->entity?tr.ent->entity->model.c_str():"world",weapon->entnum,viewer->entnum,pos.x,pos.y,pos.z);return;}
        if(tr.fraction<1) {
            if(tr.surfaceFlags&SURF_SKY)return;
            gi.SendServerCommand(viewer->entnum,"ac_mortar %.3f %.3f %.3f %.5f %.5f %.5f",tr.endpos[0],tr.endpos[1],tr.endpos[2],tr.plane.normal[0],tr.plane.normal[1],tr.plane.normal[2]);
            if(gi.Cvar_Get("ac_mortar_debug","0",0)->integer)gi.Printf("AC_MORTAR_AIM turret=%d point=%.3f,%.3f,%.3f flight=%.3f speed=%.1f gravity=%.1f\n",weapon->entnum,tr.endpos[0],tr.endpos[1],tr.endpos[2],(step+tr.fraction)*dt,speed,gravity);
            return;
        }
        pos=end;
    }
}
