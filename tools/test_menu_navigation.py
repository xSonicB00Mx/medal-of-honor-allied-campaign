"""Isolated native main-menu return/music and campaign presentation regression."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image

ap=argparse.ArgumentParser()
ap.add_argument('game', choices=['AA','SH','BT'])
ap.add_argument('run')
ap.add_argument('--in-game', action='store_true')
ap.add_argument('--installed', action='store_true', help='Use the delivered menu packages without historical overrides')
a=ap.parse_args()
r=Path(__file__).resolve().parents[1]
rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/menu-navigation'/a.run
p.mkdir(parents=True,exist_ok=False)
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe',b/'openmohaa.exe')
for folder in ['main','mainta','maintt']:
    h=p/folder;h.mkdir()
    if not a.installed:
        for f in (r/'generated-local/shared-menus/packages'/folder).glob('*.pk3'):shutil.copy2(f,h/f.name)
(p/'ac_progress.dat').write_text('ACPROG1 4095 12 keep\n')
number,folder,mapname={'AA':(0,'main','m1l1'),'SH':(1,'mainta','t1l1'),'BT':(2,'maintt','e1l1')}[a.game]
cmd=['wait 2500']
if a.in_game:cmd+=['map '+mapname,'wait 12000','finishloadingscreen','set autopaused 0','ac_main_menu','wait 800']
cmd+=['ac_ui_report main','screenshot silent']
for command in ['ac_campaign 0 0','ac_level_list','ac_briefing']:
    cmd += [command,'wait 600','ac_ui_report','screenshot silent','ac_main_menu','wait 600','ac_ui_report main','screenshot silent']
if not a.in_game:
    for menu in ['options_main','video_options','audio_options','advancedoptions','controls','war_records','loadsave']:
        cmd+=['ac_main_menu','pushmenu '+menu,'wait 600','ac_ui_report '+menu,'screenshot silent']
    cmd+=['ac_main_menu','set ui_signshader ac_shared/textures/ac/widescreen/operations_sign','wait 600','screenshot silent',
          'ac_campaign 12 1','wait 600','screenshot silent']
cmd+=['echo AC_NAV_DONE','quit']
(p/folder/'nav.cfg').write_text('\n'.join(cmd)+'\n')
settings=dict(com_target_game=number,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,autopaused=0,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1600,r_customheight=900,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1)
args=[str(b/'openmohaa.exe')]
for k,v in settings.items():args+=['+set',k,str(v)]
proc=subprocess.Popen(args+['+exec','nav.cfg'],cwd=rt)
try:proc.wait(timeout=100)
except subprocess.TimeoutExpired:proc.terminate();proc.wait();raise
log=(p/folder/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AC_NAV_DONE' in log
current=re.findall(r'AC_UI_CURRENT (\S+)',log)
assert current[:7]==['main','ac_campaign_operations','main','ac_level_list','main','ac_briefing_room','main'],current
assert not any(t in log for t in ['Unknown command',"Couldn't find menu",'UI EXCEPTION'])
assert (p/'ac_progress.dat').read_text()=='ACPROG1 4095 12 keep\n'
music=re.findall(r'AC_UI_MUSIC (.*?) offset=(\d+)',log)
if not a.in_game:
    offsets=[int(v) for _,v in music[:7]]
    assert offsets[-1]>offsets[0] and offsets==sorted(offsets),music
    ui=(p/folder/'ui/ac_campaign_operations.urc').read_text()
    status=re.search(r'name "status".*?\n}',ui,re.S)[0]
    assert 'CURRENT' in status and 'fgcolor 1 0.58 0.45 1' in status
else:
    assert all(int(v)>6 for v in re.findall(r'AC_MAIN_MENU context=\d+ active=(\d+)',log)), 'Lost live game'
for f in (p/folder/'screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
result=dict(game=a.game,in_game=a.in_game,menus=current,music=music,passed=True)
(p/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
