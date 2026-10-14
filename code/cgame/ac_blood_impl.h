// Visual particles only. No server entity, damage callback or gameplay RNG.
#include <cmath>
namespace {
struct ACDrop {bool active;int born,last,target,usage;unsigned seed;vec3_t pos,velocity,barrier,normal;};
ACDrop acDrops[256]={};unsigned acCursor=0;unsigned acSeen[128]={};unsigned acSeenCursor=0;
unsigned ACRandom(unsigned& state){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
float ACUnit(unsigned& state){return (ACRandom(state)&0xffffff)/16777216.f;}
bool ACMarkable(const trace_t& tr) {
    return tr.fraction<1 && !tr.startsolid && !tr.allsolid && tr.entityNum==ENTITYNUM_WORLD
        && !(tr.surfaceFlags&(SURF_SKY|SURF_PUDDLE))
        // Terrain collision proxies carry NOMARKS/NODRAW; actual draw surfaces are filtered by the renderer.
        && (!(tr.surfaceFlags&(SURF_NOMARKS|SURF_NODRAW)) || (tr.surfaceFlags&(SURF_SNOW|SURF_DIRT|SURF_GRASS|SURF_SAND|SURF_MUD|SURF_GRAVEL)))
        && !(tr.contents&(CONTENTS_WATER|CONTENTS_SLIME|CONTENTS_LAVA));
}
void ACBloodMark(const trace_t& tr,float radius,unsigned& seed,const char *branch) {
    if(!ACMarkable(tr))return;
    CG_ACImpactMark(cgi.R_RegisterShader("ac/mp1_blood"),tr.endpos,tr.plane.normal,ACUnit(seed)*360,radius);
    if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer)cgi.Printf("AC_MARK %s %.3f %.3f %.3f\n",branch,tr.endpos[0],tr.endpos[1],tr.endpos[2]);
}
void ACSpawnDrops(const vec3_t point,const vec3_t normal,int target,unsigned seed,bool exit,int usage) {
    for(int i=0;i<6;++i) {
        ACDrop& d=acDrops[acCursor++%256];d={};d.active=true;d.born=d.last=cg.time;d.target=target;d.usage=usage;d.seed=seed+i+1;
        // Test the tiny start offset too; never step across a close floor or wall.
        vec3_t goal;VectorMA(point,0.15f,normal,goal);trace_t tr;
        CG_Trace(&tr,point,vec3_origin,vec3_origin,goal,target,MASK_SHOT,qfalse,qtrue,"AC blood start");
        if(tr.startsolid || tr.fraction<1){if(i==0 && cgi.Cvar_Get("ac_fx_debug","0",0)->integer>1)cgi.Printf("AC_DROP_START rejected entity=%d solid=%d fraction=%f\n",tr.entityNum,tr.startsolid,tr.fraction);d.active=false;continue;}
        VectorCopy(goal,d.pos);VectorCopy(point,d.barrier);VectorCopy(normal,d.normal);vec3_t tangent;PerpendicularVector(tangent,normal);vec3_t other;CrossProduct(normal,tangent,other);
        VectorScale(normal,25+ACUnit(d.seed)*45,d.velocity);
        VectorMA(d.velocity,(ACUnit(d.seed)-0.5f)*30,tangent,d.velocity);
        VectorMA(d.velocity,(ACUnit(d.seed)-0.5f)*30,other,d.velocity);
        d.velocity[2]+=10;
    }
}
}
extern "C" void CG_ACBloodEvent(void) {
    if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer>1)cgi.Printf("AC_RECEIVE argc=%d\n",cgi.Argc());
    if(cgi.Argc()!=19)return;
    unsigned event=(unsigned)strtoul(cgi.Argv(1),NULL,10),seed=(unsigned)strtoul(cgi.Argv(2),NULL,10);
    for(unsigned seen:acSeen)if(seen==event)return;acSeen[acSeenCursor++%128]=event;
    int target=atoi(cgi.Argv(3)),group=atoi(cgi.Argv(4)),hasExit=atoi(cgi.Argv(5));
    if(target<0 || target>=MAX_GENTITIES || group<1 || group>4)return;
    vec3_t entry,normal,exit,dir;
    for(int i=0;i<3;++i){entry[i]=atof(cgi.Argv(6+i));normal[i]=atof(cgi.Argv(9+i));exit[i]=atof(cgi.Argv(12+i));dir[i]=atof(cgi.Argv(15+i));
        if(!std::isfinite(entry[i]) || !std::isfinite(normal[i]) || !std::isfinite(exit[i]) || !std::isfinite(dir[i]))return;}
    if(!cgi.Cvar_Get("ac_world_blood","1",CVAR_ARCHIVE)->integer)return;
    ACSpawnDrops(entry,normal,target,seed,false,atoi(cgi.Argv(18)));
    if(hasExit) {
        ACSpawnDrops(exit,dir,target,seed^0xa511e9b3u,true,atoi(cgi.Argv(18)));
        vec3_t end;VectorMA(exit,96,dir,end);trace_t tr;
        CG_Trace(&tr,exit,vec3_origin,vec3_origin,end,target,MASK_SHOT,qfalse,qtrue,"AC rear blood");
        ACBloodMark(tr,3.5f,seed,"rear");
    }
}
extern "C" void CG_ACBloodFrame(void) {
    bool enabled=cgi.Cvar_Get("ac_world_blood","1",CVAR_ARCHIVE)->integer!=0;
    for(auto& d:acDrops) {
        if(!d.active)continue;
        if(cg_entities[d.target].currentValid && cg_entities[d.target].currentState.usageIndex!=d.usage){d.active=false;continue;}
        if(!enabled || cg.time<d.last || cg.time-d.born>2200){d.active=false;continue;}
        // Bounded 16 ms substeps and swept segments preserve first-surface collision.
        while(d.last<cg.time && d.active) {
            int ms=cg.time-d.last;if(ms>16)ms=16;float dt=ms*0.001f;vec3_t next;VectorMA(d.pos,dt,d.velocity,next);next[2]-=0.5f*320*dt*dt;
            vec3_t delta;VectorSubtract(next,d.barrier,delta);if(DotProduct(delta,d.normal)<0){d.active=false;break;}
            trace_t tr;CG_Trace(&tr,d.pos,vec3_origin,vec3_origin,next,d.target,MASK_SHOT,qfalse,qtrue,"AC falling blood");
            if(tr.fraction<1 || tr.startsolid){if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer>1)cgi.Printf("AC_DROP_HIT entity=%d solid=%d fraction=%f flags=%d\n",tr.entityNum,tr.startsolid,tr.fraction,tr.surfaceFlags);ACBloodMark(tr,0.9f+ACUnit(d.seed)*0.8f,d.seed,"drop");d.active=false;break;}
            VectorCopy(next,d.pos);d.velocity[2]-=320*dt;d.last+=ms;
        }
        if(d.active){refEntity_t sprite={};sprite.reType=RT_SPRITE;sprite.customShader=cgi.R_RegisterShader("ac/mp1_drop");
            VectorCopy(d.pos,sprite.origin);sprite.radius=0.7f;sprite.scale=1;for(int i=0;i<4;++i)sprite.shaderRGBA[i]=255;cgi.R_AddRefEntityToScene(&sprite,ENTITYNUM_NONE);}
    }
}
extern "C" void CG_ACBloodReset(void){memset(acDrops,0,sizeof(acDrops));memset(acSeen,0,sizeof(acSeen));acCursor=acSeenCursor=0;}
