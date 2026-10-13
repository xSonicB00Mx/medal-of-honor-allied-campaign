"""Document CP0 providers, without copying third party resource contents into Git."""
import argparse, hashlib, json, zipfile
from collections import defaultdict
from pathlib import Path
from inventory_cp00 import sha, save

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input',type=Path); args=ap.parse_args()
    repo=Path(__file__).resolve().parents[1]; root=args.input
    providers={}; archives={}; resources=defaultdict(list)
    for game in ('main','mainta','maintt'):
        for p in sorted((root/game).glob('*.pk3'),key=lambda p:p.name.lower()):
            rel=p.relative_to(root).as_posix(); z=zipfile.ZipFile(p); archives[rel]=z
            for e in z.infolist():
                if e.is_dir(): continue
                key=e.filename.replace('\\','/').lower()
                resources[key].append(dict(package=rel,entry=e.filename,crc32=f'{e.CRC:08x}',size=e.file_size))
    contexts={}
    for name,dirs in [('AA',['main']),('SH',['main','mainta']),('BT',['main','maintt'])]:
        # Derived from FS_Startup and FS_AddGameDirectory. Runtime `path/which` must confirm.
        effective={}
        for game in dirs:
            for key,pp in resources.items():
                for provider in pp:
                    if provider['package'].split('/')[0]==game: effective[key]=provider
            for p in (root/game).rglob('*'):
                if p.is_file() and p.suffix.lower()!='.pk3' and 'save' not in p.parts and 'configs' not in p.parts:
                    key=p.relative_to(root/game).as_posix().lower()
                    effective[key]=dict(loose=p.relative_to(root).as_posix(),sha256=sha(p))
        collisions=[]
        for key,pp in resources.items():
            relevant=[x for x in pp if x['package'].split('/')[0] in dirs]
            if not any('Restoration_' in x['package'] for x in relevant): continue
            variants=[]
            for x in relevant:
                data=archives[x['package']].read(x['entry'])
                variants.append(dict(**x,sha256=hashlib.sha256(data).hexdigest()))
            collisions.append(dict(resource=key,providers=variants,predicted_effective=effective[key],decision='PRESERVE_INSTALLED_WCR_BASELINE',runtime_verified=False))
        contexts[name]=dict(search_directories_low_to_high=dirs,resources=collisions)
    save(repo/'third_party/resource_conflicts.json',dict(schema=1,engine='a2f340195975f4f042e28a60b62561dd9a0b2700',status='STATIC_PREDICTION_REQUIRES_RUNTIME_CONFIRMATION',contexts=contexts))
    print({k:len(v['resources']) for k,v in contexts.items()})

if __name__=='__main__': main()
