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
#ifdef __cplusplus
extern "C" {
#endif
struct dtiki_s;
void TIKI_ACSurfaceTrace(struct dtiki_s *tiki, const ac_pose_t *pose, const vec3_t start,
    const vec3_t direction, ac_surface_hit_t *hit);
#ifdef __cplusplus
}
#endif
