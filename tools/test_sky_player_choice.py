"""Sky quality is a player preference, including during weather and old-save loads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--baseline', action='store_true')
ap.add_argument('--games', default='0,1,2', help='Comma-separated content contexts')
ap.add_argument('--baseline-error-log', type=Path,
                help='Old-DLL control log for matching pre-existing mission script errors')
a = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', a.run)
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
rt = R/'runtime-local/CP09-r1'
personal = R/'profiles-local/CP08-r1/user'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
snapshot = lambda: {f.relative_to(personal).as_posix(): sha(f)
                    for f in personal.rglob('*') if f.is_file()}
before = snapshot()
results = []

def script_errors(log):
    location = ''
    found = set()
    for line in log.splitlines():
        match = re.search(r'\(([^()]+\.scr, \d+)\):', line)
        if match:
            location = match.group(1)
        if 'Script Error :' in line:
            found.add((location, line.split('Script Error :', 1)[1].strip()))
    return found

for game, folder, start in [(0, 'main', 'loadgame reference'),
                             (1, 'mainta', 'loadgame reference'), (2, 'maintt', 'map e1l1')]:
    if str(game) not in a.games.split(','):
        continue
    if a.baseline and game:
        continue
    p = R/'profiles-local/CP09'/a.run/folder
    p.mkdir(parents=True, exist_ok=False)
    b = p/'bin'
    b.mkdir()
    for f in list(rt.glob('*.dll')) + [rt/'openmohaa.exe']:
        shutil.copy2(f, b/f.name)
    if not a.baseline:
        shutil.copy2(R/'build-local/cp00-r3/RelWithDebInfo/game.dll', b/'game.dll')
    for f in personal.rglob('*.cfg'):
        d = p/f.relative_to(personal)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, d)
    h = p/folder
    h.mkdir(exist_ok=True)
    d = h/'save/omconfig'
    d.mkdir(parents=True, exist_ok=True)
    for f in (personal/folder/'save/omconfig').glob('quick.*'):
        shutil.copy2(f, d/('reference'+f.suffix))
    (h/'skycheck.scr').write_text('''main:
 println ("AC_SKY observe=" + (getcvar r_fastsky))
end
block_on:
 setcvar "R_FASTSKY" "1"
 println ("AC_SKY script_on=" + (getcvar r_fastsky))
 setcvar "ac_sky_probe_other" "7"
 println ("AC_SKY other=" + (getcvar ac_sky_probe_other))
end
block_off:
 setcvar "r_fastsky" "0"
 println ("AC_SKY script_off=" + (getcvar r_fastsky))
end
weather:
 waitthread global/weather.scr::flash
 println ("AC_SKY weather_flash=" + (getcvar r_fastsky))
 waitthread global/weather.scr::unflash
 println ("AC_SKY weather_restore=" + (getcvar r_fastsky))
 level.fastsky_save = 1
 waitthread global/weather.scr::unflash
 println ("AC_SKY stale_restore=" + (getcvar r_fastsky))
end
watch:
 for (local.i=0;local.i<180;local.i++)
 {
  if ((getcvar r_fastsky) != "0")
   println ("AC_SKY unexpected=" + (getcvar r_fastsky))
  wait 0.1
 }
 println "AC_SKY watch_done"
end
''')
    cmd = ['wait 800', start, 'wait 5000', 'finishloadingscreen', 'wait 1000',
           'god', 'seta r_fastsky 0', 'script player exec skycheck.scr block_on']
    if game == 0:
        cmd += ['seta r_fastsky 0', 'script player exec skycheck.scr weather']
    if not a.baseline:
        cmd += ['seta r_fastsky 0', 'script player exec skycheck.scr watch',
                'wait 19000', 'savegame sky_choice', 'wait 300',
                'loadgame sky_choice', 'wait 5000', 'finishloadingscreen',
                'wait 1000', 'script player exec skycheck.scr',
                'vid_restart', 'wait 2500', 'finishloadingscreen', 'wait 700',
                'script player exec skycheck.scr', 'screenshot silent', 'seta r_fastsky 1',
                'script player exec skycheck.scr block_off', 'wait 300',
                'screenshot silent', 'writeconfig omconfig.cfg']
    cmd += ['echo AC_SKY_DONE', 'quit']
    for label in ['block_on', 'block_off', 'weather', 'watch']:
        (h/f'sky_{label}.scr').write_text(
            f'main:\n waitthread skycheck.scr::{label}\nend\n')
    cmd = [re.sub(r'exec skycheck.scr (\w+)', r'exec sky_\1.scr', c) for c in cmd]
    (h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
    args = [str(b/'openmohaa.exe')]
    for k, v in dict(com_target_game=game, fs_basepath=rt, fs_homepath=p,
                     fs_steampath=rt, fs_gogpath=rt, fs_microsoftstorepath=rt,
                     net_enabled=0, logfile=2, developer=1, cheats=1, ac_campaign_mode=1,
                     thereisnomonkey=1, cl_playintro=0, r_fullscreen=0, r_mode=-1,
                     r_customwidth=1280, r_customheight=720, com_maxfps=60,
                     com_maxfpsUnfocused=60).items():
        args += ['+set', k, str(v)]
    def run(cfg):
        proc = subprocess.run(args+['+exec', cfg], cwd=b, timeout=100,
                              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        log = (h/'qconsole.log').read_text(encoding='latin1')
        assert proc.returncode == 0 and 'AC_SKY_DONE' in log
        assert 'Script file compile error' not in log
        errors = script_errors(log)
        if errors:
            assert a.baseline_error_log, errors
            known = script_errors(a.baseline_error_log.read_text(encoding='latin1'))
            assert errors <= known, errors - known
            assert not any('skycheck' in site for site, _ in errors)
        return log
    log = run('probe.cfg')
    (out/f'{folder}.log').write_text(log, encoding='latin1')
    assert 'AC_SKY other=7' in log
    if a.baseline:
        assert 'AC_SKY weather_flash=1' in log and 'AC_SKY stale_restore=1' in log
    else:
        assert 'AC_SKY script_on=0' in log and 'AC_SKY script_off=1' in log
        assert 'AC_SKY unexpected=' not in log and 'AC_SKY watch_done' in log
        assert log.count('AC_SKY observe=0') == 2
        if game == 0:
            assert all('AC_SKY '+key+'=0' in log for key in
                       ['weather_flash', 'weather_restore', 'stale_restore'])
        prefs = (p/'main/ac_preferences.cfg').read_text()
        assert 'seta r_fastsky "1"' in prefs
        if game == 0:
            for context, subdir in [(1, 'mainta'), (2, 'maintt')]:
                (p/subdir/'cross.cfg').write_text(
                    'wait 1200\nr_fastsky\necho AC_SKY_DONE\nquit\n')
                cross_args = args.copy()
                cross_args[cross_args.index('com_target_game')+1] = str(context)
                cross = subprocess.run(cross_args+['+exec', 'cross.cfg'], cwd=b,
                                       timeout=40, stdout=subprocess.DEVNULL,
                                       stderr=subprocess.STDOUT)
                cross_log = (p/subdir/'qconsole.log').read_text(encoding='latin1')
                assert cross.returncode == 0 and 'AC_SKY_DONE' in cross_log
                assert re.search(r'"r_fastsky" is:"1', cross_log)
                (out/f'cross-{subdir}.log').write_text(cross_log, encoding='latin1')
        # Explicit On must survive process restart; then restore Off explicitly.
        (h/'restart.cfg').write_text('wait 1200\nr_fastsky\nseta r_fastsky 0\nwait 300\n'
                                     'writeconfig omconfig.cfg\necho AC_SKY_DONE\nquit\n')
        restarted = run('restart.cfg')
        (out/f'{folder}-restart.log').write_text(restarted, encoding='latin1')
        assert re.search(r'"r_fastsky" is:"1', restarted), restarted[-5000:]
        assert 'seta r_fastsky "0"' in (p/'main/ac_preferences.cfg').read_text()
        from PIL import Image
        for i, f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
            Image.open(f).save(out/f'{folder}-{i}.png')
    results.append(dict(game=folder, passed=True,
                        preexisting_script_errors=sorted(script_errors(log))))
    assert snapshot() == before
    print(folder, 'passed', flush=True)

result = dict(engine_sha256=sha(rt/'openmohaa.exe'),
              game_sha256=sha(b/'game.dll'), personal_files_unchanged=len(before),
              cases=results, baseline=a.baseline)
(out/'result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
