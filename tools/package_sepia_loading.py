"""Package the user-supplied AA fallback loading artwork without changing other menus."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('source', type=Path)
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
work = root/'generated-local/widescreen/sepia'
work.mkdir(parents=True, exist_ok=True)
data = args.source.read_bytes()
(work/'sepiaload.png').write_bytes(data)
with Image.open(io.BytesIO(data)) as image:
    assert image.width * 9 == image.height * 16
    buffer = io.BytesIO()
    image.convert('RGB').save(buffer, format='TGA')
body = None
for package in sorted((root/'runtime-local/CP08-r1/main').glob('*.pk3'), key=lambda p:p.name.lower()):
    if package.name == 'zzzzzzzz_AC_SepiaLoading.pk3':
        continue
    with zipfile.ZipFile(package) as z:
        if 'ui/loading_default.urc' in z.namelist():
            body = z.read('ui/loading_default.urc').decode('latin1').replace('\r','')
assert body is not None
pattern = r'(?is)resource\s+Label\s*\{[^{}]*shader\s+"sepiaload_[ab]"[^{}]*\}'
body, count = re.subn(pattern, '', body)
assert count == 2
texture = 'textures/ac/widescreen/aa-sepiaload'
body = re.sub(r'(?m)^(menu[^\n]*\n)', lambda m:m[0]+f'widescreenbackground "{texture}"\n', body, count=1)
assert 'postinclude ui/loadingbar.txt' in body
shader = f'{texture}\n{{\n nomipmaps\n nopicmip\n {{\n clampmap {texture}.tga\n rgbGen global\n alphaGen global\n blendFunc blend\n }}\n}}\n'
package = work/'packages/main/zzzzzzzz_AC_SepiaLoading.pk3'
package.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('ui/loading_default.urc',body.encode('latin1'))
    z.writestr('scripts/ac_sepiaload.shader',shader)
    z.writestr(texture+'.tga',buffer.getvalue())
report = [dict(game='AA',package=package.relative_to(root).as_posix(),
    sha256=hashlib.sha256(package.read_bytes()).hexdigest(),
    source_sha256=hashlib.sha256(data).hexdigest(),provider='User-supplied artwork',
    menus=['ui/loading_default.urc'])]
(work/'packages/package-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
