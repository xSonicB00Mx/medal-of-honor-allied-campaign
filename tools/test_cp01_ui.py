"""Rendered UI/HUD capture and actual widget geometry, isolated from user profiles."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);ap.add_argument('--run-id',required=True);ap.add_argument('--fullscreen',default=0,type=int);ap.add_argument('--checkpoint',default='CP01');args=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local'/(args.checkpoint+'-r1')
assert re.fullmatch('[A-Za-z0-9-]+',args.run_id)
profile=r/'profiles-local'/(args.checkpoint+'-r1')/args.run_id;assert not profile.exists()
num,folder,source={'AA':(0,'main',None),'SH':(1,'mainta','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':(2,'maintt','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[args.game]
home=profile/folder;home.mkdir(parents=True);start='map m2l1'
if source:
 (home/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2((r/source).with_suffix(ext),home/('save/omconfig/ui_reference'+ext))
 start='loadgame ui_reference'
commands=['wait 1000',start,'wait 2500','screenshot','finishloadingscreen','wait 4500','echo AC_PHASE_DEFAULT','ac_ui_report hud_compass','screenshot','set ac_hud_scale 1.25','set ac_hud_safe 0.9','wait 800','echo AC_PHASE_SCALED','ac_ui_report hud_compass','screenshot','savegame cp01_ui','wait 800','loadgame cp01_ui','wait 2000','finishloadingscreen','wait 1500','echo AC_PHASE_LOADED','ac_ui_report hud_compass','pushmenu options_main','wait 1200','ac_ui_report options_main','screenshot','ac_ui_options','wait 1000','ac_ui_report ac_scaling','screenshot','set ac_menu_scale 0.85','wait 1000','echo AC_PHASE_SMALL','ac_ui_report ac_scaling','screenshot','echo AC_UI_TEST_DONE','quit']
(home/'ui-test.cfg').write_text('\n'.join(commands)+'\n',encoding='ascii')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=profile,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,r_fullscreen=args.fullscreen,r_mode=-1,r_customwidth=args.width,r_customheight=args.height,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ui_console=0,cg_fov=90)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
p=subprocess.Popen(cmd+['+exec','ui-test.cfg'],cwd=rt)
try:p.wait(timeout=130)
except subprocess.TimeoutExpired:p.terminate();p.wait();raise
log=(home/'qconsole.log').read_text(encoding='latin1')
images=[]
for f in sorted((home/'screenshots').glob('*.tga')):
 out=f.with_suffix('.png');im=Image.open(f);im.save(out);images.append(dict(path=out.relative_to(r).as_posix(),size=im.size,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
errors=[l for l in log.splitlines() if any(t in l for t in ['Unknown command','Failed to find resource','Invalid event','compile error','Script Error'])]
geometry=[l.split('] ',1)[-1] for l in log.splitlines() if re.search(r'] (AC_UI|AC_PHASE)',l)]
result=dict(engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cgame_sha256=hashlib.sha256((rt/'cgame.dll').read_bytes()).hexdigest(),game=args.game,requested=[args.width,args.height],fullscreen=bool(args.fullscreen),exit_code=p.returncode,completed='AC_UI_TEST_DONE' in log,errors=errors,geometry=geometry,images=images,scope='Actual rendered window/framebuffer and transformed widget geometry; no physical-monitor or OS-DPI-switch claim.')
out=r/'checkpoints'/args.checkpoint/f'{args.run_id}.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(game=args.game,completed=result['completed'],errors=errors,images=[i['size'] for i in images],geometry=geometry[:12])),flush=True)
assert p.returncode==0 and result['completed'] and not errors
assert len(images)==6 and all(i['size']==[args.width,args.height] or i['size']==(args.width,args.height) for i in images)

roots=re.findall(r'AC_UI_ROOT hud_compass ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',log)
assert len(roots)==3
roots=[[float(v) for v in row] for row in roots]
if args.game!='AA':assert all(abs(row[2]-row[3])<.01 for row in roots)
assert abs(roots[1][2]/roots[0][2]-1.25)<.002
assert roots[1]==roots[2], 'Save/load changed HUD geometry'
