"""Render native objectives and shader-state fixtures without touching the user profile."""
from pathlib import Path
import argparse, json, re, shutil, subprocess
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--installed',action='store_true');args=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',args.run)
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/special-hud'/args.run;home=p/folder;(home/'probe').mkdir(parents=True,exist_ok=False)
if not args.installed:
    shutil.copy2(root/'generated-local/hud-upscale/special/packages'/folder/'zzzzzzzz_AC_SpecialHUD.pk3',home)
start='devmap m2l1'
if num:
    source=root/(['','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'][num])
    (home/'save/omconfig').mkdir(parents=True)
    for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),home/('save/omconfig/reference'+ext))
    start='loadgame reference'
commands=['wait 1000',start,'wait 6000','finishloadingscreen','wait 5000'];labels=[]
def script(name,body):
    (home/'probe'/f'{name}.scr').write_text('main:\n $player nodamage\n'+body+'\nend\n')
    commands.extend(['set developer 1',f'script player exec probe/{name}.scr','wait 1500','set developer 0'])
def phase(name,extra=()):
    commands.extend([*extra,'wait 1200','screenshot silent']);labels.append(name)
body='\n'.join(f' addobjective {i} 1 "Hidden diagnostic objective" ( 0 0 0 )' for i in range(1,21))
body+='\n addobjective 1 3 "Secure the checkpoint." ( 0 0 0 )\n addobjective 2 2 "Find the documents and return to the rendezvous point without alerting the enemy patrol." ( 0 0 0 )\n addobjective 3 2 "Locate the radio operator." ( 0 0 0 )\n setcurrentobjective 2'
script('objectives',body)
phase('objectives-166',['+scores']);phase('objectives-100',['set ac_hud_scale 1'])
phase('closed',['-scores','set ac_hud_scale 1.66'])
# Deliberate asset fixture, not evidence of normal SP use of the directional marker.
body=''
for i,(shader,x,y,w,h,a) in enumerate([
    ('textures/hud/directional_arrow',70,80,32,32,1),
    *([('textures/hud/clip_aa_gun',x,180,64,64,a) for x,a in [(70,1),(150,.5),(230,.1)]] if num else [])],200):
    body+=f'\n huddraw_shader {i} "{shader}"\n huddraw_align {i} left top\n huddraw_virtualsize {i} 1\n huddraw_rect {i} {x} {y} {w} {h}\n huddraw_color {i} 1 1 1\n huddraw_alpha {i} {a}'
script('indicators',body);phase('indicator-fixture')
commands+=['echo AC_SPECIAL_DONE','quit'];(home/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=(0 if num else 1),ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=rt,timeout=180)
log=(home/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_SPECIAL_DONE' in log
errors=[l for l in log.splitlines() if any(s in l for s in ['Script Error','Unknown command','Invalid event','compile error','AC_SAVE_REJECT','command not available'])];assert not errors,errors
outputs=[]
for i,f in enumerate(sorted((home/'screenshots').glob('*.tga'))):
    im=Image.open(f);assert im.size==(3840,2160)
    out=root/'artifacts-local'/f'SpecialHUD-{args.game}-{args.run}-{labels[i]}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(labels)
report=dict(game=args.game,run=args.run,installed=args.installed,outputs=outputs,errors=errors,exit_code=r.returncode)
out=root/'generated-local/hud-upscale/special'/f'{args.run}-test.json';out.write_text(json.dumps(report,indent=2));print(out)
