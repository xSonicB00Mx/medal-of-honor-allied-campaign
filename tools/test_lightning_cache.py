"""Native lightning-cache lifecycle regression in an isolated AA save copy.

Clones the map's real visible intro-door brush, then moves, rotates, hides,
shows and removes the clone. Renderer counters prove dynamic invalidation and
static reuse; screenshots are review artifacts, not automated visual proof.
Same-map Save/Load verifies reuse; a graphics restart verifies invalidation.
Only in this fixture, authored wind shutters are hidden so the stationary
control is actually stationary. Separate ordinary weather tests keep them.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--debug', type=int, choices=[2, 4], default=2)
a = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', a.run)
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
p = R/'profiles-local/CP09'/a.run
h = p/'main'
h.mkdir(parents=True, exist_ok=False)
b = p/'bin'
b.mkdir()
rt = R/'runtime-local/CP09-r1'
personal = R/'profiles-local/CP08-r1/user'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
snapshot = lambda: {f.relative_to(personal).as_posix(): sha(f)
                    for f in personal.rglob('*') if f.is_file()}
before = snapshot()
for f in list(rt.glob('*.dll'))+[rt/'openmohaa.exe']:
    shutil.copy2(f, b/f.name)
for name in ['openmohaa.exe', 'game.dll', 'cgame.dll']:
    shutil.copy2(R/'build-local/cp00-r3/RelWithDebInfo'/name, b/name)
for f in personal.rglob('*.cfg'):
    dest = p/f.relative_to(personal)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dest)
save = h/'save/omconfig'
save.mkdir(parents=True)
for f in (personal/'main/save/omconfig').glob('quick.*'):
    shutil.copy2(f, save/('reference'+f.suffix))

(h/'cache_setup.scr').write_text('''main:
 if (level.farplane_color == NIL)
  level.farplane_color = $world.farplane_color
 if (level.weatherFs == NIL)
  level.weatherFs = 0
 level.thundertime = 99999
 level.ac_cache_flash = 1
 $player hide
 $player.origin = ( -2760 -5160 588 )
 level.ac_cache_cam = spawn Camera
 level.ac_cache_cam fov 90
 level.ac_cache_cam.origin = ( -2760 -5160 588 )
 level.ac_cache_cam.angles = ( 0 90 0 )
 cuecamera level.ac_cache_cam
 // Native diagnosis proved these authored shutters rotate every frame.
 // Hide only their test-profile copies to isolate the controlled door below.
 for (local.i=1;local.i<level.lshutters+1;local.i++)
  level.lshutter[local.i] hide
 for (local.i=1;local.i<level.rshutters+1;local.i++)
  level.rshutter[local.i] hide
 println AC_CACHE_SHUTTERS_HIDDEN
 println AC_CACHE_SETUP
 while (1)
 {
  if (level.ac_cache_flash == 1)
   waitthread global/weather.scr::flash
  else
   waitthread global/weather.scr::unflash
  waitframe
 }
end
''')
actions = {
    'spawn': '''level.ac_cache_brush = spawn script_object
 level.ac_cache_brush model "*12"
 level.ac_cache_brush.origin = ( -2792 -5096 588 )
 level.ac_cache_brush.angles = ( 0 0 0 )
 level.ac_cache_brush alwaysdraw
 println ("AC_CACHE_SPAWN ent=" + level.ac_cache_brush.entnum + " brush=" + level.ac_cache_brush.brushmodel + " origin=" + level.ac_cache_brush.origin)''',
    'translate': '''level.ac_cache_brush.origin = ( -2696 -5096 588 )
 println ("AC_CACHE_TRANSLATE origin=" + level.ac_cache_brush.origin)''',
    'rotate': '''level.ac_cache_brush.angles = ( 0 45 0 )
 println ("AC_CACHE_ROTATE angles=" + level.ac_cache_brush.angles)''',
    'dark-move': '''level.ac_cache_brush.origin = ( -2600 -5096 588 )
 println ("AC_CACHE_DARK_MOVE origin=" + level.ac_cache_brush.origin)''',
    'reflash': 'level.ac_cache_flash = 1\n println AC_CACHE_REFLASH',
    'hide': 'level.ac_cache_brush hide\n println AC_CACHE_HIDE',
    'show': 'level.ac_cache_brush show\n println AC_CACHE_SHOW',
    'remove': '''level.ac_cache_brush remove
 level.ac_cache_brush = NIL
 println AC_CACHE_REMOVE''',
}
(h/'cache_unflash.scr').write_text('main:\n level.ac_cache_flash = 0\n waitthread global/weather.scr::unflash\nend\n')
for name, body in actions.items():
    (h/f'cache_{name}.scr').write_text(f'main:\n {body}\nend\n')
setup = ['loadgame reference', 'wait 5000', 'finishloadingscreen', 'wait 1000',
         'god', 'notarget', 'set r_fastsky 0', 'set r_acLightningDebug 2',
         'set r_acTAA 0', 'set r_acObjectMotionBlur 0', 'ui_hud 0',
         'set cg_drawviewmodel 0', 'set ui_crosshair 0', 'set ui_gmbox 0',
         'set ui_gmboxspam 0', 'set g_subtitle 0',
         'script player exec cache_setup.scr', 'wait 800',
         f'set r_acLightningDebug {a.debug}']
cmd = ['wait 800']+setup
cases = ['baseline', 'spawn', 'stable', 'translate', 'rotate', 'dark-move', 'reflash', 'hide', 'show',
         'remove', 'reload', 'reload-stable', 'restart']
for name in cases:
    if name == 'dark-move':
        cmd += ['script player exec cache_unflash.scr', 'wait 500']
    cmd += [f'echo AC_CACHE_CASE {name} BEGIN']
    if name in actions:
        cmd += [f'script player exec cache_{name}.scr']
    elif name == 'reload':
        cmd += setup
    elif name == 'restart':
        cmd += ['vid_restart', 'wait 5000', 'finishloadingscreen', 'wait 800']
    cmd += ['wait 700', 'screenshot silent', 'r_fastsky',
            f'echo AC_CACHE_CASE {name} END']
cmd += ['echo AC_CACHE_DONE', 'quit']
(h/'cache_probe.cfg').write_text('\n'.join(cmd)+'\n')
args = [str(b/'openmohaa.exe')]
for k, v in dict(com_target_game=0, fs_basepath=rt, fs_homepath=p,
                 fs_steampath=rt, fs_gogpath=rt, fs_microsoftstorepath=rt,
                 net_enabled=0, logfile=2, developer=1, cheats=1,
                 thereisnomonkey=1, ac_campaign_mode=1, cl_playintro=0,
                 r_fullscreen=0, r_mode=-1, r_customwidth=1920,
                 r_customheight=1080, r_ext_multisample=0,
                 r_acLightningDebug=2, com_maxfps=60,
                 com_maxfpsUnfocused=60).items():
    args += ['+set', k, str(v)]
returncode = None
launch_error = None
try:
    proc = subprocess.run(args+['+exec', 'cache_probe.cfg'], cwd=b, timeout=100,
                          stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    returncode = proc.returncode
except (subprocess.TimeoutExpired, OSError) as error:
    launch_error = str(error)
finally:
    personal_unchanged = snapshot() == before
log_path = h/'qconsole.log'
log = log_path.read_text(encoding='latin1') if log_path.exists() else ''
(out/'qconsole.log').write_text(log, encoding='latin1')
shots = sorted((h/'screenshots').glob('*.tga'))
for index, shot in enumerate(shots):
    name = cases[index] if index < len(cases) else f'unexpected-{index}'
    with Image.open(shot) as im:
        im.convert('RGB').save(out/f'{name}.png')
failures = []
checks = []
def expect(condition, requirement, **details):
    if not condition:
        failures.append(dict(requirement=requirement, **details))
expect(personal_unchanged, 'Personal profile remains unchanged')
expect(returncode == 0 and not launch_error and 'AC_CACHE_DONE' in log,
       'Native process completes', returncode=returncode, error=launch_error)
expect('AC_SAVE_ACCEPT context=0 map=m5l1b' in log, 'Reference is the AA m5l1b save')
expect('Script Error' not in log and 'Script file compile error' not in log,
       'No fixture script errors')
expect(len(shots) == len(cases), 'All native screenshots captured', count=len(shots))
expect('AC_CACHE_SHUTTERS_HIDDEN' in log, 'Controlled fixture hides continuously moving shutters')
expect(bool(re.search(r'AC_CACHE_SPAWN ent=\d+ brush=\*12 origin=', log)),
       'Spawned entity reports the verified real brush model')
line_pattern = re.compile(r'AC_LIGHTNING [^\r\n]+')
def fields(line):
    return {key: value for key, value in re.findall(r'(\w+)=([^\s]+)', line)}
all_rows = [fields(line) for line in line_pattern.findall(log)]
expect(any(row.get('static_rebuilt') == '1' for row in all_rows),
       'Initial world prepares immutable architecture')
for row in all_rows:
    expect(row.get('gl_error') == '0' and row.get('incoming_error') == '0',
           'No pending or lightning GL errors', row=row)
base_count = None
for name in cases:
    begin, end = f'AC_CACHE_CASE {name} BEGIN', f'AC_CACHE_CASE {name} END'
    if begin not in log or end not in log:
        expect(False, 'Case markers complete', case=name)
        continue
    section = log.split(begin, 1)[1].split(end, 1)[0]
    rows = [fields(line) for line in line_pattern.findall(section)]
    if name == 'dark-move':
        expect('AC_CACHE_DARK_MOVE origin=' in section, 'Door moves during unflash', case=name)
        expect(not rows, 'Unflash performs no atlas refresh or draw work', case=name, samples=len(rows))
        expect('"r_fastsky" is:"0"' in section, 'Fastsky preference stays zero', case=name)
        checks.append(dict(case=name, samples=len(rows), inactive_atlas_work_skipped=not rows))
        continue
    required = ['static_rebuilt', 'dynamic_rebuilt', 'brushes', 'spatial']
    usable = [row for row in rows if all(key in row for key in required)]
    expect(len(usable) >= 6, 'Sufficient renderer cache samples', case=name, count=len(usable))
    if len(usable) < 6:
        continue
    static = sum(int(row['static_rebuilt']) for row in usable)
    dynamic = sum(int(row['dynamic_rebuilt']) for row in usable)
    tail = usable[-6:]
    count = int(tail[-1]['brushes'])
    check = dict(case=name, samples=len(usable), static_rebuilds=static,
                 dynamic_rebuilds=dynamic, settled_brush_count=count)
    checks.append(check)
    expect(all(row['spatial'] == '1' for row in tail), 'Spatial atlas valid after settling', **check)
    expect(all(row['static_rebuilt'] == row['dynamic_rebuilt'] == '0' for row in tail),
           'Unchanged frames reuse both caches', **check)
    if name == 'restart':
        expect(static >= 1, 'Graphics restart rebuilds immutable architecture', **check)
    else:
        expect(static == 0, 'Door/camera/same-world SaveLoad reuse immutable architecture', **check)
    if name in actions:
        expect(dynamic >= 1, 'Changed door invalidates dynamic atlas', **check)
    if name == 'baseline':
        base_count = count
    if base_count is not None:
        expected_count = base_count + int(name in ['spawn', 'stable', 'translate', 'rotate', 'reflash', 'show'])
        expect(count == expected_count, 'Brush membership follows spawn/hide/show/remove',
               expected_count=expected_count, **check)
    expect('"r_fastsky" is:"0"' in section, 'Fastsky preference stays zero', case=name)
result = dict(passed=not failures, acceptance_eligible=False,
              scope='Cache lifecycle only; screenshots require separate visual review',
              fixture_hides_authored_wind_shutters=True,
              checks=checks, failures=failures, process_returncode=returncode,
              launch_error=launch_error, screenshots=len(shots),
              personal_profile_unchanged=personal_unchanged,
              personal_files_unchanged=len(before),
              engine_sha256=sha(b/'openmohaa.exe'), game_sha256=sha(b/'game.dll'),
              cgame_sha256=sha(b/'cgame.dll'))
(out/'result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
assert not failures, 'See result.json for cache lifecycle failures'
