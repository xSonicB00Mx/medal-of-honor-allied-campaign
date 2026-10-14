"""Exercise existing option pages and renderer restarts without desktop input."""
import argparse,json,re,subprocess,hashlib
from pathlib import Path
from PIL import Image
a=argparse.ArgumentParser();a.add_argument('game',choices=['AA','SH','BT']);a=a.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP01-r1';p=r/f'profiles-local/CP01-r1/reflow-{a.game}';f={'AA':'main','SH':'mainta','BT':'maintt'}[a.game];h=p/f
assert not p.exists();h.mkdir(parents=True)
commands=['wait 1500','set ac_menu_scale 0.85']
for name in ['options_main','audio_options','controls','video_options','advancedoptions']:
 commands += ['pushmenu '+name,'wait 700','ac_ui_report '+name,'screenshot','popmenu 0','wait 300']
for w,t,full in [(1600,900,0),(1920,1200,1),(1280,960,0)]:
 commands += [f'set r_customwidth {w}',f'set r_customheight {t}',f'set r_fullscreen {full}','vid_restart','wait 1800','ac_ui_options','wait 600','ac_ui_report ac_scaling','screenshot','popmenu 1','wait 400']
commands+=['ac_menu_scale','echo CP01_REFLOW_DONE','quit'];(h/'reflow.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=['AA','SH','BT'].index(a.game),fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,ui_console=0,r_fullscreen=0,r_allowResize=1,r_mode=-1,r_customwidth=1280,r_customheight=960,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','reflow.cfg'],cwd=rt,timeout=100);log=(h/'qconsole.log').read_text(encoding='latin1')
errors=[l for l in log.splitlines() if any(t in l for t in ['Script Error','Unknown command','Failed to find resource','compile error'])];geometry=[l.split('] ',1)[-1] for l in log.splitlines() if '] AC_UI' in l];images=[]
for f in sorted((h/'screenshots').glob('*.tga')):
 im=Image.open(f);out=f.with_suffix('.png');im.save(out);images.append(dict(path=out.relative_to(r).as_posix(),size=im.size))
result=dict(game=a.game,completed='CP01_REFLOW_DONE' in log,exit_code=proc.returncode,errors=errors,geometry=geometry,images=images,engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),scope='Existing WCR option pages and actual renderer/window/fullscreen reinitialization via video cvars; not an OS drag, Alt-Tab or DPI-switch claim.')
(r/f'checkpoints/CP01/reflow-{a.game}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
assert proc.returncode==0 and result['completed'] and not errors and len(images)==8
assert [tuple(x['size']) for x in images[-3:]]==[(1600,900),(1920,1200),(1280,960)]
assert all('AC_UI missing' not in x for x in geometry)
assert re.search(r'"ac_menu_scale" is:\s*"0.85',log)
print(a.game,'PASS option menus and window/fullscreen reflow',flush=True)
