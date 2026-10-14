// Visual particles only. No server entity, damage callback or gameplay RNG.
#include <cmath>
namespace {
struct ACDrop {bool active;int born,last,target,usage;unsigned seed;vec3_t pos,velocity,barrier,normal;};
ACDrop acDrops[256]={};unsigned acCursor=0;unsigned acSeen[128]={};unsigned acSeenCursor=0;
struct ACRear {bool active;int target,usage;unsigned seed;vec3_t point,dir;};
ACRear acRear[128]={};unsigned acRearCursor=0;
struct ACEmission {bool active;int target,usage,born;unsigned seed;bool hasExit;ac_surface_point_t point[2];vec3_t dir;};
ACEmission acEmissions[128]={};unsigned acEmissionCursor=0;
unsigned ACRandom(unsigned& state){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
float ACUnit(unsigned& state){return (ACRandom(state)&0xffffff)/16777216.f;}
bool ACMarkable(const trace_t& tr) {
    return tr.fraction<1 && !tr.startsolid && !tr.allsolid && (tr.entityNum==ENTITYNUM_WORLD || (tr.entityNum>0 && tr.entityNum<ENTITYNUM_WORLD && cg_entities[tr.entityNum].currentValid && cg_entities[tr.entityNum].currentState.solid==SOLID_BMODEL))
        && !(tr.surfaceFlags&(SURF_SKY|SURF_PUDDLE))
        // Invisible collision proxies may carry NOMARKS/NODRAW. Filter the actual draw surface instead.
        && !(tr.contents&(CONTENTS_WATER|CONTENTS_SLIME|CONTENTS_LAVA));
}
void ACBloodMark(const trace_t& tr,float radius,unsigned& seed,const char *branch) {
    if(!ACMarkable(tr))return;
    CG_ACImpactMark(cgi.R_RegisterShader("ac/mp1_blood"),tr.endpos,tr.plane.normal,ACUnit(seed)*360,radius*1.5f,tr.entityNum);
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
    if(cgi.Argc()!=31)return;
    unsigned event=(unsigned)strtoul(cgi.Argv(1),NULL,10),seed=(unsigned)strtoul(cgi.Argv(2),NULL,10);
    for(unsigned seen:acSeen)if(seen==event)return;acSeen[acSeenCursor++%128]=event;
    int target=atoi(cgi.Argv(3)),group=atoi(cgi.Argv(4)),hasExit=atoi(cgi.Argv(5));
    if(target<0 || target>=MAX_GENTITIES || group<1 || group>4)return;
    vec3_t entry,normal,exit,dir;
    for(int i=0;i<3;++i){entry[i]=atof(cgi.Argv(6+i));normal[i]=atof(cgi.Argv(9+i));exit[i]=atof(cgi.Argv(12+i));dir[i]=atof(cgi.Argv(15+i));
        if(!std::isfinite(entry[i]) || !std::isfinite(normal[i]) || !std::isfinite(exit[i]) || !std::isfinite(dir[i]))return;}
    if(!cgi.Cvar_Get("ac_world_blood","1",CVAR_ARCHIVE)->integer)return;
    auto& emission=acEmissions[acEmissionCursor++%128];emission={};emission.target=target;emission.usage=atoi(cgi.Argv(18));
    emission.seed=seed;emission.born=cg.time;emission.hasExit=hasExit!=0;VectorCopy(dir,emission.dir);
    for(int branch=0;branch<(hasExit?2:1);++branch) {
        auto& p=emission.point[branch];int arg=19+branch*6;
        p.mesh=atoi(cgi.Argv(arg));p.surface=atoi(cgi.Argv(arg+1));p.triangle=atoi(cgi.Argv(arg+2));float sum=0;
        if(p.mesh<0 || p.mesh>=32 || p.surface<0 || p.surface>=32 || p.triangle<0 || p.triangle>65535)return;
        for(int i=0;i<3;++i){p.bary[i]=atof(cgi.Argv(arg+3+i));if(!std::isfinite(p.bary[i]) || p.bary[i]<-.001f || p.bary[i]>1.001f)return;sum+=p.bary[i];}
        if(fabsf(sum-1)>.002f)return;
    }
    emission.active=true;
}
extern "C" void CG_ACBloodBody(refEntity_t *model) {
    if(!model || !model->tiki || (model->renderfx&RF_INVISIBLE))return;
    bool needed=false;for(const auto& d:acDrops)if(d.active && d.target==model->entityNumber){needed=true;break;}
    if(!needed)for(const auto& r:acRear)if(r.active && r.target==model->entityNumber){needed=true;break;}
    if(!needed)for(const auto& e:acEmissions)if(e.active && e.target==model->entityNumber){needed=true;break;}
    if(!needed)return;
    ac_pose_t pose={};pose.entityNumber=model->entityNumber;pose.frames=model->frameInfo;pose.boneTags=model->bone_tag;pose.boneQuats=model->bone_quat;
    pose.actionWeight=model->actionWeight;pose.scale=model->scale;pose.surfaces=model->surfaces;VectorCopy(model->origin,pose.origin);MatrixToEulerAngles(model->axis,pose.angles);
    cgi.AC_CacheCollision(model->tiki,&pose,cg.clientFrame);
    // Resolve the confirmed barycentric hit in the same rendered pose used by
    // collision. A server-pose world position can start inside the pain animation.
    for(auto& e:acEmissions)if(e.active && e.target==model->entityNumber) {
        e.active=false;if(cg_entities[e.target].currentState.usageIndex!=e.usage || !cgi.Cvar_Get("ac_world_blood","1",CVAR_ARCHIVE)->integer)continue;
        for(int branch=0;branch<(e.hasExit?2:1);++branch) {
            const auto& p=e.point[branch];ac_patch_triangle_t tri={};tri.mesh=p.mesh;tri.surface=p.surface;tri.triangle=p.triangle;
            for(int i=0;i<3;++i)tri.vertex[i].bary[i]=1;
            vec3_t v[3]={},point={0,0,0},edge1,edge2,normal;
            cgi.AC_DeformPatch(model->tiki,&pose,&tri,1,v);
            if(VectorCompare(v[0],vec3_origin))continue;
            VectorSubtract(v[1],v[0],edge1);VectorSubtract(v[2],v[0],edge2);CrossProduct(edge2,edge1,normal);if(VectorNormalize(normal)<1e-6f)continue;
            for(int i=0;i<3;++i)VectorMA(point,p.bary[i],v[i],point);
            ACSpawnDrops(point,normal,e.target,e.seed^(branch?0xa511e9b3u:0),branch!=0,e.usage);
            if(branch && DotProduct(normal,e.dir)>.05f) {
                auto& rear=acRear[acRearCursor++%128];rear.active=true;rear.target=e.target;rear.usage=e.usage;rear.seed=e.seed;
                VectorCopy(point,rear.point);VectorCopy(e.dir,rear.dir);
            }
        }
    }
}
extern "C" void CG_ACBloodFrame(void) {
    bool enabled=cgi.Cvar_Get("ac_world_blood","1",CVAR_ARCHIVE)->integer!=0;
    for(auto& e:acEmissions)if(e.active && (!enabled || cg.time-e.born>250 || cg.time<e.born))e.active=false;
    for(auto& rear:acRear)if(rear.active) {
        rear.active=false;if(!enabled || !cg_entities[rear.target].currentValid || cg_entities[rear.target].currentState.usageIndex!=rear.usage)continue;
        vec3_t start,end;VectorMA(rear.point,.15f,rear.dir,start);VectorMA(rear.point,96,rear.dir,end);trace_t tr;
        CG_Trace(&tr,rear.point,vec3_origin,vec3_origin,end,rear.target,MASK_SHOT,qfalse,qtrue,"AC rear blood");
        float bodyFraction=1;int body=cgi.AC_CollideSegment(rear.target,cg.clientFrame,start,end,&bodyFraction);
        if(body<0 || (body && (.15f+bodyFraction*95.85f)<=tr.fraction*96)) {
            if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer>1)cgi.Printf("AC_REAR_BODY_BLOCK status=%d\n",body);
            continue;
        }
        ACBloodMark(tr,7.0f,rear.seed,"rear");
    }
    for(auto& d:acDrops) {
        if(!d.active)continue;
        if(cg_entities[d.target].currentValid && cg_entities[d.target].currentState.usageIndex!=d.usage){d.active=false;continue;}
        if(!enabled || cg.time<d.last || cg.time-d.born>2200){d.active=false;continue;}
        // Bounded 16 ms substeps and swept segments preserve first-surface collision.
        while(d.last<cg.time && d.active) {
            int ms=cg.time-d.last;if(ms>16)ms=16;float dt=ms*0.001f;vec3_t next;VectorMA(d.pos,dt,d.velocity,next);next[2]-=0.5f*320*dt*dt;
            trace_t tr;CG_Trace(&tr,d.pos,vec3_origin,vec3_origin,next,d.target,MASK_SHOT,qfalse,qtrue,"AC falling blood");
            float bodyFraction=1;int body=cgi.AC_CollideSegment(d.target,cg.clientFrame,d.pos,next,&bodyFraction);
            if(body<0 || (body && bodyFraction<=tr.fraction)){if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer>1)cgi.Printf("AC_DROP_BODY_BLOCK status=%d\n",body);d.active=false;break;}
            if(tr.fraction<1 || tr.startsolid){if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer>1)cgi.Printf("AC_DROP_HIT entity=%d solid=%d fraction=%f flags=%d\n",tr.entityNum,tr.startsolid,tr.fraction,tr.surfaceFlags);ACBloodMark(tr,3.0f+ACUnit(d.seed)*2.0f,d.seed,"drop");d.active=false;break;}
            VectorCopy(next,d.pos);d.velocity[2]-=320*dt;d.last+=ms;
        }
        if(d.active){refEntity_t sprite={};sprite.reType=RT_SPRITE;sprite.customShader=cgi.R_RegisterShader("ac/mp1_drop");
            VectorCopy(d.pos,sprite.origin);sprite.radius=2.7f;sprite.scale=1;sprite.shaderTime=d.born*.001f;for(int i=0;i<4;++i)sprite.shaderRGBA[i]=255;cgi.R_AddRefEntityToScene(&sprite,ENTITYNUM_NONE);}
    }
}
extern "C" void CG_ACBloodReset(void){memset(acDrops,0,sizeof(acDrops));memset(acRear,0,sizeof(acRear));memset(acEmissions,0,sizeof(acEmissions));memset(acSeen,0,sizeof(acSeen));acCursor=acSeenCursor=acRearCursor=acEmissionCursor=0;}
