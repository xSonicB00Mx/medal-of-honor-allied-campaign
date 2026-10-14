"""Install a reviewed local widescreen batch with input checks and a rollback copy.

The resulting packages contain game artwork and must never be uploaded to GitHub.
"""
import argparse
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from inventory_cp00 import sha, save

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--batch', required=True)
ap.add_argument('--mp1', required=True, type=Path)
args = ap.parse_args()
assert args.batch.replace('-', '').isalnum()
root = Path(__file__).resolve().parents[1]
work = root/'generated-local/widescreen'
runtime = root/'runtime-local/CP08-r1'
backup = work/'backups'/args.batch
assert not backup.exists(), 'Preserve earlier rollback copies'
source = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
assert not subprocess.check_output(['git','diff','HEAD','--','code'],cwd=root,text=True), 'Commit engine changes first'
old = json.loads((runtime/'build-manifest.json').read_text())
approved = json.loads((work/'approved.json').read_text())
packages = json.loads((work/'packages/package-report.json').read_text())
profile = root/'profiles-local/CP08-r1/user'
def profile_hashes():
    return {p.relative_to(profile).as_posix():sha(p) for p in profile.rglob('*') if p.is_file()}
before = profile_hashes()
integrity = {}
for label,base,manifest in [
    ('original',root.parent,root/'generated-local/CP00-r4/input-manifest.json'),
    ('runtime_base',runtime,root/'generated-local/CP00-r4/runtime-data-manifest.json')]:
    rows = json.loads(manifest.read_text())
    for row in rows:
        assert sha(base/row['path']) == row['sha256'], (label,row['path'])
    integrity[label+'_files_unchanged'] = len(rows)
    print(label,len(rows),'verified',flush=True)
mp = json.loads((root/'third_party/mp1/manifest.json').read_text())['files']
for row in mp:
    assert sha(args.mp1/row['path']) == row['sha256'], row['path']
integrity['mp1_files_unchanged'] = len(mp)
for row in old['owned_files']:
    assert sha(runtime/row['path']) == row['sha256'], ('Runtime drift',row['path'])
updates = {'openmohaa.exe':root/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'}
for package in packages:
    file = root/package['package']
    assert sha(file) == package['sha256']
    with zipfile.ZipFile(file) as z:
        assert z.testzip() is None
    updates[file.parent.name+'/'+file.name] = file
backup.mkdir(parents=True)
shutil.copy2(runtime/'build-manifest.json',backup/'build-manifest.json')
absent = []
for name in updates:
    target = runtime/name
    if target.exists():
        (backup/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(target,backup/name)
        assert sha(backup/name) == sha(target)
    else:
        absent.append(name)
save(backup/'rollback.json',dict(previously_absent=absent,source_commit=old['source_commit']))
for name,file in updates.items():
    shutil.copy2(file,runtime/name)
    assert sha(runtime/name) == sha(file)
owned = {r['path'] for r in old['owned_files']} | set(updates)
manifest = {**old,'source_commit':source,'engine_source_commit':source,
    'game_dll_source_commit':old.get('game_dll_source_commit',old['engine_source_commit']),
    'owned_files':[dict(path=n,sha256=sha(runtime/n)) for n in sorted(owned)],
    'widescreen':dict(batch=args.batch,approved_artworks=sorted(approved),
        completion='PARTIAL_GEMINI_QUOTA_BLOCKED',center='Original textures and widgets unchanged',
        provider='Google Gemini / Nano Banana',breakthrough_loading_changed=False,
        spearhead_letterboxed_loading_changed=False),
    'personal_acceptance':False,'merged':False}
save(runtime/'build-manifest.json',manifest)
assert profile_hashes() == before, 'User profile must remain untouched'
integrity['user_profile_files_unchanged'] = len(before)
integrity['rollback_copy'] = backup.relative_to(root).as_posix()
save(work/(args.batch+'-integrity.json'),integrity)
artifact = root/'artifacts-local'/('CP08-r1-'+args.batch+'-update.zip')
with zipfile.ZipFile(artifact,'x',zipfile.ZIP_DEFLATED) as z:
    for name in [*updates,'build-manifest.json']:
        z.write(runtime/name,'runtime-local/CP08-r1/'+name)
with zipfile.ZipFile(artifact) as z:
    assert z.testzip() is None
save(work/(args.batch+'-delivery.json'),dict(source_commit=source,integrity=integrity,
    package=artifact.relative_to(root).as_posix(),sha256=sha(artifact),upload_allowed=False,
    approved_artworks=sorted(approved),completion='PARTIAL_GEMINI_QUOTA_BLOCKED'))
print(json.dumps(integrity),flush=True)
