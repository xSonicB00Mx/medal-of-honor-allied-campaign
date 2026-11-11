"""Read-only fixture sources; isolated briefing and saved-wound visual comparisons."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('kind',choices=['briefing','wound']);ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--revision',default='r2');ap.add_argument('--run-id',required=True);ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local'/('CP05-'+a.revision);p=r/'profiles-local/CP05-r2'/a.run_id
assert not p.exists() and re.fullmatch('[A-Za-z0-9-]+',a.run_id)
n,f,mapname={'AA':(0,'main','briefing1'),'SH':(1,'mainta','briefingt1'),'BT':(2,'maintt','briefinge1')}[a.game];h=p/f;h.mkdir(parents=True)
if a.kind=='briefing':
 commands=['wait 1000',f'map briefing/{mapname}','wait 3000','finishloadingscreen','wait 3000','screenshot','wait 7000','screenshot','set ac_hud_scale 1.5','set ac_hud_safe .8','wait 1000','screenshot']
else:
 source=r/'profiles-local/CP05-r1'/('live-'+a.game+'-r2')/f
 (h/'save/omconfig').mkdir(parents=True);shutil.copytree(source/'cp00',h/'cp00')
 for ext in ['.sav','.ssv','.tga']:shutil.copy2(source/('save/omconfig/cp03_blood'+ext),h/('save/omconfig/reference'+ext))
 commands=['wait 1000','loadgame reference','wait 3000','finishloadingscreen','wait 2000','set developer 1','script player exec cp00/inspect.scr','wait 800','screenshot','set r_light_nolight 1','wait 600','screenshot','set r_light_nolight 0','set r_entlight_scale .2','wait 600','screenshot','set r_entlight_scale 1','wait 600','set ac_body_wounds 0','wait 300','screenshot','set ac_body_wounds 1','wait 300','screenshot','savegame cp05_r2_roundtrip','wait 500','loadgame cp05_r2_roundtrip','wait 3000','finishloadingscreen','wait 500','screenshot']
commands+=['echo AC_PRESENTATION_DONE','quit'];(h/'probe.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=a.width,r_customheight=a.height,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_fx_debug=2,ac_world_blood=1,ac_body_wounds=1,ac_blood_mist=1,ac_hud_scale=1,ac_hud_safe=1).items():cmd+=['+set',k,str(v)]
result=subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for image in sorted((h/'screenshots').glob('*.tga')):
 out=image.with_suffix('.png');Image.open(image).save(out);images.append(out.relative_to(r).as_posix())
report=dict(kind=a.kind,game=a.game,revision=a.revision,dimensions=[a.width,a.height],completed='AC_PRESENTATION_DONE' in log,exit=result.returncode,images=images,binaries={name:hashlib.sha256((rt/name).read_bytes()).hexdigest() for name in ['openmohaa.exe','game.dll','cgame.dll']},archive=re.findall(r'AC_WOUND_ARCHIVE[^\r\n]+',log),errors=[l for l in log.splitlines() if any(x in l for x in ['Script Error','Unknown command','Invalid event','compile error'])])
out=r/'checkpoints/CP05/r2';out.mkdir(exist_ok=True);(out/(a.run_id+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({**report,'images':len(images)}),flush=True);assert report['completed'] and result.returncode==0 and not report['errors']
