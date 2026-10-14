"""Load an actual CP4 wound save in CP5, shoot again, then round-trip CP5."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--run-id',default='compat-cp04');args=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP05-r1';p=r/'profiles-local/CP05-r1'/args.run_id;h=p/'main'
assert not p.exists()
source=r/'profiles-local/CP04-r1/wound-AA-v5/main'
(h/'save/omconfig').mkdir(parents=True)
for ext in ('.sav','.ssv','.tga'):shutil.copy2(source/('save/omconfig/cp03_blood'+ext),h/('save/omconfig/reference'+ext))
shutil.copytree(source/'cp00',h/'cp00')
(h/'compat.cfg').write_text('\n'.join([
 'seta ac_fx_debug 2','wait 1000','loadgame reference','wait 3000','finishloadingscreen','wait 1000','set developer 1',
 'script player exec cp00/inspect.scr','wait 1500','screenshot','echo AC_COMPAT_NEW_HIT',
 'script player exec cp00/colt45.scr','wait 2300','+attack','wait 120','-attack','wait 1200','screenshot',
 'savegame cp05_compat','wait 700','loadgame cp05_compat','wait 3000','finishloadingscreen','set developer 1','wait 1200','screenshot','echo AC_COMPAT_DONE','quit'])+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=960,com_maxfps=60,cl_playintro=0).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','compat.cfg'],cwd=rt,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');old=json.loads((r/'checkpoints/CP04/wound-AA-v5.json').read_text())
def transforms(text):
 return set(re.findall(r'AC_WOUND_DRAW[^\r\n]*?id=(\d+) branch=(\d+) seed=(\d+) rotation=([^ ]+) flip=([^ ]+)',text))
expected=transforms('\n'.join(old['drawn'])); before,after=log.split('AC_COMPAT_NEW_HIT',1)
assert proc.returncode==0 and 'AC_COMPAT_DONE' in log
assert expected and expected<=transforms(before),'CP4 orientation changed on migration'
roundtrip=after.rsplit('AC_WOUND_ARCHIVE load',1)[1]
assert expected<=transforms(roundtrip),'CP4 orientation changed on CP5 round-trip'
new=transforms(roundtrip)-expected
assert {t[1] for t in new}=={'0','1'},'New entry/exit not restored, possibly event ID collision'
assert all(t[1]=='0' for t in transforms(before)),'Historical exits must not be invented'
assert not any(t in log for t in ('Script Error','Unknown command','Invalid event','AC_WOUND_REMOVED'))
images=[]
for im in sorted((h/'screenshots').glob('*.tga')):
 out=im.with_suffix('.png');Image.open(im).save(out);images.append(out.relative_to(r).as_posix())
result=dict(complete=True,old_wounds_preserved=len(expected),new_wounds_restored=len(new),historical_exits_created=False,old_transforms=sorted(expected),new_transforms=sorted(new),images=images,binaries={f:hashlib.sha256((rt/f).read_bytes()).hexdigest() for f in ('openmohaa.exe','cgame.dll','game.dll')})
(r/'checkpoints/CP05'/(args.run_id+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
