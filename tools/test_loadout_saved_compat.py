"""Load an earlier isolated save with the current build, without editing its source."""
from pathlib import Path
import argparse,json,shutil,subprocess

a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('source_profile');args=a.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1'
source=r/'profiles-local/loadout'/args.source_profile
p=r/'profiles-local/loadout'/args.run;p.mkdir(parents=True,exist_ok=False)
shutil.copy2(source/'ac_progress.dat',p/'ac_progress.dat')
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
for folder in ['main','mainta','maintt']:
 h=p/folder;h.mkdir()
 for f in (r/'generated-local/loadout/packages'/folder).glob('*.pk3'):shutil.copy2(f,h/f.name)
save=p/'maintt/save/omconfig';save.mkdir(parents=True)
for f in (source/'maintt/save/omconfig').glob('loadout_lifecycle.*'):shutil.copy2(f,save/f.name)
(p/'maintt/probe.cfg').write_text('set autopaused 0\nloadgame loadout_lifecycle\nwait 6000\nfinishloadingscreen\nac_progress_report\necho AC_OLD_SAVE_LOADED\nquit\n')
settings=dict(com_target_game=2,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1)
cmd=[str(b/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=60)
log=(p/'maintt/qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AC_SAVE_ACCEPT context=2 map=e3l3' in log and 'AC_OLD_SAVE_LOADED' in log
assert (p/'ac_progress.dat').read_bytes()==(source/'ac_progress.dat').read_bytes()
report=dict(old_save_loaded=True,exit=proc.returncode,progress_unchanged=True)
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
