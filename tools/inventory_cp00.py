"""Read-only input inventory and verified independent CP0 snapshot. No extraction."""
import argparse, hashlib, json, os, shutil, zipfile
from pathlib import Path

def sha(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def files(root):
    for base, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            p = Path(base)/name
            if p.is_symlink() or p.is_junction():
                raise ValueError(f'Linked input rejected: {p}')
        for name in sorted(names):
            yield Path(base)/name

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--mp1', type=Path, required=True)
    ap.add_argument('--backup', type=Path, required=True)
    args=ap.parse_args()
    repo=Path(__file__).resolve().parents[1]
    src=args.input.resolve(); backup=args.backup.resolve()
    if src == backup or src in backup.parents and backup.parts[len(src.parts)] not in ('_ac-backup-local',):
        raise ValueError('Use the explicitly separate _ac-backup-local destination')
    roots=[p for p in src.iterdir() if p.name not in ('allied-campaign-workspace','_ac-tools-local','_ac-backup-local')]
    paths=[]
    for p in roots:
        paths.extend(files(p) if p.is_dir() else [p])
    records=[]; packages=[]; wcr=[]
    for p in sorted(paths):
        rel=p.relative_to(src).as_posix()
        digest=sha(p)
        dest=backup/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists(): shutil.copy2(p,dest)
        if sha(dest)!=digest: raise ValueError(f'Backup mismatch: {rel}')
        records.append(dict(path=rel,size=p.stat().st_size,sha256=digest))
        if p.suffix.lower()=='.pk3':
            entries=[]
            with zipfile.ZipFile(p) as z:
                bad=z.testzip()
                if bad: raise ValueError(f'Corrupt PK3: {rel}:{bad}')
                for e in z.infolist():
                    if e.is_dir(): continue
                    name=e.filename.replace('\\','/')
                    if name.startswith('/') or '..' in name.split('/') or ':' in name: raise ValueError(name)
                    entries.append(dict(path=name,size=e.file_size,crc32=f'{e.CRC:08x}'))
                meta=dict(path=rel,sha256=digest,entries=entries)
                packages.append(meta)
                if p.name.startswith('Restoration_'):
                    wcr.append(dict(path=rel,sha256=digest,resources=len(entries),installed=True))
                    for e in entries:
                        if any(x in e['path'].lower() for x in ('readme','changelog','credits','license')):
                            print('WCR DOCUMENT',rel,e['path'],flush=True)
            print('PK3 verified',rel,len(entries),flush=True)
    fingerprint=hashlib.sha256('\n'.join(r['path']+' '+r['sha256'] for r in wcr).encode()).hexdigest()
    save(repo/'generated-local/input-manifest.json',records)
    save(backup.parent/'CP00-input-manifest.json',records)
    save(repo/'generated-local/resource-inventory.json',packages)
    save(repo/'third_party/wcr/manifest.json',dict(schema=1,status='INVENTARISIERT_LAUFZEIT_OFFEN',version=None,version_evidence='No standalone WCR readme/changelog found; do not infer version from website',package_fingerprint=fingerprint,modules=wcr,loose_files='See excluded complete input manifest; provenance checked against local uninstaller where possible',source='https://www.moddb.com/mods/war-chest-restored'))
    patch=[r for r in packages if r['path'].startswith('_forCodex/')]
    save(repo/'third_party/bt_drops/manifest.json',dict(schema=1,status='NUR_INVENTARISIERT_NICHT_AKTIV',source='https://community.pcgamingwiki.com/files/file/2604-medal-of-honor-allied-assault-breakthrough-ammo-and-health-drops/',packages=patch,transport_zip='No outer ZIP found. Provided PK3 is itself a ZIP container.',author=None,version=None))
    mp=[]
    for p in files(args.mp1):
        rel=p.relative_to(args.mp1).as_posix()
        if p.suffix.lower() in ('.ras','.mpm','.exe'):
            mp.append(dict(path=rel,size=p.stat().st_size,sha256=sha(p)))
    save(repo/'third_party/mp1/manifest.json',dict(schema=1,files=mp,status='INVENTARISIERT_KEIN_IMPORT',extractor_found=False))
    assets=[r for r in records if r['path'].startswith('_forCodex/') and r['path'].endswith('.png')]
    save(repo/'third_party/user_assets.json',dict(schema=1,files=assets,redistribution_permission='not established; keep excluded'))
    save(repo/'checkpoints/CP00/input-summary.json',dict(files=len(records),bytes=sum(x['size'] for x in records),pk3=len(packages),wcr_package_fingerprint=fingerprint,backup_hash_verification=True,reparse_points=False,independent_write_protected_backup=False))
    print('VERIFIED SNAPSHOT',len(records),'files',flush=True)

if __name__=='__main__': main()
