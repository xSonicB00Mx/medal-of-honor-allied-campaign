"""Verify migration of legacy flinch settings and precedence of saved percentages."""
from pathlib import Path
import json,subprocess,shutil
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';root=r/'profiles-local/flinch/migration-percent';root.mkdir(parents=True,exist_ok=False)
b=root/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe',b/'openmohaa.exe')
rows=[]
for name,legacy,percent,expected in [('off',0,None,0),('reduced',1,None,20),('original',2,None,100),('existing',0,70,70),('fresh',None,None,20)]:
 p=root/name;h=p/'main';(h/'configs').mkdir(parents=True)
 config=''
 if legacy is not None:config+=f'seta ac_player_flinch_mode "{legacy}"\n'
 if percent is not None:config+=f'seta ac_player_flinch_percent "{percent}"\n'
 (h/'configs/omconfig.cfg').write_text(config)
 (h/'test.cfg').write_text('wait 300\nwriteconfig verified\nquit\n')
 settings=dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,cl_playintro=0,ac_campaign_mode=0,r_fullscreen=0,r_mode=-1,r_customwidth=960,r_customheight=540,config='omconfig.cfg')
 args=[str(b/'openmohaa.exe')]
 for k,v in settings.items():args+=['+set',k,str(v)]
 proc=subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=30)
 assert proc.returncode==0
 text=(h/'configs/verified.cfg').read_text()
 assert f'seta ac_player_flinch_percent "{expected}"' in text,(name,text)
 rows.append(dict(case=name,expected=expected,passed=True))
(root/'result.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
