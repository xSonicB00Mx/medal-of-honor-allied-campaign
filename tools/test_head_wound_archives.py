from pathlib import Path
import subprocess,shutil,re,json
from PIL import Image
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';results=[]
for source,label,expected in [('fixed-aa','head-legacy-v2-r2',8),('head-wrap-aa','head-nose-v3-r2',2)]:
 p=r/'profiles-local/wound-regression'/label;h=p/'main';(h/'save/omconfig').mkdir(parents=True,exist_ok=False);runner=p/'runner';runner.mkdir()
 for f in rt.glob('*.dll'):shutil.copy2(f,runner/f.name)
 for n in ['openmohaa.exe','cgame.dll','game.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,runner/n)
 shutil.copytree(r/f'profiles-local/wound-regression/{source}/main/fixture',h/'fixture')
 for ext in ['sav','ssv','tga']:shutil.copy2(r/f'profiles-local/wound-regression/{source}/main/save/omconfig/quick.{ext}',h/f'save/omconfig/reference.{ext}')
 (h/'test.cfg').write_text('\n'.join(['wait 1000','loadgame reference','wait 4000','finishloadingscreen','wait 2000','screenshot silent','savegame rerecord','wait 1500','loadgame rerecord','wait 3500','finishloadingscreen','wait 2000','screenshot silent','echo HEAD_ARCHIVE_DONE','quit']))
 cmd=[str(runner/'openmohaa.exe')]
 for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=0,ac_fx_debug=2,ac_body_wounds=1).items():cmd+=['+set',k,str(v)]
 proc=subprocess.run(cmd+['+exec','test.cfg'],cwd=rt,timeout=90)
 log=(h/'qconsole.log').read_text(encoding='latin1');counts=re.findall(r'AC_WOUND_ARCHIVE load count=(\d+)',log)
 assert proc.returncode==0 and 'HEAD_ARCHIVE_DONE' in log and counts==[str(expected)]*2 and 'AC_WOUND_DRAW' in log,(label,counts)
 for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):Image.open(f).save(r/'artifacts-local'/f'Wound-{label}-{i}.png')
 results.append(dict(run=label,load_counts=counts,exit=proc.returncode));print('PASS',label,flush=True)
(r/'generated-local/head-wound-archives.json').write_text(json.dumps(results,indent=2))
