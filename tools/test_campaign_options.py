"""Native rendered options and widget bounds at normal/extreme legacy scales."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--run-id');ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('width',type=int);ap.add_argument('height',type=int);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP05a-r3';p=r/'profiles-local/CP05a-r3'/(a.run_id or f'menu-{a.game}-{a.width}x{a.height}');h=p/({'AA':'main','SH':'mainta','BT':'maintt'}[a.game]);assert not p.exists();h.mkdir(parents=True)
commands=['wait 1200','set developer 0','set ui_console 0','pushmenu options_main','wait 600','screenshot','ac_ui_report options_main','ac_ui_options','wait 600','ac_ui_report ac_scaling','screenshot','set ac_menu_scale 0.65','set ac_hud_scale 2','set ac_ui_auto 0','wait 600','ac_ui_report ac_scaling','screenshot','set ac_menu_scale 1.5','set ac_ui_auto 1','wait 600','ac_ui_report ac_scaling','screenshot','popmenu 0','wait 300','ac_ui_options','wait 300','ac_ui_report ac_scaling','echo AC_OPTIONS_DONE','quit']
(h/'test.cfg').write_text('\n'.join(commands)+'\n');cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=['AA','SH','BT'].index(a.game),fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=a.width,r_customheight=a.height,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','test.cfg'],cwd=rt,timeout=60);log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for im in sorted((h/'screenshots').glob('*.tga')):
 out=im.with_suffix('.png');Image.open(im).save(out);images.append(out.relative_to(r).as_posix())
roots=re.findall(r'AC_UI_ROOT ac_scaling ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',log)
assert len(roots)==4 and len(set(roots))==1,roots
x,y,w,t=map(float,roots[0]);assert abs(w/t-16/9)<.002 and abs(x-(a.width-w)/2)<.1 and abs(y-(a.height-t)/2)<.1
chunks=log.split('AC_UI_ROOT ac_scaling')[1:];bounds=[]
for chunk in chunks:
 rows=re.findall(r'AC_UI_CHILD (\S+) ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',chunk.split('AC_UI drawable',1)[0]);assert len(rows)==25,len(rows)
 rects=[(name,*map(float,vals)) for name,*vals in rows]
 for name,cx,cy,cw,ch in rects:assert cx>=-.1 and cy>=-.1 and cx+cw<=w+.1 and cy+ch<=t+.1,(name,cx,cy,cw,ch,w,t)
 for i,(n,ax,ay,aw,ah) in enumerate(rects):
  for m,bx,by,bw,bh in rects[i+1:]:assert min(ax+aw,bx+bw)-max(ax,bx)<=.1 or min(ay+ah,by+bh)-max(ay,by)<=.1,(n,m)
 bounds.append(rects)
errors=[l for l in log.splitlines() if any(s in l for s in ['Unknown command','Failed to find resource','Invalid event'])]
result=dict(game=a.game,resolution=[a.width,a.height],completed='AC_OPTIONS_DONE' in log,exit=proc.returncode,errors=errors,root=roots[0],bounds=bounds,images=images,engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),overlap_free=True,stable_when_scaling_changes=True)
(r/'checkpoints/CP05a/r3'/((a.run_id or f'menu-{a.game}-{a.width}x{a.height}')+'.json')).write_text(json.dumps(result,indent=2)+'\n');assert result['completed'] and not errors and proc.returncode==0
print(a.game,a.width,a.height,'PASS centered 16:9, 25 non-overlapping controls, stable scale',flush=True)
