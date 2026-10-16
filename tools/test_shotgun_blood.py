"""Nine real pellets, per-contact wounds/drops, save/load and dying actor coverage."""
from pathlib import Path
import argparse, subprocess, shutil, re, json
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('run');ap.add_argument('--death',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/shotgun'/a.run
num=['AA','SH','BT'].index(a.game);h=p/['main','mainta','maintt'][num];(h/'fixture').mkdir(parents=True,exist_ok=False)
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text().replace('level.cp00_subject ai_off','level.cp00_subject ai_off\n    level.cp00_subject.health = '+('1' if a.death else '10000')+'\n    level.cp00_subject.enablePain = 0').replace('models/weapons/colt45.tik','models/weapons/shotgun.tik')
(h/'fixture/base.scr').write_text(fixture)
(h/'fixture/inspect.scr').write_text('main:\n local.dir = vector_normalize (level.cp00_subject.origin - level.cp00_base)\n $player.origin = level.cp00_subject.origin - local.dir * 65 + ( 0 0 10 )\n $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 50 )) - ($player.origin + ( 0 0 64 )))\nend\n')
start='devmap m2l1'
if num:
    source=r/['','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'][num]
    (h/'save/omconfig').mkdir(parents=True)
    for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),h/('save/omconfig/reference'+ext))
    start='loadgame reference'
cmd=['wait 1000',start,'wait 4000','finishloadingscreen','wait 3000','god','script player exec fixture/base.scr','wait 2500','script player ammo shotgun 100','echo SHOTGUN_BEGIN','+attack','wait 100','-attack','wait 120','screenshot silent','wait 2200','echo SHOTGUN_END','screenshot silent']
if not a.death:
    cmd+=['script player exec fixture/inspect.scr','wait 1200','screenshot silent','savegame pellet','wait 1500','loadgame pellet','wait 4000','finishloadingscreen','wait 1500','screenshot silent']
cmd+=['echo SHOTGUN_DONE','quit'];(h/'test.cfg').write_text('\n'.join(cmd)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=0,ac_fx_debug=2,ac_body_wounds=1,ac_world_blood=1,ac_blood_mist=1)
args=[str(b/'openmohaa.exe')]
for k,v in settings.items():args+=['+set',k,str(v)]
result=subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=110)
log=(h/'qconsole.log').read_text(encoding='latin1');assert result.returncode==0 and 'SHOTGUN_DONE' in log
segment=log.split('SHOTGUN_BEGIN',1)[1].split('SHOTGUN_END',1)[0]
hits=re.findall(r'AC_HIT id=(\d+).*?group=5 seed=(\d+) entry=1 exit=(\d+)',segment)
assert len(hits)==9,hits
wounds=re.findall(r'AC_WOUND id=(\d+) branch=(\d+).*?group=5 radius=([\d.]+).*?triangles=(\d+)',segment)
assert len(wounds)==sum(1+int(x[2]) for x in hits),wounds
assert all(float(rad)==1.8 and int(n)>0 for _,_,rad,n in wounds),wounds
received=set(re.findall(r'AC_WOUND_RECEIVED id=(\d+) branch=(\d+)',segment))
assert received=={(id,branch) for id,branch,_,_ in wounds},received
drops=re.findall(r'AC_DROPS target=\d+ seed=(\d+) branch=(\d+) count=(\d+)',segment)
assert {int(seed) for seed,branch,n in drops if branch=='0' and int(n)>0}=={int(seed) for _,seed,_ in hits},drops
assert 'AC_MIST' in segment and 'AC_MARK drop' in log
archives=re.findall(r'AC_WOUND_ARCHIVE (save|load) count=(\d+)',log)
if not a.death:assert ('save',str(len(wounds))) in archives and ('load',str(len(wounds))) in archives,archives
else:assert 'CP00_DEATH_EVENT count=1' in log and 'AC_CORPSE' in segment
errors=[line for line in log.splitlines() if any(s in line for s in ['Script Error','Unknown command','Invalid event','reliable command overflow'])];assert not errors,errors
for f in (h/'screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
report=dict(game=a.game,death=a.death,pellets=len(hits),wounds=len(wounds),droplets=sum(int(x[2]) for x in drops),archives=archives,server_timing=re.findall(r'AC_SHOTGUN[^\n]+',log),passed=True)
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
