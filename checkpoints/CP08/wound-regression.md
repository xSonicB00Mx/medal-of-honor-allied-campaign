# Head wounds and quicksave persistence

## Reproduced causes

The installed baseline produced valid skinned head intersections at test heights 65 and 70, but discarded the complete entry patches when clipping exceeded AC_PATCH_MAX (64 triangles). The torso patch remained visible until savegame quick. Actor::Archive called setModel on both save and load; PF_setmodel assigns a fresh usageIndex on every call. The client correctly retired wounds belonging to that previous model instance. The records were serialized before the invalidation and reappeared on load; the failure occurred immediately after saving.

## Corrections

Actor model reconstruction now runs only when loading, preserving live instance identity during all save types. Save layout and compatibility are unchanged. Patch construction retries a budget-overflowing patch at 75% of its previous radius, centered on the original barycentric hit. At most nine attempts; no increase to packet/save or scene budgets and no arbitrary trimming of the final connected patch. The same seed, rotation, mirror and material are retained. Detailed faces can receive a smaller complete wound instead of no wound.

The full-detail flag was accidentally checked only in the LOD authoring-tool branch. It now controls the actual skeletal backend LOD collapse, so wound anchors and the rendered surface share the same triangles. Unwounded and distant actors retain normal LOD.

No new lifetime timer is necessary: fixed storage remains 64 wounds total, 16 per actor, 64 triangles per wound, 512 drawn triangles per actor and eight wounded actors per frame. Neither unbounded allocations nor expanding save records are introduced. Gameplay hit detection, damage and weapon spread are unchanged.

## Validation

Native isolated-profile regression fires real pistol shots at torso and several head heights, inspects the wounds, quicksaves twice, then quickloads. The test compares exact event/branch/seed sets drawn before save, after save and after load, validates complete patches within the hard budget and checks script errors. Heights above the visible head may legitimately miss the mesh and are not forced to create wounds. Screenshots are retained locally for visual checking. Old add-on reference saves exercise backwards compatibility.

Personal acceptance and merge are not claimed. No exhaustive test of every head variant, animation or view distance is claimed.

AA and SH retained all eight wounds across both quicksaves and quickload; BT retained all ten after a genuine death event. All generated patches had 1-64 triangles, no script errors. Evidence: wound-regression-tests.json. Visual screenshots show head/torso wounds after saving and loading, and torso wounds on the saved BT corpse.
