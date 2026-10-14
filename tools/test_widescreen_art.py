"""Render approved widescreen artwork in isolated profiles; leave the user build untouched."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--run-id', required=True)
ap.add_argument('--game', choices=['AA', 'SH', 'BT'], default='AA')
ap.add_argument('--width', type=int, default=1920)
ap.add_argument('--height', type=int, default=1080)
ap.add_argument('--menus', nargs='+', default=['main', 'briefing1a'])
ap.add_argument('--without-art', action='store_true')
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
assert re.fullmatch('[a-zA-Z0-9-]+', args.run_id)
runtime = root/'runtime-local/CP08-r1'
work = root/'generated-local/widescreen'
binary = work/'bin'
binary.mkdir(exist_ok=True)
for dll in runtime.glob('*.dll'):
    shutil.copy2(dll, binary/dll.name)
shutil.copy2(root/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe', binary/'openmohaa.exe')
profile = root/'profiles-local/widescreen'/args.run_id
assert not profile.exists()
profile.mkdir(parents=True)
for folder in ['main', 'mainta', 'maintt']:
    (profile/folder).mkdir()
    package = work/'packages'/folder/'zzzzzz_AC_Widescreen.pk3'
    if package.exists() and not args.without_art:
        shutil.copy2(package, profile/folder/package.name)
number, folder = {'AA':(0,'main'), 'SH':(1,'mainta'), 'BT':(2,'maintt')}[args.game]
home = profile/folder
commands = ['wait 2000']
for menu in args.menus:
    assert re.fullmatch('[a-zA-Z0-9_-]+', menu)
    # The operations map is created dynamically by its console command.
    command = 'ac_campaign' if menu == 'ac_campaign_operations' else f'pushmenu {menu}'
    commands += [command, 'wait 1200', f'ac_ui_report {menu}', 'screenshot', 'wait 200']
commands += ['echo AC_WIDESCREEN_TEST_DONE', 'quit']
(home/'wide-test.cfg').write_text('\n'.join(commands)+'\n', encoding='ascii')
settings = dict(com_target_game=number, fs_basepath=runtime, fs_homepath=profile,
    fs_steampath=runtime, fs_gogpath=runtime, fs_microsoftstorepath=runtime,
    net_enabled=0, logfile=2, developer=0, r_fullscreen=0, r_mode=-1,
    r_customwidth=args.width, r_customheight=args.height, com_maxfps=60,
    com_maxfpsUnfocused=60, cl_playintro=0, ui_console=0)
cmd = [str(binary/'openmohaa.exe')]
for key, value in settings.items():
    cmd += ['+set', key, str(value)]
process = subprocess.Popen(cmd+['+exec','wide-test.cfg'], cwd=runtime)
try:
    process.wait(timeout=90)
except subprocess.TimeoutExpired:
    process.terminate()
    process.wait()
    raise
log = (home/'qconsole.log').read_text(encoding='latin1')
errors = [line for line in log.splitlines() if any(error in line for error in
    ['Unknown command', 'Invalid event', 'Failed to find resource', 'Script Error', "Couldn't find menu"]) ]
images = []
for file in sorted((home/'screenshots').glob('*.tga')):
    output = file.with_suffix('.png')
    with Image.open(file) as image:
        image.save(output)
        assert image.size == (args.width, args.height)
    images.append(str(output))
result = dict(game=args.game, dimensions=[args.width,args.height], menus=args.menus,
    exit_code=process.returncode, completed='AC_WIDESCREEN_TEST_DONE' in log,
    errors=errors, images=images, geometry=[line for line in log.splitlines() if 'AC_UI_ROOT' in line])
(work/(args.run_id+'.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
assert process.returncode == 0 and result['completed'] and not errors
assert len(images) == len(args.menus)
