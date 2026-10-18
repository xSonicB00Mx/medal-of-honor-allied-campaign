"""Native AA/SH/BT hit feedback and options persistence, isolated from personal saves."""
from pathlib import Path
import argparse,subprocess,shutil,json,re
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('run');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/flinch'/a.run
num=['AA','SH','BT'].index(a.game);h=p/['main','mainta','maintt'][num];(h/'fixture').mkdir(parents=True,exist_ok=False)
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
for folder in ['main','mainta','maintt']:
 (p/folder).mkdir(exist_ok=True)
 for f in (r/'generated-local/flinch/packages'/folder).glob('*.pk3'):shutil.copy2(f,p/folder/f.name)
(h/'fixture/hit.scr').write_text('main:\n $player.health = 100\n $player hurt 10 bullet ( 1 1 1 )\nend\n')
start='devmap m2l1'
if num:
 source=r/['','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'][num]
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
cmd=['wait 1000',start,'wait 4000','finishloadingscreen','wait 1000','set ac_flinch_debug 1']
for state in [0,1,2,0]:
 cmd += ['echo FLINCH_PHASE_'+str(state),'set ac_player_flinch_mode '+str(state),'script player exec fixture/hit.scr','wait 80','screenshot silent','wait 900']
cmd+=['echo FLINCH_END','ac_ui_options','wait 500','ac_ui_report ac_scaling','screenshot silent','set ac_player_flinch_mode 1','writeconfig omconfig.cfg','echo FLINCH_DONE','quit']
(h/'test.cfg').write_text('\n'.join(cmd)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=0)
args=[str(b/'openmohaa.exe')]
for k,v in settings.items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=100)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'FLINCH_DONE' in log
errors=[l for l in log.splitlines() if any(x in l for x in ['Script Error','Unknown command','Invalid event'])];assert not errors,errors
rows=re.findall(r'AC_FLINCH enabled=(\d+) health=([\d.]+) alpha=([\d.]+) source=([^ ]+) camera=([^\r\n]+)',log)
assert rows
for state in ['0','1','2']:
 hits=[row for row in rows if row[0]==state and float(row[2])>0]
 assert hits,(state,rows[:5])
 assert any(any(abs(float(x))>0.01 for x in row[3].split(',')) for row in hits)
 if state=='0':assert all(all(float(x)==0 for x in row[4].split(',')) for row in hits),hits
 else:
  scale=0.2 if state=='1' else 1.0
  assert all(abs(float(y)-float(x)*scale)<0.0011 for row in hits for x,y in zip(row[3].split(','),row[4].split(',')))
assert 'playerFlinch' in log
assert 'seta ac_player_flinch_mode "1"' in (h/'configs/omconfig.cfg').read_text()
for f in (h/'screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
report=dict(game=a.game,feedback_samples=len(rows),off_camera_zero=True,reduced_exactly_20_percent=True,original_exactly_100_percent=True,red_blend_preserved=True,archived_preference_saved=True,errors=errors)
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
