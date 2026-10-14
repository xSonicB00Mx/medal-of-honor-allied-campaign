"""Reproduce BT dirt-road versus grass blood on the same saved native corpse."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('--runtime',default='CP05a-r1');ap.add_argument('--run-id',required=True);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local'/a.runtime;p=r/'profiles-local/CP05a-r2'/a.run_id;h=p/'maintt'
assert re.fullmatch(r'CP05a-r[12]',a.runtime) and re.fullmatch(r'[A-Za-z0-9-]+',a.run_id) and not p.exists()
(h/'save/omconfig').mkdir(parents=True);(h/'probe').mkdir()
source=r/'profiles-local/CP05a-r1/final-BT/maintt/save/omconfig/corpse.sav'
for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),h/('save/omconfig/reference'+ext))
(h/'probe/aim.scr').write_text('main:\n    local.aim = level.cp00_subject gettagposition "Bip01 Spine2"\n    $player.origin = level.cp00_subject.origin + ( -45 -45 35 )\n    $player.viewangles = vector_toangles (local.aim - ($player.origin + ( 0 0 64 )))\nend\n')
(h/'probe/ground.scr').write_text('main:\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 25 0 )) - ($player.origin + ( 0 0 64 )))\nend\n')
commands=['wait 1000','loadgame reference','wait 3000','finishloadingscreen','wait 2000','set developer 1','set ac_fx_debug 3','set ac_corpse_effects 1','set ac_world_blood 1','script player give models/weapons/colt45.tik','script player use models/weapons/colt45.tik','script player ammo pistol 100','wait 1500','script player exec probe/aim.scr','wait 300','screenshot','echo AC_ROAD_BEGIN']
for _ in range(3):commands+=['+attack','wait 80','-attack','wait 1400']
commands+=['script player exec probe/ground.scr','wait 700','screenshot','wait 1000','screenshot','wait 24000','screenshot','wait 8000','screenshot','echo AC_ROAD_DONE','quit']
(h/'test.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=2,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=960,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_fx_debug=3).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','test.cfg'],cwd=rt,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for im in sorted((h/'screenshots').glob('*.tga')):
 out=im.with_suffix('.png');Image.open(im).save(out);images.append(out.relative_to(r).as_posix())
events=re.findall(r'AC_(?:DROP|MARK|NEAREST|ROAD|CORPSE|SURFACE)[^\r\n]*',log)
result=dict(run=a.run_id,runtime=a.runtime,map='e2l2',completed='AC_ROAD_DONE' in log,exit=proc.returncode,binaries={x:hashlib.sha256((rt/x).read_bytes()).hexdigest() for x in ['openmohaa.exe','game.dll','cgame.dll']},source_save_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),events=events,images=images,errors=[l for l in log.splitlines() if any(x in l for x in ['Script Error','Unknown command','Invalid event','compile error'])])
out=r/'checkpoints/CP05a/r2';out.mkdir(exist_ok=True);(out/(a.run_id+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({**result,'events':len(events),'images':len(images)}),flush=True)
assert result['completed'] and proc.returncode==0 and not result['errors']
