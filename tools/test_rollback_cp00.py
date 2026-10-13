"""Rollback only a disposable, independently copied candidate; input paths read-only."""
import argparse, json, shutil
from pathlib import Path
from inventory_cp00 import sha, save

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('candidate',type=Path); ap.add_argument('--destination',type=Path,required=True); args=ap.parse_args()
    repo=Path(__file__).resolve().parents[1]; candidate=args.candidate.resolve(); dest=args.destination.resolve()
    allowed=(repo/'runtime-local').resolve()
    if dest.parent!=allowed or not dest.name.startswith('rollback-test-') or dest.exists():
        raise ValueError('A new runtime-local/rollback-test-* directory is required')
    if candidate.parent!=allowed or not (candidate/'COMPLETE').is_file(): raise ValueError('Invalid completed candidate')
    manifest=json.loads((candidate/'build-manifest.json').read_text())
    data=json.loads((repo/'generated-local/runtime-data-manifest.json').read_text())
    # Independent byte copies, not links. Profiles are deliberately outside the runtime.
    shutil.copytree(candidate,dest)
    profile=repo/'profiles-local'/manifest['build_id']
    before={p.relative_to(profile).as_posix():sha(p) for p in profile.rglob('*') if p.is_file()}
    for row in manifest['owned_files']:
        path=(dest/row['path']).resolve()
        if dest not in path.parents or path.is_symlink(): raise ValueError('Unsafe ownership path')
        if sha(path)!=row['sha256']: raise ValueError('Modified owned file; refusing deletion')
        path.unlink()
    for name in ('COMPLETE','build-manifest.json'):
        (dest/name).unlink()
    expected={r['path']:r['sha256'] for r in data}
    actual={p.relative_to(dest).as_posix():sha(p) for p in dest.rglob('*') if p.is_file()}
    if actual!=expected: raise ValueError('Rollback did not restore exact WCR data set')
    after={p.relative_to(profile).as_posix():sha(p) for p in profile.rglob('*') if p.is_file()}
    assert before==after
    prefix='' if manifest['build_id']=='CP00-r1' else manifest['build_id']+'-'
    save(repo/f'checkpoints/CP00/{prefix}rollback-result.json',dict(status='PASS',candidate=manifest['build_id'],data_files=len(actual),wcr_preserved=True,profiles_unchanged=True,original_candidate_unchanged=all(sha(candidate/r['path'])==r['sha256'] for r in manifest['owned_files']),scope='Disposable runtime copy; engine and owned launchers removed, exact pre-engine WCR data restored. Original programs remain in the full input snapshot.'))
    print('PASS: isolated rollback, exact WCR data, unchanged profiles and original candidate')

if __name__=='__main__': main()
