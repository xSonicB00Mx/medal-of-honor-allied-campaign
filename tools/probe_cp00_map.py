"""Start an unchanged WCR map in a fresh diagnostic profile; no completion claim."""
import argparse
import json
import re
import subprocess
import time
from pathlib import Path

from inventory_cp00 import sha, save

ap = argparse.ArgumentParser()
ap.add_argument('game', choices=['AA', 'SH', 'BT'])
ap.add_argument('map', choices=['m1l1', 'm2l1', 't1l2', 'e3l4','briefing/briefing1','briefing/briefingt1','briefing/briefinge1'])
ap.add_argument('--run-id', required=True)
ap.add_argument('--seconds', type=int, default=30)
ap.add_argument('--candidate', default='CP00-r2')
args = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', args.run_id)
assert re.fullmatch(r'CP00-r\d+', args.candidate)
assert 5 <= args.seconds <= 120
assert args.map in {'AA': ['m1l1', 'm2l1','briefing/briefing1'], 'SH': ['t1l2','briefing/briefingt1'], 'BT': ['e3l4','briefing/briefinge1']}[args.game]
briefing=args.map.startswith('briefing/')
repo = Path(__file__).resolve().parents[1]
runtime = repo / 'runtime-local' / args.candidate
profile = repo / 'profiles-local' / args.candidate / args.run_id
assert not profile.exists(), 'Never overwrite an existing profile'
folder = {'AA': 'main', 'SH': 'mainta', 'BT': 'maintt'}[args.game]
home = profile / folder
home.mkdir(parents=True)
resources = [f'maps/{args.map}.scr']
if args.map == 'e3l4':
    resources += ['maps/e3l4/escape.scr', 'maps/e3l4/tower.scr', 'maps/e3l4/outro.scr']
commands = ['wait 1000', f'map {args.map}', 'wait 3000', 'finishloadingscreen']
commands += [f'which {name}' for name in resources]
commands += ['wait 2000', 'screenshot', f'wait {args.seconds * 1000}', 'screenshot']
if not briefing: commands += [f'savegame cp00_{args.map}', 'wait 1500']
commands += [f'echo CP00_MAP_PROBE_DONE_{args.map}', 'quit']
(home / 'cp00-probe.cfg').write_text('\n'.join(commands) + '\n', encoding='ascii')
cmd = [str(runtime / 'openmohaa.exe')]
settings = {'com_target_game': str(['AA', 'SH', 'BT'].index(args.game)),
            'fs_basepath': str(runtime), 'fs_homepath': str(profile),
            'fs_steampath': str(runtime), 'fs_gogpath': str(runtime),
            'fs_microsoftstorepath': str(runtime), 'net_enabled': '0',
            'logfile': '2', 'developer': '1', 'r_fullscreen': '0',
            'r_mode': '-1', 'r_customwidth': '1280', 'r_customheight': '960',
            'com_maxfps': '60', 'com_maxfpsUnfocused': '60',
            'cl_playintro': '0', 'skill': '1'}
for name, value in settings.items():
    cmd += ['+set', name, value]
cmd += ['+echo', 'BUILD_ID=' + args.candidate + '-PROBE-' + args.map, '+exec', 'cp00-probe.cfg']
started = time.monotonic()
proc = subprocess.Popen(cmd, cwd=runtime)
print('Started map probe', args.map, 'PID', proc.pid, flush=True)
timed_out = False
try:
    proc.wait(timeout=args.seconds + 90)
except subprocess.TimeoutExpired:
    timed_out = True
    proc.terminate()
    proc.wait(timeout=15)
log = (home / 'qconsole.log').read_text(encoding='latin1')
evidence = [{'path': p.relative_to(repo).as_posix(), 'sha256': sha(p)}
            for p in sorted(profile.rglob('*')) if p.is_file()]
result = dict(candidate=args.candidate, game=args.game, map=args.map, run_id=args.run_id,
              engine_source_commit=json.loads((runtime / 'build-manifest.json').read_text())['engine_source_commit'],
              engine_sha256=sha(runtime / 'openmohaa.exe'),
              wcr_package_fingerprint=json.loads((runtime / 'build-manifest.json').read_text()).get('wcr_package_fingerprint','0d681481b7deaaa76fbeb5466de634e6e6b0caf271b975e1f8052408b41f4fe9'),
              exit_code=proc.returncode, timed_out=timed_out,
              elapsed_seconds=round(time.monotonic() - started, 2),
              active_state='CS_ACTIVE' in log,
              script_errors=[line.split('] ', 1)[-1] for line in log.splitlines() if 'Script Error :' in line],
              commands_finished=f'CP00_MAP_PROBE_DONE_{args.map}' in log,
              complete_save_triplet=not briefing and all((home / f'save/omconfig/cp00_{args.map}.{ext}').is_file()
                                       for ext in ('sav', 'ssv', 'tga')),
              resource_origins=[line.split('] ', 1)[-1].replace(str(runtime), '$RUNTIME')
                                for line in log.splitlines() if 'File "' in line and 'found in' in line],
              evidence=evidence,
              scope='Map startup and idle scene only. No combat, MG42 progression, natural transition or finale completion asserted.')
save(repo / f'checkpoints/CP00/{args.run_id}.json', result)
print(json.dumps({k: v for k, v in result.items() if k != 'evidence'}), flush=True)
raise SystemExit(0 if proc.returncode==0 and not timed_out and result['active_state'] and result['commands_finished'] and (briefing or result['complete_save_triplet']) else 1)
