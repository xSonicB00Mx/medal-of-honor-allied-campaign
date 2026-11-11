# Curvature-aware head wound projection

The head path now uses a wider projection volume and accepts steep forward-facing facets instead of applying the body's 0.45 normal cutoff and 1.5-unit slab. Coincident head edges are welded across duplicate UV seam vertices (0.01 world-unit tolerance); body clothing retains strict index connectivity. The wound remains barycentrically attached to the animated skin, uses the same lit alpha material and keeps the original orientation and hit center.

Head patches have a bounded 256-triangle allowance, while body patches retain 64. Dense facial hits no longer need aggressive radius reduction in the checked cases. Existing per-actor and scene draw limits remain 512 triangles and eight wounded actors; storage remains 64 wounds / 16 per actor. Overflow still produces a complete smaller patch, never a partial triangle list. This is a conforming surface projection, not a camera-facing sprite.

The first native closeup exposed another source of cracks: offsetting each triangle by its separate facet normal opens gaps along curved faces. Head vertices now stay on the exact skin surface and use the already-existing polygonOffset material for depth separation. Body offsets remain unchanged. Full-detail skeletal rendering from the previous fix remains active for drawn wounds.

The wound archive writes schema ACW3 and reads previous ACW1 (32 triangles) and ACW2 (64 triangles) records at their original sizes. Old wounds keep their saved geometry; newly created head wounds use the new projection. New saves require this or a later compatible build. All runtime modules are built and installed together; no original meshes, textures or personal saves are edited.

Validation results and deployment follow below. No exhaustive coverage of every head/animation/weapon combination or personal acceptance is claimed.

Final native AA/BT tests passed with 135/89 and 186/50 entry/exit triangles respectively, preserving the full 1.8/3.5 radii without shrinking. Both survive two quicksaves, quickload and actor rotations. The earlier SH mouth test passed before the final removal of facet-normal offsets. Final archive tests load ACW2 (eight wounds) and ACW3 (two wounds), resave and reload with identical counts. Missing fixture scripts in the first compatibility attempt were copied alongside the isolated save before retrying. The exact earlier nose wound was visually checked again on the final engine: the thin bright facet cracks are removed. Evidence: head-wound-projection-tests.json.

Installed head-wound-projection-r1 from 023b0e24; all 62 runtime hashes and final tested binaries match. All 111 personal-profile files, 9072 original files, 9000 runtime-base files and eight MP1 inputs preserved. Screenshot bundle: artifacts-local/CP08-Head-Wounds-Screenshots.zip.
