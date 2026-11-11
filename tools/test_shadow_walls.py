"""Native m2l2a ceiling occlusion: a soldier on the floor above the camera.

The BSP ceiling must not reveal his silhouette from below. The upper-room
view supplies a positive control. Read-only assets, separate disposable profile.
"""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image
import numpy as np

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--baseline',action='store_true');a=ap.parse_args()
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
(h/'fixture.scr').write_text('''main:
    level.wall_actor = spawn models/human/german_wehrmact_soldier.tik origin ( -4050 -4100 -46 ) gun "Mauser KAR 98K"
    level.wall_actor ai_off
    // Keep the hidden test caster submitted, so PVS cannot mask a shadow leak.
    level.wall_actor svflags "+broadcast"
    println ("AC_WALL_ACTOR " + level.wall_actor.entnum)
    level.wall_actor.health = 10000
    level.wall_cam = spawn Camera
    $player hide
    cuecamera level.wall_cam
    local.hit = trace ( -4050 -4100 -200 ) ( -4050 -4100 40 ) 1
    println ("AC_WALL_TRACE " + local.hit)
end
''')
views=[((-4050,-4100,-200),(-4050,-4100,-128)),((-4000,-4200,100),(-4050,-4100,-10))]
vec=lambda v:'( '+' '.join(map(str,v))+' )'
cmd=['wait 800','devmap m2l2a','wait 5000','finishloadingscreen','god','notarget','wait 700',
     'script player exec fixture.scr','wait 500','ui_hud 0','set cg_drawviewmodel 0','set ui_crosshair 0']
for i,(eye,target) in enumerate(views):
    (h/f'view{i}.scr').write_text(f'''main:
    $player.origin = {vec(eye)}
    level.wall_cam.origin = {vec(eye)}
    level.wall_cam.angles = vector_toangles ({vec(target)} - level.wall_cam.origin)
    println AC_WALL_VIEW_{i}
end
''')
    cmd += [f'script player exec view{i}.scr','wait 500','set r_acModelShadows 0','wait 200','screenshot silent',
            'set r_acModelShadows 1','wait 500','screenshot silent']
cmd+=['echo AC_WALL_DONE','quit'];(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,
                net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,
                r_mode=-1,r_customwidth=1600,r_customheight=900,com_maxfps=60,com_maxfpsUnfocused=60,
                r_fastsky=0,r_acShadowDebug=3,r_acAmbientOcclusion=0,cg_shadows=0,ui_gmbox=0,ui_gmboxspam=0,g_subtitle=0).items():
    args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_WALL_DONE' in log
errors=[l for l in log.splitlines() if any(e in l for e in ['Script Error','Script file compile error','Unknown command','Invalid event','AC shadows shader:','AC shadows link:'])]
assert not errors,errors
actor=int(re.search(r'AC_WALL_ACTOR (\d+)',log)[1])
below=log.split('AC_WALL_VIEW_0',1)[1].split('AC_WALL_VIEW_1',1)[0]
assert f'AC_LIGHT owner={actor} ' in below,'Hidden soldier was not tested by shadow pass'
assert 'AC_WALL_TRACE ( -4050.000 -4100.000 -128.125 )' in log,'Expected solid ceiling not hit'
costs=[(int(ms),int(err)) for ms,err in re.findall(r'AC_SHADOW_COST ms=(\d+) gl_error=(\d+)',log)]
assert costs and all(err==0 for _,err in costs)
imgs=sorted((h/'screenshots').glob('*.tga'));assert len(imgs)==4
for i,f in enumerate(imgs):Image.open(f).save(out/f'{i//2}-{["off","on"][i%2]}.png')
diff=np.asarray(Image.open(imgs[0]),dtype=float)-np.asarray(Image.open(imgs[1]),dtype=float)
roi=diff[150:750,250:1350,:3].mean(2)
upper=(np.asarray(Image.open(imgs[2]),dtype=float)-np.asarray(Image.open(imgs[3]),dtype=float))[610:750,600:1000,:3].mean(2)
assert int((upper>2).sum())>100,'Visible floor shadow missing'
assert hashes()==before
result=dict(engine_sha256=sha(engine),personal_files_unchanged=len(before),shadow_cost_ms=[ms for ms,_ in costs],
            ceiling_darkened_pixels=int((roi>2).sum()),ceiling_mean_darkening=float(roi.mean()),
            visible_floor_darkened_pixels=int((upper>2).sum()),hidden_caster_submitted=True,
            trace=re.findall(r'AC_WALL_TRACE.*',log),blocker_surfaces=[int(x) for x in re.findall(r'AC_SHADOW_BLOCKERS surfaces=(\d+)',log)])
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if not a.baseline:
    assert result['blocker_surfaces'] and max(result['blocker_surfaces'])>0
    assert result['ceiling_darkened_pixels']==0,result
