"""Replay and optional entries must not overwrite the main campaign resume slot."""
import json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP08-r1';results=[]
for name,map,op,replay in [('replay-protection','m1l1',0,1),('optional-protection','m4l0',-1,0)]:
 p=R/'profiles-local/CP08-r1'/name;h=p/'main';assert not p.exists();(h/'save/omconfig').mkdir(parents=True)
 state='ACPROG1 1 1 protected_main\n';(p/'ac_progress.dat').write_text(state);target=h/'save/omconfig/protected_main.sav';target.write_bytes(b'protected main save sentinel')
 (h/'probe.cfg').write_text('wait 4000\nfinishloadingscreen\nsavegame protected_main\nwait 800\nac_progress_report\nquit\n')
 cmd=[str(rt/'openmohaa.exe')]
 for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,autopaused=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1,ac_operation=op,ac_replay=replay,ac_expected_map=map).items():cmd+=['+set',k,str(v)]
 proc=subprocess.run(cmd+['+map',map,'+exec','probe.cfg'],cwd=rt,timeout=40);log=(h/'qconsole.log').read_text(encoding='latin1')
 result=dict(case=name,exit=proc.returncode,progress_unchanged=(p/'ac_progress.dat').read_text()==state,save_unchanged=target.read_bytes()==b'protected main save sentinel',events=[x for x in log.splitlines() if '] AC_' in x or 'AC_SAVE_PROTECTED' in x]);results.append(result)
 assert proc.returncode==0 and result['progress_unchanged'] and result['save_unchanged'] and 'AC_SAVE_PROTECTED' in log
(R/'checkpoints/CP08/save-protection.json').write_text(json.dumps(dict(engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cases=results),indent=2)+'\n');print('Replay and optional entry preserve progress and main resume bytes.')
