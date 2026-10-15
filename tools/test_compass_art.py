"""Inspect compass registration at fixed headings with an isolated UHD profile."""
from pathlib import Path
import argparse,json,shutil,subprocess
from PIL import Image
a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('--game',choices=['AA','SH','BT'],default='AA');a.add_argument('--installed',action='store_true');args=a.parse_args()
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/compass'/args.run;h=p/folder;(h/'probe').mkdir(parents=True,exist_ok=False)
if not args.installed:shutil.copy2(root/'generated-local/hud-upscale/compass/packages'/folder/'zzzzzzzz_AC_Compass.pk3',h)
angles=[(0,0),(0,90),(0,180),(0,270),(30,45),(-30,225)] if num==0 else [(0,45),(0,225)]
commands=['wait 1000','devmap '+['m2l1','t1l3','e3l1'][num],'wait 6000','finishloadingscreen','set ac_hud_scale 1.66','set developer 0','wait '+('30000' if num==2 else '5000')]
for i,(pitch,yaw) in enumerate(angles):
 (h/'probe'/f'{i}.scr').write_text(f'main:\n $player nodamage\n $player.viewangles = ( {pitch} {yaw} 0 )\nend\n')
 commands += [f'script player exec probe/{i}.scr','wait 2500','screenshot silent']
commands+=['ac_hud_scale','echo AC_COMPASS_CAPTURE_DONE','quit'];(h/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1,ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=rt,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_COMPASS_CAPTURE_DONE' in log
outputs=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
 im=Image.open(f);assert im.size==(3840,2160)
 out=root/'artifacts-local'/f'HUD-Compass-{args.game}-{args.run}-{i:02}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(angles)
report=dict(game=args.game,run=args.run,installed=args.installed,angles=angles,outputs=outputs,exit_code=r.returncode)
(root/'generated-local/hud-upscale/compass'/f'{args.run}-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
