"""Verify CP0 inputs and collect local test evidence; never change source assets."""
import argparse, json, shutil, zipfile
from pathlib import Path
from inventory_cp00 import sha, save

ap=argparse.ArgumentParser(); ap.add_argument('--mp1',type=Path,required=True); ap.add_argument('--candidate',default='CP00-r1'); args=ap.parse_args()
if not args.candidate.replace('-','').isalnum(): raise ValueError('Invalid candidate')
repo=Path(__file__).resolve().parents[1]
src=repo.parent
baseline=src/'_ac-backup-local/CP00-input'
runtime=repo/'runtime-local'/args.candidate
prefix='' if args.candidate=='CP00-r1' else args.candidate+'-'
records=json.loads((repo/'generated-local/input-manifest.json').read_text())
for row in records:
    for root in (src,baseline):
        assert sha(root/row['path'])==row['sha256'], (root,row['path'])
print('PASS: all original and snapshot hashes',len(records),flush=True)
mp=json.loads((repo/'third_party/mp1/manifest.json').read_text())['files']
for row in mp:
    assert sha(args.mp1/row['path'])==row['sha256']
manifest=json.loads((runtime/'build-manifest.json').read_text())
data=json.loads((repo/'generated-local/runtime-data-manifest.json').read_text())
for row in data+manifest['owned_files']:
    assert sha(runtime/row['path'])==row['sha256'],row['path']
print('PASS: runtime data and owned files',flush=True)
evidence=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    report=json.loads((repo/f'checkpoints/CP00/scene-{game}.json').read_text())
    assert report['game_loaded'] and report['exit_code']==0 and not report['timeout']
    profile=repo/f'profiles-local/CP00-r1/scene-{game}'
    target=repo/f'profiles-local/{args.candidate}/{game}/{folder}/save/omconfig'
    target.mkdir(parents=True,exist_ok=True)
    # A save is a three-file set: level data, metadata, and menu thumbnail.
    save_paths=[f'{folder}/save/omconfig/cp00_{game.lower()}.{ext}' for ext in ('sav','ssv','tga')]
    for path in save_paths:
        source=profile/path; dest=target/source.name
        if dest.exists(): assert sha(dest)==sha(source),'Refuse changed user save'
        else: shutil.copy2(source,dest)
    tested_profile=repo/f'profiles-local/{args.candidate}/{game}'
    paths=[*profile.rglob('qconsole.log'),*profile.rglob('shot*.tga'),*target.glob('cp00_*'),*tested_profile.rglob('qconsole.log'),*tested_profile.rglob('shot*.tga')]
    evidence.extend(dict(path=p.relative_to(repo).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in paths)
save(repo/f'checkpoints/CP00/{prefix}local-evidence.json',dict(candidate=args.candidate,files=evidence,assets_uploaded=False))
save(repo/f'checkpoints/CP00/{prefix}integrity-final.json',dict(original_files=len(records),original_hashes_unchanged=True,independent_snapshot_hashes_match=True,mp1_recorded_files_unchanged=len(mp),runtime_data_hashes_match=len(data),runtime_owned_hashes_match=len(manifest['owned_files']),independent_write_protection=False))
art=repo/'artifacts-local'; art.mkdir(exist_ok=True)
package=art/f'{args.candidate}-local-runtime.zip'
if package.exists(): raise ValueError('Package exists; preserve it')
with zipfile.ZipFile(package,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
    for p in sorted(runtime.rglob('*')):
        if p.is_file(): z.write(p,Path('runtime-local')/args.candidate/p.relative_to(runtime))
    for game in ('AA','SH','BT'):
        p=repo/f'Start-{args.candidate}-{game}.cmd'; z.write(p,p.name)
        for p in (repo/f'profiles-local/{args.candidate}/{game}').rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(repo))
with zipfile.ZipFile(package) as z: assert z.testzip() is None
save(repo/f'checkpoints/CP00/{prefix}local-package.json',dict(path=package.relative_to(repo).as_posix(),sha256=sha(package),bytes=package.stat().st_size,contains_original_game_data=True,upload_allowed=False,crc_verified=True))
print('PASS: local package verified; never upload this package',flush=True)
