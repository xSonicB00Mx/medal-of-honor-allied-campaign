// Included once in cg_archive.cpp so the same validated record is drawn and saved.
#include <cmath>
#include <cstddef>
namespace {
struct ACStoredWound {ac_wound_t data;bool active,rebind;};
ACStoredWound acWounds[64]={};unsigned acWoundCursor=0;
byte acPacket[sizeof(ac_wound_t)]={};unsigned acPacketId=0,acPacketOffset=0,acPacketSize=0;int acPacketBranch=0;
bool ACValidWound(const ac_wound_t& w) {
    if(w.version!=1 || w.entity<0 || w.entity>=MAX_GENTITIES || w.usage<=0 || w.group<1 || w.group>4 || w.branch<0 || w.branch>1
        || w.flipU<0 || w.flipU>1 || w.flipV<0 || w.flipV>1 || !std::isfinite(w.rotation) || w.rotation<0 || w.rotation>=360
        || !memchr(w.model,0,sizeof(w.model)) || !w.model[0] || w.patch.count<1 || w.patch.count>AC_PATCH_MAX)return false;
    for(int i=0;i<w.patch.count;++i) {
        const auto& tri=w.patch.triangle[i];if(tri.mesh<0 || tri.mesh>=32 || tri.surface<0 || tri.surface>=32 || tri.triangle<0 || tri.triangle>65535)return false;
        for(const auto& v:tri.vertex) {
            float sum=0;for(float b:v.bary){if(!std::isfinite(b) || b<-.001f || b>1.001f)return false;sum+=b;}
            if(fabsf(sum-1)>0.002f)return false;
            for(float uv:v.uv)if(!std::isfinite(uv) || uv<-.001f || uv>1.001f)return false;
        }
    }
    return true;
}
int ACHex(char c){if(c>='0' && c<='9')return c-'0';if(c>='a' && c<='f')return c-'a'+10;return -1;}
}
extern "C" void CG_ACWoundsReset(void) {memset(acWounds,0,sizeof(acWounds));acWoundCursor=0;acPacketOffset=acPacketSize=0;}
extern "C" void CG_ACWoundsEvent(void) {
    if(cgi.Argc()!=6)return;
    unsigned id=strtoul(cgi.Argv(1),nullptr,10);int branch=atoi(cgi.Argv(2));unsigned offset=strtoul(cgi.Argv(3),nullptr,10),size=strtoul(cgi.Argv(4),nullptr,10);
    const char *hex=cgi.Argv(5);size_t length=strlen(hex);
    if(size>sizeof(ac_wound_t) || size<offsetof(ac_wound_t,patch)+sizeof(int) || length>640 || length%2 || offset>size || length/2>size-offset)return;
    if(offset==0){memset(acPacket,0,sizeof(acPacket));acPacketOffset=0;acPacketId=id;acPacketBranch=branch;acPacketSize=size;}
    if(id!=acPacketId || branch!=acPacketBranch || offset!=acPacketOffset || size!=acPacketSize)return;
    for(size_t i=0;i<length;i+=2){int a=ACHex(hex[i]),b=ACHex(hex[i+1]);if(a<0 || b<0){acPacketSize=0;return;}acPacket[offset+i/2]=(a<<4)|b;}
    acPacketOffset+=length/2;if(acPacketOffset!=size)return;
    ac_wound_t w={};memcpy(&w,acPacket,size);acPacketSize=0;
    if(!ACValidWound(w) || w.event!=id || w.branch!=branch || size!=offsetof(ac_wound_t,patch)+offsetof(ac_patch_t,triangle)+w.patch.count*sizeof(ac_patch_triangle_t))return;
    int same=0;for(auto& old:acWounds)if(old.active && old.data.entity==w.entity && old.data.usage==w.usage){if(old.data.event==w.event && old.data.branch==w.branch)return;++same;}
    // Max 16 wounds per actor; FIFO ring gives a hard 64-wound scene budget.
    if(same>=16)for(unsigned i=0;i<64;++i){auto& old=acWounds[(acWoundCursor+i)%64];if(old.active && old.data.entity==w.entity){old.active=false;break;}}
    auto& slot=acWounds[acWoundCursor++%64];slot.data=w;slot.active=true;slot.rebind=false;
    if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer)cgi.Printf("AC_WOUND_RECEIVED id=%u branch=%d triangles=%d rotation=%.6f flip=%d,%d\n",w.event,w.branch,w.patch.count,w.rotation,w.flipU,w.flipV);
}
extern "C" void CG_ACWoundsDraw(refEntity_t *model,int usage) {
    if(!model || !model->tiki || model->entityNumber<0 || model->entityNumber>=MAX_GENTITIES)return;
    const char *name=cgi.R_GetModelName(model->hModel);
    if(model->renderfx & RF_INVISIBLE)return;
    for(auto& w:acWounds)if(w.active && w.data.entity==model->entityNumber) {
        if(Q_stricmp(w.data.model,name)){if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer)cgi.Printf("AC_WOUND_REMOVED model=%s expected=%s\n",name,w.data.model);w.active=false;continue;}
        if(w.rebind){w.data.usage=usage;w.rebind=false;}
        if(w.data.usage!=usage)w.active=false;
    }
    if(!cgi.Cvar_Get("ac_body_wounds","1",CVAR_ARCHIVE)->integer)return;
    vec3_t distance;VectorSubtract(model->origin,cg.refdef.vieworg,distance);float range=VectorLength(distance);
    if(range>=512 || CG_FrustumCullSphere(model->origin,128))return;
    static int frame=-1,actors=0,lastDump=-1000;static bool dump=false;if(frame!=cg.time){frame=cg.time;actors=0;dump=(cg.time-lastDump>=1000 || cg.time<lastDump);if(dump)lastDump=cg.time;}if(actors>=8)return;
    ac_patch_triangle_t triangles[512];int materials[512],count=0;
    for(const auto& w:acWounds)if(w.active && w.data.entity==model->entityNumber) {
        for(int i=0;i<w.data.patch.count && count<512;++i){triangles[count]=w.data.patch.triangle[i];materials[count++]=(w.data.branch || w.data.group>=3)?1:0;}
    }
    if(!count)return;
    if(dump && cgi.Cvar_Get("ac_fx_debug","0",0)->integer>1)for(const auto& w:acWounds)if(w.active && w.data.entity==model->entityNumber)cgi.Printf("AC_WOUND_DRAW time=%d id=%u branch=%d seed=%u rotation=%.6f flip=%d,%d triangles=%d range=%.1f\n",cg.time,w.data.event,w.data.branch,w.data.seed,w.data.rotation,w.data.flipU,w.data.flipV,w.data.patch.count,range);
    ++actors;model->acFullDetail=qtrue;
    ac_pose_t pose={};pose.entityNumber=model->entityNumber;pose.frames=model->frameInfo;pose.boneTags=model->bone_tag;pose.boneQuats=model->bone_quat;
    pose.actionWeight=model->actionWeight;pose.scale=model->scale;pose.surfaces=model->surfaces;VectorCopy(model->origin,pose.origin);MatrixToEulerAngles(model->axis,pose.angles);
    vec3_t positions[1536];cgi.AC_DeformPatch(model->tiki,&pose,triangles,count,positions);
    qhandle_t shader[2]={cgi.R_RegisterShader("ac/wound_small"),cgi.R_RegisterShader("ac/wound_large")};
    float alpha=range<=384?1:(512-range)/128;
    for(int i=0;i<count;++i) {
        if(VectorCompare(positions[i*3],vec3_origin))continue;
        vec3_t e1,e2,normal,light;VectorSubtract(positions[i*3+1],positions[i*3],e1);VectorSubtract(positions[i*3+2],positions[i*3],e2);CrossProduct(e2,e1,normal);VectorNormalize(normal);
        cgi.R_GetLightingForDecal(light,normal,positions[i*3]);polyVert_t verts[3]={};
        for(int j=0;j<3;++j){VectorCopy(positions[i*3+j],verts[j].xyz);for(int k=0;k<2;++k)verts[j].st[k]=triangles[i].vertex[j].uv[k];for(int k=0;k<3;++k)verts[j].modulate[k]=(byte)Q_clamp_int((int)light[k],0,255);verts[j].modulate[3]=(byte)(255*alpha);}
        cgi.R_AddPolyToScene(shader[materials[i]],3,verts,0);
    }
}
void CG_ACWoundsArchive(MemArchiver& archive) {
    if(archive.IsReading()){CG_ACWoundsReset();if(archive.FinishedReading())return;}
    int magic=0x41435731,count=0;archive.ArchiveInteger(&magic);if(magic!=0x41435731)cgi.Error(ERR_DROP,"Unsupported AC wound save schema");
    if(archive.IsWriting())for(const auto& w:acWounds)if(w.active)++count;
    archive.ArchiveInteger(&count);if(count<0 || count>64)cgi.Error(ERR_DROP,"Invalid AC wound save count");
    if(archive.IsWriting()){for(auto& w:acWounds)if(w.active)archive.ArchiveRaw(&w.data,sizeof(w.data));}
    else for(int i=0;i<count;++i){auto& w=acWounds[i];archive.ArchiveRaw(&w.data,sizeof(w.data));if(!ACValidWound(w.data))cgi.Error(ERR_DROP,"Invalid AC wound save geometry");w.active=true;w.rebind=true;acWoundCursor=i+1;}
    if(cgi.Cvar_Get("ac_fx_debug","0",0)->integer)cgi.Printf("AC_WOUND_ARCHIVE %s count=%d\n",archive.IsWriting()?"save":"load",count);
}
