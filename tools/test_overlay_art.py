"""Capture actual equipped optics and the native gas-mask HUD in isolated profiles."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--installed',action='store_true');ap.add_argument('--width',type=int,default=3840);ap.add_argument('--height',type=int,default=2160);args=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',args.run)
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/overlays'/args.run;home=p/folder;(home/'probe').mkdir(parents=True,exist_ok=False)
runner=rt
if not args.installed:
    shutil.copy2(root/'generated-local/hud-upscale/overlays/packages'/folder/'zzzzzzzz_AC_Overlays.pk3',home)
    runner=p/'runner';runner.mkdir()
    for f in [rt/'openmohaa.exe',*rt.glob('*.dll')]:shutil.copy2(f,runner/f.name)
    shutil.copy2(root/'build-local/cp00-r3/RelWithDebInfo/cgame.dll',runner/'cgame.dll')
commands=['wait 1000','devmap '+['m2l1','t1l3','e3l1'][num],'wait 6000','finishloadingscreen','set ac_hud_scale 1.66','set developer 0','wait '+('30000' if num==2 else '5000')]
labels=[]
def script(name,body):
    (home/'probe'/f'{name}.scr').write_text('main:\n $player nodamage\n'+body+'\nend\n')
    commands.extend([f'script player exec probe/{name}.scr','wait 2000'])
def capture(name):
    commands.extend(['screenshot silent']);labels.append(name)
for name,model,zoom in [('springfield','weapons/springfield',True),('kar98','weapons/kar98sniper',True),('binoculars','items/binoculars',False),('camera','items/camera',False)]:
    script(name,f' $player give models/{model}.tik\n wait 0.2\n $player use models/{model}.tik')
    if zoom:commands.extend(['+attacksecondary','wait 100','-attacksecondary','wait 800'])
    capture(name)
    if zoom:commands.extend(['+attacksecondary','wait 100','-attacksecondary','wait 800'])
script('gas',' $player use models/weapons/springfield.tik\n huddraw_shader 20 "textures/hud/gasmask_overlay"\n huddraw_align 20 left top\n huddraw_rect 20 0 0 640 480\n huddraw_virtualsize 20 1\n huddraw_color 20 1 1 1\n huddraw_alpha 20 1')
capture('gasmask')
script('clear',' huddraw_alpha 20 0');capture('overlay cleared')
commands+=['echo AC_OVERLAYS_CAPTURE_DONE','quit'];(home/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=args.width,r_customheight=args.height,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1,ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(runner/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=runner,timeout=180)
log=(home/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_OVERLAYS_CAPTURE_DONE' in log
errors=[l for l in log.splitlines() if any(s in l for s in ['Script Error','Unknown command','Invalid event','compile error'])]
assert not errors,errors
outputs=[]
for i,f in enumerate(sorted((home/'screenshots').glob('*.tga'))):
    im=Image.open(f);assert im.size==(args.width,args.height)
    out=root/'artifacts-local'/f'HUD-Overlays-{args.game}-{args.run}-{i:02}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(labels)
report=dict(game=args.game,run=args.run,installed=args.installed,width=args.width,height=args.height,hud_scale=1.66,labels=labels,outputs=outputs,exit_code=r.returncode,cgame_sha256=hashlib.sha256((runner/'cgame.dll').read_bytes()).hexdigest(),errors=errors)
(root/'generated-local/hud-upscale/overlays'/f'{args.run}-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
