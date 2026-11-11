"""Compare development-mode start diagnostics with the pre-progression CP6 engine."""
import json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP06-r1';out=[]
for g,m in [(2,'e1l2'),(2,'e1l4'),(2,'e2l3'),(2,'e3l2'),(2,'e3l3'),(2,'e3l4'),(1,'t1l3')]:
 p=R/'profiles-local/CP07-r1'/('baseline-'+m);h=p/['main','mainta','maintt'][g];assert not p.exists();h.mkdir(parents=True)
 (h/'probe.cfg').write_text('wait 3500\nfinishloadingscreen\ntoggleconsole\nwait 10000\nquit\n')
 cmd=[str(rt/'openmohaa.exe')]
 for k,v in dict(com_target_game=g,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,autopaused=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1).items():cmd+=['+set',k,str(v)]
 proc=subprocess.run(cmd+['+map',m,'+exec','probe.cfg'],cwd=rt,timeout=40)
 log=(h/'qconsole.log').read_text(encoding='latin1');out.append(dict(map=m,exit=proc.returncode,errors=[x for x in log.splitlines() if 'Script Error :' in x]));print(m,len(out[-1]['errors']),flush=True)
(R/'checkpoints/CP07/baseline-diagnostics.json').write_text(json.dumps(dict(scope='Direct starts without progression or synthetic completion; CP6 baseline in developer mode',engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cases=out),indent=2)+'\n')
