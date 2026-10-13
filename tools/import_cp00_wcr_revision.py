"""Capture a user-authorized local WCR revision without touching earlier inputs."""
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path
from inventory_cp00 import files, sha, save

ap=argparse.ArgumentParser()
ap.add_argument('--revision',required=True)
args=ap.parse_args()
if not args.revision.replace('-','').isalnum(): raise ValueError('Invalid revision')
repo=Path(__file__).resolve().parents[1]
src=repo.parent
snapshot=repo/'input-local'/args.revision
out=repo/'generated-local'/args.revision
assert not snapshot.exists() and not (out/'input-manifest.json').exists(), 'Preserve earlier revisions'
old=json.loads((repo/'generated-local/input-manifest.json').read_text())
old_by_path={r['path']:r for r in old}
old_packages={r['path']:r for r in json.loads((repo/'generated-local/resource-inventory.json').read_text())}
paths=[]
for root in sorted(src.iterdir()):
    if root.name in ('allied-campaign-workspace','_ac-tools-local','_ac-backup-local'): continue
    if root.is_symlink() or root.is_junction(): raise ValueError('Linked root')
    paths.extend(files(root) if root.is_dir() else [root])
records=[]; packages=[]; modules=[]; diffs=[]
snapshot.mkdir(parents=True)
for p in sorted(paths):
    rel=p.relative_to(src).as_posix(); digest=sha(p)
    dest=snapshot/rel; dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dest)
    assert sha(dest)==digest and sha(p)==digest, ('Input changed during capture',rel)
    records.append(dict(path=rel,size=p.stat().st_size,sha256=digest))
    if p.suffix.lower()!='.pk3': continue
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None, rel
        entries=[]
        for e in z.infolist():
            if e.is_dir(): continue
            name=e.filename.replace('\\','/')
            assert not name.startswith('/') and '..' not in name.split('/') and ':' not in name
            entries.append(dict(path=name,size=e.file_size,crc32=f'{e.CRC:08x}'))
    packages.append(dict(path=rel,sha256=digest,entries=entries))
    if p.name.startswith('Restoration_'):
        modules.append(dict(path=rel,sha256=digest,resources=len(entries),installed=True))
        before={e['path']:(e['size'],e['crc32']) for e in old_packages.get(rel,{}).get('entries',[])}
        after={e['path']:(e['size'],e['crc32']) for e in entries}
        diffs.append(dict(path=rel,added=sorted(after.keys()-before.keys()),removed=sorted(before.keys()-after.keys()),changed=sorted(k for k in before.keys()&after.keys() if before[k]!=after[k])))
assert len(modules)==7, 'Review changed package composition before activation'
fingerprint=hashlib.sha256('\n'.join(m['path']+' '+m['sha256'] for m in modules).encode()).hexdigest()
save(out/'input-manifest.json',records)
save(out/'resource-inventory.json',packages)
manifest=dict(schema=1,status='NUTZER_AUTORISIERTE_LOKALE_REVISION_LAUFZEIT_OFFEN',version=None,version_evidence='Local files supplied and replacement authorized by user; no verified release identifier',package_fingerprint=fingerprint,modules=modules,loose_files='Full revision inventory retained locally; unchanged unless listed in revision report',source='User-provided local installation; no download',authorization='User confirmed intentional WCR update and requested future use in chat on 2026-10-13')
save(repo/f'third_party/wcr/revisions/{args.revision}.json',manifest)
new_by_path={r['path']:r for r in records}
save(repo/f'checkpoints/CP00/{args.revision}-import.json',dict(revision=args.revision,files=len(records),bytes=sum(r['size'] for r in records),independent_copy_verified=True,write_protected=False,input_manifest_sha256=sha(out/'input-manifest.json'),package_fingerprint=fingerprint,added_files=sorted(new_by_path.keys()-old_by_path.keys()),removed_files=sorted(old_by_path.keys()-new_by_path.keys()),changed_files=[dict(path=k,before=old_by_path[k]['sha256'],after=new_by_path[k]['sha256']) for k in sorted(new_by_path.keys()&old_by_path.keys()) if old_by_path[k]['sha256']!=new_by_path[k]['sha256']],package_resource_changes=diffs))
print('VERIFIED',args.revision,len(records),'files; WCR',fingerprint)
