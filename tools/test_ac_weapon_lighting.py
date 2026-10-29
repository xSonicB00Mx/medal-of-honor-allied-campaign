"""Actual first-person MP40 fire with isolated profile and on/off light comparison."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('--enabled',type=int,default=1);a.add_argument('--installed',action='store_true');a.add_argument('--save',action='store_true');a.add_argument('--look-down',action='store_true');a=a.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;h=p/'main';h.mkdir(parents=True)
b=p/'bin';b.mkdir();rt=R/'runtime-local/CP09-r1';build=rt if a.installed else R/'build-local/cp00-r3/RelWithDebInfo'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
personal=R/'profiles-local/CP08-r1/user'
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/n,b/n)
(h/'fixture.scr').write_text("""main:
    $player.origin = ( -4170 -4090 -44 )
    $player.viewangles = ( 20 180 0 )
    $player give models/weapons/mp40.tik
    $player use models/weapons/mp40.tik
    println AC_REAL_FIRE_READY
end
""")
cmd=['wait 800','devmap m2l2a','wait 5000','finishloadingscreen','god','notarget','wait 500','script player exec fixture.scr','wait 1000','ui_hud 0','set ui_crosshair 0','screenshot silent','echo AC_REAL_FIRE_BEGIN','+attack']
if a.save:
 dest=h/'save/omconfig';dest.mkdir(parents=True)
 for f in (personal/'main/save/omconfig').glob('quick.*'):shutil.copy2(f,dest/('reference'+f.suffix))
 (h/'fixture.scr').write_text('main:\n    println ("AC_REAL_FIRE_READY origin=" + $player.origin + " angles=" + $player.viewangles)\nend\n')
 cmd[1]='loadgame reference'
if a.look_down:
 f=h/'fixture.scr';s=f.read_text();s=s.replace('main:\n','main:\n    local.angles = $player.viewangles\n    local.angles[0] = 60\n    $player.viewangles = local.angles\n',1);f.write_text(s)
for i in range(24):cmd+=['wait 45','screenshot silent']
cmd+=['-attack','echo AC_REAL_FIRE_END','wait 600','screenshot silent','echo AC_REAL_FIRE_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,r_customwidth=1600,r_customheight=900,com_maxfps=60,com_maxfpsUnfocused=60,r_fastsky=0,r_acLightingDebug=2,r_acAmbientOcclusion=0,r_acModelShadows=0,r_acModelLighting=0,r_acSoftParticles=0,r_acDynamicLighting=a.enabled,ac_campaign_mode=0,ui_gmbox=0,ui_gmboxspam=0,g_subtitle=0).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_REAL_FIRE_DONE' in log and 'AC_REAL_FIRE_READY' in log
errors=[l for l in log.splitlines() if any(e in l for e in ['Script Error','Script file compile error','Unknown command','Invalid event','command not available'])];assert not errors,errors
images=[];frames=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
 dst=out/f'fire-{i}.png';im=Image.open(f).convert('RGB');im.save(dst);images.append(dst.relative_to(R).as_posix());frames.append(np.asarray(im,dtype=float))
assert len(images)==26,len(images)
# Diagnostic only: recoil/particles preclude a registered pixel comparison.
# test_ac_muzzle_response.py asserts the stationary measured-light response.
roi=np.s_[200:500,100:500];base=frames[0][roi];diff=[float(np.maximum(f[roi]-base,0).mean()) for f in frames[1:-1]]
assert hashes()==before
result=dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),game_sha256=sha(rt/'game.dll'),enabled=a.enabled,images=images,wall_brightness=diff,peak=max(diff),peak_index=diff.index(max(diff))+1,personal_files_unchanged=len(before))
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('DONE fire',a.enabled,'peak',result['peak'],'image',result['peak_index'],flush=True)
