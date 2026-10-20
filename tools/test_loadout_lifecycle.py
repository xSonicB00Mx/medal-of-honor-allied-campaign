"""Exercise real Operations/score commands, child process, save and default gates.

Seeded isolated progress is a boundary test, not a natural mission playthrough.
"""
from pathlib import Path
from collections import Counter
import argparse,json,shutil,subprocess,time,re,zipfile

a=argparse.ArgumentParser()
a.add_argument('run')
a.add_argument('case',choices=['replay','new','score','default','locked'])
a.add_argument('--game',type=int,default=0,choices=[0,1,2])
a.add_argument('--native-resources',action='store_true',help='Default-equipment baseline without the additive weapon packages')
a.add_argument('--baseline-report',type=Path,help='Recorded native baseline; retain matching warnings and reject new errors')
args=a.parse_args()
assert not args.native_resources or args.case=='default'
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1'
p=r/'profiles-local/loadout'/args.run;p.mkdir(parents=True,exist_ok=False)
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
folders=['main','mainta','maintt'];op,levelmap,index=[(1,'m2l1',6),(14,'t3l1',51),(6,'e3l3',20)][args.game]
completed=(1<<(op+1))-1 if args.case in ['replay','score','default'] else (1<<op)-1
if args.case=='locked':completed=0
state=f'ACPROG1 {completed} {completed.bit_count()} keep\n';(p/'ac_progress.dat').write_text(state)
for folder in folders:
 h=p/folder;(h/'probe').mkdir(parents=True);(h/'save/omconfig').mkdir(parents=True)
 (h/'custom.cfg').write_text('set cheats 1\n')
 (h/'save/omconfig/keep.sav').write_bytes(b'PRESERVE USER SAVE')
 if not args.native_resources:
  for f in (r/'generated-local/loadout/packages'/folder).glob('*.pk3'):shutil.copy2(f,h/f.name)
 else:
  # The candidate selects the replay statemap even with DEFAULT. Its BT map is
  # byte-identical to the native BT table; leave every other native asset intact.
  (h/'global').mkdir()
  with zipfile.ZipFile(next((r/'generated-local/loadout/packages/maintt').glob('*.pk3'))) as z:
   for part in ['legs','torso']:
    n=f'global/ac_loadout_{part}.st';(h/n).write_bytes(z.read(n))
 (h/'probe/ready.scr').write_text('main:\n $player nodamage\n $player give models/weapons/thompsonsmg.tik\n $player use models/weapons/thompsonsmg.tik\nend\n')
 commands=['set autopaused 0','wait 3000','finishloadingscreen']
 if args.case!='score' and args.game!=2:commands += [f'map {levelmap}','wait 4000','finishloadingscreen']
 commands += ['script player skipcinematic','wait 3000','script player exec probe/ready.scr','wait 30000' if args.game else 'wait 5000','ac_progress_report','ac_loadout_authorized','echo AC_INITIAL','script player state']
 if args.case in ['replay','default']:
  commands += ['savegame loadout_lifecycle','wait 700','loadgame loadout_lifecycle','wait 4000','finishloadingscreen','echo AC_RESTORED','script player state']
 commands += ['writeconfig loadout_received','echo AC_LIFECYCLE_DONE','quit']
 (h/'ac_context_ready.cfg').write_text('\n'.join(commands)+'\n')
initial=['wait 800','ac_loadout select 2 30']
if args.case=='default':initial+=['ac_loadout default']
initial += [f'ac_level_replay {index} 1' if args.case=='score' else f'ac_mission {op}']
if args.case=='locked':initial+=['wait 500','ac_loadout_authorized','echo AC_LIFECYCLE_DONE','quit']
(p/'main/initial.cfg').write_text('\n'.join(initial)+'\n')
settings=dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1)
cmd=[str(b/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.Popen(cmd+['+exec','initial.cfg'],cwd=rt)
deadline=time.monotonic()+90;children=set();done=False
while time.monotonic()<deadline:
 time.sleep(.2)
 logs='\n'.join(f.read_text(encoding='latin1') for f in p.glob('*/qconsole.log'))
 children.update(map(int,re.findall(r'AC_CONTEXT_RESTART.*child=(\d+)',logs)))
 if 'AC_LIFECYCLE_DONE' in logs:done=True;time.sleep(1);break
 if proc.poll() is not None and not children:break
if not done:
 if proc.poll() is None:proc.terminate()
 if children:subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Id '+','.join(map(str,children))+' -ErrorAction SilentlyContinue | Stop-Process'],capture_output=True)
 raise AssertionError('Lifecycle did not finish')
proc.wait(timeout=10)
target=(p/(folders[args.game] if args.case!='locked' else 'main')/'qconsole.log').read_text(encoding='latin1')
applied=re.findall(r'AC_LOADOUT_APPLIED[^\n]+',target)
models=re.findall(r'AC_WEAPON_STATE model=(\S+)',target)
after=(p/'ac_progress.dat').read_text()
if args.case=='new':assert after.split()[1:3]==state.split()[1:3]
else:assert after==state
for folder in folders:assert (p/folder/'save/omconfig/keep.sav').read_bytes()==b'PRESERVE USER SAVE'
if args.case=='replay':
 assert len(applied)==1 and 'models/weapons/it_w_moschetto.tik' in models,(applied,models)
 restored=target.split('AC_RESTORED')[-1]
 assert 'model=models/weapons/it_w_moschetto.tik' in restored
elif args.case=='default':assert not any('AC_LOADOUT_GIVE' in x for x in target.splitlines()) and 'models/weapons/it_w_moschetto.tik' not in models
else:assert not applied and 'models/weapons/it_w_moschetto.tik' not in models
if args.case=='locked':assert 'AC_MISSION_LOCKED' in target and not children
prefs=(p/'main/ac_preferences.cfg').read_text()
assert re.search(r'seta ac_loadout_2 "'+('0' if args.case=='default' else '30')+'"',prefs)
errors=[x for x in target.splitlines() if 'Script Error' in x or 'Unknown command' in x or 'AC_LOADOUT_ERROR' in x]
unexpected=errors
if args.baseline_report:
 baseline=json.loads(args.baseline_report.read_text());assert baseline['case']=='default' and baseline['game']==args.game
 normalize=lambda s:re.sub(r'^\[[^\]]*\]\s*','',s)
 known=Counter(normalize(e) for e in baseline['errors'])
 unexpected=[]
 for e in errors:
  text=normalize(e)
  if known[text]>0:known[text]-=1
  else:unexpected.append(e)
report=dict(case=args.case,game=args.game,passed=not unexpected,errors=errors,unexpected_errors=unexpected,native_resources=args.native_resources,applied=applied,child_restarts=len(children),progress_and_save_unchanged=True,preference_persisted=True)
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
assert not unexpected,unexpected
