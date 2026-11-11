"""Install supplied menu artwork and preserve the effective options controls."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
from PIL import Image

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('source',type=Path)
args=ap.parse_args()
root=Path(__file__).resolve().parents[1]
work=root/'generated-local/menu-background';work.mkdir(parents=True,exist_ok=True)
data=args.source.read_bytes();(work/'source.jpg').write_bytes(data)
with Image.open(io.BytesIO(data)) as im:
    assert abs(im.width/im.height-16/9)<0.02
    b=io.BytesIO();im.convert('RGB').save(b,format='TGA')
texture='textures/ac/menu_background'
shader=f'{texture}\n{{\n nopicmip\n nomipmaps\n {{\n clampmap {texture}.tga\n rgbGen identity\n }}\n}}\n'
reports=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    body=None
    for base in (['main'] if folder=='main' else ['main',folder]):
        for p in sorted((root/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
            if p.name=='zzzzzzzzzz_AC_MenuBackground.pk3':continue
            with zipfile.ZipFile(p) as z:
                if 'ui/ac_scaling.urc' in z.namelist():body=z.read('ui/ac_scaling.urc').decode('latin1')
    assert body and 'widescreenbackground' not in body
    head,tail=body.split('\n',1)
    body=head+'\nwidescreenbackground "'+texture+'"\n'+tail
    p=work/'packages'/folder/'zzzzzzzzzz_AC_MenuBackground.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr(texture+'.tga',b.getvalue())
        z.writestr('scripts/ac_menu_background.shader',shader)
        z.writestr('ui/ac_scaling.urc',body.encode('latin1'))
    reports.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(data).hexdigest()))
(work/'packages/package-report.json').write_text(json.dumps(reports,indent=2)+'\n')
print('Shared menu artwork packaged for AA/SH/BT.')
