"""Native two-region menu previews, hidden unlocks and inherited WCR map actions."""
import argparse,json,subprocess,hashlib,re,zipfile
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--completed',type=int,default=0);ap.add_argument('--game',type=int,default=0);ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/CP08-r1'/a.run;h=p/['main','mainta','maintt'][a.game];assert not p.exists();h.mkdir(parents=True)
(p/'ac_progress.dat').write_text(f'ACPROG1 {(1<<a.completed)-1} {a.completed} -\n')
cmds=['wait 1200','pushmenu main','wait 700','ac_ui_report main','screenshot silent']
for region in [0,1]:cmds += [f'ac_campaign -1 {region}','wait 700','ac_ui_report ac_campaign_operations','screenshot silent']
# A locked direct selection must fall back to a visible operation, never reveal it.
cmds+=['ac_campaign 14 1','wait 400','echo AC_TWO_REGIONS_DONE','quit'];(h/'probe.cfg').write_text('\n'.join(cmds)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=a.game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,r_fullscreen=0,r_mode=-1,r_customwidth=a.width,r_customheight=a.height,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=50);log=(h/'qconsole.log').read_text(encoding='latin1');ui=(h/'ui/ac_campaign_operations.urc').read_text()
assert proc.returncode==0 and 'AC_TWO_REGIONS_DONE' in log
for word in ['LOCKED','AVAILABLE','NEXT','map_credit','region_2']:assert word not in ui
ops=json.loads((r/'mod/campaign/missions.json').read_text())['operations']
for i,o in enumerate(ops):
 if i>a.completed:assert o['display_name'] not in ui,(i,o['display_name'])
assert len(re.findall(r'name "region_\d"',ui))==2
images=[]
for f in sorted((h/'screenshots').glob('*.tga')):
 im=Image.open(f);assert im.size==(a.width,a.height);im.save(f.with_suffix('.png'));images.append(f.with_suffix('.png').relative_to(r).as_posix())
with zipfile.ZipFile(rt/['main','mainta','maintt'][a.game]/'zzzzz_AC_Campaign.pk3') as z:
 main=z.read('ui/main.urc').decode('latin1');block=re.search(r'resource\s+Button\s*\{[^}]*name "new game old"[^}]*\}',main).group()
 assert 'stuffcommand "ac_campaign"' in block and 'ac_campaign_entry' not in main
result=dict(exit=proc.returncode,game=a.game,completed_seed=a.completed,requested=[a.width,a.height],engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),images=images,locked_names_hidden=True,main_map_action='ac_campaign',geometry=[x for x in log.splitlines() if 'AC_UI_ROOT' in x])
(r/'checkpoints/CP08'/(a.run+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
