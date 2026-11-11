"""Package the canonical shared options layout, preserving existing artwork packages."""
from pathlib import Path
import zipfile, json, hashlib
r=Path(__file__).resolve().parents[1]
sources={name:(r/'mod/ui'/name).read_text(encoding='utf-8').encode('latin1')
         for name in ['ac_scaling.urc','ac_temporal.urc']}
assert all(b'widescreenbackground "textures/ac/menu_background"' in source for source in sources.values())
rows=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 p=r/'generated-local/flinch/packages'/folder/'zzzzzzzzzzzzz_AC_FlinchOptions.pk3'
 p.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for name,source in sources.items():
   info=zipfile.ZipInfo('ui/'+name,(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
   z.writestr(info,source)
 rows.append(dict(game=game,package=p.relative_to(r).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(r/'generated-local/flinch/packages/package-report.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Shared options layout packaged for AA/SH/BT.')
