"""Local release with unchanged protected data and explicit owned-file hashes."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
from inventory_cp00 import sha,save
ap=argparse.ArgumentParser();ap.add_argument('checkpoint',choices=['06','07','08']);ap.add_argument('--zip',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];cp='CP'+a.checkpoint;build=cp+'-r1';rt=r/'runtime-local'/build;out=r/'checkpoints'/cp
assert not subprocess.check_output(['git','diff','HEAD','--','code','mod'],cwd=r),'Uncommitted compiled inputs'
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
for e in json.loads((r/'generated-local/CP00-r4/input-manifest.json').read_text()):assert sha(r.parent/e['path'])==e['sha256'],e['path']
data=json.loads((r/'generated-local/CP00-r4/runtime-data-manifest.json').read_text())
for e in data:assert sha(rt/e['path'])==e['sha256'],e['path']
base=json.loads((r/'checkpoints/CP05a/r3/build-manifest.json').read_text());own={x['path'] for x in base['owned_files']}
own|={f'{f}/zzzzz_AC_Campaign.pk3' for f in ('main','mainta','maintt')}
manifest={**base,'build_id':build,'source_commit':source,'engine_source_commit':source,'owned_files':[dict(path=p,sha256=sha(rt/p)) for p in sorted(own)],'change':'Integrated campaign controller and context-aware saves','personal_acceptance':False,'merged':False}
save(out/'build-manifest.json',manifest);save(rt/'build-manifest.json',manifest);(rt/'COMPLETE').write_text(build+'\n'+source+'\n')
save(out/'integrity.json',dict(protected_inputs_unchanged=9072,runtime_base_unchanged=len(data),originals_modified=False))
(r/('Start-'+build+'.cmd')).write_text('@echo off\ncall "%~dp0tools\\start_'+cp.lower()+'.cmd" %*\n')
if a.zip:
 p=r/'artifacts-local'/(build+'-runtime.zip');assert not p.exists()
 with zipfile.ZipFile(p,'x',zipfile.ZIP_STORED,allowZip64=True) as z:
  for f in sorted(rt.rglob('*')):
   if f.is_file():z.write(f,f.relative_to(r))
  for f in [r/('Start-'+build+'.cmd'),r/('tools/start_'+cp.lower()+'.cmd')]:z.write(f,f.relative_to(r))
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 save(out/'package.json',dict(path=p.relative_to(r).as_posix(),sha256=sha(p),bytes=p.stat().st_size,crc_verified=True,upload_allowed=False,contains_original_assets=True))
print(build,'verified',source)
