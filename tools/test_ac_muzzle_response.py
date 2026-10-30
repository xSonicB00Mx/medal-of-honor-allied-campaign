"""Repeat a measured Thompson muzzle light at a fixed camera in a save COPY.

Actual-fire coverage lives in test_ac_weapon_lighting.py. This isolates the
renderer response from recoil, random particles and flash lifetime.
The fixed ROIs require the m3l2 save from the reported regression; this is
case-specific reproduction, not a test for arbitrary personal saves.
"""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--installed',action='store_true');ap.add_argument('--generic',action='store_true');ap.add_argument('--verify',action='store_true');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;h=p/'main';h.mkdir(parents=True);b=p/'bin';b.mkdir()
rt=R/'runtime-local/CP09-r1';build=rt if a.installed else R/'build-local/cp00-r3/RelWithDebInfo'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
personal=R/'profiles-local/CP08-r1/user'
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/n,b/n)
dest=h/'save/omconfig';dest.mkdir(parents=True)
for f in (personal/'main/save/omconfig').glob('quick.*'):shutil.copy2(f,dest/('reference'+f.suffix))
(h/'fixture.scr').write_text('''main:
    level.fx_light = spawn models/weapons/mp40.tik targetname "fx_light"
    level.fx_light.origin = ( -3628.93 1877.32 47.52 )
    level.fx_light svflags "+broadcast"
    level.fx_light light .25 .20 .15 150
    level.fx_light lightOff
    level.fx_cam = spawn Camera
    level.fx_cam.origin = ( -3631.103 1905.205 82.125 )
    level.fx_cam.angles = ( 60 -79.173 0 )
    $player hide
    cuecamera level.fx_cam
    println AC_MUZZLE_READY
end
''')
cmd=['wait 800','loadgame reference','wait 5000','finishloadingscreen','god','notarget','wait 500','script player exec fixture.scr','wait 600','ui_hud 0','set cg_drawviewmodel 0','set ui_crosshair 0','screenshot silent',
 'script fx_light lightOn','set r_acDynamicLighting 0','wait 300','screenshot silent',
 'set r_acDynamicLighting 1','wait 300','screenshot silent',
 'script fx_light lightOff','wait 300','screenshot silent','set r_acModelLighting 1','wait 300','screenshot silent','echo AC_MUZZLE_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,r_customwidth=1600,r_customheight=900,com_maxfps=60,com_maxfpsUnfocused=60,r_fastsky=0,r_acLightingDebug=2,r_acAmbientOcclusion=0,r_acModelShadows=0,r_acModelLighting=0,r_acSoftParticles=0,r_acDynamicLighting=1,r_fastdlights=0,ac_campaign_mode=0,ui_gmbox=0,ui_gmboxspam=0,g_subtitle=0).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+set','r_ignoreFastPath',str(int(a.generic)),'+exec','probe.cfg'],cwd=b,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_MUZZLE_DONE' in log and 'AC_MUZZLE_READY' in log
assert 'CM_LoadMap( maps/m3l2.bsp' in log, 'This fixture requires the reported m3l2 save'
assert not any(x in log for x in ['Script Error','Script file compile error','Unknown command','Invalid event'])
images=[];frames=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
 dst=out/f'muzzle-{i}.png';im=Image.open(f).convert('RGB');im.save(dst);images.append(dst.relative_to(R).as_posix());frames.append(np.array(im,dtype=float))
assert len(frames)==5
values={}
for name,(y0,y1,x0,x1) in dict(floor=(600,800,430,700),wall=(180,300,20,180),head=(130,190,420,480),torso=(240,320,250,400),right_body=(190,250,960,1070)).items():
 roi=np.s_[y0:y1,x0:x1]
 values[name]=dict(legacy=float((frames[1]-frames[0])[roi].mean()),occluded=float((frames[2]-frames[0])[roi].mean()),drift=float(abs(frames[3]-frames[0])[roi].mean()),local_probes=float(abs(frames[4]-frames[3])[roi].mean()))
assert hashes()==before
result=dict(engine_sha256=sha(build/'openmohaa.exe'),images=images,values=values,personal_files_unchanged=len(before))
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(values),flush=True)
if a.verify:
 for name in ['head','torso','right_body','wall']:
  v=values[name];assert v['drift']<.01 and v['legacy']>3 and v['occluded']>.7*v['legacy'],(name,v)
 print('PASS: real muzzle parameters retain illumination with occlusion enabled')
