// SP visual transport. Bounded chunks keep each reliable command under 1 KiB.
#include "../qcommon/ac_visual_random.h"
static void ACSendWound(Entity *target,const ac_pose_t& pose,const ac_surface_point_t& point,
    unsigned event,unsigned seed,int group,int branch) {
    if(!gi.Cvar_Get("ac_body_wounds","1",CVAR_ARCHIVE)->integer)return;
    ac_wound_t w={};w.version=2;w.event=event;
    w.seed=ACVisualOrientation(seed,branch,w.rotation,w.flipU,w.flipV);
    w.entity=target->edict->s.number;w.usage=target->edict->s.usageIndex;w.group=group;w.branch=branch;
    Q_strncpyz(w.model,gi.getConfigstring(CS_MODELS+target->edict->s.modelindex),sizeof(w.model));
    float radius=(branch || group>=3)?AC_LARGE_RADIUS:AC_SMALL_RADIUS;
    gi.AC_BuildPatch(target->edict->tiki,&pose,&point,radius,w.rotation,w.flipU,w.flipV,&w.patch);
    if(gi.Cvar_Get("ac_fx_debug","0",0)->integer)
        gi.Printf("AC_WOUND id=%u branch=%d entity=%d usage=%d group=%d radius=%.2f seed=%u rotation=%.6f flip=%d,%d triangles=%d\n",event,branch,w.entity,w.usage,group,radius,w.seed,w.rotation,w.flipU,w.flipV,w.patch.count);
    if(!w.patch.count)return;
    // Send a tiny ordered reference instead of fragmenting SP snapshots with
    // two full patches per MG hit. Geometry, precision and saves are unchanged.
    const auto local=gi.AC_StoreLocalWound(&w);
    if(local) {gi.SendServerCommand(-1,"ac_wound_local %llu",local);return;}
    const unsigned size=offsetof(ac_wound_t,patch)+offsetof(ac_patch_t,triangle)+w.patch.count*sizeof(ac_patch_triangle_t);
    const byte *bytes=(const byte*)&w;const char digits[]="0123456789abcdef";
    for(unsigned offset=0;offset<size;offset+=448) {
        char hex[897];unsigned count=size-offset;if(count>448)count=448;
        for(unsigned i=0;i<count;++i){hex[i*2]=digits[bytes[offset+i]>>4];hex[i*2+1]=digits[bytes[offset+i]&15];}hex[count*2]=0;
        gi.SendServerCommand(-1,"ac_wound %u %d %u %u %s",event,branch,offset,size,hex);
    }
}
