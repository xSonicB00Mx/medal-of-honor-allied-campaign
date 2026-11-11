"""Compare the SAME native frame with object blur off/on in a copied user save."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',type=int,default=0);ap.add_argument('--npc',action='store_true');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;folder=['main','mainta','maintt'][a.game];h=p/folder;h.mkdir(parents=True)
rt=R/'runtime-local/CP09-r1';build=R/'build-local/cp00-r3/RelWithDebInfo';personal=R/'profiles-local/CP08-r1/user'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes();b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/n,b/n)
for f in personal.rglob('*.cfg'):
    dest=p/f.relative_to(personal);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
src=max((personal/folder/'save/omconfig').glob('*.sav'),key=lambda f:f.stat().st_mtime)
dest=h/'save/omconfig';dest.mkdir(parents=True)
for f in src.parent.glob(src.stem+'.*'):shutil.copy2(f,dest/('reference'+f.suffix))
cmd=['wait 800','loadgame reference','wait 5000','finishloadingscreen','god','notarget',
     'set r_acObjectMotionBlur 100','wait 1000','set r_acTemporalDebug 4','wait 300',
     '+forward','wait 800','set r_acTemporalDebug 4','wait 200','-forward',
     '+attack','wait 800','set r_acTemporalDebug 4','wait 200','-attack','wait 800',
     'reload','wait 350','set r_acTemporalDebug 4','wait 800',
     'set r_acObjectMotionBlur 0','wait 300','set r_acTemporalDebug 4','wait 300',
     'echo AC_OBJECT_COMPARE_DONE','quit']
if a.npc:
    assert a.game==0
    (h/'runner.scr').write_text('''main:
    level.runner = spawn models/human/german_wehrmact_soldier.tik origin ( -4050 -4100 -46 ) gun "Mauser KAR 98K"
    level.runner threatbias ignoreme
    level.runner.health = 10000
    level.runner animloop rifle_run_forward
    level.runner.angles = ( 0 0 0 )
    local.cam = spawn Camera
    local.cam.origin = ( -4000 -4250 35 )
    local.cam.angles = vector_toangles (( -4050 -4100 -5 ) - local.cam.origin)
    $player hide
    cuecamera local.cam
    println AC_RUNNER_READY
end
''')
    cmd=['wait 800','devmap m2l2a','wait 5000','finishloadingscreen','god','notarget',
         'script player exec runner.scr','set r_acObjectMotionBlur 100']
    (h/'reset_runner.scr').write_text('main:\n    level.runner.origin = ( -4050 -4100 -46 )\n    level.runner animloop rifle_run_forward\nend\n')
    for strength in [100,50,100,100,0]:
        cmd += [f'set r_acObjectMotionBlur {strength}','script player exec reset_runner.scr','wait 350','set r_acTemporalDebug 4','wait 300']
    cmd += ['echo AC_OBJECT_COMPARE_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=a.game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,
 net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,
 r_customwidth=3840,r_customheight=2160,com_maxfps=90,com_maxfpsUnfocused=90,r_acTemporalDebug=0).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=100)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_OBJECT_COMPARE_DONE' in log
assert not any(e in log for e in ['AC temporal shader:','AC temporal link:','Unknown command','Invalid event'])
if a.npc:assert 'AC_RUNNER_READY' in log and 'does not exist' not in log and 'Script Error' not in log
rows=re.findall(r'AC_TEMPORAL_COMPARE index=(\d+) size=(\d+)x(\d+) elapsed=(\d+) strength=([\d.]+) history=(\d+)',log)
assert len(rows)==5,rows
results=[]
for row in rows:
    i,w,hh,dt,strength,valid=map(float,row);i,w,hh=int(i),int(w),int(hh)
    sharp=np.fromfile(h/f'temporal-{i:03d}-sharp.rgba',np.uint8).reshape(hh,w,4)
    blurred=np.fromfile(h/f'temporal-{i:03d}-blur.rgba',np.uint8).reshape(hh,w,4)
    obj=np.fromfile(h/f'temporal-{i:03d}-objects.f32',np.float32).reshape(hh,w,4);assert np.isfinite(obj).all()
    # Normalize the velocity metric to 1/60s, independently of the slider;
    # changed_pixels measures the actual final strength in the native pass.
    motion=np.linalg.norm(obj[:,:,:2]*[w,hh],axis=2)*16.6667/max(dt,1)
    diff=np.max(abs(sharp[:,:,:3].astype(int)-blurred[:,:,:3].astype(int)),axis=2);mask=obj[:,:,3]>0
    results.append(dict(index=i,elapsed=dt,history=valid,strength=strength,object_pixels=int(mask.sum()),
        motion_pixels=int(np.sum(mask&(motion>.5))),changed_pixels=int(np.sum(diff>3)),
        mean_object_change=float(np.mean(diff[mask])) if mask.any() else 0))
    if strength==0:assert diff.max()==0
    for label,img in [('sharp',sharp),('blur',blurred)]:Image.fromarray(img[::-1]).save(out/f'{i}-{label}.png')
assert hashes()==before
assert sum(f['changed_pixels'] for f in results if f['strength']>0)>1000,'No visible blur in native moving-object comparison'
if a.npc:assert max(f['changed_pixels'] for f in results)>50000,'Running NPC has no clear blur footprint'
result=dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),
    game_sha256=sha(rt/'game.dll'),personal_files_unchanged=len(before),reference='m2l2a running NPC fixture' if a.npc else src.name,frames=results)
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
