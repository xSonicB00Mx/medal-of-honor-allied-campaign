"""Native menu/hover/cursor captures in disposable profiles."""
from pathlib import Path
import argparse,json,re,shutil,subprocess
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--font-scale',action='store_true');ap.add_argument('--baseline',action='store_true');ap.add_argument('--installed',action='store_true');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/menu-polish'/a.run
num=['AA','SH','BT'].index(a.game);folder=['main','mainta','maintt'][num];home=p/folder;home.mkdir(parents=True,exist_ok=False)
runner=rt
if not a.baseline and not a.installed:
 runner=p/'runner';runner.mkdir()
 for f in [*rt.glob('*.dll'),r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe']:shutil.copy2(f,runner/f.name)
 shutil.copy2(r/'generated-local/menu-polish/packages'/folder/'zzzzzzzzz_AC_MenuPolish.pk3',home)
start='devmap m2l1'
if num:
 source=r/(['','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'][num])
 (home/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),home/('save/omconfig/reference'+ext))
 start='loadgame reference'
cmds=['wait 1500',start,'wait 6500','finishloadingscreen','wait 5000','god','set developer 0','pushmenu main','wait 1500'];labels=[]
def shot(name,commands):
 cmds.extend([*commands,'wait 800','screenshot silent']);labels.append(name)
if a.font_scale:
 for menu,opening in [('ac_scaling','ac_ui_options'),('controls','loadmenu controls; pushmenu controls')]:
  cmds.extend(['popmenu 0','wait 500',opening,'wait 500'])
  for scale in ['1','0.65','1.5','1']:
   shot(menu+'-'+scale,['set ac_menu_scale '+scale,'wait 200','echo FONT_GEOMETRY_BEGIN','ac_ui_report '+menu,'echo FONT_GEOMETRY_END'])
 for scale in ['1','0.65']:
  shot('hud-'+scale,['popmenu 0','wait 500','set ac_menu_scale '+scale,'ac_ui_report hud_compass'])
else:
 shot('main',[])
 shot('back-hover',['widgetcommand backtogame mouse_entered 0 0 0'])
 shot('quit-hover',['widgetcommand backtogame mouse_exited 0 0 0','widgetcommand Default mouse_entered 0 0 0'])
 shot('options',['popmenu 0','wait 500','ac_ui_options'])
 shot('controls',['popmenu 0','wait 500','loadmenu controls','pushmenu controls'])
 shot('mission-list',['popmenu 0','wait 500','ac_level_list'])
 shot('hud',['popmenu 0'])
cmds+=['echo AC_MENU_POLISH_DONE','quit'];(home/'capture.cfg').write_text('\n'.join(cmds)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=a.width,r_customheight=a.height,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=(0 if num else 1),ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(runner/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
result=subprocess.run(cmd+['+exec','capture.cfg'],cwd=rt,timeout=160)
log=(home/'qconsole.log').read_text(encoding='latin1');assert result.returncode==0 and 'AC_MENU_POLISH_DONE' in log, (result.returncode, log[-1500:])
errors=[l for l in log.splitlines() if any(t in l for t in ['Unknown command','Invalid event','Script Error',"Couldn't load font",'Error parsing font'])];assert not errors,errors
if a.font_scale:
 blocks=re.findall(r'FONT_GEOMETRY_BEGIN\n(.*?)FONT_GEOMETRY_END',re.sub(r'(?m)^\[[^\]]+\] ', '', log.replace('\r','')),re.S)
 frames=[[l for l in b.splitlines() if l.startswith(('AC_UI_ROOT','AC_UI_CHILD'))] for b in blocks]
 assert len(frames)==8 and all(frames), frames
 assert all(f==frames[0] for f in frames[:4]), 'Options geometry moved'
 assert all(f==frames[4] for f in frames[4:]), 'Controls geometry moved'
 print('PASS fixed geometry at 65%, 100%, 150%, 100%')
images=[]
for i,f in enumerate(sorted((home/'screenshots').glob('*.tga'))):
 im=Image.open(f);assert im.size==(a.width,a.height)
 dest=r/'artifacts-local'/f'MenuPolish-{a.run}-{labels[i]}.png';im.save(dest);images.append(dest.relative_to(r).as_posix())
assert len(images)==len(labels)
(r/'generated-local/menu-polish'/f'{a.run}-test.json').write_text(json.dumps(dict(game=a.game,images=images,errors=errors,baseline=a.baseline,installed=a.installed),indent=2))
print('PASS',a.run)
