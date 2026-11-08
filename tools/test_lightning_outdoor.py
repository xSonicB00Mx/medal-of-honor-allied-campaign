"""Native window/interior lightning regression, always in an isolated save copy.

The default fixtures look at an enclosed room, an intact window and a broken
window. Use --survey to verify additional cameras before assigning pixel ROIs.
JSON views may override their map coordinates and normalized indoor/indoor_highlight/outdoor/
exterior_geometry/exterior_facade/sheltered_geometry boxes. --no-fog is diagnostic only,
never visual acceptance.
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
ap.add_argument('--installed', action='store_true')
ap.add_argument('--survey', action='store_true', help='Only capture the unflashed camera views')
ap.add_argument('--no-fog', action='store_true', help='Diagnostic control only: disable native farplane fog')
ap.add_argument('--dump-depth', action='store_true', help='Diagnostic scene/roof depth readback; not acceptance')
ap.add_argument('--no-shadow-ao', action='store_true', help='Verify weather masking independently of optional shadows/AO')
ap.add_argument('--msaa', type=int, choices=[0, 2, 4, 8, 16], help='Explicit native multisample setting')
ap.add_argument('--views', type=Path, help='JSON list of name, eye, angles and optional indoor/outdoor ROIs')
ap.add_argument('--width', type=int, default=1920)
ap.add_argument('--height', type=int, default=1080)
a = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', a.run)

# These m5l1b cameras/ROIs were verified in native 1920x1080 screenshots. Both
# intact transparent window panes and broken windows must transmit the flash.
def normalized_box(x0, y0, x1, y1):
    return [x0 / 1920, y0 / 1080, x1 / 1920, y1 / 1080]

views = [
    dict(name='closed-interior', eye=[-2760, -5160, 588], angles=[0, 270, 0],
         indoor=[normalized_box(400, 200, 1500, 850),
                 # Rear wall beside the folding-screen silhouette. A raw
                 # cross-object normal once lit a single full-height UHD column.
                 normalized_box(1641, 300, 1645, 1070)],
         # These doorway/header pixels are geometrically indoors. A sparse
         # bright seam (+94 at UHD) passed the large-room MAD average. Check
         # positive pixel outliers as well as regional means at both scales.
         indoor_highlight=[normalized_box(250, 200, 680, 270),
                           normalized_box(630, 228, 665, 250)]),
    dict(name='lower-window', eye=[-2760, -5160, 380], angles=[0, 90, 0],
         indoor=[normalized_box(100, 100, 700, 850), normalized_box(1400, 100, 1650, 850),
                 normalized_box(820, 200, 850, 650)],
         outdoor=[normalized_box(1085, 185, 1135, 245)],
         exterior_geometry=[normalized_box(885, 310, 935, 390)]),
    dict(name='outdoor-high', eye=[700, 401, 782], angles=[0, 180, 0],
         outdoor=[normalized_box(1300, 30, 1450, 180)],
         # Native image plus upward BSP rays confirm exposed shingle roof.
         # (1800,120) -> (78.03,945.22,1054.11), normal (0,-.60745,.79436).
         exterior_geometry=[normalized_box(1800, 90, 1870, 140)],
         # Both stone facades are outdoors despite shallow roof/eave coverage.
         # They must receive lateral sky light across the wall, not just along
         # isolated trim. A vertical-only ceiling mask wrongly darkened them.
         # Exclude the actual dark arch opening in the bottom-left of the
         # near wall; retain the lower wall to its right as a separate control.
         exterior_facade=[normalized_box(1500, 430, 1750, 565),
                          normalized_box(1620, 570, 1750, 620),
                          normalized_box(1300, 500, 1400, 630)]),
    dict(name='upper-window', eye=[-2760, -5160, 588], angles=[0, 90, 0],
         indoor=[normalized_box(100, 100, 700, 850), normalized_box(1400, 100, 1650, 750),
                 # BSP rays prove x820..824 is the side-facing wooden reveal
                 # (normal +X), which sees lateral sky. The opaque inward frame
                 # starts at x826 with normal -Y and must stay unlit.
                 normalized_box(826, 200, 850, 650)],
         outdoor=[normalized_box(1060, 245, 1120, 325)],
         exterior_geometry=[normalized_box(880, 350, 930, 400)]),
]
if a.views:
    views = json.loads(a.views.read_text())
for view in views:
    assert re.fullmatch(r'[A-Za-z0-9-]+', view['name'])
    assert len(view['eye']) == len(view['angles']) == 3
    for kind in ['indoor', 'indoor_highlight', 'outdoor', 'exterior_geometry', 'exterior_facade', 'sheltered_geometry']:
        for box in view.get(kind, []):
            assert len(box) == 4 and 0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1

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
for f in list(rt.glob('*.dll')) + [rt/'openmohaa.exe']:
    shutil.copy2(f, b/f.name)
if not a.installed:
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

(h/'outdoor_fixture.scr').write_text('''main:
 if (level.farplane_color == NIL)
  level.farplane_color = $world.farplane_color
 if (level.weatherFs == NIL)
  level.weatherFs = 0
 level.thundertime = 99999
 level.ac_outdoor_flash = 0
 level.ac_outdoor_cam = spawn Camera
 level.ac_outdoor_cam fov 90
 $player hide
 cuecamera level.ac_outdoor_cam
 println ("AC_OUTDOOR_BASE=" + level.farplane_color)
 println ("AC_OUTDOOR_WORLD farplane=" + $world.farplane + " bias=" + $world.farplane_bias)
 while (1)
 {
  if (level.ac_outdoor_flash == 1)
   waitthread global/weather.scr::flash
  else
   waitthread global/weather.scr::unflash
  waitframe
 }
end
''')
for phase, mode in [('before', 0), ('flash', 1), ('after', 0)]:
    (h/f'outdoor_{phase}.scr').write_text(f'main:\n level.ac_outdoor_flash = {mode}\nend\n')
vec = lambda v: '( '+' '.join(map(str, v))+' )'
for view in views:
    (h/f'outdoor_{view["name"]}.scr').write_text(f'''main:
 $player.origin = {vec(view['eye'])}
 level.ac_outdoor_cam.origin = {vec(view['eye'])}
 level.ac_outdoor_cam.angles = {vec(view['angles'])}
 cuecamera level.ac_outdoor_cam
 println AC_OUTDOOR_VIEW_{view['name']}
end
''')

cmd = ['wait 800', 'loadgame reference', 'wait 5000', 'finishloadingscreen',
       'wait 1000', 'god', 'notarget', 'seta r_fastsky 0', f'set r_acLightningDebug {3 if a.dump_depth else 2}',
       'set r_acObjectMotionBlur 0', 'ui_hud 0', 'set cg_drawviewmodel 0',
       'set ui_crosshair 0', 'set ui_gmbox 0', 'set ui_gmboxspam 0', 'set g_subtitle 0',
       f'set r_farplane_nofog {int(a.no_fog)}',
       'script player exec outdoor_fixture.scr', 'wait 500']
cases = []
if a.no_shadow_ao:
    cmd += ['set r_acModelShadows 0', 'set r_acAmbientOcclusion 0', 'wait 500']
for view in views:
    cmd += [f'script player exec outdoor_{view["name"]}.scr', 'wait 500']
    for taa in ([0] if a.survey else [0, 1]):
        cmd += [f'set r_acTAA {taa}']
        for phase in (['before'] if a.survey else ['before', 'flash', 'after']):
            label = f'{view["name"]}-taa{taa}-{phase}'
            cases.append(dict(name=label, view=view['name'], taa=taa, phase=phase))
            cmd += [f'script player exec outdoor_{phase}.scr', 'wait 500',
                    f'echo AC_OUTDOOR_CASE {label} BEGIN', 'wait 150',
                    'screenshot silent', 'r_fastsky', 'farplane_info', 'r_farplane',
                    'r_farplane_bias', 'r_farplane_nofog', 'r_ext_multisample',
                    f'echo AC_OUTDOOR_CASE {label} END']
if not a.survey:
    cmd += ['script player exec outdoor_flash.scr', 'wait 300', 'savegame outdoor_flash',
            'wait 400', 'loadgame outdoor_flash', 'wait 5000', 'finishloadingscreen',
            'wait 700']
    for phase in ['saved-flash', 'loaded-after']:
        if phase == 'loaded-after':
            cmd += ['script player exec outdoor_after.scr', 'wait 500']
        label = f'{views[-1]["name"]}-taa1-{phase}'
        cases.append(dict(name=label, view=views[-1]['name'], taa=1, phase=phase))
        cmd += [f'echo AC_OUTDOOR_CASE {label} BEGIN', 'wait 150',
                'screenshot silent', 'r_fastsky', 'farplane_info', 'r_farplane',
                'r_farplane_bias', 'r_farplane_nofog', 'r_ext_multisample',
                f'echo AC_OUTDOOR_CASE {label} END']
cmd += ['echo AC_OUTDOOR_DONE', 'quit']
(h/'outdoor_probe.cfg').write_text('\n'.join(cmd)+'\n')
args = [str(b/'openmohaa.exe')]
for k, v in dict(com_target_game=0, fs_basepath=rt, fs_homepath=p,
                 fs_steampath=rt, fs_gogpath=rt, fs_microsoftstorepath=rt,
                 net_enabled=0, logfile=2, developer=1, cheats=1,
                 thereisnomonkey=1, ac_campaign_mode=1, cl_playintro=0,
                 r_fullscreen=0, r_mode=-1, r_customwidth=a.width,
                 r_customheight=a.height, com_maxfps=60,
                 com_maxfpsUnfocused=60).items():
    args += ['+set', k, str(v)]
if a.msaa is not None:
    args += ['+set', 'r_ext_multisample', str(a.msaa)]
process_returncode = None
launch_error = None
timed_out = False
try:
    process = subprocess.run(args+['+exec', 'outdoor_probe.cfg'], cwd=b, timeout=120,
                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    process_returncode = process.returncode
except subprocess.TimeoutExpired as error:
    timed_out = True
    launch_error = str(error)
except OSError as error:
    launch_error = str(error)
finally:
    personal_unchanged = snapshot() == before
log_path = h/'qconsole.log'
log = log_path.read_text(encoding='latin1') if log_path.exists() else ''
(out/'qconsole.log').write_text(log, encoding='latin1')
# Export every completed screenshot before validating process completion. A
# native crash while loading the test save must not discard all earlier data.
shots = sorted((h/'screenshots').glob('*.tga'))
capture_errors = []
for index, shot in enumerate(shots):
    label = cases[index]['name'] if index < len(cases) else f'unexpected-{index}'
    dest = out/f'{label}.png'
    try:
        with Image.open(shot) as source:
            source.convert('RGB').save(dest)
        if index < len(cases):
            cases[index]['image'] = dest.relative_to(R).as_posix()
    except (OSError, ValueError) as error:
        # Keep even an incomplete native image for crash diagnostics.
        shutil.copy2(shot, out/f'{label}.tga')
        capture_errors.append(dict(case=label, error=str(error)))
launch = dict(process_returncode=process_returncode,
              process_returncode_hex=(f'0x{process_returncode & 0xffffffff:08x}'
                                      if process_returncode is not None else None),
              timed_out=timed_out, launch_error=launch_error,
              completed_marker='AC_OUTDOOR_DONE' in log,
              expected_screenshots=len(cases), actual_screenshots=len(shots),
              capture_errors=capture_errors, cases=cases,
              personal_profile_unchanged=personal_unchanged,
              personal_file_count=len(before),
              engine_sha256=sha(b/'openmohaa.exe'), game_sha256=sha(b/'game.dll'),
              cgame_sha256=sha(b/'cgame.dll'))
(out/'launch-result.json').write_text(json.dumps(launch, indent=2)+'\n')
assert personal_unchanged, 'Personal profile changed; see launch-result.json'
assert not launch_error and process_returncode == 0 and launch['completed_marker'], launch
assert 'AC_SAVE_ACCEPT context=0 map=m5l1b' in log, 'Reference must be the current m5l1b save'
assert 'Script Error' not in log and 'Script file compile error' not in log
assert not capture_errors, capture_errors
assert len(shots) == len(cases), (len(shots), len(cases))
gl_errors = []
for case, shot in zip(cases, shots):
    label = case['name']
    section = log.split(f'AC_OUTDOOR_CASE {label} BEGIN', 1)[1].split(
        f'AC_OUTDOOR_CASE {label} END', 1)[0]
    assert '"r_fastsky" is:"0"' in section
    for field in ['gl_error', 'incoming_error']:
        values = [int(value) for value in re.findall(rf'\b{field}=(\d+)', section)]
        nonzero = sorted(set(value for value in values if value))
        if nonzero:
            gl_errors.append(dict(case=label, field=field, values=nonzero))
    if a.msaa is not None:
        assert f'"r_ext_multisample" is:"{a.msaa}"' in section, label
checks = []
failures = [dict(requirement='No pending or lightning-pass GL errors', **issue) for issue in gl_errors]

def expect(condition, check, requirement):
    if not condition:
        failures.append(dict(requirement=requirement, **check))

def facade_coverage(before, flash):
    # Signed RGB mean per pixel: changing rain or a thin illuminated trim must
    # not hide a large unlit facade behind an acceptable regional average.
    count = before.width * before.height
    lit = sum(sum(f) - sum(b) >= 18 for b, f in zip(
        before.get_flattened_data(), flash.get_flattened_data()))
    return dict(facade_lit_pixel_fraction=lit / count,
                facade_pixel_delta_threshold=6.0,
                facade_required_lit_fraction=0.95)


def indoor_highlights(before, current, taa):
    # A tiny leak can be obvious while contributing almost nothing to MAD.
    # Track the largest positive CHANNEL change (not RGB mean). TAA may move
    # texture edges slightly, so allow isolated modest changes, never a flash.
    changes = sorted(max(0, *(f - b for b, f in zip(base, flash)))
                     for base, flash in zip(before.get_flattened_data(), current.get_flattened_data()))
    count = len(changes)
    percentile_index = min(count - 1, (count * 999 + 999) // 1000 - 1)
    highlighted = sum(value > 8 for value in changes)
    return dict(maximum_channel_brightening=changes[-1],
                percentile999_channel_brightening=changes[percentile_index],
                pixels_brightened_above8=highlighted,
                fraction_brightened_above8=highlighted / count,
                maximum_channel_tolerance=24 if taa else 8,
                percentile999_tolerance=8)


def expect_indoor_highlights(check):
    expect(check['maximum_channel_brightening'] <= check['maximum_channel_tolerance'], check,
           'Interior highlight maximum <= 8 without TAA / <= 24 with TAA')
    expect(check['percentile999_channel_brightening'] <= check['percentile999_tolerance'], check,
           'Interior highlight 99.9th percentile <= 8')


if not a.survey:
    for view in views:
        for taa in [0, 1]:
            images = {phase: Image.open(out/f'{view["name"]}-taa{taa}-{phase}.png').convert('RGB')
                      for phase in ['before', 'flash', 'after']}
            for kind in ['indoor', 'indoor_highlight', 'outdoor', 'exterior_geometry', 'exterior_facade', 'sheltered_geometry']:
                for normalized in view.get(kind, []):
                    box = tuple(round(n * (a.width if i % 2 == 0 else a.height))
                                for i, n in enumerate(normalized))
                    means = {phase: sum(ImageStat.Stat(im.crop(box)).mean)/3 for phase, im in images.items()}
                    difference = ImageChops.difference(images['before'].crop(box), images['flash'].crop(box))
                    mad = sum(ImageStat.Stat(difference).mean)/3
                    check = dict(view=view['name'], taa=taa, kind=kind, box=box, means=means,
                                 flash_delta=means['flash']-means['before'], mean_absolute_difference=mad)
                    if kind == 'exterior_facade':
                        check.update(facade_coverage(images['before'].crop(box), images['flash'].crop(box)))
                    elif kind == 'indoor_highlight':
                        check.update(indoor_highlights(images['before'].crop(box), images['flash'].crop(box), taa))
                    checks.append(check)
                    if not a.installed:
                        if kind in ['indoor', 'indoor_highlight', 'sheltered_geometry']:
                            expect(mad <= 3.0, check, 'Interior/sheltered flash MAD <= 3')
                            if kind == 'indoor_highlight':
                                expect_indoor_highlights(check)
                        elif kind == 'outdoor':
                            expect(check['flash_delta'] >= 10.0, check, 'Exterior sky flash delta >= 10')
                        elif kind in ['exterior_geometry', 'exterior_facade'] and not a.no_fog:
                            expect(check['flash_delta'] >= 10.0, check, 'Exterior geometry flash delta >= 10')
                            if kind == 'exterior_facade':
                                expect(check['facade_lit_pixel_fraction'] >= 0.95, check,
                                       'At least 95% of exterior facade pixels brighten by >= 6')
                        expect(abs(means['after']-means['before']) <= 3.0, check, 'Unflash recovery delta <= 3')
            for im in images.values():
                im.close()
    assert (save/'outdoor_flash.sav').is_file()
    # The active weather thread/camera are archived together. Verify the flash
    # still observes the interior mask after loading and then clears normally.
    view = views[-1]
    baseline = Image.open(out/f'{view["name"]}-taa1-before.png').convert('RGB')
    for phase in ['saved-flash', 'loaded-after']:
        with Image.open(out/f'{view["name"]}-taa1-{phase}.png') as source:
            restored = source.convert('RGB')
        for kind in ['indoor', 'indoor_highlight', 'outdoor', 'exterior_geometry', 'exterior_facade', 'sheltered_geometry']:
            for normalized in view.get(kind, []):
                box = tuple(round(n * (a.width if i % 2 == 0 else a.height))
                            for i, n in enumerate(normalized))
                base = baseline.crop(box)
                current = restored.crop(box)
                delta = (sum(ImageStat.Stat(current).mean)-sum(ImageStat.Stat(base).mean))/3
                mad = sum(ImageStat.Stat(ImageChops.difference(base, current)).mean)/3
                check = dict(view=view['name'], taa=1, phase=phase, kind=kind,
                             box=box, flash_delta=delta, mean_absolute_difference=mad)
                if kind == 'exterior_facade':
                    check.update(facade_coverage(base, current))
                elif kind == 'indoor_highlight':
                    check.update(indoor_highlights(base, current, 1))
                checks.append(check)
                if not a.installed:
                    if kind in ['indoor', 'indoor_highlight', 'sheltered_geometry'] or phase == 'loaded-after':
                        expect(mad <= 3.0, check, 'Restored interior/unflash MAD <= 3')
                        if kind == 'indoor_highlight':
                            expect_indoor_highlights(check)
                    elif kind == 'outdoor':
                        expect(delta >= 10.0, check, 'Restored exterior sky flash delta >= 10')
                    elif kind in ['exterior_geometry', 'exterior_facade'] and not a.no_fog:
                        expect(delta >= 10.0, check, 'Restored exterior geometry flash delta >= 10')
                        if kind == 'exterior_facade':
                            expect(check['facade_lit_pixel_fraction'] >= 0.95, check,
                                   'At least 95% of restored exterior facade pixels brighten by >= 6')
        restored.close()
    baseline.close()
result = dict(passed=not failures, survey=a.survey, installed_baseline=a.installed,
              launch=launch,
              diagnostic_no_fog=a.no_fog,
              optional_shadows_ao_disabled=a.no_shadow_ao,
              requested_msaa=a.msaa, gl_errors=gl_errors,
              acceptance_eligible=not a.no_fog and not a.dump_depth and not a.survey and not a.installed,
              pixel_acceptance_checked=bool(checks),
              views=views, cases=cases, checks=checks, failures=failures,
              engine_sha256=sha(b/'openmohaa.exe'), game_sha256=sha(b/'game.dll'),
              cgame_sha256=sha(b/'cgame.dll'), personal_files_unchanged=len(before))
(out/'result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: result[k] for k in ('passed', 'survey', 'installed_baseline',
    'engine_sha256', 'game_sha256', 'cgame_sha256', 'personal_files_unchanged')}, indent=2))
assert not failures, f'{len(failures)} pixel checks failed; see {out / "result.json"}'
