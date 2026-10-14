"""Verify protected inputs and package the local CP1 candidate. Never upload ZIP."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from inventory_cp00 import sha,save
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP01-r1'
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
assert not subprocess.check_output(['git','diff','HEAD','--','code','mod','tools/start_campaign.cmd'],cwd=r), 'Dirty build inputs'
base=json.loads((r/'runtime-local/CP00-r4/build-manifest.json').read_text(encoding='utf-8'))
inputs=json.loads((r/'generated-local/CP00-r4/input-manifest.json').read_text(encoding='utf-8'))
drift=[]
for e in inputs:
 p=r.parent/e['path'];actual=sha(p) if p.is_file() else None
 if actual!=e['sha256']:drift.append(dict(path=e['path'],expected=e['sha256'],actual=actual))
assert not drift,drift
data=json.loads((r/'generated-local/CP00-r4/runtime-data-manifest.json').read_text(encoding='utf-8'))
for e in data:assert sha(rt/e['path'])==e['sha256'],e['path']
for e in json.loads((r/'third_party/mp1/manifest.json').read_text(encoding='utf-8'))['files']:
 assert sha(Path('D:/SteamLibrary/steamapps/common/Max Payne')/e['path'])==e['sha256']
own=[e['path'] for e in base['owned_files']]+['main/zzzz_AC_UI.pk3','mainta/zzzz_AC_UI.pk3','maintt/zzzz_AC_UI.pk3','maintt/zzzz_AC_BT_Drops.pk3']
manifest=dict(schema=2,build_id='CP01-r1',source_commit=source,engine_source_commit=source,upstream_commit=base['upstream_commit'],wcr_package_fingerprint=base['wcr_package_fingerprint'],data_manifest_sha256=base['data_manifest_sha256'],runtime_data_manifest=base['runtime_data_manifest'],input_manifest=base['input_manifest'],data_files=len(data),owned_files=[dict(path=p,sha256=sha(rt/p)) for p in own],save_schema='Unchanged OpenMoHAA archive layout; saves load in tested contexts. BT patch requires a new mission for full activation.',weapon_policy='WCR preserved; no CP2 or later effects',toolchain=dict(cmake='4.4.4',msbuild='17.14.51',generator='Visual Studio 17 2022 x64',configuration='RelWithDebInfo',flex_bison='2.5.25',options=['USE_HTTP=OFF','USE_RENDERER_DLOPEN=OFF','BUILD_RENDERER_GL2=OFF']),merge_recipe='tools/import_cp00a.py at '+source,ui_recipe='tools/package_cp01_ui.py at '+source,status='IMPLEMENTED_TESTED_WITH_DOCUMENTED_COVERAGE_LIMITS',personal_acceptance=False,merged=False)
save(rt/'build-manifest.json',manifest);save(r/'checkpoints/CP01/build-manifest.json',manifest)
(rt/'COMPLETE').write_text('CP01-r1\n'+source+'\n',encoding='ascii')
save(r/'checkpoints/CP01/integrity.json',dict(original_files_unchanged=len(inputs),runtime_base_files_unchanged=len(data),mp1_recorded_files_unchanged=True,owned_files=len(own),hardlinks_created=False,original_differences=drift,external_backup=False))
out=r/'artifacts-local/CP01-r1-local-runtime.zip';assert not out.exists()
with zipfile.ZipFile(out,'x',zipfile.ZIP_STORED,allowZip64=True) as z:
 for p in sorted(rt.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(r))
 for p in [r/'tools/start_campaign.cmd',*[r/f'Start-CP01-r1-{g}.cmd' for g in ('AA','SH','BT')]]:z.write(p,p.relative_to(r))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
save(r/'checkpoints/CP01/local-package.json',dict(path=out.relative_to(r).as_posix(),sha256=sha(out),bytes=out.stat().st_size,crc_verified=True,contains_original_game_data=True,upload_allowed=False,source_commit=source))
print('PASS: original inputs, runtime base, MP1 and local ZIP verified',flush=True)
