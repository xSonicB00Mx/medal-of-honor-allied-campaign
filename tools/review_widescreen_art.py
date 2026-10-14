"""Stage a single downloaded outpaint and an original-center review composite."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('asset')
ap.add_argument('--download', type=Path)
ap.add_argument('--approve', help='Visual inspection notes; only use after inspecting the composite')
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
work = root/'generated-local/widescreen'
original = work/'effective'/(args.asset+'.png')
assert original.is_file(), original
target = work/'queue'/(args.asset+'-guide-result.jpg')
if args.download:
    assert args.download.is_file()
    assert not target.exists(), 'Never silently replace a reviewed generation'
    shutil.copy2(args.download, target)
with Image.open(target) as image:
    composite = image.convert('RGB').resize((1536,864), Image.Resampling.LANCZOS)
with Image.open(original) as image:
    composite.paste(image.convert('RGB').resize((1152,864), Image.Resampling.LANCZOS), (192,0))
preview = work/(args.asset+'-preview.png')
composite.save(preview)
if args.approve:
    path = work/'approved.json'
    approvals = json.loads(path.read_text(encoding='utf-8'))
    approvals[args.asset] = dict(status='approved', file=str(target.relative_to(root)),
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        conversation='https://gemini.google.com/app/4cc7b207ff2827b7', review=args.approve)
    path.write_text(json.dumps(approvals,indent=2)+'\n', encoding='utf-8')
print(preview)
