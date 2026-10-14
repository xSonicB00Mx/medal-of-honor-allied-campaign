// Allied Campaign visual-only surface contract. No damage or random calls.
#pragma once
typedef struct {
    int mesh, surface, triangle;
    float bary[3];
    vec3_t position, normal;
    float distance;
} ac_surface_point_t;
typedef struct {
    int entryValid, exitValid;
    ac_surface_point_t entry, exit;
} ac_surface_hit_t;
typedef struct {
    int entityNumber;
    const frameInfo_t *frames;
    const int *boneTags;
    const vec4_t *boneQuats;
    float actionWeight, scale;
    vec3_t origin, angles;
    const byte *surfaces;
} ac_pose_t;
#define AC_PATCH_MAX 32
typedef struct { float bary[3], uv[2]; } ac_patch_vertex_t;
typedef struct {
    int mesh, surface, triangle;
    ac_patch_vertex_t vertex[3];
} ac_patch_triangle_t;
typedef struct { int count; ac_patch_triangle_t triangle[AC_PATCH_MAX]; } ac_patch_t;
// Versioned local SP wire/save record. No pointers, handles or shared texture state.
typedef struct {
    unsigned version, event, seed;
    int entity, usage, group, branch, flipU, flipV;
    float rotation;
    char model[MAX_QPATH];
    ac_patch_t patch;
} ac_wound_t;
#ifdef __cplusplus
extern "C" {
#endif
struct dtiki_s;
void TIKI_ACSurfaceTrace(struct dtiki_s *tiki, const ac_pose_t *pose, const vec3_t start,
    const vec3_t direction, ac_surface_hit_t *hit);
void TIKI_ACBuildPatch(struct dtiki_s *tiki,const ac_pose_t *pose,const ac_surface_point_t *point,
    float radius,float rotation,int flipU,int flipV,ac_patch_t *patch);
void TIKI_ACDeformPatch(struct dtiki_s *tiki,const ac_pose_t *pose,const ac_patch_triangle_t *triangles,
    int count,vec3_t *vertices);
#ifdef __cplusplus
}
#endif
