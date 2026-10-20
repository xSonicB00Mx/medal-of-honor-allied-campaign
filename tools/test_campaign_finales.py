"""Native finale boundaries with seeded progress, not natural playthroughs."""
from pathlib import Path
import argparse, json, shutil, subprocess, time

ap=argparse.ArgumentParser(); ap.add_argument('run'); ap.add_argument('operation',type=int); ap.add_argument('--replay',action='store_true'); ap.add_argument('--baseline',action='store_true'); ap.add_argument('--installed',action='store_true'); args=ap.parse_args()
r=Path(__file__).resolve().parents[1]; rt=r/'runtime-local/CP08-r1'; p=r/'profiles-local/campaign-finales'/args.run
p.mkdir(parents=True,exist_ok=False)
ops=json.loads((r/'mod/campaign/missions.json').read_text())['operations']; op=ops[args.operation]
game=['AA','SH','BT'].index(op['source_game']); folders=['main','mainta','maintt']; h=p/folders[game]
for folder in folders:
 (p/folder/'probe').mkdir(parents=True)
 if not args.baseline and not args.installed:
  for package in (r/'generated-local/campaign-finales/packages'/folder).glob('*.pk3'): shutil.copy2(package,p/folder/package.name)
 (p/folder/'ac_context_ready.cfg').write_text('wait 1500\nac_progress_report\necho AC_FINALE_CHILD_READY\nquit\n')
completed=(1<<(args.operation+int(args.replay)))-1
(p/'ac_progress.dat').write_text(f'ACPROG1 {completed} {args.operation+int(args.replay)} -\n')
fixture={13:'waitthread maps/m6l3e.scr::roll_credits',11:'level.escaped = 1\nwaitthread maps/e3l4/outro.scr::RollTheCredits',14:'bsptransition briefing/briefingd1'}[args.operation]
(h/'probe/complete.scr').write_text('main:\n$player nodamage\n'+fixture+'\nend\n')
commands=['wait 4000','finishloadingscreen','set autopaused 0','script player exec probe/complete.scr','wait 9000','+attack','wait 500','-attack','wait 4500','ac_progress_report','echo AC_FINALE_PROBE_DONE']
if args.baseline: commands=['wait 4000','finishloadingscreen','echo AC_FINALE_BASELINE_DONE','quit']
(h/'test.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,autopaused=0,r_fullscreen=0,r_mode=-1,r_customwidth=960,r_customheight=540,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1,ac_operation=args.operation,ac_replay=int(args.replay),ac_expected_map=op['map_chain'][-1])
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.Popen(cmd+['+map',op['map_chain'][-1],'+exec','test.cfg'],cwd=rt)
deadline=time.monotonic()+55; logs=''; stopped=False
while time.monotonic()<deadline:
 time.sleep(.2)
 logs='\n'.join(f.read_text(encoding='latin1') for f in p.rglob('qconsole.log'))
 if args.replay and 'AC_REPLAY_COMPLETE' in logs:
  proc.terminate(); stopped=True; break
 if args.operation==14 and 'AC_MISSION_COMPLETE sh_berlin' in logs and 'trFMV::play(), playing debriefing.roq' in logs:
  proc.terminate(); stopped=True; break
 if proc.poll() is not None and (args.baseline or args.replay or 'AC_FINALE_CHILD_READY' in logs):break
else:
 proc.terminate(); stopped=True
proc.wait(timeout=5)
state=(p/'ac_progress.dat').read_text().split(); expected=completed if args.replay else completed|(1<<args.operation)
errors=[line for line in logs.splitlines() if any(s in line for s in ['Script Error','Unknown command','Invalid event'])]
events=[line for line in logs.splitlines() if ('] AC_' in line or 'AC_FINALE_CONTINUE' in line or 'maps/credits' in line or 'briefingd1' in line) and '.pk3' not in line]
report=dict(operation=op['id'],replay=args.replay,completed=int(state[1]),expected=expected,events=events,errors=errors,stopped=stopped)
if args.baseline:
 (p/'result.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report)); raise SystemExit(0)
baseline=r/'profiles-local/campaign-finales'/('baseline-'+str(args.operation))/'result.json'
known=json.loads(baseline.read_text())['errors'] if baseline.exists() else []
error_text=lambda lines: [line.split('Script Error :',1)[-1] for line in lines]
assert error_text(errors)==error_text(known),errors
report['baseline_errors_identical']=True
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
assert int(state[1])==expected
if args.operation!=14:
 assert 'AC_FINALE_CONTINUE '+op['source_game'] in logs
 assert ('AC_REPLAY_COMPLETE' if args.replay else 'AC_MISSION_COMPLETE') in logs
 assert 'maps/credits' not in logs
 if not args.replay: assert 'AC_FINALE_CHILD_READY' in logs
else:
 assert 'AC_MISSION_COMPLETE sh_berlin' in logs
 assert 'trFMV::play(), playing debriefing.roq' in logs
 # The debriefing-to-credits script is not replaced by this patch.
 from package_campaign_finales import effective
 _, ending=effective(['main','mainta'],'maps/briefing/briefingd1.scr')
 assert '$player stufftext "spmap credits"' in ending.decode('latin1')
