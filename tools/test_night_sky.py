"""Native night-sky regression using an isolated copy of a supplied SH save."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--installed',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP09-r1';p=r/'profiles-local/night-sky'/a.run;p.mkdir(parents=True,exist_ok=False)
out=r/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=True)
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
src=r/'profiles-local/CP08-r1/user'
def snapshot():return {f.relative_to(src).as_posix():digest(f) for f in src.rglob('*') if f.is_file()}
before=snapshot();b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
engine=(rt if a.installed else r/'build-local/cp00-r3/RelWithDebInfo')/'openmohaa.exe';shutil.copy2(engine,b/engine.name)
for d in ['main','mainta','maintt']:(p/d).mkdir()
shutil.copy2(src/'main/ac_preferences.cfg',p/'main/ac_preferences.cfg')
s=p/'mainta/save/omconfig';s.mkdir(parents=True)
for f in (src/'mainta/save/omconfig').glob('t1l10001.*'):shutil.copy2(f,s/f.name)
(p/'mainta/view.scr').write_text('main:\n local.cam = spawn Camera\n local.cam.origin = ( -2800 -2400 -6500 )\n local.cam.angles = ( 0 90 0 )\n cuecamera local.cam\nend\n')
cmd=['wait 1000','loadgame t1l10001','wait 5000','finishloadingscreen','set developer 1','script player exec view.scr','wait 500']
for fast,fog in [(1,0),(0,0),(1,1)]:
 cmd += [f'set r_fastsky {fast}',f'set r_farplane_nofog {fog}','wait 500','screenshot silent']
cmd+=['echo AC_NIGHT_DONE','quit'];(p/'mainta/probe.cfg').write_text('\n'.join(cmd)+'\n')
opts=dict(com_target_game=1,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1600,r_customheight=900,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1)
args=[str(b/'openmohaa.exe')]
for k,v in opts.items():args+=['+set',k,str(v)]
x=subprocess.run(args+['+exec','probe.cfg'],cwd=rt,timeout=60)
log=(p/'mainta/qconsole.log').read_text(encoding='latin1');assert x.returncode==0 and 'AC_NIGHT_DONE' in log and 'AC_SAVE_ACCEPT context=1 map=t1l1' in log
images=[];bright=[]
for f in sorted((p/'mainta/screenshots').glob('*.tga')):
 im=Image.open(f).convert('RGB');dest=f.with_suffix('.png');im.save(dest);images.append(str(dest.relative_to(r)))
 # The old hard-coded clear color becomes (151,151,255) after gamma.
 bright.append(sum(1 for red,green,blue in im.getdata() if blue>240 and 120<red<190 and abs(red-green)<3))
assert len(images)==3
assert before==snapshot(),'Personal profile changed'
if a.installed:assert bright[0]>10000,bright
else:assert bright[0]==0 and bright[2]==0,bright
result=dict(engine_sha256=digest(engine),passed=True,personal_files_unchanged=len(before),old_blue_pixels=bright,images=images,loaded_existing_save=True)
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
