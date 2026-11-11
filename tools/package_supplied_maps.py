"""Replace only campaign region textures, retaining projection and UI bindings."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('sources', type=Path, help='Directory containing region0.png and region1.png')
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
work = root/'generated-local/CP08/supplied-maps'
work.mkdir(parents=True, exist_ok=True)
textures = {}
sources = []
for i in range(2):
    data = (args.sources/f'region{i}.png').read_bytes()
    (work/f'region{i}.png').write_bytes(data)
    with Image.open(io.BytesIO(data)) as image:
        assert image.size == (2240,1320), 'Maps must match the existing geographic canvas'
        buffer = io.BytesIO()
        image.convert('RGB').save(buffer,format='TGA')
    textures[f'textures/ac_campaign/region{i}.tga'] = buffer.getvalue()
    sources.append(dict(region=i,sha256=hashlib.sha256(data).hexdigest()))
report = []
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    package = work/'packages'/folder/'zzzzzzzz_AC_CampaignMaps.pk3'
    package.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in textures.items():
            z.writestr(name,data)
    report.append(dict(game=game,package=package.relative_to(root).as_posix(),
        sha256=hashlib.sha256(package.read_bytes()).hexdigest(),sources=sources))
(work/'packages/package-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Packaged two supplied maps for all three campaigns; geometry unchanged.')
