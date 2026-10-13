"""Exercise actual Windows launchers, menu callbacks, thumbnails and FOV restart.

Only run on a newly deployed candidate: this creates its initial test profiles.
No fs_* override is passed by the test, so a broken launcher cannot be masked.
"""
import argparse, json, re, shutil, subprocess, time
from pathlib import Path
from inventory_cp00 import sha, save

ap=argparse.ArgumentParser()
ap.add_argument('--candidate',required=True)
ap.add_argument('--game',choices=['AA','SH','BT'],required=True)
args=ap.parse_args()
assert re.fullmatch(r'CP00-r[0-9]+',args.candidate)
repo=Path(__file__).resolve().parents[1]
game=args.game; folder={'AA':'main','SH':'mainta','BT':'maintt'}[game]
profile=repo/'profiles-local'/args.candidate/game
assert profile.exists() and not any(profile.iterdir()),'Use a fresh profile; preserve user data'
reference=repo/f'profiles-local/CP00-r1/scene-{game}/{folder}/save/omconfig'
saves=profile/folder/'save/omconfig'; saves.mkdir(parents=True)
for ext in ('sav','ssv','tga'):
    source=reference/f'cp00_{game.lower()}.{ext}'
    shutil.copy2(source,saves/source.name)
    assert sha(source)==sha(saves/source.name)
evidence=repo/'generated-local'/args.candidate/game; evidence.mkdir(parents=True,exist_ok=True)
logpath=profile/folder/'qconsole.log'

def run(label,commands):
    cfg=profile/folder/f'cp00-{label}.cfg'
    assert not cfg.exists()
    cfg.write_text('\n'.join(commands)+f'\necho CP00_{label}_DONE\nquit\n',encoding='ascii')
    cmd=['cmd.exe','/d','/c','call',str(repo/f'Start-{args.candidate}-{game}.cmd'),
         '+set','net_enabled','0','+set','developer','1','+set','r_fullscreen','0',
         '+set','r_mode','-1','+set','r_customwidth','1280','+set','r_customheight','960',
         '+set','com_maxfps','60','+set','com_maxfpsUnfocused','60',
         '+set','cl_playintro','0','+exec',cfg.name]
    assert not any(x.startswith('fs_') for x in cmd)
    subprocess.run(cmd,cwd=repo,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    deadline=time.monotonic()+100
    while time.monotonic()<deadline:
        log=logpath.read_text(encoding='latin1') if logpath.exists() else ''
        if f'CP00_{label}_DONE' in log and 'RE_Shutdown( 1 )' in log: break
        time.sleep(.5)
    else: raise RuntimeError('Launcher test timeout; preserve profile and inspect game')
    time.sleep(1)
    assert 'refusing to create relative path' not in log
    shutil.copy2(logpath,evidence/f'{label}.log')
    return log

first=run('menu',[
    'wait 1000',f'loadgame cp00_{game.lower()}','wait 2500','finishloadingscreen',
    'wait 1500','pushmenu loadsave','wait 1200','screenshot',
    'widgetcommand LoadSaveList savegame','wait 1800','screenshot',
    'popmenu 0','set cg_fov 90','cg_fov','wait 1200'])
created=[p for p in saves.glob('*.ssv') if not p.name.startswith('cp00_')]
assert created,'Menu callback did not create a new save'
for p in created:
    assert p.with_suffix('.sav').is_file() and p.with_suffix('.tga').stat().st_size>18
assert 'Game Loaded' in first,'Reference load failed'
configs=list(profile.rglob('omconfig.cfg'))
assert len(configs)==1
assert re.search(r'seta cg_fov "90"',configs[0].read_text(encoding='latin1'))
second=run('restart',[
    'wait 1000','echo CP00_FOV_RESTART','cg_fov','pushmenu video_options',
    'wait 1200','screenshot','popmenu 0','pushmenu loadsave','wait 1200','screenshot',
    f'loadgame {created[0].stem}','wait 2500','finishloadingscreen','wait 1200','screenshot'])
fov_lines=[l for l in second.splitlines() if '"cg_fov"' in l]
assert any(re.search(r'is:\s*"90',l) for l in fov_lines),fov_lines
assert 'Game Loaded' in second,'New menu save could not be loaded after restart'
result=dict(candidate=args.candidate,game=game,actual_workspace_cmd_used=True,
    fs_path_override_in_test=False,menu_callback_save_created=[p.name for p in created],
    new_save_has_thumbnail=True,new_menu_save_loaded_after_restart=True,
    load_method='Console command; actual Load-button click requires separate UI check',fov_90_persisted=True,
    fov_restart_lines=fov_lines,path_rejection=False,
    visual_check='PENDING; inspect screenshots before claiming menu rendering passed',
    evidence=[dict(path=p.relative_to(repo).as_posix(),sha256=sha(p))
              for p in [*evidence.glob('*.log'),*profile.rglob('*.tga'),configs[0]]])
save(repo/f'checkpoints/CP00/{args.candidate}-{game}-launcher-test.json',result)
print('PASS',game,': actual launcher, menu save/load, thumbnail, FOV 90 after restart',flush=True)
