"""Local-only candidate package with protected-input and baseline integrity checks."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
from inventory_cp00 import sha,save
ap=argparse.ArgumentParser();ap.add_argument('checkpoint',choices=['03','04','05']);ap.add_argument('--revision',default='r1');ap.add_argument('--zip',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];cp='CP'+a.checkpoint;build=cp+'-'+a.revision;rt=r/'runtime-local'/build;report=r/'checkpoints'/cp
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
assert not subprocess.check_output(['git','diff','HEAD','--','code','mod'],cwd=r),'Dirty compiled inputs'
inputs=json.loads((r/'generated-local/CP00-r4/input-manifest.json').read_text())
for e in inputs: assert sha(r.parent/e['path'])==e['sha256'],e['path']
base=json.loads((r/'checkpoints/CP02/build-manifest.json').read_text())
data=json.loads((r/'generated-local/CP00-r4/runtime-data-manifest.json').read_text())
for e in data: assert sha(rt/e['path'])==e['sha256'],e['path']
for e in json.loads((r/'third_party/mp1/manifest.json').read_text())['files']: assert sha(Path('D:/SteamLibrary/steamapps/common/Max Payne')/e['path'])==e['sha256']
own={e['path'] for e in base['owned_files']}|{'main/zzzz_AC_MP1.pk3'}
if int(a.checkpoint)>=4:own.add('main/zzzz_AC_Wounds.pk3')
manifest={**base,'build_id':build,'source_commit':source,'engine_source_commit':source,'owned_files':[dict(path=p,sha256=sha(rt/p)) for p in sorted(own)],'weapon_policy':'mod/effects/weapon_policy.json version 3','status':'TECHNICAL_CANDIDATE_WITH_REPORTED_TEST_LIMITS','personal_acceptance':False,'merged':False,'save_schema':'Original server save layout; CP4+ appends versioned cgame wound state. New wound saves require this or later build.'}
manifest['ui_recipe']='tools/package_cp01_ui.py at '+source
manifest['change']={'03':'MP1 drops and precise world stains','04':'Animated entry wounds and archived transforms','05':'Directional large exit wounds, current-pose particle blocking, shared mist policy and English UI'}[a.checkpoint]
if int(a.checkpoint)>=5:manifest['save_schema']='Unchanged server saves; cgame ACW2 with up to 64 triangles/wound; reads original and CP4 ACW1 saves without inventing historical exits. CP5 saves require CP5 or later compatible reader.'
save(report/'build-manifest.json',manifest);save(rt/'build-manifest.json',manifest);(rt/'COMPLETE').write_text(build+'\n'+source+'\n')
save(report/'integrity.json',dict(protected_inputs_unchanged=len(inputs),runtime_base_files_unchanged=len(data),mp1_unchanged=True,originals_modified=False))
if a.zip:
 out=r/'artifacts-local'/(build+'-runtime.zip');assert not out.exists()
 with zipfile.ZipFile(out,'x',zipfile.ZIP_STORED,allowZip64=True) as z:
  for p in sorted(rt.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(r))
  for p in [r/('tools/start_'+cp.lower()+'.cmd'),*[r/('Start-'+build+'-'+g+'.cmd') for g in ('AA','SH','BT')]]:z.write(p,p.relative_to(r))
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 save(report/'package.json',dict(path=out.relative_to(r).as_posix(),sha256=sha(out),bytes=out.stat().st_size,crc_verified=True,upload_allowed=False,contains_original_assets=True,source_commit=source))
print(build+': protected inputs and runtime integrity passed')
