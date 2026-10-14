#include "ac_weapon_policy.h"
#include <cstddef>
#include "ac_wound_send.h"
// Called exactly once before damage for each confirmed, live human bullet contact.
// Geometry and the isolated hash stream never consume gameplay randomness.
static void ACVisualHit(Entity *target,Weapon *weapon,const Vector& point,const Vector& direction) {
    if(g_gametype->integer!=GT_SINGLE_PLAYER || !target || !target->IsSubclassOfActor()
        || !target->edict->tiki || target->health<=0 || !weapon)return;
    int group=ACWeaponGroup(weapon->model.c_str());if(!group)return;
    static unsigned int serial=0;unsigned int event=++serial;
    ac_pose_t pose={};auto *e=target->edict;
    pose.entityNumber=e->s.number;pose.frames=e->s.frameInfo;pose.boneTags=e->s.bone_tag;
    pose.boneQuats=e->s.bone_quat;pose.actionWeight=e->s.actionWeight;pose.scale=e->s.scale;
    VectorCopy(target->origin,pose.origin);VectorCopy(target->angles,pose.angles);pose.surfaces=e->s.surfaces;
    vec3_t start;VectorMA(point,-64,direction,start);ac_surface_hit_t geometry={};
    gi.AC_SurfaceTrace(e->tiki,&pose,start,direction,&geometry);
    unsigned int seed=event*747796405u+(unsigned int)level.inttime*2891336453u+(unsigned int)e->s.number*277803737u;
    if(gi.Cvar_Get("ac_fx_debug","0",0)->integer)
        gi.Printf("AC_HIT id=%u time=%d entity=%d generation=%.3f weapon=%s group=%d seed=%u entry=%d exit=%d surface=%d/%d/%d\n",
            event,level.inttime,e->s.number,e->spawntime,weapon->model.c_str(),group,seed,geometry.entryValid,geometry.exitValid,
            geometry.entry.mesh,geometry.entry.surface,geometry.entry.triangle);
    if(gi.Cvar_Get("ac_fx_debug","0",0)->integer) {
        unsigned poseHash=2166136261u;const byte *bytes=(const byte*)pose.frames;
        for(unsigned i=0;i<sizeof(frameInfo_t)*MAX_FRAMEINFOS;++i)poseHash=(poseHash^bytes[i])*16777619u;
        gi.Printf("AC_CONTEXT id=%u context=%d usage=%d model=%s alive=1 pose=%u ray=%.5f,%.5f,%.5f\n",event,gi.Cvar_Get("com_target_game","0",0)->integer,e->s.usageIndex,target->model.c_str(),poseHash,direction.x,direction.y,direction.z);
    }
    if(!geometry.entryValid)return;
    ACSendWound(target,pose,geometry.entry,event,seed,group,0);
    if(geometry.exitValid)ACSendWound(target,pose,geometry.exit,event,seed,group,1);
    const auto& a=geometry.entry;const auto& b=geometry.exit;
    gi.SendServerCommand(-1,"ac_hit %u %u %d %d %d %.3f %.3f %.3f %.5f %.5f %.5f %.3f %.3f %.3f %.5f %.5f %.5f %d",
        event,seed,e->s.number,group,geometry.exitValid,a.position[0],a.position[1],a.position[2],a.normal[0],a.normal[1],a.normal[2],
        b.position[0],b.position[1],b.position[2],direction.x,direction.y,direction.z,e->s.usageIndex);
}
