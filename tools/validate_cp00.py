"""CI checks metadata and prevents accidental addition of protected local products."""
import hashlib, json, subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
def git(*args): return subprocess.check_output(['git',*args],cwd=root,text=True)
for path in (root/'third_party').rglob('*.json'):
    json.loads(path.read_text(encoding='utf-8-sig'))
manifest=json.loads((root/'third_party/wcr/manifest.json').read_text())
modules=manifest['modules']
assert len(modules)==7 and all(m['installed'] for m in modules)
actual=hashlib.sha256('\n'.join(m['path']+' '+m['sha256'] for m in modules).encode()).hexdigest()
assert actual==manifest['package_fingerprint']
tracked=git('ls-files').splitlines()
assert not any(p.split('/')[0] in {'input-local','runtime-local','generated-local','profiles-local','artifacts-local','config-local','logs-local','build-local'} for p in tracked)
assert not any(p.lower().endswith(('.pk3','.ras','.sav','.ssv','.bundle')) for p in tracked)
patch=json.loads((root/'third_party/bt_drops/manifest.json').read_text())
assert patch['status']=='NUR_INVENTARISIERT_NICHT_AKTIV'
print('PASS: JSON, WCR fingerprint, seven preserved modules, protected file exclusions, CP0-only drop status')
