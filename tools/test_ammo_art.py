"""Capture actual ammunition HUDs in an isolated UHD profile; never touch user saves."""
from pathlib import Path
import argparse,json,shutil,subprocess
from PIL import Image
a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('--game',choices=['AA','SH','BT'],default='AA');a.add_argument('--installed',action='store_true');args=a.parse_args()
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/ammo'/args.run;h=p/folder;h.mkdir(parents=True,exist_ok=False)
if not args.installed:shutil.copy2(root/'generated-local/hud-upscale/ammo/packages'/folder/'zzzzzzzz_AC_Ammo.pk3',h)
weapons=['m1_garand','colt45','shotgun','bazooka','panzerschreck','m2frag_grenade','steilhandgranate'] if num==0 else ['thompsonsmg','colt45','M18_smoke_grenade'] if num==1 else ['thompsonsmg','Uk_W_Piat','It_W_Bomba','It_W_BombaBreda']
(h/'probe').mkdir()
commands=['wait 1000','devmap '+['m2l1','t1l3','e3l1'][num],'wait 6000','finishloadingscreen','set ac_hud_scale 1.66','set developer 0','wait '+('30000' if num==2 else '5000')]
for i,w in enumerate(weapons):
 w=w.lower()
 (h/'probe'/f'{i}.scr').write_text(f'main:\n $player nodamage\n $player give models/weapons/{w}.tik\n wait 0.2\n $player use models/weapons/{w}.tik\nend\n')
 commands += [f'script player exec probe/{i}.scr','wait 2200','screenshot silent']
 if i==0:commands+=['+attack','wait '+('3500' if num==0 else '350'),'-attack','wait 600','screenshot silent','reload','wait 3500','screenshot silent']
commands+=['ac_hud_scale','echo AC_AMMO_CAPTURE_DONE','quit']
(h/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1,ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=rt,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_AMMO_CAPTURE_DONE' in log
outputs=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
 im=Image.open(f);assert im.size==(3840,2160)
 out=root/'artifacts-local'/f'HUD-Ammo-{args.game}-{args.run}-{i:02}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(weapons)+2
report=dict(game=args.game,run=args.run,installed=args.installed,width=3840,height=2160,hud_scale=1.66,outputs=outputs,exit_code=r.returncode)
(root/'generated-local/hud-upscale/ammo'/f'{args.run}-test.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
