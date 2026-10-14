// Included once by tiki_surface.cpp. Server-time skinned triangles, not hitbox decals.
#include "../qcommon/ac_effects.h"
#include "../skeletor/skeletor.h"
#include <vector>
#include <algorithm>
#include <cmath>

namespace {
struct ACVertex { vec3_t p; };
bool ACBodySurface(const char *name) {
    char lower[MAX_QPATH]; Q_strncpyz(lower,name,sizeof(lower)); Q_strlwr(lower);
    const char *excluded[] = {"helmet","weapon","rifle","pistol","pack","gear","canteen","pouch","eye","teeth"};
    for (const char *word : excluded) if (strstr(lower,word)) return false;
    return true;
}
bool ACSkin(dtiki_t *tiki, const ac_pose_t *pose, skelHeaderGame_t *mesh,
    skelSurfaceGame_t *surface, int meshIndex, std::vector<ACVertex>& vertices) {
    auto *skel=(skeletor_c*)TIKI_GetSkeletor(tiki,pose->entityNumber);
    if (!skel || surface->numVerts<=0 || surface->numVerts>16384) return false;
    int morphWeights[12800]={}; skel->GetMorphWeightFrame(morphWeights, false);
    float axis[3][3]; AnglesToAxis(pose->angles,axis);
    vertices.resize(surface->numVerts);
    auto *vertex=surface->pVerts;
    for (int i=0;i<surface->numVerts;++i) {
        if (vertex->numWeights<=0 || vertex->numWeights>32 || vertex->numMorphs<0 || vertex->numMorphs>128) return false;
        const auto *morph=(const skeletorMorph_t*)(vertex+1);
        const auto *weights=(const skelWeight_t*)((const byte*)morph+sizeof(*morph)*vertex->numMorphs);
        vec3_t local={0,0,0},morphOffset={0,0,0};
        for(int m=0;m<vertex->numMorphs;++m) if(morph[m].morphIndex>=0 && morph[m].morphIndex<12800)
            VectorMA(morphOffset,(float)morphWeights[morph[m].morphIndex],morph[m].offset,morphOffset);
        for (int w=0;w<vertex->numWeights;++w) {
            if(weights[w].boneIndex<0 || weights[w].boneIndex>=mesh->numBones) return false;
            int bone=meshIndex ? tiki->m_boneList.GetLocalFromGlobal(mesh->pBones[weights[w].boneIndex].channel) : weights[w].boneIndex;
            if(bone<0 || bone>=tiki->m_boneList.NumChannels()) return false;
            const SkelMat4& transform=skel->GetBoneFrame(bone);
            vec3_t offset; VectorCopy(weights[w].offset,offset);
            if(w==0) VectorAdd(offset,morphOffset,offset);
            for(int k=0;k<3;++k) local[k]+=weights[w].boneWeight*(offset[0]*transform.val[0][k]+offset[1]*transform.val[1][k]+offset[2]*transform.val[2][k]+transform.val[3][k]);
        }
        VectorAdd(local,tiki->load_origin,local); VectorScale(local,tiki->load_scale*pose->scale,local);
        VectorCopy(pose->origin,vertices[i].p);
        for(int k=0;k<3;++k) VectorMA(vertices[i].p,local[k],axis[k],vertices[i].p);
        vertex=(skeletorVertex_t*)((byte*)weights+sizeof(*weights)*vertex->numWeights);
    }
    return true;
}
bool ACRayTriangle(const vec3_t start,const vec3_t dir,const vec3_t a,const vec3_t b,const vec3_t c,ac_surface_point_t& out) {
    vec3_t e1,e2,h,s,q; VectorSubtract(b,a,e1);VectorSubtract(c,a,e2);CrossProduct(dir,e2,h);
    float det=DotProduct(e1,h);if(fabsf(det)<0.000001f)return false;
    VectorSubtract(start,a,s);float u=DotProduct(s,h)/det;if(u<0 || u>1)return false;
    CrossProduct(s,e1,q);float v=DotProduct(dir,q)/det;if(v<0 || u+v>1)return false;
    float t=DotProduct(e2,q)/det;if(t<0 || t>256)return false;
    // SKD front faces use clockwise winding, matching the renderer.
    CrossProduct(e2,e1,out.normal);if(VectorNormalize(out.normal)<0.0001f)return false;
    out.distance=t;out.bary[0]=1-u-v;out.bary[1]=u;out.bary[2]=v;VectorMA(start,t,dir,out.position);return true;
}
}
void TIKI_ACSurfaceTrace(dtiki_t *tiki,const ac_pose_t *pose,const vec3_t start,const vec3_t direction,ac_surface_hit_t *hit) {
    memset(hit,0,sizeof(*hit));if(!tiki || !pose || !tiki->a->bIsCharacter)return;
    TIKI_SetPoseInternal(TIKI_GetSkeletor(tiki,pose->entityNumber),pose->frames,pose->boneTags,pose->boneQuats,pose->actionWeight);
    std::vector<ac_surface_point_t> contacts;std::vector<ACVertex> vertices;int globalSurface=0;
    for(int m=0;m<tiki->numMeshes;++m) {
        auto *mesh=TIKI_GetSkel(tiki->mesh[m]);if(!mesh)continue;auto *surface=mesh->pSurfaces;
        for(int s=0;s<mesh->numSurfaces && surface;++s,++globalSurface,surface=surface->pNext) {
            if(globalSurface>=tiki->num_surfaces || globalSurface>=32 || (pose->surfaces && (pose->surfaces[globalSurface]&MDL_SURFACE_NODRAW)) || !ACBodySurface(surface->name))continue;
            if(!ACSkin(tiki,pose,mesh,surface,m,vertices))continue;
            for(int t=0;t<surface->numTriangles;++t) {
                const auto *idx=surface->pTriangles+t*3;
                if(idx[0]<0 || idx[1]<0 || idx[2]<0 || idx[0]>=surface->numVerts || idx[1]>=surface->numVerts || idx[2]>=surface->numVerts)continue;
                ac_surface_point_t p={};p.mesh=m;p.surface=s;p.triangle=t;
                if(ACRayTriangle(start,direction,vertices[idx[0]].p,vertices[idx[1]].p,vertices[idx[2]].p,p))contacts.push_back(p);
            }
        }
    }
    std::sort(contacts.begin(),contacts.end(),[](const ac_surface_point_t&a,const ac_surface_point_t&b){return a.distance<b.distance;});
    if(Cvar_VariableIntegerValue("ac_fx_debug")) {
        Com_Printf("AC_SURFACE contacts=%d", (int)contacts.size());
        for(size_t i=0;i<contacts.size() && i<8;++i) Com_Printf(" %.2f:%.2f",contacts[i].distance,DotProduct(contacts[i].normal,direction));
        Com_Printf("\n");
    }
    for(const auto& point:contacts) {
        float facing=DotProduct(point.normal,direction);
        if(!hit->entryValid) {
            if(facing < -0.12f){hit->entry=point;hit->entryValid=1;}
        } else if(point.distance-hit->entry.distance>0.25f && point.distance-hit->entry.distance<80.f && facing>0.12f) {
            hit->exit=point;hit->exitValid=1;break;
        }
    }
}
