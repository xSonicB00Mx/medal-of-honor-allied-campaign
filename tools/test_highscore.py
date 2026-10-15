"""Native highscore verification with isolated profiles and scripted native completion.

Combat uses real weapon discharges and native grenade explosions, not score commands.
Never reads or writes the active user profile.
"""
import argparse, hashlib, json, re, shutil, subprocess, time
from pathlib import Path
from PIL import Image

a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('--case',choices=['combat','empty','abort','death','restart','inspect','campaign'],default='combat')
a.add_argument('--operation',type=int,default=1);a.add_argument('--difficulty',type=int,default=1)
a.add_argument('--baseline-diagnostics',type=Path);a.add_argument('--direct',action='store_true');a.add_argument('--scores',type=Path);a.add_argument('--corrupt',action='store_true');a.add_argument('--backup',type=Path)
a.add_argument('--width',type=int,default=1920);a.add_argument('--height',type=int,default=1080);a.add_argument('--installed',action='store_true');args=a.parse_args()
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP08-r1';p=R/'profiles-local/highscore'/args.run
assert not p.exists();p.mkdir(parents=True)
ops=json.loads((R/'mod/campaign/missions.json').read_text())['operations'];o=ops[args.operation]
levels=[(i,m) for i,o in enumerate(ops) for m in o['map_chain']];index=levels.index((args.operation,o['map_chain'][0]))
folder=['main','mainta','maintt'][['AA','SH','BT'].index(o['source_game'])]
binary=rt if args.installed else p/'bin'
if not args.installed:
 binary.mkdir()
 for f in rt.glob('*.dll'):shutil.copy2(f,binary/f.name)
 for name in ['openmohaa.exe','game.dll']:shutil.copy2(R/'build-local/cp00-r3/RelWithDebInfo'/name,binary/name)
state='ACPROG1 32767 15 keep\n';(p/'ac_progress.dat').write_text(state)
if args.scores:shutil.copy2(args.scores,p/'ac_scores.dat')
if args.corrupt:(p/'ac_scores.dat').write_text('CORRUPT - PRESERVE ME')
if args.backup:shutil.copy2(args.backup,p/'ac_scores.dat.bak')
before=(p/'ac_scores.dat').read_bytes() if (p/'ac_scores.dat').exists() else None
for f in ['main','mainta','maintt']:
 h=p/f;(h/'probe').mkdir(parents=True);(h/'save/omconfig').mkdir(parents=True)
 (h/'save/omconfig/keep.sav').write_bytes(b'CAMPAIGN SAVE SENTINEL')
 shutil.copy2(R/'tools/highscore_fixture.scr',h/'probe/combat.scr')
 (h/'probe/complete.scr').write_text(f'main:\n $player nodamage\n bsptransition {o["map_chain"][1] if len(o["map_chain"])>1 else o["completion_event"]["native_next"]}\nend\n')
 (h/'probe/die.scr').write_text('main:\n $player takedamage\n $player kill\nend\n')
 commands=['wait 5000','finishloadingscreen','set developer 1','ac_score_report']
 if args.case=='combat':commands+=['script player exec probe/combat.scr','wait 6500','ac_score_report']
 if args.case in ['combat','empty']:
  commands+=['savegame keep','wait 200','screenshot silent','popmenu 0','savegame forbidden','wait 200','popmenu 0','autosavegame','loadgame keep','wait 200','popmenu 0','loadlastgame','wait 200','popmenu 0','ac_load 0 keep','wait 200','popmenu 0','pushmenu loadsave','wait 200','popmenu 0','ac_score_report','script player exec probe/complete.scr','wait 7000','+attack','wait 300','-attack','wait 1200','ac_ui_report ac_score_results','screenshot silent','ac_level_list 0 0 1','wait 600','screenshot silent','echo AC_TEST_DONE','quit']
 elif args.case=='abort':commands+=['script player exec probe/combat.scr','wait 6500','ac_score_report','disconnect','wait 700','ac_level_list','wait 400','echo AC_TEST_DONE','quit']
 elif args.case in ['death','restart']:
  commands+=['script player exec probe/die.scr' if args.case=='death' else 'restart','wait 1800','screenshot silent','echo AC_TEST_DONE','quit']
 elif args.case=='campaign':commands+=['savegame regular','wait 600','loadgame regular','wait 2500','finishloadingscreen','ac_progress_report','echo AC_TEST_DONE','quit']
 (h/'ac_context_ready.cfg').write_text('\n'.join(commands)+'\n')
(p/'main/ac_preferences.cfg').write_text('seta skill 1\nseta g_skill 1\n')
start=['wait 1000',f'ac_level_replay {index} {args.difficulty}']
if args.case=='inspect':start=['wait 1000','ac_level_list 0 0 1','wait 500','screenshot silent','ac_level_list 4 52 2','wait 500','screenshot silent','echo AC_TEST_DONE','quit']
settings=dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,autopaused=0,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=args.width,r_customheight=args.height,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1)
if args.direct:
 settings.update(developer=0,com_target_game=['AA','SH','BT'].index(o['source_game']),ac_operation=args.operation,ac_expected_map=o['map_chain'][0],ac_replay=2,ac_level_skill=args.difficulty,ac_campaign_skill=1,ac_campaign_g_skill=1)
 start=['wait 1000','difficulty'+['Easy','Medium','Hard'][args.difficulty],f'devmap {o["map_chain"][0]}','exec ac_context_ready.cfg']
if args.case=='campaign':
 settings.update(ac_replay=0,ac_operation=-1,ac_expected_map='')
 settings['com_target_game']=['AA','SH','BT'].index(o['source_game']);start=['wait 1000',f'map {o["map_chain"][0]}','exec ac_context_ready.cfg']
(p/['main','mainta','maintt'][settings['com_target_game']]/'probe.cfg').write_text('\n'.join(start)+'\n')
cmd=[str(binary/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.Popen(cmd+['+exec','probe.cfg'],cwd=rt);children=set();beg=time.monotonic();text='';done=False
try:
 while time.monotonic()-beg<95:
  time.sleep(.2);text='\n'.join(f.read_text(encoding='latin1') for f in p.glob('*/qconsole.log'))
  children.update(map(int,re.findall(r'AC_CONTEXT_RESTART[^\n]*child=(\d+)',text)))
  if 'AC_TEST_DONE' in text:done=True;time.sleep(1);break
  if proc.poll() is not None and not children:break
finally:
 if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
 if children:subprocess.run(['powershell','-NoProfile','-Command',f'Get-Process -Id {",".join(map(str,children))} -ErrorAction SilentlyContinue | Stop-Process'],capture_output=True)
images=[]
for f in p.glob('*/screenshots/*.tga'):
 Image.open(f).save(f.with_suffix('.png'));images.append(f.with_suffix('.png').relative_to(R).as_posix())
events=[s for s in text.splitlines() if 'AC_' in s or 'CP00_PLACEMENT' in s]
errors=[s for s in text.splitlines() if any(e in s for e in ['Script Error','Unknown command','Invalid event','compile error','command not available'])]
known=json.loads(args.baseline_diagnostics.read_text())['errors'] if args.baseline_diagnostics else []
unexpected=[e for e in errors if e.split('Script Error : ',1)[-1] not in known]
after=(p/'ac_scores.dat').read_bytes() if (p/'ac_scores.dat').exists() else None
result=dict(run=args.run,case=args.case,operation=args.operation,difficulty=args.difficulty,done=done,events=events,errors=errors,unexpected_errors=unexpected,images=images,records_changed=before!=after,binaries={n:hashlib.sha256((binary/n).read_bytes()).hexdigest() for n in ['openmohaa.exe','game.dll']})
report=R/'generated-local'/f'highscore-{args.run}.json';report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
assert done and not unexpected
assert (p/'ac_progress.dat').read_text()==state
for f in ['main','mainta','maintt']:assert (p/f/'save/omconfig/keep.sav').read_bytes()==b'CAMPAIGN SAVE SENTINEL'
if args.case in ['combat','empty']:
 assert 'AC_SCORE_COMPLETE' in text and 'AC_SCORE_SAVE_LOAD_BLOCKED' in text
 assert not any(p.glob('*/save/omconfig/forbidden.sav'))
 ui=(p/folder/'ui/ac_score_results.urc').read_text();assert 'FINAL SCORE' in ui and 'aa-statsscreen_game' in ui
 if args.corrupt and not args.backup:assert after==before and 'SCORE NOT SAVED' in ui
 else:assert after is not None
if args.case=='combat':
 assert 'AC_FIXTURE_DONE' in text
 m=re.search(r'AC_SCORE_COMPLETE level=\d+ skill=\d+ kills=(\d+) heads=(\d+) shots=(\d+) hits=(\d+) grenadeBonus=(\d+) friendlyDamage=(\d+) score=(\d+)',text)
 k,h,s,hits,g,ff,total=map(int,m.groups());base=100*k+50*h+g
 assert total==max(0,base+(base*hits//(2*s) if s else 0)-2*ff)
 assert k>=6 and h>=1 and s==5 and hits>=1 and g>=800 and ff>0,(k,h,s,hits,g,ff)
if args.case in ['abort','death','restart']:assert after==before and 'AC_SCORE_COMPLETE' not in text
if args.case=='campaign':assert (p/folder/'save/omconfig/regular.sav').exists() and 'AC_SCORE_SAVE_LOAD_BLOCKED' not in text
result['passed']=True;report.write_text(json.dumps(result,indent=2)+'\n')
