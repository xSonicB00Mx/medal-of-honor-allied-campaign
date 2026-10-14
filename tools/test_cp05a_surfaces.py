"""Visible blood regression: native shots, reacting actor, early flight and ground images."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('--map',default='m2l1');ap.add_argument('--run-id',required=True)
ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--wall',action='store_true')
ap.add_argument('--static',action='store_true');ap.add_argument('--mist',type=int,default=1);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local'/'CP05a-r1';p=r/'profiles-local/CP05a-r1'/a.run_id
assert not p.exists() and re.fullmatch('[A-Za-z0-9-]+',a.run_id)
n,f,src={'AA':(0,'main',None),'SH':(1,'mainta','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':(2,'maintt','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[a.game]
h=p/f;(h/'probe').mkdir(parents=True);start='map '+a.map
if src:
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2((r/src).with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
fixture=(r/('tools/cp03_wall_fixture.scr' if a.wall else 'tools/cp00_baseline_fixture.scr')).read_text()
if not a.static:fixture=fixture.replace('level.cp00_subject ai_off','level.cp00_subject.enableEnemy = 0\n    level.cp00_subject ai_on')
fixture=fixture.replace('    level.cp00_subject thread deathwatch','    level.cp00_subject.health = 10000\n    level.cp00_subject thread deathwatch')
(h/'probe/base.scr').write_text(fixture)
(h/'probe/aim.scr').write_text('main:\n    $player give models/weapons/colt45.tik\n    $player use models/weapons/colt45.tik\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 50 )) - ($player.origin + ( 0 0 64 )))\nend\n')
(h/'probe/ground.scr').write_text('main:\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 2 )) - ($player.origin + ( 0 0 64 )))\nend\n')
commands=['wait 1000',start,'wait 3000','finishloadingscreen','wait 2000','set ui_console 0','set developer 1','script player exec probe/base.scr','wait 1200','script player exec probe/aim.scr','script player ammo pistol 100','wait 2000','screenshot','+attack','wait 50','-attack','screenshot','wait 100','screenshot','wait 150','screenshot','wait 300','screenshot','script player exec probe/ground.scr','wait 300','screenshot','wait 1000','screenshot','wait 12000','screenshot','wait 14000','screenshot','wait 7000','screenshot','echo AC_FEEDBACK_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_fx_debug=2,ac_world_blood=1,ac_body_wounds=1,ac_blood_mist=a.mist).items():cmd+=['+set',k,str(v)]
result=subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for image in sorted((h/'screenshots').glob('*.tga')):
 out=image.with_suffix('.png');Image.open(image).save(out);images.append(out.relative_to(r).as_posix())
report=dict(run=a.run_id,candidate='CP05a-r1',map=a.map,game=a.game,reacting=not a.static,wall=a.wall,mist=a.mist,completed='AC_FEEDBACK_DONE' in log,exit=result.returncode,images=images,
 binaries={name:hashlib.sha256((rt/name).read_bytes()).hexdigest() for name in ['openmohaa.exe','game.dll','cgame.dll']},
 events=re.findall(r'AC_(?:HIT|DROP|MARK|REAR|RECEIVE)[^\r\n]*',log),errors=[l for l in log.splitlines() if any(x in l for x in ['Script Error','Unknown command','Invalid event','compile error'])])
out=r/'checkpoints/CP05a';out.mkdir(exist_ok=True);(out/(a.run_id+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({**report,'images':len(images),'events':len(report['events'])}),flush=True)
assert report['completed'] and result.returncode==0 and not report['errors']
