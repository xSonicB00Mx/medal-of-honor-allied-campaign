"""Prepare isolated r4 user profiles from verified, unmodified map-start saves.

Never overwrites existing profiles or launchers. No mission flags or runtime
assets are modified. Run once after the r4 map-start probes and deployment.
"""
import json
import shutil
from pathlib import Path

from inventory_cp00 import sha, save


def main():
    repo = Path(__file__).resolve().parents[1]
    candidate = 'CP00-r4'
    runtime = repo / 'runtime-local' / candidate
    build = json.loads((repo / f'checkpoints/CP00/{candidate}-build.json').read_text(encoding='utf-8'))
    assert (runtime / 'COMPLETE').is_file()
    for item in build['owned_files']:
        assert sha(runtime / item['path']) == item['sha256'], item['path']
    wcr = json.loads((repo / f'third_party/wcr/revisions/{candidate}.json').read_text(encoding='utf-8'))
    for item in wcr['modules']:
        if item['installed']:
            assert sha(runtime / item['path']) == item['sha256'], item['path']
    jobs = [('AA', 'main', 0, 'MG42', 'm2l1', 'r4-mg42-start-AA'),
            ('BT', 'maintt', 2, 'Finale', 'e3l4', 'r4-finale-start-BT')]
    prepared = []
    # Preflight both jobs before creating anything.
    for game, folder, target, label, mapname, reference in jobs:
        profile = repo / f'profiles-local/{candidate}/mission-{label}-{game}'
        launcher = repo / f'Start-{candidate}-{label}-{game}.cmd'
        assert not profile.exists() and not launcher.exists(), 'Preserve existing user data'
        report = json.loads((repo / f'checkpoints/CP00/{reference}.json').read_text(encoding='utf-8'))
        assert report['engine_source_commit'] == build['engine_source_commit']
        assert report['wcr_package_fingerprint'] == wcr['package_fingerprint']
        assert report['complete_save_triplet'] and report['active_state']
        hashes = {entry['path']: entry['sha256'] for entry in report['evidence']}
        sources = []
        for ext in ('sav', 'ssv', 'tga'):
            source = repo / f'profiles-local/{candidate}/{reference}/{folder}/save/omconfig/cp00_{mapname}.{ext}'
            assert sha(source) == hashes[source.relative_to(repo).as_posix()]
            sources.append(source)
        config = repo / f'profiles-local/{candidate}/{game}/{folder}/configs/omconfig.cfg'
        assert config.is_file()
        prepared.append((game, folder, target, mapname, profile, launcher, sources, config, report))
    records = []
    for game, folder, target, mapname, profile, launcher, sources, config, report in prepared:
        saves = profile / folder / 'save/omconfig'
        saves.mkdir(parents=True)
        configs = profile / folder / 'configs'
        configs.mkdir()
        shutil.copy2(config, configs / config.name)
        for source in sources:
            shutil.copy2(source, saves / source.name)
            assert sha(source) == sha(saves / source.name)
        profile_rel = str(profile.relative_to(repo))
        launcher.write_text(
            '@echo off\nsetlocal\n'
            f'for %%I in ("%~dp0runtime-local\\{candidate}") do set "AC_BASE=%%~fI"\n'
            f'for %%I in ("%~dp0{profile_rel}") do set "AC_PROFILE=%%~fI"\n'
            'if not exist "%AC_BASE%\\COMPLETE" (echo Kandidat unvollstaendig. & pause & exit /b 1)\n'
            'cd /d "%AC_BASE%"\n'
            f'echo Allied Campaign - {candidate} - {game} - {mapname} Spieltest\n'
            'echo Im Lademenue den vorbereiteten Spielstand oder den eigenen Fortschritt laden.\n'
            f'start "" "openmohaa.exe" +set com_target_game {target} '
            '+set fs_basepath "%AC_BASE%" +set fs_homepath "%AC_PROFILE%" '
            '+set fs_steampath "%AC_BASE%" +set fs_gogpath "%AC_BASE%" '
            '+set fs_microsoftstorepath "%AC_BASE%" +set logfile 2 '
            f'+echo "BUILD_ID={candidate}" %*\n', encoding='ascii', newline='\r\n')
        records.append(dict(game=game, map=mapname, launcher=launcher.name,
                            profile=profile.relative_to(repo).as_posix(),
                            reference_run=report['run_id'],
                            wcr_package_fingerprint=report['wcr_package_fingerprint'],
                            files=[dict(path=p.relative_to(repo).as_posix(), sha256=sha(p))
                                   for p in [launcher, configs / config.name, *saves.iterdir()]]))
    save(repo / f'checkpoints/CP00/{candidate}-progression-preparation.json', dict(
        candidate=candidate, engine_source_commit=build['engine_source_commit'],
        profiles=records, scope='Unmodified r4 map-start saves; natural progression remains untested.'))
    print('Prepared two independent progression profiles and workspace launchers.')


if __name__ == '__main__':
    main()
