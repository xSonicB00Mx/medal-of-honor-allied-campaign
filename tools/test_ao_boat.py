"""Isolated Normandy landing-boat diagnosis: separate AO and model shadows."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageStat

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
(h/'camera.scr').write_text('''main:
    clearfade
    releaseplayer
    hidemenu dday1
    hidemenu dday2
    level.boat_cam = spawn Camera
    level.boat_cam.origin = $player.origin + ( 0 0 64 )
    level.boat_angles = $player.viewangles
    level.boat_cam.angles = level.boat_angles
    cuecamera level.boat_cam
    $player hide
    println ("AO_BOAT origin=" + level.boat_cam.origin + " angles=" + level.boat_angles)
end
''')
angles=[(20,0),(20,-30),(20,30),(45,0),(0,0)]
modes=[('off',0,0,0),('shadow',0,1,0),('ao',1,0,1),('both',1,1,0)]
cmd=['wait 800','map m3l1a','wait 18000','finishloadingscreen','wait 700',
     'script player exec camera.scr','ui_hud 0','set cg_drawviewmodel 0','set ui_crosshair 0','set cg_shadows 0']
for i,(pitch,yaw) in enumerate(angles):
    (h/f'angle{i}.scr').write_text(f'main:\n    level.boat_cam.angles = level.boat_angles + ( {pitch} {yaw} 0 )\n    println AO_BOAT_VIEW_{i}\nend\n')
    cmd += [f'script player exec angle{i}.scr','wait 100']
    for name,ao,sh,debug in modes:
        cmd += [f'echo AO_BOAT_PHASE {i} {name}',f'set r_acAmbientOcclusion {ao}',f'set r_acModelShadows {sh}',f'set r_acAODebug {debug}',
                'wait 200','screenshot silent']
cmd+=['echo AO_BOAT_DONE','quit'];(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,
                net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,
                r_customwidth=1600,r_customheight=900,com_maxfps=60,com_maxfpsUnfocused=60,r_fastsky=0,r_acShadowDebug=3).items():
    args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AO_BOAT_DONE' in log
assert all(f'AO_BOAT_VIEW_{i}' in log for i in range(len(angles)))
errors=[l for l in log.splitlines() if any(e in l for e in ['Script Error','Unknown command','Invalid event','AC AO shader:','AC shadows shader:','AC shadows link:'])]
assert not errors,errors
costs=[(int(ms),int(error)) for ms,error in re.findall(r'AC_SHADOW_COST ms=(\d+) gl_error=(\d+)',log)]
assert costs and all(error==0 for _,error in costs),costs
imgs=sorted((h/'screenshots').glob('*.tga'));assert len(imgs)==len(angles)*len(modes)
for i,f in enumerate(imgs):
    im=Image.open(f)
    assert max(ImageStat.Stat(im.crop((200,100,1400,700))).stddev)>5, 'Blank/faded scene capture'
    im.save(out/f'{i//len(modes)}-{modes[i%len(modes)][0]}.png')
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=sha(engine),angles=angles,modes=modes,
    personal_files_unchanged=len(before),camera=re.findall('AO_BOAT origin=.*',log),
    shadow_cost_ms=[ms for ms,_ in costs],note='Boat and actors remain animated; visual views, not identical-frame pixel comparisons.'),indent=2)+'\n')
print('PASS landing boat captures')
