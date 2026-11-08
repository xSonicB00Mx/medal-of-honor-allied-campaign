"""Native paired old/new-DLL test for a BT save archived during lightning.

Only an isolated copy of e2l20000 is loaded. The old DLL calls the original
weather flash once, then archives a long wait, not a repeating flash fixture.
The candidate must recover that flash before issuing any fresh weather request.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image, ImageStat

R = Path(__file__).resolve().parents[1]
OLD_GAME_SHA = '3d6e1833ec1709f903d9177e748ba34224b3a883e14576b2074acf8624fa590c'
ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--old-runtime', type=Path, default=R/'runtime-local/CP09-r1')
ap.add_argument('--width', type=int, default=1920)
ap.add_argument('--height', type=int, default=1080)
a = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', a.run)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a.old_runtime/'game.dll') == OLD_GAME_SHA, 'The pre-lightning DLL is required'
personal = R/'profiles-local/CP08-r1/user'
snapshot = lambda: {f.relative_to(personal).as_posix(): sha(f)
                    for f in personal.rglob('*') if f.is_file()}
before = snapshot()
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
p = R/'profiles-local/CP09'/a.run
h = p/'maintt'
h.mkdir(parents=True, exist_ok=False)
save = h/'save/omconfig'
save.mkdir(parents=True)
for f in personal.rglob('*.cfg'):
    dest = p/f.relative_to(personal)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dest)
for f in (personal/'maintt/save/omconfig').glob('e2l20000.*'):
    shutil.copy2(f, save/('reference'+f.suffix))
assert (save/'reference.sav').exists()

bins = {}
for stage in ['old', 'candidate']:
    b = p/('bin-'+stage)
    b.mkdir()
    for f in list(a.old_runtime.glob('*.dll')) + [a.old_runtime/'openmohaa.exe']:
        shutil.copy2(f, b/f.name)
    if stage == 'candidate':
        for name in ['openmohaa.exe', 'game.dll', 'cgame.dll']:
            shutil.copy2(R/'build-local/cp00-r3/RelWithDebInfo'/name, b/name)
    bins[stage] = b

# Do not even read the new marker or the AA-only storm flag in these scripts:
# reading an undefined script variable could create an archived NIL entry.
scripts = {
    'legacy_weather_prepare.scr': '''main:
 if (level.farplane_color == NIL)
  level.farplane_color = $world.farplane_color
 if (level.weatherFs == NIL)
  level.weatherFs = 0
 level.thundertime = 99999
 println ("AC_LEGACY_BASE=" + level.farplane_color)
end
''',
    'legacy_weather_hold.scr': '''main:
 waitthread global/weather.scr::flash
 println ("AC_LEGACY_HELD fastsky=" + (getcvar r_fastsky))
 wait 10000
end
''',
    'legacy_weather_off.scr': '''main:
 waitthread global/weather.scr::unflash
 println ("AC_LEGACY_UNFLASH fastsky=" + (getcvar r_fastsky))
end
''',
    'legacy_plain_fog.scr': '''main:
 $world farplane_color (0.9 0.9 0.9)
 println ("AC_LEGACY_PLAIN_FOG fastsky=" + (getcvar r_fastsky))
end
''',
}
for name, script in scripts.items():
    (h/name).write_text(script)

def capture(label):
    return [f'echo AC_LEGACY_CASE {label} BEGIN', 'wait 300',
            'screenshot silent', 'r_fastsky', f'echo AC_LEGACY_CASE {label} END']

old_commands = ['wait 800', 'loadgame reference', 'wait 5000',
                'finishloadingscreen', 'wait 1000', 'god', 'notarget',
                'seta r_fastsky 0', 'set r_acTAA 1', 'set r_acObjectMotionBlur 0',
                'script player exec legacy_weather_prepare.scr', 'wait 200']
old_commands += capture('old-before')
old_commands += ['script player exec legacy_weather_hold.scr', 'wait 500']
old_commands += capture('old-held')
old_commands += ['savegame legacy_flash', 'wait 700', 'echo AC_LEGACY_OLD_DONE', 'quit']

# No flash script is executed in this process. The archived wait must resume
# without re-entering flash; the first stable frame proves state restoration.
new_commands = ['wait 800', 'seta r_fastsky 0', 'set r_acLightningDebug 1',
                'set r_acTAA 1', 'set r_acObjectMotionBlur 0',
                'echo AC_LEGACY_LOAD_BEGIN', 'loadgame legacy_flash', 'wait 5000',
                'finishloadingscreen', 'wait 800']
new_commands += capture('recovered-first-stable')
new_commands += ['script player exec legacy_weather_off.scr', 'wait 500']
new_commands += capture('unflash')
new_commands += ['script player exec legacy_plain_fog.scr', 'wait 500']
new_commands += capture('plain-bright-fog')
new_commands += ['script player exec legacy_weather_off.scr', 'wait 200',
                 'echo AC_LEGACY_CANDIDATE_DONE', 'quit']

def launch(stage, commands, labels):
    (h/'legacy_probe.cfg').write_text('\n'.join(commands)+'\n')
    b = bins[stage]
    args = [str(b/'openmohaa.exe')]
    values = dict(com_target_game=2, fs_basepath=a.old_runtime, fs_homepath=p,
                  fs_steampath=a.old_runtime, fs_gogpath=a.old_runtime,
                  fs_microsoftstorepath=a.old_runtime, net_enabled=0,
                  logfile=2, developer=1, cheats=1, thereisnomonkey=1,
                  ac_campaign_mode=1, cl_playintro=0, r_fullscreen=0, r_mode=-1,
                  r_customwidth=a.width, r_customheight=a.height,
                  com_maxfps=60, com_maxfpsUnfocused=60)
    for name, value in values.items():
        args += ['+set', name, str(value)]
    shots_before = set((h/'screenshots').glob('*.tga'))
    process = subprocess.run(args+['+exec', 'legacy_probe.cfg'], cwd=b, timeout=55,
                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    log = (h/'qconsole.log').read_text(encoding='latin1')
    (out/f'{stage}.log').write_text(log, encoding='latin1')
    assert process.returncode == 0 and f'AC_LEGACY_{stage.upper()}_DONE' in log, stage
    assert 'Script Error' not in log and 'Script file compile error' not in log, stage
    shots = sorted(set((h/'screenshots').glob('*.tga')) - shots_before)
    assert len(shots) == len(labels), (stage, len(shots))
    cases = []
    for label, shot in zip(labels, shots):
        section = log.split(f'AC_LEGACY_CASE {label} BEGIN', 1)[1].split(
            f'AC_LEGACY_CASE {label} END', 1)[0]
        assert '"r_fastsky" is:"0"' in section, label
        draws = re.findall(r'AC_LIGHTNING strength=([0-9.]+).*?gl_error=(\d+)', section)
        if stage == 'candidate':
            if label == 'recovered-first-stable':
                assert draws and all(float(s) > 0 and e == '0' for s, e in draws), label
            else:
                assert not draws, label
        im = Image.open(shot).convert('RGB')
        dest = out/f'{label}.png'
        im.save(dest)
        sky = im.crop((a.width//4, 0, a.width*3//4, a.height//5))
        world = im.crop((a.width//4, a.height//3, a.width*3//4, a.height*2//3))
        cases.append(dict(name=label, image=dest.relative_to(R).as_posix(),
                          active_frames=len(draws), sky_mean=sum(ImageStat.Stat(sky).mean)/3,
                          world_mean=sum(ImageStat.Stat(world).mean)/3,
                          incoming_gl_errors=sorted(set(map(int, re.findall(
                              r'incoming_error=(\d+)', section))))))
    return log, cases

try:
    old_log, old_cases = launch('old', old_commands, ['old-before', 'old-held'])
    assert old_log.count('AC_LEGACY_HELD fastsky=0') == 1
    assert (save/'legacy_flash.sav').is_file() and (save/'legacy_flash.ssv').is_file()
    legacy_sha = sha(save/'legacy_flash.sav')
    candidate_log, candidate_cases = launch('candidate', new_commands,
        ['recovered-first-stable', 'unflash', 'plain-bright-fog'])
    assert sha(save/'legacy_flash.sav') == legacy_sha, 'Candidate changed the legacy input save'
    assert 'AC_LEGACY_HELD fastsky=' not in candidate_log, 'Archived flash was re-executed'
    assert 'AC_SAVE_ACCEPT context=2 map=e2l2' in candidate_log
    first, off, _ = candidate_cases
    assert first['sky_mean'] > off['sky_mean'] + 15
    assert first['world_mean'] > off['world_mean'] + 15
finally:
    assert snapshot() == before, 'Personal profile changed'

result = dict(passed=True, game='maintt', map='e2l2', source_save='e2l20000',
              legacy_save_sha256=legacy_sha, personal_files_unchanged=len(before),
              scope='One real BT flash on old DLL, archived wait, recover on new DLL before any fresh flash',
              old_cases=old_cases, candidate_cases=candidate_cases,
              binaries={stage: {name: sha(b/name) for name in
                        ['openmohaa.exe', 'game.dll', 'cgame.dll']} for stage, b in bins.items()})
(out/'result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
