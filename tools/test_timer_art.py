"""Exercise native stopwatch and fuse events in isolated UHD profiles."""
from pathlib import Path
import argparse,json,shutil,subprocess
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--installed',action='store_true');args=ap.parse_args()
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/timers'/args.run;home=p/folder;(home/'probe').mkdir(parents=True,exist_ok=False)
if not args.installed:
    shutil.copy2(root/'generated-local/hud-upscale/timers/packages'/folder/'zzzzzzzz_AC_Timers.pk3',home)
commands=['wait 1000','devmap '+['m2l1','t1l3','e3l1'][num],'wait 6000','finishloadingscreen','set ac_hud_scale 1.66','set developer 0','wait '+('30000' if num==2 else '5000')]
labels=[]
def event(name,duration,kind,waits):
    (home/'probe'/f'{name}.scr').write_text(f'main:\n $player nodamage\n $player stopwatch {duration} {kind}\nend\n')
    commands.append(f'script player exec probe/{name}.scr')
    for wait,label in waits:
        commands.extend([f'wait {wait}','ui_stopwatch','screenshot silent']);labels.append(label)
for duration in [46,31,16]:event(f'watch{duration}',duration,0,[(1000,f'watch approximately {duration-1}s')])
event('watchend',1,0,[(150,'watch near zero'),(1500,'watch expired')])
if num:
    event('fuse',5,1,[(300,'lit fuse long'),(2200,'lit fuse half'),(3000,'lit fuse expired')])
    event('wet',3,2,[(300,'wet fuse with target'),(1500,'wet fuse fixed length'),(1600,'wet fuse expired')])
commands+=['echo AC_TIMERS_CAPTURE_DONE','quit'];(home/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1,ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=rt,timeout=150)
log=(home/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_TIMERS_CAPTURE_DONE' in log
outputs=[]
for i,f in enumerate(sorted((home/'screenshots').glob('*.tga'))):
    im=Image.open(f);assert im.size==(3840,2160)
    out=root/'artifacts-local'/f'HUD-Timers-{args.game}-{args.run}-{i:02}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(labels)
report=dict(game=args.game,run=args.run,installed=args.installed,width=3840,height=2160,hud_scale=1.66,labels=labels,outputs=outputs,exit_code=r.returncode)
(root/'generated-local/hud-upscale/timers'/f'{args.run}-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
