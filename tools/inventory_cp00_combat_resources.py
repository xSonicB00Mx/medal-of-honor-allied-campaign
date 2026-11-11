"""Inventory baseline weapon IDs and human corpse resources; no asset export."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
from inventory_cp00 import save

repo = Path(__file__).resolve().parents[1]
runtime = repo/'runtime-local/CP00-r4'
contexts = {}
for game, directories in [('AA',['main']),('SH',['main','mainta']),('BT',['main','maintt'])]:
    effective = {}
    for directory in directories:
        for package in sorted((runtime/directory).glob('*.pk3'),key=lambda p:p.name.lower()):
            with zipfile.ZipFile(package) as archive:
                for name in archive.namelist():
                    key = name.lower()
                    weapon = key.startswith('models/weapons/') and key.endswith('.tik')
                    corpse = key.startswith(('models/static/body_', 'models/animate/body_', 'models/animate/allied_')) and ('body_' in key or '_dead' in key) and key.endswith('.tik')
                    if weapon or corpse or key in ('global/ai.scr','global/killed.scr'):
                        data = archive.read(name)
                        effective[key] = (package.relative_to(runtime).as_posix(),name,data)
    entries = []
    for key,(provider,name,data) in sorted(effective.items()):
        text = data.decode('latin1')
        kind = 'death_script' if key.startswith('global/') else 'human_corpse_model'
        if key.startswith('models/weapons/'):
            if not re.search(r'(?im)^\s*classname\s+weapon\s*$',text):
                continue
            kind = 'weapon'
        record = dict(resource=key,kind=kind,predicted_provider=provider,
                      entry=name,sha256=hashlib.sha256(data).hexdigest())
        if kind == 'weapon':
            record['declared_fields'] = {}
            for field in ('name','weapongroup','weaponclass','bulletdamage','bulletrange','ammotype'):
                values = re.findall(r'(?im)^\s*'+field+r'\s+([^\r\n/]+)',text)
                if values:
                    record['declared_fields'][field] = [v.strip() for v in values]
            record['note'] = 'Text declarations only; conditionals/includes and runtime origin require separate verification.'
        entries.append(record)
    contexts[game] = entries
save(repo/'checkpoints/CP00/CP00-r4-combat-resource-catalog.json',dict(
    candidate='CP00-r4',wcr_package_fingerprint=json.loads((repo/'third_party/wcr/revisions/CP00-r4.json').read_text(encoding='utf-8'))['package_fingerprint'],
    scope='Static package-order inventory, not full runtime coverage. No original asset content included.',
    contexts=contexts))
print({game:{kind:sum(e['kind']==kind for e in entries) for kind in ('weapon','human_corpse_model','death_script')} for game,entries in contexts.items()})
