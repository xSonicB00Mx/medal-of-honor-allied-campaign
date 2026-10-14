"""Inventory local full-screen UI artwork; never upload or alter the runtime.

Outputs include copyrighted source pixels and must stay in ignored local folders.
This is preparation for a manually reviewed, strictly serial Gemini outpaint queue.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows, unique = [], {}
    for game, folder in [('AA', 'main'), ('SH', 'mainta'), ('BT', 'maintt')]:
        entries = {}
        for directory in (['main'] if game == 'AA' else ['main', folder]):
            for package in sorted((args.runtime / directory).glob('*.pk3'), key=lambda p: p.name.lower()):
                with zipfile.ZipFile(package) as z:
                    for name in z.namelist():
                        entries[name.lower()] = (package, name)

        def read(name):
            package, entry = entries[name.lower()]
            with zipfile.ZipFile(package) as z:
                return z.read(entry)

        shaders = {}
        for name in entries:
            if not name.endswith('.shader'):
                continue
            text = re.sub(r'//[^\n]*', '', read(name).decode('latin1').replace('\r', ''))
            # Outer shader definitions contain nested stage braces.
            for match in re.finditer(r'(?m)^\s*([^\s{}]+)\s*\n\s*\{', text):
                start, depth, end = match.end(), 1, match.end()
                while end < len(text) and depth:
                    depth += (text[end] == '{') - (text[end] == '}')
                    end += 1
                maps = re.findall(r'(?mi)^\s*(?:clampmap|map)\s+([^\s]+)', text[start:end])
                if len(maps) == 1:
                    shaders[match.group(1).lower()] = maps[0].lower()

        for name in sorted(entries):
            if not name.startswith('ui/') or not name.endswith(('.urc', '.inc')):
                continue
            loading = name.startswith('ui/loading_')
            if loading and not re.match(r'ui/loading_(?:m[1-6]l|t[1-3]l|e[1-3]l)', name):
                continue
            if loading and game == 'BT':
                continue  # Explicit user exclusion, even for inherited AA resources.
            if loading and game == 'SH' and not name.startswith('ui/loading_t'):
                continue
            text = read(name).decode('latin1').replace('\r', '')
            layers = []
            for block in re.findall(r'(?is)resource\s+Label\s*\{([^{}]*)\}', text):
                if re.search(r'(?mi)^\s*enabledcvar\b', block):
                    continue
                rect = re.search(r'(?mi)^\s*rect\s+([\d. -]+)', block)
                shader = re.search(r'(?mi)^\s*shader\s+"?([^"\s]+)', block)
                if not rect or not shader:
                    continue
                values = [float(v) for v in rect.group(1).split()]
                if len(values) != 4:
                    continue
                x, y, w, h = values
                if y != 0 or h < 480 or w < 128 or x < 0 or x >= 640:
                    continue
                tex = shaders.get(shader.group(1).lower(), shader.group(1).lower())
                if tex not in entries:
                    tex = next((tex + ext for ext in ['.tga', '.jpg', '.png'] if tex + ext in entries), '')
                if not tex:
                    continue
                # Match the renderer's default r_loadjpg=1: expansion JPGs may
                # override inherited AA TGA names even in an explicit shader.
                jpg = str(Path(tex).with_suffix('.jpg')).replace('\\', '/')
                if tex.endswith(('.tga', '.jpg')) and jpg in entries:
                    tex = jpg
                raw = read(tex)
                try:
                    image = Image.open(io.BytesIO(raw)).convert('RGBA')
                except Exception:
                    continue
                rect = [round(v) for v in values]
                image = image.resize((rect[2], rect[3]), Image.Resampling.BICUBIC)
                layers.append((rect, image, dict(shader=shader.group(1), texture=tex,
                    provider=str(entries[tex][0].relative_to(args.runtime)), sha256=digest(raw))))
            if not layers or min(r[0] for r, _, _ in layers) != 0 or max(r[0]+r[2] for r, _, _ in layers) < 640:
                continue
            image = Image.new('RGBA', (640, 480), (0, 0, 0, 255))
            for rect, layer, _ in layers:
                image.alpha_composite(layer, (rect[0], rect[1]))
            image = image.convert('RGB')
            sha = digest(image.tobytes())
            asset_id = unique.get(sha)
            if not asset_id:
                asset_id = game + '-' + Path(name).stem
                unique[sha] = asset_id
                image.save(args.output / (asset_id + '.png'))
            # SH film frames are assessed separately; preserve their intentional black border.
            band = list(image.crop((0, 0, 640, 50)).get_flattened_data())
            black_top = sum(max(p) <= 8 for p in band) / len(band)
            rows.append(dict(game=game, ui=name, asset_id=asset_id,
                category='loading' if loading else ('briefing' if 'brief' in name else 'menu'),
                pixel_sha256=sha, layers=[dict(rect=r, **meta) for r, _, meta in layers],
                black_top_fraction=round(black_top, 4),
                state='inspect-letterbox' if game == 'SH' and loading and black_top > .98 else 'awaiting-generation',
                generation=None))
    manifest = dict(runtime=str(args.runtime), provider='Google Gemini / Nano Banana (user requested)',
        max_simultaneous_generations=1, generations_submitted=0, breakthrough_loading_excluded=True,
        note='Source reconstruction only; visual review required before upload. No runtime changes.', assets=rows)
    (args.output / 'queue.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    ids = list(dict.fromkeys(row['asset_id'] for row in rows))
    for start in range(0, len(ids), 16):
        subset = ids[start:start+16]
        sheet = Image.new('RGB', (1280, ((len(subset)+3)//4)*260), '#202020')
        draw = ImageDraw.Draw(sheet)
        for i, asset_id in enumerate(subset):
            x, y = (i%4)*320, (i//4)*260
            draw.text((x+5, y+3), asset_id, fill='white')
            with Image.open(args.output/(asset_id+'.png')) as image:
                sheet.paste(image.resize((320,240)), (x,y+20))
        sheet.save(args.output/f'contact-{start//16+1:02d}.jpg')
    print(json.dumps(dict(ui_resources=len(rows), unique_backgrounds=len(ids),
        letterboxed_sh=sum(r['state']=='inspect-letterbox' for r in rows), output=str(args.output))))


if __name__ == '__main__':
    main()
