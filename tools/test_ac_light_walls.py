"""Native light occlusion across a BSP ceiling, with a visible floor control."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image
import numpy as np

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--baseline',action='store_true');ap.add_argument('--fast',action='store_true');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;h=p/'main';h.mkdir(parents=True,exist_ok=False)
b=p/'bin';b.mkdir();rt=R/'runtime-local/CP09-r1'
engine=(rt if a.baseline else R/'build-local/cp00-r3/RelWithDebInfo')/'openmohaa.exe'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
personal=R/'profiles-local/CP08-r1/user'
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
shutil.copy2(engine,b/engine.name)
(h/'fixture.scr').write_text("""main:
    level.fx_light = spawn models/weapons/mp40.tik targetname "fx_light"
    level.fx_light.origin = ( -4050 -4100 50 )
    level.fx_light svflags "+broadcast"
    level.fx_light light 1 .3 .08 320
    level.fx_light lightOn
    level.wall_cam = spawn Camera
    $player hide
    cuecamera level.wall_cam
end
""")
views=[((-4050,-4100,-200),(-4050,-4100,-128)),((-4000,-4200,100),(-4050,-4100,-40))]
vec=lambda v:'( '+' '.join(map(str,v))+' )'
cmd=['wait 800','devmap m2l2a','wait 5000','finishloadingscreen','god','notarget','wait 700',
 'script player exec fixture.scr','wait 500','ui_hud 0','set cg_drawviewmodel 0','set ui_crosshair 0']
for i,(eye,target) in enumerate(views):
 (h/f'view{i}.scr').write_text(f"""main:
    $player.origin = {vec(eye)}
    level.wall_cam.origin = {vec(eye)}
    level.wall_cam.angles = vector_toangles ({vec(target)} - level.wall_cam.origin)
    println AC_LIGHT_VIEW_{i}
end
""")
 cmd += [f'script player exec view{i}.scr','wait 400','script fx_light lightOff','wait 200','screenshot silent',
         'script fx_light lightOn','set r_acDynamicLighting 0','wait 300','screenshot silent',
         'set r_acDynamicLighting 1','wait 300','screenshot silent']
cmd+=['echo AC_LIGHT_WALL_DONE','quit'];(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,
 net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,
 r_customwidth=1600,r_customheight=900,com_maxfps=60,com_maxfpsUnfocused=60,r_fastsky=0,r_acLightingDebug=2,r_fastdlights=int(a.fast),
 r_acAmbientOcclusion=0,r_acModelShadows=0,r_acModelLighting=0,cg_shadows=0,ui_gmbox=0,ui_gmboxspam=0,g_subtitle=0).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_LIGHT_WALL_DONE' in log
errors=[l for l in log.splitlines() if 'LOCALIZATION ERROR:' not in l and any(e in l for e in ['ERROR:','Script Error','Script file compile error','Unknown command','Invalid event'])];assert not errors,errors
images=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
 dst=out/f'wall-{i}.png';Image.open(f).save(dst);images.append(dst.relative_to(R).as_posix())
assert len(images)==6
values=[]
for j in [0,3]:
 base=np.array(Image.open(R/images[j]).convert('RGB'),dtype=float)
 old=np.array(Image.open(R/images[j+1]).convert('RGB'),dtype=float)
 new=np.array(Image.open(R/images[j+2]).convert('RGB'),dtype=float)
 roi=np.s_[150:700,200:1400] if j==0 else np.s_[650:850,300:1050]
 oldd=np.max(old-base,axis=2)[roi];newd=np.max(new-base,axis=2)[roi]
 values.append(dict(old_pixels=int((oldd>3).sum()),new_pixels=int((newd>3).sum()),old_mean=float(oldd.mean()),new_mean=float(newd.mean())))
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(images=images,values=values,engine_sha256=sha(engine)),indent=2))
print(values,flush=True)
assert values[0]['old_pixels']>1000 and values[0]['new_pixels']<values[0]['old_pixels']*.01,values
assert values[1]['new_pixels']>1000,values
print('PASS blocked ceiling and visible floor')
