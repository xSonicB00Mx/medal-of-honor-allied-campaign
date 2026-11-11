"""Compare event acceptance and save/reload retention; never modify mission flags."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from inventory_cp00 import sha, save

ap = argparse.ArgumentParser()
ap.add_argument('--candidate', required=True)
ap.add_argument('--run-id', required=True)
ap.add_argument('--save-probe', required=True, type=Path)
ap.add_argument('--expect', choices=['accepted', 'rejected'], required=True)
args = ap.parse_args()
assert re.fullmatch(r'CP00-r\d+', args.candidate)
assert re.fullmatch(r'[A-Za-z0-9-]+', args.run_id)
repo = Path(__file__).resolve().parents[1]
rt = repo / 'runtime-local' / args.candidate
profile = repo / 'profiles-local' / args.candidate / args.run_id
assert not profile.exists(), 'Preserve earlier evidence'
home = profile / 'mainta'
(home / 'cp00').mkdir(parents=True)
setup = '''main:
    println "CP00_OFFSET_SETUP"
    local.a = spawn ThrobbingBox_ExplodePlayerFlak88 targetname "cp00_offset_a"
    local.a.origin = (0 0 -8192)
    local.a notsolid
    local.a SetDamage 0
    local.a StopWatchDuration 0.2
    local.a explosionoffset "17.25 29.5 128"
    local.a setthread exploded
    local.b = spawn ThrobbingBox_ExplodePlayerFlak88 targetname "cp00_offset_b"
    local.b.origin = (0 0 -8192)
    local.b notsolid
    local.b SetDamage 0
    local.b StopWatchDuration 0.2
    local.b explosionoffset "-31.5 41.75 300"
    local.b setthread exploded
    println "CP00_OFFSET_READY"
end
exploded:
    println ("CP00_OFFSET_EXPLODED=" + self.targetname)
end
'''
(home / 'cp00/setup.scr').write_text(setup, encoding='ascii')
(home / 'cp00/trigger.scr').write_text('main:\n$cp00_offset_a doUse $player\n$cp00_offset_b doUse $player\nend\n', encoding='ascii')

def run(label, commands):
    cfg = home / f'cp00-{label}.cfg'
    cfg.write_text('\n'.join(commands + [f'echo CP00_OFFSET_{label}_DONE', 'quit']) + '\n', encoding='ascii')
    cmd = [str(rt / 'openmohaa.exe')]
    settings = {'com_target_game': '1', 'fs_basepath': str(rt), 'fs_homepath': str(profile),
                'fs_steampath': str(rt), 'fs_gogpath': str(rt), 'fs_microsoftstorepath': str(rt),
                'net_enabled': '0', 'logfile': '2', 'developer': '1', 'sv_cheats': '1',
                'r_fullscreen': '0', 'r_mode': '-1', 'r_customwidth': '1280',
                'r_customheight': '960', 'com_maxfps': '60', 'com_maxfpsUnfocused': '60',
                'cl_playintro': '0', 'skill': '1'}
    for name, value in settings.items(): cmd += ['+set', name, value]
    cmd += ['+echo', 'BUILD_ID=' + args.candidate + '-OFFSET-TEST', '+exec', cfg.name]
    proc = subprocess.Popen(cmd, cwd=rt)
    try: proc.wait(timeout=90)
    except subprocess.TimeoutExpired:
        proc.terminate(); proc.wait(timeout=15); raise
    log = (home / 'qconsole.log').read_text(encoding='latin1')
    shutil.copy2(home / 'qconsole.log', home / f'{label}.log')
    assert proc.returncode == 0 and f'CP00_OFFSET_{label}_DONE' in log
    return log

first = run('first', ['wait 1000', 'map t1l2', 'wait 3000', 'finishloadingscreen',
                     'wait 1500', 'which maps/t1l2.scr', 'script player exec cp00/setup.scr',
                     'wait 500', 'savegame cp00_offset_before', 'wait 1500'])
second = run('reload', ['wait 1000', 'loadgame cp00_offset_before', 'wait 2500',
                       'finishloadingscreen', 'wait 1000', 'savegame cp00_offset_after',
                       'wait 1500', 'script player exec cp00/trigger.scr', 'wait 2000'])
counts = {}
for label in ('before', 'after'):
    saved = home / f'save/omconfig/cp00_offset_{label}.sav'
    counts[label] = [int(x) for x in subprocess.check_output([str(args.save_probe.resolve()), str(saved)], text=True).split()]
errors = [line for line in first.splitlines() if "Failed execution of command 'explosionoffset'" in line]
accepted = not errors and counts == {'before': [1, 1], 'after': [1, 1]}
rejected = len(errors) == 4 and counts == {'before': [0, 0], 'after': [0, 0]}
callbacks = re.findall(r'CP00_OFFSET_EXPLODED=(cp00_offset_[ab])', second)
passed = (accepted if args.expect == 'accepted' else rejected) and sorted(callbacks) == ['cp00_offset_a', 'cp00_offset_b'] and 'Game Loaded' in second
result = dict(candidate=args.candidate, engine_source_commit=json.loads((rt / 'build-manifest.json').read_text())['engine_source_commit'],
              game_dll_sha256=sha(rt / 'game.dll'), expected=args.expect, accepted=accepted,
              offset_rejection_count=len(errors), vector_occurrences=counts, callbacks=callbacks, passed=passed,
              scope='Event acceptance, native-compatible inert offset, archive retention and synthetic detonation callbacks; not natural Flak mission completion',
              evidence=[dict(path=p.relative_to(repo).as_posix(), sha256=sha(p)) for p in sorted(profile.rglob('*')) if p.is_file()])
save(repo / f'checkpoints/CP00/{args.run_id}.json', result)
print(json.dumps({k: v for k, v in result.items() if k != 'evidence'}))
raise SystemExit(0 if passed else 1)
