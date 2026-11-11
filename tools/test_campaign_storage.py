"""Real engine persistence/recovery tests in disposable profiles."""
import json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP07-r1';out=[]
def run(name,seed=None,backup=None,commands=None,initial=None):
 p=R/'profiles-local/CP07-r1'/name;assert not p.exists();h=p/'main';h.mkdir(parents=True)
 if seed is not None:(p/'ac_progress.dat').write_text(seed)
 if backup is not None:(p/'ac_progress.dat.bak').write_text(backup)
 (p/'ac_progress.dat.tmp').write_text('interrupted incomplete write')
 (h/'probe.cfg').write_text('\n'.join(commands or ['wait 600','ac_progress_report','ac_mission 14','ac_progress_report','ac_campaign','wait 600','ac_ui_report ac_campaign_operations','screenshot','quit'])+'\n')
 cmd=[str(rt/'openmohaa.exe')]
 for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1).items():cmd+=['+set',k,str(v)]
 proc=subprocess.run(cmd+(initial or [])+['+exec','probe.cfg'],cwd=rt,timeout=50)
 log=(h/'qconsole.log').read_text(encoding='latin1');result=dict(name=name,exit=proc.returncode,events=[x for x in log.splitlines() if '] AC_' in x],state=(p/'ac_progress.dat').read_text() if (p/'ac_progress.dat').exists() else None,errors=[x for x in log.splitlines() if 'Script Error :' in x]);out.append(result);return log,result
log,r=run('storage-fresh');assert 'completed=0 resume=0' in log and 'AC_MISSION_LOCKED' in log
log,r=run('storage-committed','ACPROG1 7 3 -\n');assert 'completed=7 resume=3' in log
log,r=run('storage-corrupt-main','broken','ACPROG1 7 3 -\n');assert 'AC_PROGRESS_RECOVERED' in log and r['state']=='broken'
log,r=run('storage-missing-main',None,'ACPROG1 7 3 -\n');assert 'AC_PROGRESS_RECOVERED' in log
log,r=run('storage-corrupt-both','broken','broken');assert 'AC_PROGRESS_ERROR' in log and r['state']=='broken'
log,r=run('storage-invalid-resume','ACPROG1 3 14 -\n');assert 'AC_PROGRESS_ERROR' in log
(R/'checkpoints/CP07/storage.json').write_text(json.dumps(dict(engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cases=out),indent=2)+'\n');print('Six native storage/recovery cases passed.')
