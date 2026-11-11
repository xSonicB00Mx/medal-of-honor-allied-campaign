"""Real single-player weapon shots; isolated profiles and instrumented live targets."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('--run-id',required=True);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP02-r1';p=r/'profiles-local/CP02-r1'/a.run_id
assert re.fullmatch('[A-Za-z0-9-]+',a.run_id) and not p.exists()
n,f,src={'AA':(0,'main',None),'SH':(1,'mainta','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':(2,'maintt','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[a.game]
h=p/f;(h/'cp00').mkdir(parents=True);start='map m2l1'
if src:
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2((r/src).with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text().replace('level.cp00_subject ai_off','level.cp00_subject ai_off\n    level.cp00_subject.health = 10000')
(h/'cp00/base.scr').write_text(fixture)
commands=['wait 1000',start,'wait 3000','finishloadingscreen','wait 3000','set ui_console 0','set developer 1','script player exec cp00/base.scr','wait 1500']
for state in [0,1]:
 commands += [f'set ac_blood_mist {state}']
 for gun,ammo in [('colt45','pistol'),('mp40','smg'),('kar98','rifle'),('bar','mg')]:
  (h/f'cp00/{gun}.scr').write_text(f'main:\n    $player give models/weapons/{gun}.tik\n    $player use models/weapons/{gun}.tik\n    local.aim = level.cp00_subject.origin + ( 0 0 50 )\n    $player.viewangles = vector_toangles (local.aim - ($player.origin + ( 0 0 64 )))\nend\n')
  commands += [f'echo CP02_SHOT_{state}_{gun}',f'script player exec cp00/{gun}.scr',f'script player ammo {ammo} 100','wait 2300','+attack','wait 120','-attack','wait 800','+attack','wait 120','-attack','screenshot','wait 800']
commands += ['savegame cp02_mist','wait 700','loadgame cp02_mist','wait 3000','finishloadingscreen','wait 1000','ac_blood_mist','ac_ui_options','wait 500','screenshot','set ac_blood_mist 0','popmenu 1','ac_blood_mist','wait 500','writeconfig omconfig.cfg','wait 200','echo CP02_DONE','quit']
(h/'mist.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=960,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_fx_debug=1).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','mist.cfg'],cwd=rt,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for image in sorted((h/'screenshots').glob('*.tga')):
 out=image.with_suffix('.png');Image.open(image).save(out);images.append(out.relative_to(r).as_posix())
result=dict(game=a.game,exit=proc.returncode,completed='CP02_DONE' in log,engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cgame_sha256=hashlib.sha256((rt/'cgame.dll').read_bytes()).hexdigest(),images=images,mist_events=re.findall(r'AC_MIST[^\r\n]+',log),errors=[l for l in log.splitlines() if any(t in l for t in ['Script Error','Unknown command','Invalid event','compile error','command not available'])],saved_off='seta ac_blood_mist "0"' in (h/'configs/omconfig.cfg').read_text())
(r/'checkpoints/CP02'/f'{a.run_id}.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
assert result['completed'] and proc.returncode==0 and not result['errors'] and result['saved_off'] and len(result['mist_events'])>=8
