"""Keep the real cinematic on screen for a bounded Computer Use inspection."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('game',choices=['SH','BT']);ap.add_argument('--run-id',required=True);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP05-r2';p=r/'profiles-local/CP05-r2'/a.run_id
n,f,movie={'SH':(1,'mainta','briefingt1.roq'),'BT':(2,'maintt','briefinge1.roq')}[a.game];h=p/f;h.mkdir(parents=True)
(h/'movie.cfg').write_text(f'cinematic {movie}\nwait 45000\necho AC_MOVIE_DONE\nquit\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','movie.cfg'],cwd=rt,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');report=dict(game=a.game,movie=movie,exit=proc.returncode,completed='AC_MOVIE_DONE' in log,engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),visual_inspection='See r2 visual-review.json; internal game screenshots precede the immediate cinematic draw')
(r/'checkpoints/CP05/r2'/(a.run_id+'.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
assert proc.returncode==0 and report['completed']
