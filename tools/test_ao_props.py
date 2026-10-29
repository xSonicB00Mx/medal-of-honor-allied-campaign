"""Native static-prop AO alignment and distance sweep; isolated copied runtime.

Uses the actual baked typewriter in m2l2a, not a script-spawned replacement
(the static and dynamic model transforms are different). Images require review.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from PIL import Image
import numpy as np

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--baseline', action='store_true')
a = ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+', a.run)
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
p = R/'profiles-local/CP09'/a.run
h = p/'main'
h.mkdir(parents=True, exist_ok=False)
b = p/'bin'
b.mkdir()
rt = R/'runtime-local/CP09-r1'
engine = (rt if a.baseline else R/'build-local/cp00-r3/RelWithDebInfo')/'openmohaa.exe'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
personal = R/'profiles-local/CP08-r1/user'
def hashes():
    return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before = hashes()
for f in rt.glob('*.dll'): shutil.copy2(f, b/f.name)
shutil.copy2(engine, b/engine.name)
cmd = ['wait 800','devmap m2l2a','wait 5000','finishloadingscreen','set cheats 1','set developer 1','god','notarget',
       'wait 800','ui_hud 0','set cg_drawviewmodel 0','set ui_crosshair 0',
       'set r_acModelShadows 0','set cg_shadows 0']
target = (-3933.36,-4040.54,4)
views = [(0,80,35),(65,65,40),(-65,65,40),(0,140,45),(0,200,55)]
for i,(x,y,z) in enumerate(views):
    eye = tuple(target[j]+(x,y,z)[j] for j in range(3))
    vector = lambda v: '( '+' '.join(map(str,v))+' )'
    (h/f'view{i}.scr').write_text(f'''main:
    $player.origin = {vector((eye[0],eye[1],eye[2]-50))}
    $player hide
    if (level.ao_cam == NIL)
        level.ao_cam = spawn Camera
    level.ao_cam.origin = {vector(eye)}
    level.ao_cam.angles = vector_toangles ({vector(target)} - level.ao_cam.origin)
    cuecamera level.ao_cam
    println AO_PROP_VIEW_{i}
end
''')
    cmd += [f'script player exec view{i}.scr','wait 500',
            'set r_acAmbientOcclusion 0','wait 100','screenshot silent',
            'set r_acAmbientOcclusion 1','set r_acAODebug 2','wait 100','screenshot silent',
            'set r_acAODebug 1','wait 100','screenshot silent']
    if i==0 and not a.baseline:
        cmd += ['set r_acAODebug 3','wait 200']
cmd += ['echo AO_PROPS_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args = [str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,
                fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,
                developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,
                r_customwidth=1600,r_customheight=900,com_maxfps=60,
                com_maxfpsUnfocused=60,r_fastsky=0,r_acAODebug=2).items():
    args += ['+set',k,str(v)]
proc = subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=100)
log = (h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AO_PROPS_DONE' in log
assert all(f'AO_PROP_VIEW_{i}' in log for i in range(len(views))), 'Camera scripts did not execute'
errors = [l for l in log.splitlines() if any(e in l for e in
          ['Script Error','Unknown command','Invalid event','AC AO shader:','AC AO link:'])]
assert not errors, errors
costs = [(int(t),int(e)) for t,e in re.findall(r'AC_AO_COST ms=(\d+) gl_error=(\d+)',log)]
assert costs and all(e==0 for _,e in costs)
images = sorted((h/'screenshots').glob('*.tga'))
assert len(images)==3*len(views),len(images)
for i,f in enumerate(images):
    Image.open(f).save(out/f'{i//3}-{["off","on","ao"][i%3]}.png')
alignment = None
if not a.baseline:
    g = np.fromfile(h/'ao-geometry.f32',np.float32).reshape(900,1600,4)[::-1]
    actual = np.fromfile(h/'ao-window-depth.f32',np.float32).reshape(900,1600)[::-1]
    m10,m14 = map(float,re.search(r'AC_AO_GEOMETRY .* depth=([\d.-]+) ([\d.-]+)',log).groups())
    predicted = .5*(-m10+m14/np.maximum(g[:,:,3],.001))+ .5
    # Actual baked typewriter's body, not the table/background. Correct depth
    # agrees to float rasterization precision; old unscaled body was ~2x size.
    diff = np.abs(predicted[430:540,730:860]-actual[430:540,730:860])
    alignment = dict(median=float(np.median(diff)),p99=float(np.quantile(diff,.99)))
    assert alignment['p99']<2e-6, ('AO/model depth mismatch',alignment)
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=sha(engine),views=views,
    alignment=alignment,personal_files_unchanged=len(before),pass_ms=[t for t,e in costs]),indent=2)+'\n')
print('PASS static typewriter views',flush=True)
