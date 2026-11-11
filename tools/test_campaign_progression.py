"""Synthetic native-intermission boundary tests, never a natural playthrough claim."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('operation',type=int);ap.add_argument('--case',choices=['success','replay','rawmap','failed','save','credits_guard','credits_success'],default='success');a=ap.parse_args()
ops=json.loads((R/'mod/campaign/missions.json').read_text())['operations'];o=ops[a.operation];g=['AA','SH','BT'].index(o['source_game']);folders=['main','mainta','maintt'];rt=R/'runtime-local/CP07-r1';p=R/'profiles-local/CP07-r1'/a.run;assert not p.exists()
for f in folders:(p/f/'probe').mkdir(parents=True)
h=p/folders[g];completed=(1<<a.operation)-1
if a.case=='replay':completed=(1<<(a.operation+1))-1
(p/'ac_progress.dat').write_text(f'ACPROG1 {completed} {a.operation if a.case!="replay" else a.operation+1} -\n')
current=o['map_chain'][-1];nxt=o['completion_event']['native_next']
fixture=f'main:\n    $player nodamage\n    bsptransition {nxt}\nend\n'
if a.case=='failed':fixture='main:\n    missionfailed\nend\n'
if a.case in ['credits_guard','credits_success']:
 flag='level.escaped' if g==2 else 'level.end_level'
 fixture=f'main:\n    $player nodamage\n    level.bborder = 230\n    level.tborder = 231\n    level.finalslide = 232\n    {flag} = {int(a.case=="credits_success")}\n    waitthread global/credits.scr::credits_done\nend\n'
(h/'probe/complete.scr').write_text(fixture)
commands=['wait 3500','finishloadingscreen','set developer 1','toggleconsole','wait 500','screenshot','ac_progress_report']
if a.case=='rawmap':commands+=['gamemap '+nxt,'wait 4000','ac_progress_report','echo AC_BOUNDARY_DONE','quit']
elif a.case=='save':commands+=['savegame campaign_test','wait 800','loadgame campaign_test','wait 3500','ac_progress_report','echo AC_BOUNDARY_DONE','quit']
else:commands+=['script player exec probe/complete.scr','wait 12000' if a.case.startswith('credits') else 'wait 6000','+attack','wait 500','-attack','wait 1500','ac_progress_report','echo AC_BOUNDARY_DONE','quit']
if a.case in ['success','replay','credits_success']: commands=commands[:-1]
(h/'probe.cfg').write_text('\n'.join(commands)+'\n')
for f in folders:(p/f/'ac_context_ready.cfg').write_text('wait 2500\nac_progress_report\necho AC_CHILD_READY\nquit\n')
cmd=[str(rt/'openmohaa.exe')]
settings=dict(com_target_game=g,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,autopaused=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1,ac_operation=a.operation,ac_replay=int(a.case=='replay'),ac_expected_map=current)
for k,v in settings.items():cmd+=['+set',k,str(v)]
t=time.monotonic();proc=subprocess.Popen(cmd+['+map',current,'+exec','probe.cfg'],cwd=rt);seen=set();evidence=[];stopped=False
while time.monotonic()-t<65:
    time.sleep(.4)
    logs='\n'.join(x.read_text(encoding='latin1') for x in p.rglob('qconsole.log'))
    for line in logs.splitlines():
        if ('AC_' in line or 'Script Error :' in line or 'command not available' in line) and line not in seen:seen.add(line);evidence.append(line)
    if a.case=='replay' and any('AC_REPLAY_COMPLETE' in x for x in evidence):
        time.sleep(2);proc.terminate();stopped=True;break
    if a.case=='success' and a.operation==14 and any('AC_MISSION_COMPLETE' in x for x in evidence):
        time.sleep(3);proc.terminate();stopped=True;break
    if proc.poll() is not None:
        if a.case not in ['success','credits_success'] or any('AC_CHILD_READY' in x for x in evidence):break
if proc.poll() is None: proc.terminate()
proc.wait(timeout=5)
state=(p/'ac_progress.dat').read_text().split();actual=int(state[1]);expected=completed | (1<<a.operation) if a.case in ['success','credits_success'] else completed
result=dict(operation=o['id'],case=a.case,expected_completed=expected,actual_completed=actual,pass_state=actual==expected,exit=proc.returncode,test_stopped_after_event=stopped,events=evidence,errors=[x for x in evidence if 'Script Error :' in x or 'command not available' in x],scope='Seeded test profile and synthetic native intermission/negative case; not natural mission completion',engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest())
(R/'checkpoints/CP07'/(a.run+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
assert result['pass_state'] and (proc.returncode==0 or stopped) and not result['errors']
if a.case=='success':assert any('AC_MISSION_COMPLETE' in x for x in evidence)
if a.case=='replay':assert any('AC_REPLAY_COMPLETE' in x for x in evidence)
