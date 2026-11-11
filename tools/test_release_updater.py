"""Exercise the shipped Windows updater against small disposable installations."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
from cp09_candidate import R, digest


def run_tests(release):
    parent = R/'generated-local/release-1.0.1-updater-tests'
    parent.mkdir(exist_ok=True)
    sandbox = Path(tempfile.mkdtemp(prefix='run-',dir=parent))
    source = release/'payload/Update-Allied-Campaign.cmd'
    cases = ['fresh', 'upgrade', 'modified-old', 'unknown-old', 'missing-new', 'corrupt-new', 'unsafe-path']
    for case in cases:
        root = sandbox/case
        root.mkdir()
        shutil.copy2(source, root/source.name)
        entries, files = [], []
        for game, count in [('main',24), ('mainta',21), ('maintt',23)]:
            (root/game).mkdir()
            new = root/game/'zz_AlliedCampaign.pk3'
            new.write_bytes(b'new package fixture')
            files.append(dict(path=f'{game}/{new.name}', sha256=digest(new)))
            (root/game/'Restoration_fixture.pk3').write_bytes(b'WCR untouched')
            (root/game/'Pak0.pk3').write_bytes(b'original untouched')
            for i in range(count):
                rel = f'{game}/zzz_AC_Test{i:02d}.pk3'
                data = rel.encode()
                entries.append(dict(path=rel, sha256=hashlib.sha256(data).hexdigest()))
                if case != 'fresh':
                    (root/rel).write_bytes(data)
        (root/'AlliedCampaign-User').mkdir()
        (root/'AlliedCampaign-User/progress.dat').write_bytes(b'keep my progress')
        if case == 'modified-old': (root/entries[-1]['path']).write_bytes(b'user modified')
        if case == 'unknown-old': (root/'main/zzzz_AC_Unknown.pk3').write_bytes(b'unknown')
        if case == 'missing-new': (root/'maintt/zz_AlliedCampaign.pk3').unlink()
        if case == 'corrupt-new': (root/'maintt/zz_AlliedCampaign.pk3').write_bytes(b'corrupt')
        if case == 'unsafe-path': entries[-1]['path'] = '../outside.pk3'
        (root/'Allied-Campaign-manifest.json').write_text(json.dumps(dict(version='1.0.1', files=files, obsolete_packages=entries)))
        snapshot = lambda: {p.relative_to(root).as_posix():digest(p) for p in root.rglob('*') if p.is_file()}
        before = snapshot()
        result = subprocess.run(['cmd.exe','/d','/c','Update-Allied-Campaign.cmd','--quiet'],cwd=root,
                                text=True,capture_output=True,timeout=60)
        success = case in ('fresh', 'upgrade')
        assert (result.returncode == 0) == success, (case,result.stdout,result.stderr)
        after = snapshot()
        if success:
            removed = {x['path'] for x in entries}
            assert after == {k:v for k,v in before.items() if k not in removed}
            again = subprocess.run(['cmd.exe','/d','/c','Update-Allied-Campaign.cmd','--quiet'],cwd=root,
                                   text=True,capture_output=True,timeout=60)
            assert again.returncode == 0 and snapshot() == after
        else:
            assert before == after, ('Failed preflight removed files',case)
        print('Updater case passed: '+case,flush=True)
    return cases


if __name__ == '__main__':
    run_tests(R/'artifacts-local/Allied-Campaign-1.0.1')
