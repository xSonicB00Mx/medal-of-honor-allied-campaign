#include "ac_weapon_policy.h"
#include <cstddef>
#include <cmath>
#include "../qcommon/ac_corpse_models.h"
#include "ac_wound_send.h"
// Shared confirmed visual contact: live pre-damage or independent corpse ray.
// Geometry and the isolated hash stream never consume gameplay randomness.
static void ACVisualHit(Entity *target,Weapon *weapon,const Vector& point,const Vector& direction,bool corpse=false,const ac_surface_hit_t *confirmed=nullptr) {
    if(g_gametype->integer!=GT_SINGLE_PLAYER || !target || (!corpse && !target->IsSubclassOfActor())
        || !target->edict->tiki || (!corpse && (target->health<=0 || target->IsDead())) || !weapon)return;
    int group=ACWeaponGroup(weapon->model.c_str());if(!group)return;
    static unsigned int serial=0;unsigned int event=++serial;
    ac_pose_t pose={};auto *e=target->edict;
    pose.entityNumber=e->s.number;pose.frames=e->s.frameInfo;pose.boneTags=e->s.bone_tag;
    pose.boneQuats=e->s.bone_quat;pose.actionWeight=e->s.actionWeight;pose.scale=e->s.scale;
    VectorCopy(target->origin,pose.origin);VectorCopy(target->angles,pose.angles);pose.surfaces=e->s.surfaces;
    vec3_t start;VectorMA(point,-64,direction,start);ac_surface_hit_t geometry={};
    if(confirmed)geometry=*confirmed;else gi.AC_SurfaceTrace(e->tiki,&pose,start,direction,&geometry);
    unsigned int seed=event*747796405u+(unsigned int)level.inttime*2891336453u+(unsigned int)e->s.number*277803737u;
    if(gi.Cvar_Get("ac_fx_debug","0",0)->integer)
        gi.Printf("AC_HIT id=%u time=%d entity=%d generation=%.3f weapon=%s group=%d seed=%u entry=%d exit=%d surface=%d/%d/%d\n",
            event,level.inttime,e->s.number,e->spawntime,weapon->model.c_str(),group,seed,geometry.entryValid,geometry.exitValid,
            geometry.entry.mesh,geometry.entry.surface,geometry.entry.triangle);
    if(gi.Cvar_Get("ac_fx_debug","0",0)->integer) {
        unsigned poseHash=2166136261u;const byte *bytes=(const byte*)pose.frames;
        for(unsigned i=0;i<sizeof(frameInfo_t)*MAX_FRAMEINFOS;++i)poseHash=(poseHash^bytes[i])*16777619u;
        gi.Printf("AC_CONTEXT id=%u context=%d usage=%d model=%s alive=%d pose=%u ray=%.5f,%.5f,%.5f\n",event,gi.Cvar_Get("com_target_game","0",0)->integer,e->s.usageIndex,target->model.c_str(),!corpse,poseHash,direction.x,direction.y,direction.z);
    }
    if(!geometry.entryValid)return;
    if(corpse && gi.Cvar_Get("ac_blood_mist","1",CVAR_ARCHIVE)->integer) {
        gi.SetBroadcastVisible(geometry.entry.position,NULL);
        gi.MSG_StartCGM(CGM_AC_FLESH);
        for(int k=0;k<3;++k)gi.MSG_WriteCoord(geometry.entry.position[k]);
        gi.MSG_WriteDir(geometry.entry.normal);gi.MSG_WriteBits(group>=3,1);gi.MSG_EndCGM();
    }
    ACSendWound(target,pose,geometry.entry,event,seed,group,0);
    if(geometry.exitValid)ACSendWound(target,pose,geometry.exit,event,seed,group,1);
    const auto& a=geometry.entry;const auto& b=geometry.exit;
    gi.SendServerCommand(-1,"ac_hit %u %u %d %d %d %.3f %.3f %.3f %.5f %.5f %.5f %.3f %.3f %.3f %.5f %.5f %.5f %d %d %d %d %.6f %.6f %.6f %d %d %d %.6f %.6f %.6f",
        event,seed,e->s.number,group,geometry.exitValid,a.position[0],a.position[1],a.position[2],a.normal[0],a.normal[1],a.normal[2],
        b.position[0],b.position[1],b.position[2],direction.x,direction.y,direction.z,e->s.usageIndex,
        a.mesh,a.surface,a.triangle,a.bary[0],a.bary[1],a.bary[2],b.mesh,b.surface,b.triangle,b.bary[0],b.bary[1],b.bary[2]);
}

// No collision mask, entity health, death script or damage call is modified.
// Run only on accepted sections of the original, already spread bullet ray.
static bool ACCorpse(Entity *ent) {
    if(!ent || !ent->edict->tiki || (ent->edict->s.renderfx&RF_INVISIBLE)
        || (ent->edict->r.svFlags&SVF_NOCLIENT)
        || ((ent->edict->s.renderfx&RF_DONTDRAW) && !(ent->edict->s.renderfx&RF_AC_CORPSE_PROXY)))return false;
    if(ent->IsSubclassOfActor())return ent->IsDead() || ent->health<=0;
    for(const char *name:acCorpseModels)if(!Q_stricmp(ent->model.c_str(),name))return true;
    return false;
}
// A killed actor may retain a solid box throughout its death animation. Ignore
// only those actors for this synchronous bullet query, then restore contents
// before any damage/event processing. No relink, death callback or RNG draw.
// Independent of all visual toggles: disabling blood cannot change bullet damage.
static trace_t ACTraceBullet(const Vector& start,const Vector& end,Entity *owner,int mask=MASK_SHOT_TRIG) {
    int skipped[MAX_GENTITIES],contents[MAX_GENTITIES],count=0;
    trace_t hit;
    for(;;) {
        hit=G_Trace(start,vec_zero,vec_zero,end,owner,mask,false,"BulletAttack",true);
        Entity *ent=hit.ent?hit.ent->entity:nullptr;
        if(g_gametype->integer!=GT_SINGLE_PLAYER || !ent || !ent->IsSubclassOfActor()
            || (!ent->IsDead() && ent->health>0) || !ent->edict->r.contents || count==MAX_GENTITIES)break;
        skipped[count]=ent->edict->s.number;contents[count++]=ent->edict->r.contents;
        if(gi.Cvar_Get("ac_fx_debug","0",0)->integer)
            gi.Printf("AC_BULLET_PASS entity=%d health=%.1f dead=%d solid=%d contents=%d\n",ent->edict->s.number,ent->health,ent->deadflag,ent->edict->solid,ent->edict->r.contents);
        ent->edict->r.contents=0;
    }
    while(count) {--count;g_entities[skipped[count]].r.contents=contents[count];}
    return hit;
}
static void ACCorpseSegment(const Vector& start,const Vector& end,const Vector& direction,
    Weapon *weapon,bool *seen) {
    if(g_gametype->integer!=GT_SINGLE_PLAYER || !weapon || !ACWeaponGroup(weapon->model.c_str())
        || !gi.Cvar_Get("ac_corpse_effects","1",CVAR_ARCHIVE)->integer)return;
    float length=DotProduct(end-start,direction);if(length<=0)return;
    for(int i=0;i<globals.num_entities;++i) {
        auto& e=g_entities[i];
        if(!e.inuse || !e.entity || seen[i] || !ACCorpse(e.entity))continue;
        // The engine shrinks corpse collision boxes. Broadphase uses a conservative
        // sphere; exact skinned triangles decide the hit, never that old box.
        float radius=128*fmaxf(1,e.s.scale);Vector delta=e.entity->origin-start;
        float along=DotProduct(delta,direction);
        if(along < -radius || along>length+radius || DotProduct(delta,delta)-along*along>radius*radius)continue;
        ac_pose_t pose={};pose.entityNumber=i;pose.frames=e.s.frameInfo;pose.boneTags=e.s.bone_tag;
        pose.boneQuats=e.s.bone_quat;pose.actionWeight=e.s.actionWeight;pose.scale=e.s.scale;
        VectorCopy(e.entity->origin,pose.origin);VectorCopy(e.entity->angles,pose.angles);pose.surfaces=e.s.surfaces;
        float offset=fmaxf(0,along-120);Vector from=start+direction*offset;ac_surface_hit_t geometry={};
        gi.AC_SurfaceTrace(e.tiki,&pose,from,direction,&geometry);
        if(!geometry.entryValid || offset+geometry.entry.distance>length+.05f)continue;
        seen[i]=true;
        ACVisualHit(e.entity,weapon,geometry.entry.position,direction,true,&geometry);
        if(gi.Cvar_Get("ac_fx_debug","0",0)->integer)gi.Printf("AC_CORPSE entity=%d usage=%d health=%.1f dead=%d solid=%d model=%s distance=%.3f\n",i,e.s.usageIndex,e.entity->health,e.entity->deadflag,e.solid,e.entity->model.c_str(),offset+geometry.entry.distance);
    }
}
