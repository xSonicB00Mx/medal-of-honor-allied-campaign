"""Runtime component regression for the turret setthread callback, not a mission test."""
import argparse
import json
import re
import subprocess
from pathlib import Path

from inventory_cp00 import sha, save

ap = argparse.ArgumentParser()
ap.add_argument('--run-id', required=True)
args = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', args.run_id)
repo = Path(__file__).resolve().parents[1]
runtime = repo / 'runtime-local/CP00-r2'
profile = repo / 'profiles-local/CP00-r2' / args.run_id
assert not profile.exists(), 'Preserve earlier evidence'
home = profile / 'main'
(home / 'cp00').mkdir(parents=True)
# Only our new turret is modified. No mission entity callbacks or success flags.
fixture = '''main:
    println "CP00_TURRET_BEGIN"
    local.gun = spawn models/statweapons/mg42_gun.tik targetname "cp00_test_turret"
    local.gun.origin = $player.origin + (0 0 48)
    local.gun.angles = $player.angles
    local.gun setPlayerUsable 1
    local.gun maxuseangle 360
    local.gun.cp00_count = 0
    local.gun setthread used
    wait 0.2
    local.gun doUse $player
    wait 0.5
    println ("CP00_TURRET_FIRST=" + local.gun.cp00_count)
    local.gun doUse $player
    wait 0.5
    println ("CP00_TURRET_DISMOUNT=" + local.gun.cp00_count)
    local.gun doUse $player
    wait 0.5
    println ("CP00_TURRET_SECOND=" + local.gun.cp00_count)
    local.gun doUse $player
    wait 0.2
    local.gun remove
    println "CP00_TURRET_DONE"
end

used:
    self.cp00_count++
    println ("CP00_TURRET_CALLBACK=" + self.targetname)
end
'''
(home / 'cp00/turret.scr').write_text(fixture, encoding='ascii')
commands = ['wait 1000', 'map m2l1', 'wait 3000', 'finishloadingscreen',
            'wait 1500', 'which models/statweapons/mg42_gun.tik',
            'script player exec cp00/turret.scr', 'wait 4000',
            'echo CP00_TURRET_PROCESS_DONE', 'quit']
(home / 'cp00-turret.cfg').write_text('\n'.join(commands) + '\n', encoding='ascii')
cmd = [str(runtime / 'openmohaa.exe')]
settings = {'com_target_game': '0', 'fs_basepath': str(runtime),
            'fs_homepath': str(profile), 'fs_steampath': str(runtime),
            'fs_gogpath': str(runtime), 'fs_microsoftstorepath': str(runtime),
            'net_enabled': '0', 'logfile': '2', 'developer': '1', 'sv_cheats': '1',
            'r_fullscreen': '0', 'r_mode': '-1', 'r_customwidth': '1280',
            'r_customheight': '960', 'com_maxfps': '60', 'com_maxfpsUnfocused': '60',
            'cl_playintro': '0', 'skill': '1'}
for name, value in settings.items():
    cmd += ['+set', name, value]
cmd += ['+echo', 'BUILD_ID=CP00-r2-TURRET-COMPONENT', '+exec', 'cp00-turret.cfg']
proc = subprocess.Popen(cmd, cwd=runtime)
try:
    proc.wait(timeout=75)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait(timeout=15)
    raise
log = (home / 'qconsole.log').read_text(encoding='latin1')
observed = re.findall(r'CP00_TURRET_(FIRST|DISMOUNT|SECOND)=(\d+)', log)
passed = (proc.returncode == 0 and observed == [('FIRST', '1'), ('DISMOUNT', '1'), ('SECOND', '2')]
          and log.count('CP00_TURRET_CALLBACK=cp00_test_turret') == 2
          and 'CP00_TURRET_DONE' in log
          and 'Script Error :' not in log.split('CP00_TURRET_BEGIN', 1)[-1])
result = dict(candidate='CP00-r2', scope='Isolated turret use callback; not natural MG42 mission progression',
              engine_source_commit=json.loads((runtime / 'build-manifest.json').read_text())['engine_source_commit'],
              engine_sha256=sha(runtime / 'openmohaa.exe'),
              wcr_package_fingerprint=json.loads((repo / 'third_party/wcr/manifest.json').read_text())['package_fingerprint'],
              cheats_enabled_for_fixture_execution=True, mission_flags_modified=False,
              observed=observed, passed=passed, exit_code=proc.returncode,
              upstream_fix='44ce0595c2bbe1c3d5933e16e9130c2d7cf1306d',
              evidence=[{'path': p.relative_to(repo).as_posix(), 'sha256': sha(p)}
                        for p in sorted(profile.rglob('*')) if p.is_file()])
save(repo / f'checkpoints/CP00/{args.run_id}.json', result)
print(json.dumps({k: v for k, v in result.items() if k != 'evidence'}))
raise SystemExit(0 if passed else 1)
