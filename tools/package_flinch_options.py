"""Package the canonical shared options layout, preserving existing artwork packages."""
from pathlib import Path
import zipfile, json, hashlib
r=Path(__file__).resolve().parents[1]
source=(r/'mod/ui/ac_scaling.urc').read_text(encoding='utf-8').encode('latin1')
assert b'widescreenbackground "textures/ac/menu_background"' in source
rows=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 p=r/'generated-local/flinch/packages'/folder/'zzzzzzzzzzzzz_AC_FlinchOptions.pk3'
 p.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('ui/ac_scaling.urc',source)
 rows.append(dict(game=game,package=p.relative_to(r).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(r/'generated-local/flinch/packages/package-report.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Shared options layout packaged for AA/SH/BT.')
