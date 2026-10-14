#include "../qcommon/ac_visual_random.h"
// Connected, clipped mesh triangles. Barycentric anchors survive skeletal motion.
namespace {
struct ACClipVertex { float b[3], x, y, z; };
std::vector<ACClipVertex> ACClip(const std::vector<ACClipVertex>& in,int axis,float sign,float limit) {
    std::vector<ACClipVertex> out;if(in.empty())return out;
    auto distance=[&](const ACClipVertex& p){return limit-sign*(&p.x)[axis];};
    ACClipVertex prev=in.back();float pd=distance(prev);
    for(const auto& curr:in) {
        float cd=distance(curr);
        if((pd>=0)!=(cd>=0)) {
            float t=pd/(pd-cd);ACClipVertex q={};
            for(int k=0;k<3;++k){q.b[k]=prev.b[k]+t*(curr.b[k]-prev.b[k]);(&q.x)[k]=(&prev.x)[k]+t*((&curr.x)[k]-(&prev.x)[k]);}
            out.push_back(q);
        }
        if(cd>=0)out.push_back(curr);prev=curr;pd=cd;
    }
    return out;
}
skelSurfaceGame_t *ACGetSurface(dtiki_t *tiki,int meshIndex,int surfaceIndex,skelHeaderGame_t **meshOut) {
    if(meshIndex<0 || meshIndex>=tiki->numMeshes)return nullptr;
    auto *mesh=TIKI_GetSkel(tiki->mesh[meshIndex]);if(!mesh || surfaceIndex<0 || surfaceIndex>=mesh->numSurfaces)return nullptr;
    auto *s=mesh->pSurfaces;for(int i=0;i<surfaceIndex && s;++i)s=s->pNext;
    *meshOut=mesh;return s;
}
}
void TIKI_ACBuildPatch(dtiki_t *tiki,const ac_pose_t *pose,const ac_surface_point_t *point,
    float radius,float rotation,int flipU,int flipV,ac_patch_t *patch) {
    memset(patch,0,sizeof(*patch));if(!tiki || !pose || !point || radius<=0 || radius>8)return;
    skelHeaderGame_t *mesh;auto *surf=ACGetSurface(tiki,point->mesh,point->surface,&mesh);
    if(!surf || point->triangle<0 || point->triangle>=surf->numTriangles)return;
    TIKI_SetPoseInternal(TIKI_GetSkeletor(tiki,pose->entityNumber),pose->frames,pose->boneTags,pose->boneQuats,pose->actionWeight);
    std::vector<ACVertex> vertices;if(!ACSkin(tiki,pose,mesh,surf,point->mesh,vertices))return;
    vec3_t u,v,base;PerpendicularVector(u,point->normal);CrossProduct(point->normal,u,v);
    std::vector<std::vector<ACClipVertex>> clipped(surf->numTriangles);
    for(int t=0;t<surf->numTriangles;++t) {
        auto *ix=surf->pTriangles+t*3;
        if(ix[0]<0 || ix[1]<0 || ix[2]<0 || ix[0]>=surf->numVerts || ix[1]>=surf->numVerts || ix[2]>=surf->numVerts)continue;
        vec3_t e1,e2,n;VectorSubtract(vertices[ix[1]].p,vertices[ix[0]].p,e1);VectorSubtract(vertices[ix[2]].p,vertices[ix[0]].p,e2);CrossProduct(e2,e1,n);VectorNormalize(n);
        if(DotProduct(n,point->normal)<0.45f)continue;
        std::vector<ACClipVertex> poly(3);
        for(int j=0;j<3;++j){vec3_t d;VectorSubtract(vertices[ix[j]].p,point->position,d);poly[j]={};poly[j].b[j]=1;ACVisualRotate(DotProduct(d,u),DotProduct(d,v),rotation,poly[j].x,poly[j].y);poly[j].z=DotProduct(d,point->normal);}
        for(int axis=0;axis<3;++axis)for(float sign:{-1.f,1.f})poly=ACClip(poly,axis,sign,axis==2?1.5f:radius);
        clipped[t]=std::move(poly);
    }
    // Flood only the connected impact component, excluding overlapping clothing shells.
    if(clipped[point->triangle].size()<3)return;
    std::vector<int> queue={point->triangle};std::vector<bool> seen(surf->numTriangles,false);seen[point->triangle]=true;
    for(size_t q=0;q<queue.size();++q) {
        int t=queue[q];const auto& poly=clipped[t];
        for(size_t j=1;j+1<poly.size();++j) {
            if(patch->count==AC_PATCH_MAX){if(Cvar_VariableIntegerValue("ac_fx_debug"))Com_Printf("AC_PATCH_BUDGET exceeded=%d\n",AC_PATCH_MAX);patch->count=0;return;}
            auto& tri=patch->triangle[patch->count++];tri.mesh=point->mesh;tri.surface=point->surface;tri.triangle=t;
            const ACClipVertex *p[3]={&poly[0],&poly[j],&poly[j+1]};
            for(int k=0;k<3;++k){for(int b=0;b<3;++b)tri.vertex[k].bary[b]=p[k]->b[b];ACVisualUV(p[k]->x,p[k]->y,radius,flipU,flipV,tri.vertex[k].uv);}
        }
        auto *a=surf->pTriangles+t*3;
        for(int n=0;n<surf->numTriangles;++n)if(!seen[n] && clipped[n].size()>=3) {
            auto *b=surf->pTriangles+n*3;int shared=0;
            for(int i=0;i<3;++i)for(int j=0;j<3;++j)if(a[i]==b[j])++shared;
            if(shared>=2){seen[n]=true;queue.push_back(n);}
        }
    }
}
void TIKI_ACDeformPatch(dtiki_t *tiki,const ac_pose_t *pose,const ac_patch_triangle_t *triangles,int count,vec3_t *out) {
    if(!tiki || !pose || count<0 || count>512)return;
    TIKI_SetPoseInternal(TIKI_GetSkeletor(tiki,pose->entityNumber),pose->frames,pose->boneTags,pose->boneQuats,pose->actionWeight);
    int lastMesh=-1,lastSurf=-1;skelHeaderGame_t *mesh=nullptr;skelSurfaceGame_t *surf=nullptr;std::vector<ACVertex> vertices;
    for(int i=0;i<count;++i) {
        const auto& tri=triangles[i];for(int j=0;j<3;++j)VectorClear(out[i*3+j]);
        if(lastMesh!=tri.mesh || lastSurf!=tri.surface) {
            lastMesh=tri.mesh;lastSurf=tri.surface;surf=ACGetSurface(tiki,tri.mesh,tri.surface,&mesh);
            int globalSurface=tri.surface;for(int m=0;m<tri.mesh;++m){auto *prior=TIKI_GetSkel(tiki->mesh[m]);if(prior)globalSurface+=prior->numSurfaces;}
            if(globalSurface>=32 || (pose->surfaces && (pose->surfaces[globalSurface]&MDL_SURFACE_NODRAW)))surf=nullptr;
            if(surf && !ACSkin(tiki,pose,mesh,surf,tri.mesh,vertices))surf=nullptr;
        }
        if(!surf || tri.triangle<0 || tri.triangle>=surf->numTriangles)continue;
        auto *ix=surf->pTriangles+tri.triangle*3;
        if(ix[0]<0 || ix[1]<0 || ix[2]<0 || ix[0]>=surf->numVerts || ix[1]>=surf->numVerts || ix[2]>=surf->numVerts)continue;
        vec3_t e1,e2,n;VectorSubtract(vertices[ix[1]].p,vertices[ix[0]].p,e1);VectorSubtract(vertices[ix[2]].p,vertices[ix[0]].p,e2);CrossProduct(e2,e1,n);if(VectorNormalize(n)<1e-6f)continue;
        for(int j=0;j<3;++j){VectorScale(n,0.06f,out[i*3+j]);for(int k=0;k<3;++k)VectorMA(out[i*3+j],tri.vertex[j].bary[k],vertices[ix[k]].p,out[i*3+j]);}
    }
}
