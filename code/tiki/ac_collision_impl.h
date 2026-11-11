// Only targets with active visual drops are skinned, once per rendered frame.
namespace {
struct ACCollisionTriangle {vec3_t v[3],mins,maxs;};
struct ACCollisionBody {int frame=-1,entity=-1;std::vector<ACCollisionTriangle> triangles;};
ACCollisionBody acCollision[8];int acCollisionFrame=-1,acCollisionCount=0;
}
void TIKI_ACCacheCollision(dtiki_t *tiki,const ac_pose_t *pose,int frame) {
    if(!ACSupportedBody(tiki) || !pose)return;
    if(acCollisionFrame!=frame){acCollisionFrame=frame;acCollisionCount=0;}
    if(acCollisionCount==8)return;
    auto& body=acCollision[acCollisionCount++];body.frame=frame;body.entity=pose->entityNumber;body.triangles.clear();
    TIKI_SetPoseInternal(TIKI_GetSkeletor(tiki,pose->entityNumber),pose->frames,pose->boneTags,pose->boneQuats,pose->actionWeight);
    std::vector<ACVertex> vertices;int globalSurface=0;
    for(int m=0;m<tiki->numMeshes;++m) {
        auto *mesh=TIKI_GetSkel(tiki->mesh[m]);if(!mesh)continue;auto *surface=mesh->pSurfaces;
        for(int s=0;s<mesh->numSurfaces && surface;++s,++globalSurface,surface=surface->pNext) {
            if(globalSurface>=tiki->num_surfaces || globalSurface>=32 || (pose->surfaces && (pose->surfaces[globalSurface]&MDL_SURFACE_NODRAW)))continue;
            if(!ACSkin(tiki,pose,mesh,surface,m,vertices))continue;
            for(int t=0;t<surface->numTriangles;++t) {
                auto *ix=surface->pTriangles+t*3;
                if(ix[0]<0 || ix[1]<0 || ix[2]<0 || ix[0]>=surface->numVerts || ix[1]>=surface->numVerts || ix[2]>=surface->numVerts)continue;
                if(body.triangles.size()==8192){body.frame=-1;body.triangles.clear();return;}
                ACCollisionTriangle tri={};for(int j=0;j<3;++j)VectorCopy(vertices[ix[j]].p,tri.v[j]);
                for(int k=0;k<3;++k){tri.mins[k]=std::min(tri.v[0][k],std::min(tri.v[1][k],tri.v[2][k]));tri.maxs[k]=std::max(tri.v[0][k],std::max(tri.v[1][k],tri.v[2][k]));}
                body.triangles.push_back(tri);
            }
        }
    }
}
int TIKI_ACCollideSegment(int entity,int frame,const vec3_t start,const vec3_t end,float *fraction) {
    *fraction=1;const ACCollisionBody *body=nullptr;
    for(int i=0;i<acCollisionCount;++i)if(acCollision[i].frame==frame && acCollision[i].entity==entity){body=&acCollision[i];break;}
    if(!body)return -1;
    vec3_t dir,mins,maxs;VectorSubtract(end,start,dir);float distance=VectorNormalize(dir);if(distance<1e-6f)return 0;
    for(int k=0;k<3;++k){mins[k]=std::min(start[k],end[k]);maxs[k]=std::max(start[k],end[k]);}
    bool hit=false;
    for(const auto& tri:body->triangles) {
        bool overlap=true;for(int k=0;k<3;++k)if(maxs[k]<tri.mins[k] || mins[k]>tri.maxs[k])overlap=false;
        if(!overlap)continue;ac_surface_point_t point={};
        if(ACRayTriangle(start,dir,tri.v[0],tri.v[1],tri.v[2],point) && point.distance<=distance){*fraction=std::min(*fraction,point.distance/distance);hit=true;}
    }
    return hit?1:0;
}
