"""Exercise the real slider mouse callbacks in isolated native AA/SH/BT menus."""
from pathlib import Path
import subprocess, shutil, re, json, zipfile
from PIL import Image
r=Path(__file__).resolve().parents[1]; rt=r/'runtime-local/CP08-r1'
root=r/'profiles-local/flinch/snap-r4'; root.mkdir(parents=True,exist_ok=False)
b=root/'bin'; b.mkdir()
for f in rt.glob('*.dll'): shutil.copy2(f,b/f.name)
shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe',b/'openmohaa.exe')
results=[]
for num,folder in enumerate(['main','mainta','maintt']):
 p=root/folder; h=p/folder; h.mkdir(parents=True)
 for base in ['main','mainta','maintt']:
  (p/base).mkdir(exist_ok=True)
  for f in (r/'generated-local/flinch/packages'/base).glob('*.pk3'):
   shutil.copy2(f,p/base/f.name)
   with zipfile.ZipFile(f) as z: assert 'title "ADDITIONAL OPTIONS"' in z.read('ui/ac_scaling.urc').decode()
 cmd=['wait 500','ac_ui_options','wait 300','ac_ui_report ac_scaling']
 for event in ['left_mouse_down','left_mousedragged']:
  cmd+=['widgetcommand playerFlinch left_mouse_down 600 406 1']
  for x in range(540,901,3):
   cmd += [f'widgetcommand playerFlinch {event} {x} 406 1','ac_player_flinch_percent']
  cmd+=['widgetcommand playerFlinch left_mouse_up 900 406 0']
 cmd+=['set ac_player_flinch_percent 37','wait 100','ac_player_flinch_percent','screenshot silent','writeconfig verified','echo SNAP_DONE','quit']
 (h/'test.cfg').write_text('\n'.join(cmd)+'\n')
 settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cl_playintro=0,ac_campaign_mode=0,r_fullscreen=0,r_mode=-1,r_customwidth=960,r_customheight=540)
 args=[str(b/'openmohaa.exe')]
 for k,v in settings.items(): args+=['+set',k,str(v)]
 proc=subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=45)
 log=(h/'qconsole.log').read_text(encoding='latin1')
 assert proc.returncode==0 and 'SNAP_DONE' in log
 assert not any(s in log for s in ['Unknown command','Invalid event','Script Error'])
 values=[float(v) for v in re.findall(r'"ac_player_flinch_percent" is:"([^" ]+)',log)]
 assert len(values)==243,(len(values),log[-4000:])
 assert all(v in range(0,101,10) for v in values),values
 assert set(values[:121])==set(range(0,101,10)),values
 assert set(values[121:242])==set(range(0,101,10)),values
 assert values[-1]==40
 assert 'seta ac_player_flinch_percent "40"' in (h/'configs/verified.cfg').read_text()
 for f in (h/'screenshots').glob('*.tga'): Image.open(f).save(f.with_suffix('.png'))
 results.append(dict(game=folder,mouse_samples=242,all_eleven_steps=True,saved_37_normalized_to=40))
(root/'result.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
