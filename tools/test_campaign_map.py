"""Native map/menu rendering, all selections and geometry; isolated seeded UI profiles."""
import argparse,json,subprocess,re,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',type=int,default=0);ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);ap.add_argument('--completed',type=int,default=0);ap.add_argument('--available',action='store_true');a=ap.parse_args()
rt=R/'runtime-local/CP08-r1';p=R/'profiles-local/CP08-r1'/a.run;h=p/['main','mainta','maintt'][a.game];assert not p.exists();h.mkdir(parents=True)
(p/'ac_progress.dat').write_text(f'ACPROG1 {(1<<a.completed)-1} {a.completed} '+('ui_fixture' if a.available else '-')+'\n')
ops=json.loads((R/'mod/campaign/missions.json').read_text())['operations'];cmds=['wait 1200','ac_campaign','wait 700','screenshot']
for i,o in enumerate(ops):
 cmds += [f'ac_campaign {i} {o["map_region"]}','wait 180',f'echo AC_SELECTION_{i}','ac_ui_report ac_campaign_operations']
 if i in [0,7,11,14]:cmds+=['screenshot']
cmds+=['ac_ui_options','wait 700','ac_ui_report ac_scaling','screenshot','ac_campaign 0 0','wait 500','screenshot','echo AC_MAP_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(cmds)+'\n');cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=a.game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,r_fullscreen=0,r_mode=-1,r_customwidth=a.width,r_customheight=a.height,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=65)
log=(h/'qconsole.log').read_text(encoding='latin1');errors=[x for x in log.splitlines() if any(t in x for t in ['UI EXCEPTION','Failed to find resource','Couldn\'t find menu','Script Error :'])]
roots=[[float(x) for x in row] for row in re.findall(r'AC_UI_ROOT ac_campaign_operations ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',log)]
s=min(a.width/960,a.height/540);expected=[(a.width-960*s)/2,(a.height-540*s)/2,960*s,540*s]
assert len(roots)==15 and all(all(abs(v-e)<.02 for v,e in zip(row,expected)) for row in roots),(roots,expected)
images=[]
for f in sorted((h/'screenshots').glob('*.tga')):
 im=Image.open(f);assert im.size==(a.width,a.height);im.save(f.with_suffix('.png'));images.append(str(f.with_suffix('.png').relative_to(R)))
result=dict(engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),game=a.game,requested=[a.width,a.height],completed_seed=a.completed,available_seed=a.available,exit=proc.returncode,selections=15,root_bounds=expected,errors=errors,images=images,geometry=[x for x in log.splitlines() if '] AC_UI' in x],scope='Native framebuffer and geometry; seeded preview states, not user unlocks or physical DPI changes')
(R/'checkpoints/CP08'/(a.run+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(a.run,proc.returncode,len(images),errors,flush=True);assert proc.returncode==0 and not errors and 'AC_MAP_DONE' in log and len(images)==7
