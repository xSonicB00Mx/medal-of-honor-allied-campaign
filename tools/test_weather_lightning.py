"""Native lightning regression in an isolated copy of the current AA save.

The test-only script holds each real weather phase for repeatable screenshots.
It never changes personal saves/settings or the installed weather scripts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image, ImageChops, ImageStat

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--installed', action='store_true', help='Capture the previous renderer for comparison')
ap.add_argument('--dump-depth', action='store_true', help='Diagnostic roof/scene depth readback; not acceptance')
ap.add_argument('--width', type=int, default=1920)
ap.add_argument('--height', type=int, default=1080)
ap.add_argument('--game', type=int, choices=[0, 1, 2], default=0)
ap.add_argument('--aa-exterior-camera', action='store_true',
                help='Use a fixed m5l1b exterior camera instead of the saved player view')
ap.add_argument('--save', help='Existing save basename to copy, instead of the default QA start')
ap.add_argument('--baseline-error-log', type=Path,
                help='Old-DLL control log for matching existing BT mission script errors')
a = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', a.run)
assert a.save is None or re.fullmatch(r'[A-Za-z0-9_-]+', a.save)
assert not a.aa_exterior_camera or a.game == 0
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
p = R/'profiles-local/CP09'/a.run
folder = ['main', 'mainta', 'maintt'][a.game]
h = p/folder
h.mkdir(parents=True, exist_ok=False)
b = p/'bin'
b.mkdir()
rt = R/'runtime-local/CP09-r1'
personal = R/'profiles-local/CP08-r1/user'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
snapshot = lambda: {f.relative_to(personal).as_posix(): sha(f)
                    for f in personal.rglob('*') if f.is_file()}
before = snapshot()
for f in list(rt.glob('*.dll')) + [rt/'openmohaa.exe']:
    shutil.copy2(f, b/f.name)
if not a.installed:
    for name in ['openmohaa.exe', 'game.dll', 'cgame.dll']:
        shutil.copy2(R/'build-local/cp00-r3/RelWithDebInfo'/name, b/name)
for f in personal.rglob('*.cfg'):
    d = p/f.relative_to(personal)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, d)
d = h/'save/omconfig'
d.mkdir(parents=True)
for f in (personal/folder/'save/omconfig').glob((a.save or 'quick') + '.*'):
    shutil.copy2(f, d/('reference'+f.suffix))
if a.save:
    assert (d/'reference.sav').is_file(), 'Requested reference save is missing'

# This loop is deliberately confined to the QA copy. Holding a phase avoids
# random natural thunder changing the frame between the command and screenshot.
(h/'lightning_fixture.scr').write_text('''main:
 if (level.farplane_color == NIL)
  level.farplane_color = $world.farplane_color
 if (level.weatherFs == NIL)
  level.weatherFs = 0
 level.ac_lightning_probe_mode = 0
 level.ac_lightning_probe_running = 1
 level.thundertime = 99999
 println ("AC_LIGHTNING_PROBE base=" + level.farplane_color)
 // An archived thunder wait is already scheduled: changing its next delay
 // cannot cancel it. WCR's maximum normal wait is 20*2.5 seconds, followed by
 // less than five seconds of pulses. Drain that finite remainder in AA.
 println ("AC_LIGHTNING_SETTLE_BEGIN time=" + level.time)
 local.settle_until = level.time + QA_SETTLE_SECONDS
 while (level.time < local.settle_until)
 {
  level.thundertime = 99999
  waitthread global/weather.scr::unflash
  waitframe
 }
 println ("AC_LIGHTNING_SETTLE_END time=" + level.time)
 while (level.ac_lightning_probe_running == 1)
 {
  level.thundertime = 99999
  if (level.ac_lightning_probe_mode == 1)
  {
   waitthread global/weather.scr::flash
  }
  else if (level.ac_lightning_probe_mode == 2)
  {
   $world farplane_color (0.9 0.9 0.9)
  }
  else
  {
   waitthread global/weather.scr::unflash
  }
  waitframe
 }
end
'''.replace('QA_SETTLE_SECONDS', '55' if a.game == 0 else '0'))
for label, mode in [('off', 0), ('on', 1), ('plain_fog', 2)]:
    (h/f'lightning_{label}.scr').write_text(
        f'main:\n level.ac_lightning_probe_mode = {mode}\n'
        ' println ("AC_LIGHTNING_PROBE fastsky=" + (getcvar r_fastsky))\nend\n')

# A direct e1l1 test start can retain the introduction's black screen fade
# because of the pre-existing WCR spawn errors documented by the control run.
# Remove only that cinematic overlay in this isolated visual QA profile.
(h/'lightning_clearfade.scr').write_text('main:\n clearfade\nend\n')
if a.aa_exterior_camera:
    (h/'lightning_camera.scr').write_text('''main:
 $player.origin = ( 700 401 782 )
 level.ac_lightning_camera = spawn Camera
 level.ac_lightning_camera.origin = ( 700 401 782 )
 level.ac_lightning_camera.angles = ( 0 180 0 )
 level.ac_lightning_camera fov 90
 cuecamera level.ac_lightning_camera
end
''')

# Mirror thunder variant 1's finite timing, using the original flash/unflash
# entry points. Calling thunder itself would leave another endless random loop.
(h/'lightning_pulses.scr').write_text('''main:
 level.ac_lightning_probe_running = 0
 waitframe
 waitthread global/weather.scr::unflash
 waitthread global/weather.scr::flash
 println ("AC_LIGHTNING_PULSE ON 1 time=" + level.time)
 wait 0.2
 waitthread global/weather.scr::unflash
 println ("AC_LIGHTNING_PULSE OFF 1 time=" + level.time)
 wait 1
 waitthread global/weather.scr::flash
 println ("AC_LIGHTNING_PULSE ON 2 time=" + level.time)
 wait 0.1
 waitthread global/weather.scr::unflash
 println ("AC_LIGHTNING_PULSE OFF 2 time=" + level.time)
 wait 0.1
 waitthread global/weather.scr::flash
 println ("AC_LIGHTNING_PULSE ON 3 time=" + level.time)
 wait 0.1
 waitthread global/weather.scr::unflash
 println ("AC_LIGHTNING_PULSE OFF 3 time=" + level.time)
 println ("AC_LIGHTNING_PULSE DONE fastsky=" + (getcvar r_fastsky))
end
''')

cmd = ['wait 800', 'map e1l1' if a.game == 2 and not a.save else 'loadgame reference',
       'wait 5000', 'finishloadingscreen',
       'wait 1000', 'god', 'notarget', 'seta r_fastsky 0',
       f'set r_acLightningDebug {3 if a.dump_depth else 1}', 'set r_acObjectMotionBlur 0',
       # Fixed QA HUD geometry for the opaque compass pixel assertion below.
       'set ac_hud_scale 1.5', 'set ac_hud_safe 1', 'set ui_compass_scale 0.55',
       'script player exec lightning_clearfade.scr' if a.game == 2 and not a.save else 'wait 1',
       'script player exec lightning_camera.scr' if a.aa_exterior_camera else 'wait 1',
       'script player exec lightning_fixture.scr', 'wait 60000' if a.game == 0 else 'wait 800']
cases = []

def capture(label, mode, fastsky=0, taa=1, extra=None):
    cases.append(dict(name=label, mode=mode, fastsky=fastsky, taa=taa))
    cmd.extend([f'seta r_fastsky {fastsky}', f'set r_acTAA {taa}',
                f'script player exec lightning_{mode}.scr', 'wait 400'])
    if extra:
        cmd.extend(extra)
    cmd.extend([f'echo AC_LIGHTNING_CASE {label} BEGIN', 'wait 150',
                'screenshot silent', 'r_fastsky', f'echo AC_LIGHTNING_CASE {label} END'])

for taa in [0, 1]:
    capture(f'taa{taa}-before', 'off', taa=taa)
    capture(f'taa{taa}-flash', 'on', taa=taa)
    capture(f'taa{taa}-after', 'off', taa=taa)
capture('plain-bright-fog', 'plain_fog')
capture('fastsky-before', 'off', fastsky=1)
capture('fastsky-flash', 'on', fastsky=1)
capture('fastsky-after', 'off', fastsky=1)
capture('post-fastsky-bright-fog', 'plain_fog')
capture('saved-flash', 'on', extra=['savegame lightning_flash', 'wait 400',
        'loadgame lightning_flash', 'wait 5000', 'finishloadingscreen', 'wait 700'])
capture('loaded-unflash', 'off')
capture('restart-flash', 'on', extra=['vid_restart', 'wait 3500',
        'finishloadingscreen', 'wait 700'])
capture('restart-unflash', 'off')
if a.game == 2 and a.save == 'e2l20000':
    # This archived briefing starts with an animated fade. Compare surfaces
    # after it has completed, in both temporal modes and without moving actors.
    for taa in [0, 1]:
        for phase, mode in [('before', 'off'), ('flash', 'on'), ('after', 'off')]:
            capture(f'terrain-taa{taa}-{phase}', mode, taa=taa)
cmd += ['echo AC_LIGHTNING_PULSES_BEGIN', 'script player exec lightning_pulses.scr',
        'wait 2000', 'echo AC_LIGHTNING_PULSES_END']
capture('pulse-recovered', 'off')
cmd += ['seta r_fastsky 0', 'wait 300', 'echo AC_LIGHTNING_PROBE_DONE', 'quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args = [str(b/'openmohaa.exe')]
for k, v in dict(com_target_game=a.game, fs_basepath=rt, fs_homepath=p,
                 fs_steampath=rt, fs_gogpath=rt, fs_microsoftstorepath=rt,
                 net_enabled=0, logfile=2, developer=1, cheats=1,
                 thereisnomonkey=1, ac_campaign_mode=1, cl_playintro=0,
                 r_fullscreen=0, r_mode=-1, r_customwidth=a.width,
                 r_customheight=a.height, com_maxfps=60,
                 com_maxfpsUnfocused=60).items():
    args += ['+set', k, str(v)]
try:
    proc = subprocess.run(args+['+exec', 'probe.cfg'], cwd=b, timeout=180,
                          stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
finally:
    assert snapshot() == before, 'Personal profile changed'
log = (h/'qconsole.log').read_text(encoding='latin1')
(out/'qconsole.log').write_text(log, encoding='latin1')
assert proc.returncode == 0 and 'AC_LIGHTNING_PROBE_DONE' in log
settle_begin = float(re.search(r'AC_LIGHTNING_SETTLE_BEGIN time=([0-9.]+)', log)[1])
settle_end = float(re.search(r'AC_LIGHTNING_SETTLE_END time=([0-9.]+)', log)[1])
assert settle_end - settle_begin >= (54.99 if a.game == 0 else 0)
assert 'Script file compile error' not in log
def script_errors(text):
    location = ''
    found = set()
    for line in text.splitlines():
        match = re.search(r'\(([^()]+\.scr, \d+)\):', line)
        if match:
            location = match.group(1)
        if 'Script Error :' in line:
            found.add((location, line.split('Script Error :', 1)[1].strip()))
    return found
errors = script_errors(log)

def incoming_gl_errors(text):
    # These are errors already pending on entry to the lightning pass. Keep
    # them distinct from errors raised by the pass itself; diagnose, don't hide.
    values = [int(v) for v in re.findall(r'incoming_error=(\d+)', text)]
    return dict(samples=len(values), nonzero=sum(v != 0 for v in values),
                values=sorted(set(values)))

if errors:
    assert a.baseline_error_log, errors
    known = script_errors(a.baseline_error_log.read_text(encoding='latin1'))
    assert errors <= known, errors - known
    assert not any('lightning_' in site for site, _ in errors)
assert (d/'lightning_flash.sav').exists()
pulse_log = log.split('AC_LIGHTNING_PULSES_BEGIN', 1)[1].split(
    'AC_LIGHTNING_PULSES_END', 1)[0]
assert 'AC_LIGHTNING_PULSE DONE fastsky=0' in pulse_log
pulses = []
for number in [1, 2, 3]:
    section = pulse_log.split(f'AC_LIGHTNING_PULSE ON {number}', 1)[1].split(
        f'AC_LIGHTNING_PULSE OFF {number}', 1)[0]
    draws = re.findall(r'AC_LIGHTNING strength=([0-9.]+).*?gl_error=(\d+)', section)
    if not a.installed:
        assert draws and all(float(s) > 0 and e == '0' for s, e in draws), number
    on = re.search(rf'AC_LIGHTNING_PULSE ON {number} time=([0-9.]+)', pulse_log)
    off = re.search(rf'AC_LIGHTNING_PULSE OFF {number} time=([0-9.]+)', pulse_log)
    pulses.append(dict(number=number, rendered_frames=len(draws),
                       duration=float(off[1])-float(on[1]),
                       incoming_gl_errors=incoming_gl_errors(section)))
shots = sorted((h/'screenshots').glob('*.tga'))
assert len(shots) == len(cases), (len(shots), len(cases))
for case, shot in zip(cases, shots):
    label = case['name']
    section = log.split(f'AC_LIGHTNING_CASE {label} BEGIN', 1)[1].split(
        f'AC_LIGHTNING_CASE {label} END', 1)[0]
    assert f'"r_fastsky" is:"{case["fastsky"]}"' in section, label
    flashes = re.findall(r'AC_LIGHTNING strength=([0-9.]+).*?gl_error=(\d+)', section)
    if not a.installed:
        if case['mode'] == 'on':
            assert flashes and all(float(s) > 0 and e == '0' for s, e in flashes), label
        else:
            assert not flashes, label
    im = Image.open(shot).convert('RGB')
    dest = out/f'{label}.png'
    im.save(dest)
    # Summaries aid inspection; actual before/after screenshots remain evidence.
    sky = im.crop((a.width//4, 0, a.width*3//4, a.height//5))
    if a.aa_exterior_camera:
        # Native-verified clear sky; the broad crop also contains a nearby tree.
        sky = im.crop(tuple(round(v * (a.width / 1920 if i % 2 == 0 else a.height / 1080))
                            for i, v in enumerate((1300, 30, 1450, 180))))
    world = im.crop((a.width//4, a.height//3, a.width*3//4, a.height*2//3))
    case.update(image=dest.relative_to(R).as_posix(),
                sky_mean=sum(ImageStat.Stat(sky).mean)/3,
                sky_stddev=sum(ImageStat.Stat(sky).stddev)/3,
                world_mean=sum(ImageStat.Stat(world).mean)/3,
                active_frames=len(flashes),
                incoming_gl_errors=incoming_gl_errors(section))
hud_checks = []
if a.game == 0:
    # AA's opaque compass interior, deliberately away from its rim and any
    # world/rain pixels. HUD position and scale are fixed in this QA profile;
    # widescreen pixel geometry scales with height. Compare every RGB pixel,
    # so a white screen blend accidentally covering the HUD fails decisively.
    assert a.width / a.height >= 4 / 3, 'Compass probe requires at least 4:3'
    hud_box = tuple(round(n * a.height / 1080) for n in (78, 78, 138, 138))
    for taa in [0, 1]:
        with Image.open(out/f'taa{taa}-before.png') as im:
            base_hud = im.convert('RGB').crop(hud_box)
        for phase in ['flash', 'after']:
            label = f'taa{taa}-{phase}'
            with Image.open(out/f'{label}.png') as im:
                current_hud = im.convert('RGB').crop(hud_box)
            error = sum(ImageStat.Stat(ImageChops.difference(base_hud, current_hud)).mean) / 3
            hud_checks.append(dict(case=label, opaque_compass_bbox=hud_box,
                                   mean_absolute_rgb_difference=error, tolerance=2.0))
            assert error <= 2.0, ('Lightning changed opaque compass pixels', label, error)
if not a.installed:
    indexed = {c['name']: c for c in cases}
    for taa in [0, 1]:
        before_case = indexed[f'taa{taa}-before']
        flash = indexed[f'taa{taa}-flash']
        after_case = indexed[f'taa{taa}-after']
        assert flash['sky_mean'] > before_case['sky_mean'] + 15
        # Only exposed world pixels should flash. A minimum whole-scene
        # brightness increase could require the indoor regression we fixed.
        # Window/interior masking has its own spatial pixel test.
        assert abs(after_case['sky_mean'] - before_case['sky_mean']) < 15
    assert abs(indexed['pulse-recovered']['sky_mean'] -
               indexed['restart-unflash']['sky_mean']) < 15
terrain_checks = []
if not a.installed and not a.dump_depth and a.game == 2 and a.save == 'e2l20000':
    # Depth readback proves the first patch is a coplanar downward rock face,
    # and the others are exposed terrain. A broad "all slopes must light"
    # assertion was incorrect. Check both protected and exposed pixels, so
    # alternating covered/lit triangles cannot hide in whole-image averages.
    for taa in [0, 1]:
        base_image = Image.open(out/f'terrain-taa{taa}-before.png').convert('RGB')
        flash_image = Image.open(out/f'terrain-taa{taa}-flash.png').convert('RGB')
        for kind, box1080 in [('covered', (1580, 550, 1660, 570)),
                              ('exposed', (300, 220, 370, 315)),
                              ('exposed', (1460, 370, 1500, 380)),
                              ('exposed', (1600, 480, 1680, 500)),
                              ('exposed', (1300, 750, 1500, 850))]:
            box = tuple(round(v * (a.width / 1920 if i % 2 == 0 else a.height / 1080))
                        for i, v in enumerate(box1080))
            base_pixels = list(base_image.crop(box).get_flattened_data())
            flash_pixels = list(flash_image.crop(box).get_flattened_data())
            delta = [(sum(f)-sum(b))/3 for b, f in zip(base_pixels, flash_pixels)]
            bad = sum(abs(v) > 10 if kind == 'covered' else v < 10 for v in delta)
            fraction = bad / len(delta)
            mean_delta = sum(delta) / len(delta)
            terrain_checks.append(dict(taa=taa, kind=kind, box=box,
                                       mean_delta=mean_delta, incorrect_fraction=fraction,
                                       maximum_incorrect_fraction=0.01))
            assert fraction <= 0.01, ('BT terrain classification is discontinuous', taa, kind, box, fraction)
            assert abs(mean_delta) <= 3 if kind == 'covered' else mean_delta >= 15
result = dict(passed=True, installed_baseline=a.installed, cases=cases,
              acceptance_eligible=not a.installed and not a.dump_depth,
              pulses=pulses, hud_checks=hud_checks, terrain_checks=terrain_checks,
              incoming_gl_errors=incoming_gl_errors(log),
              pulse_scope='Finite thunder variant 1 timing through original flash/unflash; no added random thunder thread',
              game=folder, reference_save=a.save, preexisting_script_errors=sorted(errors),
              aa_exterior_camera=a.aa_exterior_camera,
              settled_weather_seconds=settle_end-settle_begin,
              engine_sha256=sha(b/'openmohaa.exe'), game_sha256=sha(b/'game.dll'),
              cgame_sha256=sha(b/'cgame.dll'), personal_files_unchanged=len(before))
(out/'result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: result[k] for k in ('passed', 'game', 'reference_save',
    'engine_sha256', 'game_sha256', 'cgame_sha256', 'personal_files_unchanged')}, indent=2))
