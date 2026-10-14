"""Check archived option values across process restarts in fresh r4 profiles.

Commands exercise cvar persistence, not mouse interaction with menu widgets.
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from inventory_cp00 import sha, save


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game', choices=['AA', 'SH', 'BT'])
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--candidate', default='CP00-r4', choices=['CP00-r4','CP01-r1'])
    args = ap.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9-]+', args.run_id)
    repo = Path(__file__).resolve().parents[1]
    runtime = repo / 'runtime-local' / args.candidate
    folder = {'AA': 'main', 'SH': 'mainta', 'BT': 'maintt'}[args.game]
    profile = repo / 'profiles-local' / args.candidate / f'{args.run_id}-{args.game}'
    assert not profile.exists(), 'Preserve previous evidence and user saves'
    home = profile / folder
    (home / 'configs').mkdir(parents=True)
    source = repo / f'profiles-local/CP00-r4/{args.game}/{folder}/configs/omconfig.cfg'
    source_hash = sha(source)
    shutil.copy2(source, home / 'configs/omconfig.cfg')
    original = dict(re.findall(r'^seta (\S+) "([^"]*)"', source.read_text(encoding='latin1'), re.M))
    changed = dict(s_volume='0.55', s_musicvolume='0.35', sensitivity='4.25',
                   m_pitch='-0.022', g_subtitle='0', ui_crosshair='0',
                   cg_shadows='0', r_picmip='1', r_gamma='1.15')
    assert all(key in original for key in changed)
    if args.candidate == 'CP01-r1':
        original.update(ac_ui_auto='1',ac_menu_scale='1',ac_hud_scale='1',ac_hud_safe='1',cg_fov=original.get('cg_fov','80'))
        changed.update(ac_ui_auto='0',ac_menu_scale='0.85',ac_hud_scale='1.25',ac_hud_safe='0.9',cg_fov='90')
    evidence = repo / 'generated-local' / args.candidate / f'{args.run_id}-{args.game}'
    evidence.mkdir(parents=True, exist_ok=False)

    def run(label, commands):
        cfg = home / f'cp00-{label}.cfg'
        # Automatic config writing occurs at the beginning of a later frame.
        # Immediate set+quit in one command buffer never reaches that frame.
        cfg.write_text('\n'.join(['wait 1000', *commands, 'wait 1200', f'echo CP00_OPTIONS_{label}_DONE', 'quit'])+'\n', encoding='ascii')
        settings = dict(com_target_game=str(['AA', 'SH', 'BT'].index(args.game)),
                        fs_basepath=str(runtime), fs_homepath=str(profile),
                        fs_steampath=str(runtime), fs_gogpath=str(runtime),
                        fs_microsoftstorepath=str(runtime), net_enabled='0',
                        logfile='2', developer='0', cl_playintro='0',r_fullscreen='0',r_mode='-1',r_customwidth='1280',r_customheight='960')
        cmd = [str(runtime / 'openmohaa.exe')]
        for key, value in settings.items():
            cmd += ['+set', key, value]
        # Deliberately no tested option on the command line.
        proc = subprocess.run(cmd + ['+exec', cfg.name], cwd=runtime, timeout=60)
        logpath = home / 'qconsole.log'
        log = logpath.read_text(encoding='latin1')
        shutil.copy2(logpath, evidence / f'{label}.log')
        shutil.copy2(home / 'configs/omconfig.cfg', evidence / f'{label}-config.cfg')
        assert proc.returncode == 0 and f'CP00_OPTIONS_{label}_DONE' in log
        assert 'refusing to create relative path' not in log
        return log

    run('change', [f'set {key} {value}' for key, value in changed.items()])
    first = run('restart', list(changed) + [f'set {key} {original[key]}' for key in changed])
    second = run('restore-restart', list(changed))
    checks = []
    for key, value in changed.items():
        def observed(log):
            match = re.search(r'"' + re.escape(key) + r'" is:\s*"([^"^]*)', log)
            assert match, key
            return match.group(1)
        actual, restored = observed(first), observed(second)
        passed = float(actual) == float(value) and float(restored) == float(original[key])
        checks.append(dict(option=key, requested=value, after_restart=actual,
                           original=original[key], restored_after_restart=restored, passed=passed))
    assert sha(source) == source_hash, 'User config changed unexpectedly'
    result = dict(candidate=args.candidate, game=args.game,
                  engine_source_commit=json.loads((runtime/'build-manifest.json').read_text(encoding='utf-8'))['engine_source_commit'],
                  engine_sha256=sha(runtime/'openmohaa.exe'),
                  wcr_package_fingerprint=json.loads((repo/'third_party/wcr/revisions/CP00-r4.json').read_text(encoding='utf-8'))['package_fingerprint'],
                  checks=checks, user_config_unchanged=True,
                  scope='Cvar persistence and restoration across three processes; no UI-click or perceptual audio/input test.',
                  evidence=[dict(path=p.relative_to(repo).as_posix(), sha256=sha(p)) for p in sorted(evidence.iterdir())])
    checkpoint='CP01' if args.candidate=='CP01-r1' else 'CP00'
    save(repo / f'checkpoints/{checkpoint}/{args.run_id}-{args.game}.json', result)
    assert all(c['passed'] for c in checks), checks
    print(args.game, f'PASS: {len(checks)} options persisted and restored across restarts', flush=True)


if __name__ == '__main__':
    main()
