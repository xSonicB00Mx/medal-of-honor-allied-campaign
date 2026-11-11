"""Render long German objectives/subtitles, script HUD, optics and save UI."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);ap.add_argument('--run-id',required=True);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP01-r1';p=r/'profiles-local/CP01-r1'/a.run_id
assert re.fullmatch('[A-Za-z0-9-]+',a.run_id) and not p.exists()
n,f,src={'AA':(0,'main',None),'SH':(1,'mainta','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':(2,'maintt','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[a.game]
h=p/f;h.mkdir(parents=True);start='map m2l1'
if src:
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2((r/src).with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
german='Überqueren Sie die Brücke, zerstören Sie anschließend die feindlichen Geschütze und führen Sie sämtliche zurückgebliebenen Angehörigen Ihrer Einheit sicher zum vereinbarten Treffpunkt.'
script='main:\n'
for i in range(1,5):script+=f'    addobjective {i} 2 "{german}" (0 0 0)\n'
script+='    setcurrentobjective 1\n    huddraw_align 200 center center\n    huddraw_virtualsize 200 1\n    huddraw_rect 200 -70 80 140 20\n    huddraw_font 200 facfont-20\n    huddraw_string 200 "ÄÖÜ äöü ß – HUD"\n    huddraw_alpha 200 1\nend\n'
script=script.replace(' – ',' - ');(h/'text.scr').write_text(script,encoding='latin1')
(h/'binocular.scr').write_text('main:\n    $player give models/items/binoculars.tik\n    $player use models/items/binoculars.tik\nend\n')
(h/'scope.scr').write_text('main:\n    $player give models/weapons/springfield.tik\n    $player use models/weapons/springfield.tik\nend\n')
commands=['wait 1000',start,'wait 3000','finishloadingscreen','wait 4000','set ac_hud_scale 1.4','set ac_hud_safe 0.9','script player exec text.scr','wait 500','+scores','set subtitle0 "'+german+' '+german+'"','wait 1200','screenshot','-scores','set subtitle0 ""','script player exec binocular.scr','wait 1500','screenshot','script player exec scope.scr','wait 1500','+attacksecondary','wait 100','-attacksecondary','wait 600','screenshot','savegame cp01_text','wait 1200','pushmenu loadsave','wait 1000','screenshot','ac_ui_options','wait 500','set ac_menu_scale 0.85','wait 500','popmenu 1','wait 500','ac_menu_scale','ac_ui_options','wait 500','ac_ui_report ac_scaling','screenshot','echo CP01_TEXT_DONE','quit']
(h/'text.cfg').write_text('\n'.join(commands)+'\n',encoding='latin1')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=a.width,r_customheight=a.height,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','text.cfg'],cwd=rt,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for f in sorted((h/'screenshots').glob('*.tga')):
 out=f.with_suffix('.png');Image.open(f).save(out);images.append(out.relative_to(r).as_posix())
errors=[l for l in log.splitlines() if any(t in l for t in ['Script Error','Unknown command','Invalid event','compile error'])]
result=dict(game=a.game,completed='CP01_TEXT_DONE' in log,exit_code=proc.returncode,engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cgame_sha256=hashlib.sha256((rt/'cgame.dll').read_bytes()).hexdigest(),errors=errors,images=images,menu_preserved=bool(re.search(r'"ac_menu_scale" is:\s*"0.85',log)),scope='Synthetic German text, existing native subtitle and objective renderer; real equipped optics, save/load menu. Visual review recorded separately.')
(r/'checkpoints/CP01'/f'{a.run_id}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result),flush=True)
assert result['completed'] and proc.returncode==0 and not errors and result['menu_preserved'] and len(images)==5
