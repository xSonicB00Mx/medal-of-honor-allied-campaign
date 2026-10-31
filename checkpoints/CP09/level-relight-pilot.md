# CP09 – isolated level-lighting pilot

## Scope and rollback

Explicit user request, 2026-10-31: improve the lighting of one level, work
autonomously, supply real before/after screenshots, keep the change reversible.
Pilot: Allied Assault `m3l3`, The Nebelwerfer Hunt, using a copy of the user's
current church save. This is **not installed in CP08-r1 or CP09-r1**.

The pilot has its own executable and two separate profiles. The workspace
launchers `Start-CP09-Relight-Before.cmd` and `Start-CP09-Relight-After.cmd` load
the same copied reference save with original/new lighting respectively.
`tools/prepare_level_relight_pilot.py` prepares these only from the final bake.
Returning to the ordinary Allied Campaign launcher restores the regular game;
there is nothing to overwrite or restore in the personal installation.

`r_acLevelRelight` defaults to **0**. The sidecar is read on world load. To
switch it off within the pilot use `r_acLevelRelight 0` and `vid_restart`.
Loading a save in the same map can reuse the existing renderer world and is
therefore not a reliable way to apply this switch. A renderer restart rebuilds
from the original BSP; there is no accumulation of baked corrections.

## Implementation

- Engine exports the resolved world surfaces/patches, full-resolution terrain,
  static prop instances and their diffuse/alpha textures to the isolated
  profile. Only the world model is included; movable doors and NPCs are not
  turned into permanent baked occluders.
- Local Embree acceleration structure: 139,915 triangles, 225 materials.
- Cosine-weighted diffuse sky transport at 534,242 valid lightmap texels;
  512 directions for sky visibility and 512 for one diffuse bounce. Surface
  albedo colors the bounce. Alpha-tested foliage holes transmit rays.
- Chart-aware filtering keeps separate lightmap islands from bleeding into
  each other. Tiny bevel islands (sometimes only two texels) receive a
  world-space continuity gather across nearby compatible surfaces: same
  material, aligned normals, bounded plane distance. Opposite wall sides
  and unrelated materials are excluded. Gutters are filled locally. Original 128x128 lightmap atlas
  layout, dynamic-light update path, and moving-brush maps remain compatible.
- The sky remains overcast. The original fog, exposure, textures and camera
  settings are unchanged. New irradiance replaces 85% of the old bake, with
  an artistic calibration for this map; this is not a photometric conversion
  of every original light entity or a general-purpose BSP compiler.
- Separate 125x128x21 RGB irradiance-factor volume, 128-unit spacing and 128
  rays per probe/pass, keeps grid-lit models and static prop vertex colors
  closer to the new environment lighting. Runtime work is an eight-probe
  interpolation; static props are adjusted once on load. **No new runtime
  visibility traces, shadow maps or fullscreen passes.**
- Original NPC/pickup shadows, AO, TAA, object motion blur and weapon/explosion
  lights retain their implementations. The three previously removed lighting/
  particle experiments have not been reintroduced.

This is a static, one-bounce lighting pilot, not dynamic global illumination.
Moving geometry does not rebake the environment. The original lightmap
resolution remains a limit on tiny lighting details. The heavy mission fog
intentionally still softens distant contrast.

## Files and reproducibility

Only source/tools/documentation belong in Git. The exported game geometry,
textures, BSP, bake, screenshots, binaries and copied saves remain ignored
local data. Dependencies were installed under the D: workspace, not C:.

- Export: `tools/test_level_relight.py <run> --export`
- Bake: `tools/bake_level_relight.py --samples 512 --out <local-bake>`
- Transport invariants: `tools/test_level_relight_math.py`
- Native rejection/rollback/lifetime checks:
  `tools/test_level_relight_checks.py <run> --bake <local-bake>`
- Native captures: `tools/test_level_relight.py <run> --bake <local-bake>
  --views <local-views.json> --uhd`; `--disabled` supplies the matched original.
- Church performance route: `tools/diagnose_church_performance.py <run>
  --candidate --removed --relight-bake <local-bake>`; add `--relight-off`
  for the paired original. These are CPU wall times including driver waits,
  not GPU timestamps; the combat timeline can vary between separate loads.

Local bake dependencies: NumPy/Pillow in the existing runtime, SciPy 1.18.1
and embreex 4.4.0.post1 in `generated-local/CP09/relight-pilot/python-deps`.
Export/source inputs are fingerprinted; reusable transport caches must match
the exported geometry, material textures and sample count.

The `.aclm` sidecar has a 16-byte little-endian header (ACL1, FNV-1a of original
lightmap bytes, payload size, version 1) followed by RGB bytes. `.acgrid` has
a 44-byte header (ACG1, same source hash, version 1, channels 3, origin float3,
step float, bounds int3), followed by float32 RGB, x fastest. The pilot writer
and native reader target the current Windows x64 build. Readers validate
version, size, source, finite values and bounded dimensions before allocation.

## Validation

Five synthetic transport tests pass: opaque occlusion, sky illumination,
alpha-cutout transmission, colored diffuse reflection and island-safe filter
behavior, plus world-space continuity without crossing opposing faces or
materials. Native opt-out and malformed-sidecar checks use temporally stable
settings to distinguish true renderer differences from TAA sampling.

`relight-final-checks` passes default-off/reference comparison, wrong source
fingerprint, truncated lightmap, NaN probe and overflowing grid bounds. The
stable facade is **pixel-identical** to the original renderer when disabled
or when the lightmap is rejected (mean/max difference both 0). Whole-frame
mean difference is 0.016/255 due to non-static content; P99 is 0. Save/load,
graphics restart, another map (`m2l1`) and return to the original lighting
pass. Same-map save loading reuses the renderer world without applying the
correction twice. Restart loads it once from the original data.

`relight-perf-before` / `relight-perf-after`: identical engine, UHD, TAA,
blur 50%, shadows and AO, same six-second approach and 18-second combat
measurement. Before: 2,116 frames, median 8 ms, P95 9 ms, max 16 ms. After:
2,112 frames, median 8 ms, P95 9 ms, max 15 ms. Save/load passes. The final
small-chart continuity correction changes only baked texel values; it adds
no runtime work. All 595 personal files remain hash-identical in each run.

Pilot executable SHA-256:
`4b1f201a532732cc66714cf64e85363dfe2f4fd53f170ccba83e19138fceabc5`.
Both regular runtimes retain engine SHA-256
`f567924a3a3dbb671056a6136dc7a3d43bd6744e058622be269cf7f1eed1ee47`.

The final executable/bake also passed `relight-final-native` (four UHD views,
save/load, renderer restart, map switch and disable), `relight-final-checks`,
and `relight-final-performance`: 2,118 frames, median 8 ms, P95 9 ms, max 15 ms.
Both full and fast model-grid lookup paths apply the correction; disabled
mode returns unchanged. Performance figures are CPU wall times including
driver waits, not direct GPU timings.

## Final local delivery

- Bake: `generated-local/CP09/relight-pilot/bake-final-stitched`.
- Isolated runtime: `runtime-local/CP09-Relight-Pilot`; its manifest records
  the executable, original runtime, bake and copied-profile fingerprints.
- Both real `.cmd` launchers tested at 3840x2160. Before loads no sidecar;
  After loads it exactly once. Both load `relight_reference` successfully.
  Private playtest configurations were restored after the smoke test.
- `generated-local/CP09/relight-delivery-final` contains four comparison
  sheets and eight untouched UHD originals. The ZIP passed CRC validation:
  62,861,165 bytes, SHA-256
  `21d9f15cd54a2454afe7dd679406aa91340d20e862e42e0972573fc733965778`.
- Final lightmap SHA-256:
  `e925a43a4a7e6d191e09545516d7515198936788048b7bd6b21097916d822af1`.
  Final model grid SHA-256:
  `02d939b8f41b824cdbd0c18152cd613f14382d211bc92fb7a7e92add1c747a57`.
- All 595 personal files remain byte-identical. Both regular runtime engines
  retain the original hash above. Native tests have exited cleanly.

This technical pilot does not claim a personal campaign playthrough or user
visual acceptance. No global deployment or merge was performed.
