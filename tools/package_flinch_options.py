"""Overlay the current options menu without replacing user artwork or controls."""
from pathlib import Path
import zipfile,json,hashlib
r=Path(__file__).resolve().parents[1];rows=[]
source=(r/'mod/ui/ac_scaling.urc').read_text()
block=source[source.index('resource\nLabel\n{\nname "flinchLabel"'):source.rindex('end.')]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 body=None
 for base in (['main'] if folder=='main' else ['main',folder]):
  for p in sorted((r/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
   if p.name.endswith('_AC_FlinchOptions.pk3'):continue
   with zipfile.ZipFile(p) as z:
    if 'ui/ac_scaling.urc' in z.namelist():body=z.read('ui/ac_scaling.urc').decode('latin1').replace('\r','')
 assert body and 'widescreenbackground' in body and 'playerFlinch' not in body
 body=body.replace('set ac_corpse_effects 1"','set ac_corpse_effects 1; set ac_player_flinch_percent 20; set ac_bt_drop_limits 0; set ac_hud_outline 0"')
 for old,new in [(218,202),(286,254),(354,306)]:
  body=body.replace(f'520 {old} ',f'520 {new} ').replace(f'880 {old} ',f'880 {new} ')
 body=body.replace('title "VISUAL EFFECTS"','title "ADDITIONAL OPTIONS"').replace('end.',block+'end.')
 p=r/'generated-local/flinch/packages'/folder/'zzzzzzzzzzzzz_AC_FlinchOptions.pk3';p.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('ui/ac_scaling.urc',body.encode('latin1'))
 rows.append(dict(game=game,package=p.relative_to(r).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(r/'generated-local/flinch/packages/package-report.json').write_text(json.dumps(rows,indent=2)+'\n')
