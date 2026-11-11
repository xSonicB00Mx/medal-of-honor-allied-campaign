"""Native spread, movement, FOV, HUD size, optics and save/load probe; isolated profile."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--installed',action='store_true');ap.add_argument('--width',type=int,default=3840);ap.add_argument('--height',type=int,default=2160);args=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',args.run)
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/dynamic-crosshair'/args.run;home=p/folder;(home/'probe').mkdir(parents=True,exist_ok=False)
runner=rt
if not args.installed:
    runner=p/'runner';runner.mkdir()
    for f in [rt/'openmohaa.exe',*rt.glob('*.dll')]:shutil.copy2(f,runner/f.name)
    for name in ['game.dll','cgame.dll']:shutil.copy2(root/'build-local/cp00-r3/RelWithDebInfo'/name,runner/name)
start='devmap '+['m2l1','t1l2','e2l2'][num]
if num:
    source=root/(['','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'][num])
    (home/'save/omconfig').mkdir(parents=True)
    for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),home/('save/omconfig/reference'+ext))
    start='loadgame reference'
commands=['wait 1000',start,'wait 6000','finishloadingscreen','wait 5000','set developer 0','set ac_crosshair_debug 1']
labels=[]
def script(name,body):
    (home/'probe'/f'{name}.scr').write_text('main:\n $player nodamage\n'+body+'\nend\n')
    commands.extend(['set developer 1',f'script player exec probe/{name}.scr','wait 2000','set developer 0'])
def phase(name,extra=(),delay=700,capture=True):
    commands.extend(['echo AC_PHASE_'+name,*extra,f'wait {delay}'])
    if capture:commands.append('screenshot silent');labels.append(name)
    commands.append('echo AC_PHASE_END')
script('smg',' $player give models/weapons/thompsonsmg.tik\n wait 0.2\n $player use models/weapons/thompsonsmg.tik')
phase('standing')
phase('firing',['+attackprimary'],1000)
phase('recovery',['-attackprimary'],2500)
phase('moving',['+forward'],600)
phase('stopped',['-forward'],1000)
phase('hud1',['set ac_hud_scale 1'])
phase('hud166',['set ac_hud_scale 1.66'])
phase('fov90',['set cg_fov 90'])
phase('fov80',['set cg_fov 80'])
script('rifle',' $player give models/weapons/kar98.tik\n wait 0.2\n $player use models/weapons/kar98.tik')
phase('rifle');phase('rifle-shot',['+attackprimary'],500);phase('rifle-recovered',['-attackprimary'],1200)
script('sniper',' $player give models/weapons/springfield.tik\n wait 0.2\n $player use models/weapons/springfield.tik')
phase('scope',['+attacksecondary','wait 100','-attacksecondary'],900)
phase('unscoped',['+attacksecondary','wait 100','-attacksecondary'],900)
script('grenade',' $player give models/weapons/m2frag_grenade.tik\n wait 0.2\n $player use models/weapons/m2frag_grenade.tik')
phase('projectile')
script('restore',' $player use models/weapons/thompsonsmg.tik')
phase('save',['savegame crosshair_probe'],900)
phase('loaded',['loadgame crosshair_probe','wait 3500','finishloadingscreen'],1500)
phase('hidden',['set ui_crosshair 0'])
phase('legacy',['set ui_crosshair 1','set ac_dynamic_crosshair 0'])
commands+=['echo AC_CROSSHAIR_DONE','quit'];(home/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=args.width,r_customheight=args.height,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=(0 if num else 1),ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(runner/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=runner,timeout=240)
log=(home/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_CROSSHAIR_DONE' in log
errors=[l for l in log.splitlines() if any(s in l for s in ['Script Error','Unknown command','Invalid event','compile error','AC_SAVE_REJECT','command not available'])];assert not errors,errors
outputs=[]
for i,f in enumerate(sorted((home/'screenshots').glob('*.tga'))):
    im=Image.open(f);assert im.size==(args.width,args.height)
    out=root/'artifacts-local'/f'Crosshair-{args.game}-{args.run}-{labels[i]}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(labels)
sections={};name='startup'
for line in log.splitlines():
    line=re.sub(r'^\[[^\]]+\] ', '', line)
    if line.startswith('AC_PHASE_'):name=line[9:];sections[name]=[]
    elif line.startswith(('AC_CROSSHAIR time=','AC_SPREAD_SAMPLE')):sections.setdefault(name,[]).append(line)
report=dict(game=args.game,run=args.run,installed=args.installed,width=args.width,height=args.height,labels=labels,outputs=outputs,sections=sections,exit_code=r.returncode,binaries={n:hashlib.sha256((runner/n).read_bytes()).hexdigest() for n in ['game.dll','cgame.dll']},errors=errors)
out=root/'generated-local/dynamic-crosshair'/f'{args.run}-test.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2));print(out)
for name,lines in sections.items():print(name,len(lines),lines[-1:] if lines else [])
