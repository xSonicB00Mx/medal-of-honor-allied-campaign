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
ap.add_argument('--loading-zoom', action='store_true', help='Install only the existing SH/BT artwork zoom packages')
ap.add_argument('--with-game-binaries', action='store_true', help='Install tested game and cgame DLLs alongside the engine')
ap.add_argument('--font-packages', type=Path, help='Install a reviewed local font package report instead of widescreen packages')
ap.add_argument('--with-engine', action='store_true', help='Also install the tested engine with font layout changes')
args = ap.parse_args()
assert not (args.font_packages and args.loading_zoom)
assert not (args.font_packages and args.with_game_binaries)
assert not args.with_engine or args.font_packages
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
progress = json.loads((work/'progress.json').read_text())
remaining = [item for item in progress['remaining'] if item not in approved]
completion = 'COMPLETE' if not remaining else {
    'BLOCKED_BY_GEMINI_QUOTA': 'PARTIAL_GEMINI_QUOTA_BLOCKED',
    'BLOCKED_BY_PROVIDER': 'PARTIAL_PROVIDER_BLOCKED',
    'BLOCKED_BY_PROVIDER_AND_QUALITY': 'PARTIAL_PROVIDER_AND_QUALITY_BLOCKED',
}.get(progress['status'], 'PARTIAL_IN_PROGRESS')
packages = json.loads((args.font_packages if args.font_packages else work/('loading-zoom/packages/package-report.json' if args.loading_zoom else 'packages/package-report.json')).read_text())
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
updates = {} if args.font_packages and not args.with_engine else {'openmohaa.exe':root/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'}
if args.with_game_binaries:
    for name in ['game.dll','cgame.dll']:
        updates[name] = root/'build-local/cp00-r3/RelWithDebInfo'/name
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
widescreen = old.get('widescreen', {}) if args.loading_zoom or args.font_packages else dict(
    batch=args.batch,approved_artworks=sorted(approved),
    completion=completion,center='Full supplied artwork; original background tiles removed; controls preserved; MP entry disabled',
    provider='Google Gemini / Nano Banana and user-supplied artwork',breakthrough_loading_changed=False,
    spearhead_letterboxed_loading_changed=False)
if not args.loading_zoom and old.get('widescreen', {}).get('loading_zoom'):
    widescreen.update({key:old['widescreen'][key] for key in
        ['loading_zoom','breakthrough_loading_changed','spearhead_letterboxed_loading_changed']})
if args.loading_zoom:
    widescreen = {**widescreen, 'breakthrough_loading_changed':True,
        'spearhead_letterboxed_loading_changed':True,
        'loading_zoom':dict(batch=args.batch, maps={p['game']:len(p['maps']) for p in packages},
            generation=False, fit='Proportional cropped artwork, centered; full original frame on 4:3')}
manifest = {**old,'source_commit':source,'engine_source_commit':old['engine_source_commit'] if args.font_packages and not args.with_engine else source,
    'game_dll_source_commit':source if args.with_game_binaries else old.get('game_dll_source_commit',old['engine_source_commit']),
    'owned_files':[dict(path=n,sha256=sha(runtime/n)) for n in sorted(owned)],
    'widescreen':widescreen,
    'personal_acceptance':False,'merged':False}
if args.font_packages:
    manifest['fonts'] = dict(batch=args.batch, family='Courier New Bold',
                            metrics='Natural Courier New Bold advances; proportionate menu sizes',
                            shadow='Black 70%, 0.6 source pixels down/right',
                            packages=packages, upload_allowed=False)
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
    approved_artworks=sorted(approved),
    completion='LOADING_ZOOM_COMPLETE_OTHER_ART_PARTIAL' if args.loading_zoom else completion))
print(json.dumps(integrity),flush=True)
