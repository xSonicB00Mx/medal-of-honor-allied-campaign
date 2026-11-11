"""Mortar HUD label and code-native luminous target material."""
from pathlib import Path
import zipfile,json,hashlib,re
r=Path(__file__).resolve().parents[1];out=r/'generated-local/mortar/packages';reports=[]
shader='''ac/mortar_target
{
 nopicmip
 nomipmaps
 cull none
 {
  map $whiteimage
  blendFunc GL_SRC_ALPHA GL_ONE
  rgbGen vertex
  alphaGen vertex
 }
}
'''
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    body=None
    for base in (['main'] if folder=='main' else ['main',folder]):
        for p in sorted((r/'runtime-local/CP08-r1'/base).glob('*.pk3')):
            if p.name.endswith('_AC_MortarAim.pk3'):continue
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if n.lower()=='ui/hud_ammo_granatwerfer.urc':body=z.read(n).decode('latin1')
    p=out/folder/'zzzzzzzzzzzz_AC_MortarAim.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('scripts/ac_mortar_target.shader',shader)
        if body:
            body=body.replace('title "Granatwerfer"','title "Mortar"').replace('rect 100 86 88 16','rect 24 84 164 24')
            z.writestr('ui/hud_ammo_granatwerfer.urc',body)
    reports.append(dict(game=game,package=p.relative_to(r).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(out/'package-report.json').write_text(json.dumps(reports,indent=2)+'\n');print('Mortar HUD and target shader packaged.')
