"""Load a copy of the user's BT save; never write into the personal profile."""
from pathlib import Path
import argparse,subprocess,shutil,hashlib,json,re,math
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--turn',type=int,default=0);ap.add_argument('--expect-ground',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';user=r/'profiles-local/CP08-r1/user';p=r/'profiles-local/mortar'/a.run;h=p/'maintt';(h/'save/omconfig').mkdir(parents=True,exist_ok=False)
hashes=lambda:{str(f.relative_to(user)):hashlib.sha256(f.read_bytes()).hexdigest() for f in user.rglob('*') if f.is_file()}
before=hashes()
for ext in ['.sav','.ssv','.tga']:shutil.copy2(user/('maintt/save/omconfig/quick'+ext),h/('save/omconfig/reference'+ext))
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
for folder in ['main','mainta','maintt']:
 (p/folder).mkdir(exist_ok=True)
 for f in (r/'generated-local/mortar/packages'/folder).glob('*.pk3'):shutil.copy2(f,p/folder/f.name)
cmd=['wait 1000','loadgame reference','wait 4000','finishloadingscreen','set developer 1','set ac_mortar_debug 1','wait 1500','screenshot silent','echo MORTAR_FIRE','+attack','wait 100','-attack','wait 2500','screenshot silent','savegame mortar-test','wait 800','loadgame mortar-test','wait 4000','finishloadingscreen','wait 1000','screenshot silent','echo MORTAR_TEST_DONE','quit']
if a.turn:
 turn='right' if a.turn>0 else 'left'
 cmd[7:7]=['+'+turn,f'wait {abs(a.turn)}','-'+turn,'wait 500']
cmd[-2:-2]=['+use','wait 100','-use','wait 500','echo MORTAR_UNMOUNTED','wait 500','screenshot silent']
(h/'test.cfg').write_text('\n'.join(cmd)+'\n')
settings=dict(com_target_game=2,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=0,ac_mortar_debug=1)
args=[str(b/'openmohaa.exe')]
for k,v in settings.items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=100)
log=(h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'MORTAR_TEST_DONE' in log
assert hashes()==before,'Personal profile changed during test'
for f in (h/'screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
report=dict(predictions=re.findall(r'AC_MORTAR_AIM[^\n]+',log),impacts=re.findall(r'AC_MORTAR_IMPACT[^\n]+',log),errors=[l for l in log.splitlines() if any(s in l for s in ['Script Error','Unknown command','Invalid event','Unsupported AC wound','Failed to load'])],profile_preserved=True)
before_launch=log.split('AC_MORTAR_LAUNCH')[0]
pred=re.findall(r'AC_MORTAR_AIM[^\n]*point=([^ ]+)',before_launch)[-1]
actual=report['impacts'][-1].split('point=')[1]
report['launch_prediction_error']=math.dist(list(map(float,pred.split(','))),list(map(float,actual.split(','))))
if a.expect_ground:assert report['launch_prediction_error']<0.1
assert 'AC_MORTAR_AIM' not in log.split('MORTAR_UNMOUNTED')[-1]
assert len(report['predictions'])>20 and len(report['impacts'])>=2
if not a.turn:assert 'AC_MORTAR_BLOCK' not in log
assert (h/'save/omconfig/mortar-test.sav').exists()
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:(len(v) if k=='predictions' else v) for k,v in report.items()}))
