"""Test a real internal-restart pair with independent source/destination saves."""
import argparse,json,subprocess,time,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('source',type=int);ap.add_argument('target',type=int);a=ap.parse_args()
rt=R/'runtime-local/CP06-r1';p=R/'profiles-local/CP06-r1'/a.run;assert not p.exists()
folders=['main','mainta','maintt'];maps=['m1l2a','t1l2','e2l2']
for f in folders:(p/f).mkdir(parents=True)
source=['wait 4500','savegame cp06_before','wait 700','set cg_fov 90',f'ac_context {a.target} {maps[a.target]}']
target=['wait 4500','which global/ai.scr','which maps/'+maps[a.target]+'.scr','savegame cp06_after','wait 1000','loadgame cp06_after','wait 4500','finishloadingscreen','wait 800','cg_fov','ac_campaign','wait 800','ac_ui_report ac_campaign_aa1','screenshot','echo AC_CONTEXT_TEST_DONE','quit']
(p/folders[a.source]/'probe.cfg').write_text('\n'.join(source)+'\n')
(p/folders[a.target]/'ac_context_ready.cfg').write_text('\n'.join(target)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=a.source,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,cl_playintro=0,ac_campaign_mode=1,com_maxfps=60,com_maxfpsUnfocused=60).items():cmd+=['+set',k,str(v)]
t=time.monotonic();proc=subprocess.Popen(cmd+['+map',maps[a.source],'+exec','probe.cfg'],cwd=rt)
logpath=p/folders[a.target]/'qconsole.log';logs=''
while time.monotonic()-t<65:
    time.sleep(.5)
    if logpath.exists():
        logs=logpath.read_text(encoding='latin1')
        if 'AC_CONTEXT_TEST_DONE' in logs and 'Client Shutdown' in logs:break
proc.wait(timeout=5)
sourceLog=(p/folders[a.source]/'qconsole.log').read_text(encoding='latin1')
result=dict(source=a.source,target=a.target,exit=proc.returncode,seconds=time.monotonic()-t,completed='AC_CONTEXT_TEST_DONE' in logs,source_active=(p/folders[a.source]/'save/omconfig/cp06_before.sav').exists(),target_active=(p/folders[a.target]/'save/omconfig/cp06_after.sav').exists(),events=[x for x in sourceLog.splitlines() if 'AC_CONTEXT' in x],saves=[x.relative_to(p).as_posix() for x in p.rglob('*.sav')],providers=[x.replace(str(rt),'$RUNTIME') for x in logs.splitlines() if 'found in' in x],errors=[x for x in logs.splitlines() if 'Script Error :' in x],engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest())
out=R/'checkpoints/CP06';out.mkdir(parents=True,exist_ok=True);(out/(a.run+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
assert result['completed'] and result['source_active'] and result['target_active'] and any('cp06_after.sav' in x for x in result['saves'])
