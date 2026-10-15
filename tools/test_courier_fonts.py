"""Capture menus and live HUD with local font packages in an isolated profile."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--game', choices=['AA', 'SH', 'BT'], default='AA')
ap.add_argument('--width', type=int, default=1920)
ap.add_argument('--height', type=int, default=1080)
ap.add_argument('--original', action='store_true')
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
runtime = root/'runtime-local/CP08-r1'
profile = root/'profiles-local/courier'/args.run
assert re.fullmatch('[a-zA-Z0-9-]+', args.run) and not profile.exists()
number, folder, game_map = {'AA':(0,'main','m2l1'), 'SH':(1,'mainta','t1l2'),
                           'BT':(2,'maintt','e2l2')}[args.game]
home = profile/folder
home.mkdir(parents=True)
if not args.original:
    for f in ['main', 'mainta', 'maintt']:
        (profile/f).mkdir(exist_ok=True)
        shutil.copy2(root/'generated-local/courier/packages'/f/'zzzzzzz_AC_Courier.pk3', profile/f)
(profile/'ac_progress.dat').write_text('ACPROG1 32767 15 keep\n')
script = 'main:\n $player nodamage\n'
for index, text, color in [(200, 'Courier New: 0123456789  Aa Bb Wm il  !?.,', '1 1 1'),
                            (201, 'Objective updated - Check your orders.', '1 0.85 0.4'),
                            (202, 'LOCKED / Friendly fire / ÄÖÜ äöü ß', '1 0.35 0.3')]:
    script += f' huddraw_align {index} left top\n huddraw_virtualsize {index} 1\n'
    script += f' huddraw_rect {index} 35 {170+(index-200)*25} 550 20\n'
    script += f' huddraw_font {index} facfont-20\n huddraw_string {index} "{text}"\n'
    script += f' huddraw_color {index} {color}\n huddraw_alpha {index} 1\n'
script += 'end\n'
(home/'font_probe.scr').write_text(script, encoding='cp1252')
commands = ['wait 1000', f'devmap {game_map}', 'wait 5000', 'finishloadingscreen',
            'set developer 1', 'script player exec font_probe.scr', 'wait 1000',
            'screenshot silent', 'set ac_hud_scale 1.4', '+scores',
            'set subtitle0 "Proceed to the rendezvous. Keep your squad together."',
            'wait 700', 'screenshot silent', '-scores', 'set subtitle0 ""',
            'ac_ui_options', 'wait 700', 'screenshot silent',
            'ac_ui_report ac_scaling', 'popmenu 0', 'wait 300', 'loadmenu controls', 'pushmenu controls',
            'wait 700', 'ac_ui_report controls', 'screenshot silent', 'popmenu 0', 'ac_level_list 0 0 1',
            'wait 700', 'screenshot silent', 'imagelist', 'echo AC_FONT_TEST_DONE', 'quit']
(home/'font_probe.cfg').write_text('\n'.join(commands)+'\n')
settings = dict(com_target_game=number, fs_basepath=runtime, fs_homepath=profile,
                fs_steampath=runtime, fs_gogpath=runtime, fs_microsoftstorepath=runtime,
                net_enabled=0, logfile=2, developer=0, cheats=1, ui_console=0,
                r_fullscreen=0, r_mode=-1, r_customwidth=args.width,
                r_customheight=args.height, com_maxfps=60, com_maxfpsUnfocused=60,
                cl_playintro=0, ac_campaign_mode=1, ac_operation=-1)
cmd = [str(runtime/'openmohaa.exe')]
for k,v in settings.items():
    cmd += ['+set', k, str(v)]
process = subprocess.run(cmd+['+exec','font_probe.cfg'], cwd=runtime, timeout=100)
log = (home/'qconsole.log').read_text(encoding='latin1')
images = []
for p in sorted((home/'screenshots').glob('*.tga')):
    with Image.open(p) as image:
        assert image.size == (args.width,args.height)
        image.save(p.with_suffix('.png'))
    images.append(p.with_suffix('.png').relative_to(root).as_posix())
errors = [line for line in log.splitlines() if any(s in line for s in
          ['Script Error','Unknown command','Invalid event','compile error',"Couldn't load font"])]
result = dict(run=args.run, game=args.game, completed='AC_FONT_TEST_DONE' in log,
              exit_code=process.returncode, errors=errors, images=images,
              original=args.original, engine_sha256=hashlib.sha256((runtime/'openmohaa.exe').read_bytes()).hexdigest())
result['font_images'] = [line for line in log.splitlines() if 'gfx/fonts/' in line]
result['passed'] = result['completed'] and process.returncode == 0 and not errors and len(images)==5
result['controls_visible'] = 'AC_UI_CURRENT controls' in log
result['passed'] = result['passed'] and result['controls_visible']
(root/'generated-local/courier'/f'{args.run}.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
assert result['passed']
