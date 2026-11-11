"""Native health-state captures in isolated UHD profiles, without touching saves."""
from pathlib import Path
import argparse,json,shutil,subprocess
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--installed',action='store_true');args=ap.parse_args()
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/health'/args.run;home=p/folder;(home/'probe').mkdir(parents=True,exist_ok=False)
if not args.installed:
    shutil.copy2(root/'generated-local/hud-upscale/health/packages'/folder/'zzzzzzzz_AC_Health.pk3',home)
commands=['wait 1000','devmap '+['m2l1','t1l3','e3l1'][num],'wait 6000','finishloadingscreen','set ac_hud_scale 1.66','set developer 0','wait '+('30000' if num==2 else '5000')]
labels=[]
for hp in [100,75,50,25,1,100]:
    name=f'health{hp}.scr'
    (home/'probe'/name).write_text(f'main:\n $player nodamage\n $player max_health 100\n $player healthonly {hp}\nend\n')
    commands += [f'script player exec probe/{name}','wait 150','screenshot silent','wait 1800','screenshot silent']
    labels += [f'{hp} transition',f'{hp} settled']
commands+=['ac_hud_scale','echo AC_HEALTH_CAPTURE_DONE','quit'];(home/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1,ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=rt,timeout=150)
log=(home/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_HEALTH_CAPTURE_DONE' in log
outputs=[]
for i,f in enumerate(sorted((home/'screenshots').glob('*.tga'))):
    im=Image.open(f);assert im.size==(3840,2160)
    out=root/'artifacts-local'/f'HUD-Health-{args.game}-{args.run}-{i:02}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(labels)
report=dict(game=args.game,run=args.run,installed=args.installed,width=3840,height=2160,hud_scale=1.66,labels=labels,outputs=outputs,exit_code=r.returncode)
(root/'generated-local/hud-upscale/health'/f'{args.run}-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
