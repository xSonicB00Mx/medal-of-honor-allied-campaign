"""Native isolated tests for completed levels, replay boundaries and briefing playback."""
import argparse,hashlib,json,shutil,subprocess,time,zipfile,re
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('case',choices=['menu','replay','briefing','progress','save','locked','inspect']);a.add_argument('--operation',type=int,default=0);a.add_argument('--difficulty',type=int,default=2);a.add_argument('--state');a.add_argument('--backup');a.add_argument('--complete',action='store_true');a.add_argument('--width',type=int,default=1920);a.add_argument('--height',type=int,default=1080);a.add_argument('--campaign-skill',type=int,default=1);a.add_argument('--installed',action='store_true');args=a.parse_args()
ops=json.loads((R/'mod/campaign/missions.json').read_text())['operations']
levels=[(i,m) for i,o in enumerate(ops) for m in o['map_chain']]
rt=R/'runtime-local/CP08-r1';p=R/'profiles-local/level-replay'/args.run;assert not p.exists();p.mkdir(parents=True)
binary=rt if args.installed else p/'bin'
if not args.installed:
 binary.mkdir()
 for f in rt.glob('*.dll'):shutil.copy2(f,binary/f.name)
 shutil.copy2(R/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe',binary/'openmohaa.exe')
folders=['main','mainta','maintt'];op=args.operation;o=ops[op];game=['AA','SH','BT'].index(o['source_game']);index=levels.index((op,o['map_chain'][0]))
for folder in folders:
 h=p/folder;(h/'probe').mkdir(parents=True);(h/'save/omconfig').mkdir(parents=True)
 if not args.installed:shutil.copy2(R/'generated-local/widescreen/packages'/folder/'zzzzzz_AC_Widescreen.pk3',h/'zzzzzz_AC_Widescreen.pk3')
 (h/'save/omconfig/keep.sav').write_bytes(b'PRESERVE MAIN CAMPAIGN SAVE')
 (h/'save/omconfig/other.sav').write_bytes(b'PRESERVE OTHER CAMPAIGN SAVE')
 h.joinpath('probe/complete.scr').write_text(f'main:\n $player nodamage\n bsptransition {o["map_chain"][1] if len(o["map_chain"])>1 else o["completion_event"]["native_next"]}\nend\n')
state=f'ACPROG1 {(1<<op)-1} {op} keep\n'
if args.case in ['replay','save']:state=f'ACPROG1 {(1<<(op+1))-1} {op+1} keep\n'
if args.case=='menu':
 # Model the current user situation using valid copied metadata, never a user save write.
 state='ACPROG1 0 0 keep\n'
 (p/'main/save/omconfig/keep.acmeta').write_text(f'ACM2 0 {ops[0]["content_fingerprint"]} 0 m1l3a 0 0\n')
if args.complete:state='ACPROG1 32767 15 -\n'
if args.state is not None:state=args.state+'\n'
(p/'ac_progress.dat').write_text(state)
if args.backup is not None:(p/'ac_progress.dat.bak').write_text(args.backup+'\n')
(p/'main/ac_preferences.cfg').write_text(f'seta skill {args.campaign_skill}\nseta g_skill {args.campaign_skill}\n')
sentinels={f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('*/save/omconfig/*.sav')}
commands=['wait 1400']
settings=dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cheats=1,autopaused=0,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=args.width,r_customheight=args.height,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1)
start=[];stop='AC_TEST_DONE';force_stop=False
if args.case=='menu':
 commands+=['ac_progress_report','pushmenu main','set ui_signshader maplist_sign','wait 600','screenshot silent','ac_level_list','wait 600','screenshot silent','ac_level_list 0 0 2','wait 600','ac_ui_report ac_level_list','screenshot silent','echo AC_TEST_DONE','quit']
 if args.complete:commands=commands[:-2]+['ac_level_list 4 52 0','wait 600','screenshot silent','echo AC_TEST_DONE','quit']
elif args.case=='inspect':
 commands+=['ac_progress_report','ac_level_list','wait 600','screenshot silent','echo AC_TEST_DONE','quit']
elif args.case=='locked':
 commands+=['ac_level_replay 0 1','ac_level_list','wait 500','screenshot silent','ac_progress_report','echo AC_TEST_DONE','quit']
elif args.case=='briefing':
 commands+=['ac_briefing'];stop='AC_REPLAY_RETURN_MAIN';force_stop=True
 for folder in folders:
  (p/folder/'ac_context_ready.cfg').write_text('wait 4500\nfinishloadingscreen\nac_progress_report\n+attack\nwait 500\n-attack\n')
elif args.case in ['replay','save']:
 commands+=[f'ac_level_replay {index} {args.difficulty}'];stop='AC_REPLAY_RETURN_MAIN' if args.case=='replay' else 'AC_TEST_DONE';force_stop=args.case=='replay'
 for folder in folders:
  probe=['wait 5000','finishloadingscreen','ac_progress_report','savegame other','wait 600','savegame replay_test','wait 500','loadgame replay_test','wait 2500','finishloadingscreen','ac_progress_report']
  if args.case=='replay':probe+=['script player exec probe/complete.scr','wait 6500','+attack','wait 500','-attack']
  else:probe+=['echo AC_TEST_DONE','quit']
  (p/folder/'ac_context_ready.cfg').write_text('\n'.join(probe)+'\n')
else:
 settings.update(developer=1,com_target_game=game,ac_operation=op,ac_expected_map=o['map_chain'][0]);start=['+map',o['map_chain'][0]]
 commands=['wait 5000','finishloadingscreen','script player exec probe/complete.scr','wait 6500','+attack','wait 500','-attack'];stop='AC_LEVEL_COMPLETE';force_stop=True
# Keep parent command in main regardless of destination; child reads its context hook.
(p/folders[settings['com_target_game']]/'probe.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(binary/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.Popen(cmd+start+['+exec','probe.cfg'],cwd=rt)
events=[];seen=set();childids=set();beg=time.monotonic();done=False
while time.monotonic()-beg<240:
 time.sleep(.15)
 for log in p.glob('*/qconsole.log'):
  text=log.read_text(encoding='latin1')
  for line in text.splitlines():
   if 'AC_' in line or 'Script Error' in line or 'Unknown command' in line or 'Playing video' in line or 'command not available' in line or 'Bad or missing cinematic' in line or 'trFMV::play()' in line:
    if line not in seen:seen.add(line);events.append(line)
   match=re.search(r'AC_CONTEXT_RESTART.*child=(\d+)',line)
   if match:childids.add(int(match[1]))
 if any(stop in line for line in events):done=True;time.sleep(2);break
 if proc.poll() is not None and not childids:break
if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
# Only terminate exact test children created by this isolated run.
if childids:
 subprocess.run(['powershell','-NoProfile','-Command',f'Get-Process -Id {",".join(map(str,childids))} -ErrorAction SilentlyContinue | Stop-Process'],capture_output=True)
after=(p/'ac_progress.dat').read_text()
images=[]
for f in p.glob('*/screenshots/*.tga'):
 Image.open(f).save(f.with_suffix('.png'));images.append(f.with_suffix('.png').relative_to(R).as_posix())
report=dict(run=args.run,case=args.case,operation=o['id'],done=done,events=events,state_before=state,state_after=after,images=images,scope='Isolated seeded profile; synthetic native completion, not a natural playthrough.',engine_sha256=hashlib.sha256((binary/'openmohaa.exe').read_bytes()).hexdigest())
(R/'generated-local'/f'level-replay-{args.run}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
assert done
assert not any('Script Error' in x or 'Unknown command' in x or 'command not available' in x or 'Bad or missing cinematic' in x for x in events)
assert sentinels=={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in sentinels}
if args.case!='progress':assert after==state
if args.case=='menu':
 ui=(p/'main/ui/ac_level_list.urc').read_text();assert ('name "level_52"' in ui and '53 completed levels' in ui) if args.complete else (all(f'name "level_{i}"' in ui for i in range(3)) and 'name "level_3"' not in ui)
 assert ('ac_level_replay 52 0' if args.complete else 'ac_level_replay 0 2') in ui
if args.case=='locked':assert any('AC_LEVEL_LOCKED' in e for e in events)
if args.case in ['replay','save']:
 assert any(f'skill={args.difficulty}' in e and 'AC_LEVEL_PROGRESS' in e for e in events)
 assert any('AC_SAVE_PROTECTED campaign save' in e for e in events)
 assert any('replay=2' in e for e in events)
 prefs=(p/'main/ac_preferences.cfg').read_text();assert re.search(rf'seta skill \"?{args.campaign_skill}\"?(?:\n|$)',prefs)
if args.case=='replay':assert any(f'AC_REPLAY_RETURN_MAIN skill={args.campaign_skill}' in e for e in events)
if args.case=='briefing':assert any(('AC_BRIEFING_VIDEO '+o['briefing_replay'].split('/')[-1]+'.roq' if game else 'AC_BRIEFING_STARTED '+o['briefing_replay']) in e for e in events)
if args.case=='progress':assert int(after.split()[4+index//32])&(1<<(index%32))

report['passed']=True
(R/'generated-local'/f'level-replay-{args.run}.json').write_text(json.dumps(report,indent=2)+'\n')
