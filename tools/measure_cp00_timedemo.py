"""Record an idle WCR scene, then collect built-in timedemo frame durations.

This measures client replay, not live combat latency or display presentation.
The engine advances replay by fixed 50 ms simulation steps, without live AI.
"""
import argparse
import json
import math
import re
import shutil
import statistics
import subprocess
from pathlib import Path

from inventory_cp00 import sha, save


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game', choices=['AA', 'SH', 'BT'])
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--resume-recorded', action='store_true')
    ap.add_argument('--replay-prefix', default='replay')
    args = ap.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9-]+', args.run_id)
    assert re.fullmatch(r'[A-Za-z0-9-]+', args.replay_prefix)
    repo = Path(__file__).resolve().parents[1]
    runtime = repo / 'runtime-local/CP00-r4'
    game = args.game
    folder, mapname = {'AA': ('main', 'm2l1'), 'SH': ('mainta', 't1l2'), 'BT': ('maintt', 'e1l2')}[game]
    profile = repo / f'profiles-local/CP00-r4/{args.run_id}-{game}'
    assert profile.exists() == args.resume_recorded, 'Use fresh profile, or explicitly resume a recording'
    home = profile / folder
    if not args.resume_recorded:
        (home / 'configs').mkdir(parents=True)
    source = repo / f'profiles-local/CP00-r4/{game}/{folder}/configs/omconfig.cfg'
    original_hash = sha(source)
    if not args.resume_recorded:
        shutil.copy2(source, home / 'configs/omconfig.cfg')
    evidence = repo / f'generated-local/CP00-r4/{args.run_id}-{game}'
    if not args.resume_recorded:
        evidence.mkdir(parents=True, exist_ok=False)

    def run(label, commands):
        cfg = home / f'cp00-{label}.cfg'
        assert not cfg.exists(), 'Never overwrite previous test commands'
        cfg.write_text('\n'.join(commands)+'\n', encoding='ascii')
        settings = dict(com_target_game=str(['AA','SH','BT'].index(game)),
                        fs_basepath=str(runtime), fs_homepath=str(profile),
                        fs_steampath=str(runtime), fs_gogpath=str(runtime),
                        fs_microsoftstorepath=str(runtime), net_enabled='0',
                        logfile='1', developer='0', cl_playintro='0', ui_console='0',
                        r_fullscreen='0', r_mode='-1', r_customwidth='1280',
                        r_customheight='960', com_maxfps='60', com_maxfpsUnfocused='60',
                        com_maxfpsMinimized='60', skill='1')
        if label != 'record':
            settings['cheats'] = '1'  # Cvar protection uses cheats, not sv_cheats.
        cmd = [str(runtime/'openmohaa.exe')]
        for key, value in settings.items():
            cmd += ['+set', key, value]
        proc = subprocess.Popen(cmd + ['+exec', cfg.name], cwd=runtime)
        try:
            proc.wait(timeout=100)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=10)
            raise
        logpath = home/'qconsole.log'
        log = logpath.read_text(encoding='latin1')
        shutil.copy2(logpath, evidence/f'{label}.log')
        assert proc.returncode == 0, label
        return log

    recorded = (evidence/'record.log').read_text(encoding='latin1') if args.resume_recorded else run('record', ['wait 1000', f'map {mapname}', 'wait 3000',
                            'finishloadingscreen', 'wait 3000', 'screenshot',
                            'set g_synchronousClients 1', 'record cp00_reference',
                            'wait 30000', 'stoprecord', 'screenshot',
                            'echo CP00_RECORD_DONE', 'quit'])
    demos = list((home/'demos').glob('cp00_reference.dm_*'))
    assert len(demos) == 1 and demos[0].stat().st_size > 1024
    assert 'CP00_RECORD_DONE' in recorded and 'recording to demos/cp00_reference' in recorded
    results = []
    for label in (args.replay_prefix+'1', args.replay_prefix+'2'):
        log = run(label, ['wait 1000', 'set timedemo 1',
                         f'set cl_timedemoLog {label}-frametimes.txt',
                         'set nextdemo "echo CP00_REPLAY_DONE; quit"', 'demo cp00_reference'])
        timing = home/f'{label}-frametimes.txt'
        assert timing.is_file() and 'CP00_REPLAY_DONE' in log
        lines = timing.read_text(encoding='ascii').splitlines()
        values = [int(line) for line in lines if line and not line.startswith('#')]
        assert 100 <= len(values) < 4096, len(values)
        ordered = sorted(values)
        results.append(dict(run=label, frames=len(values), mean_ms=round(statistics.mean(values),3),
                            median_ms=statistics.median(values),
                            p95_ms=ordered[math.ceil(len(values)*.95)-1],
                            p99_ms=ordered[math.ceil(len(values)*.99)-1],
                            max_ms=max(values), clipped_at_255_ms=sum(v == 255 for v in values),
                            engine_summary=lines[0], duration_log_sha256=sha(timing)))
        shutil.copy2(timing,evidence/timing.name)
    assert sha(source) == original_hash
    result = dict(candidate='CP00-r4',game=game,map=mapname,record_seconds=30,
                  resolution=[1280,960],fov=90,renderer='GL1',skill=1,
                  engine_sha256=sha(runtime/'openmohaa.exe'),
                  engine_source_commit=json.loads((runtime/'build-manifest.json').read_text(encoding='utf-8'))['engine_source_commit'],
                  wcr_package_fingerprint=json.loads((repo/'third_party/wcr/revisions/CP00-r4.json').read_text(encoding='utf-8'))['package_fingerprint'],
                  replay_results=results, demo_sha256=sha(demos[0]),
                  scope='Idle-scene client timedemo; live AI runs only while recording. Not live-combat or display-present timings. Millisecond resolution, durations clipped to 255 ms by engine; two fresh replay processes.',
                  visual_check='PENDING', evidence=[dict(path=p.relative_to(repo).as_posix(),sha256=sha(p)) for p in sorted(evidence.iterdir())])
    save(repo/f'checkpoints/CP00/{args.run_id}-{game}.json',result)
    print(game, json.dumps(results), flush=True)


if __name__ == '__main__':
    main()
