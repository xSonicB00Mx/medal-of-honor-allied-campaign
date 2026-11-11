"""Native BT drop-policy switching across real deaths and save/load."""
from pathlib import Path
import argparse,subprocess,shutil,json,re
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('run');ap.add_argument('--installed',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/drop-options'/a.run
num=['AA','SH','BT'].index(a.game);h=p/['main','mainta','maintt'][num];(h/'fixture').mkdir(parents=True,exist_ok=False)
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
for folder in ['main','mainta','maintt']:
 (p/folder).mkdir(exist_ok=True)
 if not a.installed:
  for f in (r/'generated-local/flinch/packages'/folder).glob('*.pk3'):shutil.copy2(f,p/folder/f.name)
(h/'fixture/hit.scr').write_text('main:\n $player.health = 100\n $player hurt 10 bullet ( 1 1 1 )\nend\n')
start='devmap m2l1'
if num:
 source=r/['','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'][num]
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text()
(h/'fixture/base.scr').write_text(fixture)
(h/'fixture/kill.scr').write_text('main:\n level.cp00_subject hurt 10000 bullet ( 1 0 0 )\nend\n')
(h/'fixture/remove.scr').write_text('main:\n if (level.cp00_subject != NULL)\n  level.cp00_subject remove\nend\n')
cmd=['wait 1000',start,'wait 4000','finishloadingscreen','wait 1000','god','set ac_drop_debug 1','set ai_health_kar 1','set ai_health_mp40points 1']
for state in [1,0,1,0]:
 cmd+=['set ac_bt_drop_limits '+str(state),'script player exec fixture/base.scr','wait 1200','echo DROP_BEGIN_'+str(state),'script player exec fixture/kill.scr','wait 1200','echo DROP_END','script player exec fixture/remove.scr','wait 200']
 if state==0:cmd+=['savegame drops','wait 500','loadgame drops','wait 4000','finishloadingscreen','wait 500']
cmd+=['echo FLINCH_DONE','quit']
(h/'test.cfg').write_text('\n'.join(cmd)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=0)
args=[str(b/'openmohaa.exe')]
for k,v in settings.items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=100)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'FLINCH_DONE' in log
errors=[l for l in log.splitlines() if any(x in l for x in ['Script Error','Unknown command','Invalid event'])];assert not errors,errors
segments=re.findall(r'DROP_BEGIN_([01])(.*?)DROP_END',log,re.S)
assert len(segments)==4
checks=[]
for state,segment in segments:
 items=re.findall(r'AC_DROP_ITEM limits=([01]) model=([^ ]+) dropped=(\d)',segment)
 assert segment.count('CP00_DEATH_EVENT count=1')==1
 if a.game!='BT':
  assert 'AC_DROP_POLICY' not in segment and not items, 'BT policy leaked into AA/SH'
 elif state=='1':
  assert 'AC_DROP_POLICY limits='+state in segment
  assert not items,items
 else:
  assert 'AC_DROP_POLICY limits='+state in segment
  assert any('weapons/' in x[1].lower() and x[2]=='1' for x in items),items
  assert any('health' in x[1].lower() and x[2]=='1' for x in items),items
 checks.append(dict(limits=int(state),drops=items))
report=dict(game=a.game,difficulty_note="Loaded reference difficulty; original hard-mode guard reviewed separately",live_switches=checks,save_load=True,passed=True)
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
