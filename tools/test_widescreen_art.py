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
ap.add_argument('--menu-wait', type=int, default=1200, help='Milliseconds before each capture, including fade-in')
ap.add_argument('--menus', nargs='+', default=['main', 'briefing1a'])
ap.add_argument('--without-art', action='store_true')
ap.add_argument('--installed', action='store_true', help='Test the installed runtime and its own packages')
ap.add_argument('--all-medals', action='store_true', help='Show earned medals in this isolated test profile only')
ap.add_argument('--operations-sign', action='store_true', help='Preview the Operations hover sign without mouse input')
ap.add_argument('--menu-signs', action='store_true', help='Capture every single-player main-menu hover sign')
ap.add_argument('--overlay', type=Path, help='Additional local package directory containing main/mainta/maintt')
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
assert re.fullmatch('[a-zA-Z0-9-]+', args.run_id)
runtime = root/'runtime-local/CP08-r1'
work = root/'generated-local/widescreen'
binary = work/'bin'
if args.without_art:
    assert not list(runtime.glob('*/zzzzzz_AC_Widescreen.pk3')), 'Reference requires a runtime without the artwork package'
if args.installed:
    binary = runtime
else:
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
    if package.exists() and not args.without_art and not args.installed:
        shutil.copy2(package, profile/folder/package.name)
    if args.overlay:
        for extra in (args.overlay/folder).glob('*.pk3'):
            shutil.copy2(extra, profile/folder/extra.name)
number, folder = {'AA':(0,'main'), 'SH':(1,'mainta'), 'BT':(2,'maintt')}[args.game]
home = profile/folder
commands = ['wait 2000']
if args.operations_sign:
    commands += ['set ui_signshader newgame_sign']
if args.all_medals:
    commands += [f'set g_medal{i} 1' for i in range(6)]
    commands += [f'set g_eogmedal{i} 1' for i in range(3)]
    commands += ['set ui_medalsign armycommendation_sign', 'set ui_medaldesc armycommendation_desc']
for menu in args.menus:
    assert re.fullmatch('[a-zA-Z0-9_-]+', menu)
    # The operations map is created dynamically by its console command.
    command = {'ac_campaign_operations':'ac_campaign','ac_level_list':'ac_level_list',
               'ac_briefing_room':'ac_briefing','ac_scaling':'ac_ui_options'}.get(menu,f'pushmenu {menu}')
    commands += [command, f'wait {args.menu_wait}', f'ac_ui_report {menu}', 'screenshot', 'wait 200']
commands += ['echo AC_WIDESCREEN_TEST_DONE', 'quit']
signs = []
if args.menu_signs:
    signs = ['newgame_sign','options_sign','warrecords_sign','briefingroom_sign','maplist_sign','credits_sign'] if args.game == 'AA' else ['textures/mohmenu/new_game_sign','options_sign','textures/mohmenu/load_save_sign','textures/mohmenu/briefing_room_sign','textures/mohmenu/map_list_sign','textures/mohmenu/credits_sign']
    commands = commands[:-2]
    for sign in signs:
        commands += [f'set ui_signshader {sign}','wait 500','screenshot','wait 200']
    commands += ['echo AC_WIDESCREEN_TEST_DONE','quit']
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
assert len(images) == len(args.menus) + len(signs)
