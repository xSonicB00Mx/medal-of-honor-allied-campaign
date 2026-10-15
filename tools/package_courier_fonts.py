"""Rasterize local Courier New outlines into the existing RitualFont UV layout.

Only local font textures and filtering shaders are packaged. Original metrics, symbol fonts,
colors and text bindings remain untouched. No font file or artwork is committed.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atlas(body, font_path, scale):
    height = float(re.search(r'\bheight\s+(\S+)', body)[1])
    aspect = float(re.search(r'\baspect\s+(\S+)', body)[1])
    indices = list(map(int, re.search(r'indirections\s*\{([^}]+)', body)[1].split()))
    locations = [tuple(map(float, m.split())) for m in re.findall(
        r'\{\s*([\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+)\s*\}', body)]
    assert len(indices) == len(locations) == 256
    image = Image.new('RGBA', (256*scale, round(256/aspect)*scale))
    # Preserve the source's baseline grid. A cap height of 65% leaves space for
    # accents, descenders and a small shadow inside each original glyph cell.
    probe = ImageFont.truetype(str(font_path), 256)
    cap = probe.getbbox('H', anchor='ls')
    font = ImageFont.truetype(str(font_path), round(height*scale*.65*256/(cap[3]-cap[1])))
    rendered = set()
    for byte, index in enumerate(indices):
        if index < 0 or index in rendered:
            continue
        rendered.add(index)
        try:
            char = bytes([byte]).decode('cp1252')
        except UnicodeDecodeError:
            continue
        if char.isspace() or byte < 32:
            continue
        x, y, width, cell_height = locations[index]
        w, h = round(width*scale), round(cell_height*scale)
        if w <= 0 or h <= 0:
            continue
        # Render vector outlines at atlas resolution, then horizontally fit the
        # advance to the original cell. Punctuation retains its natural spacing.
        advance = max(1, round(font.getlength(char)))
        mask = Image.new('L', (advance+2*scale, h))
        ImageDraw.Draw(mask).text((scale, round(h*.79)), char, font=font,
                                  fill=255, anchor='ls', stroke_width=0)
        shadow_offset = max(1, round(scale*.6))
        inset = max(1, round(scale*.25))
        target_width = max(1, w-shadow_offset-2*inset)
        mask = mask.resize((target_width, h), Image.Resampling.LANCZOS)
        cell = Image.new('RGBA', (w, h))
        shadow = Image.new('RGBA', mask.size, (0, 0, 0, 0))
        shadow.putalpha(mask.point(lambda a: round(a*.7)))
        cell.alpha_composite(shadow, (inset+shadow_offset, shadow_offset))
        ink = Image.new('RGBA', mask.size, (255, 255, 255, 0))
        ink.putalpha(mask)
        cell.alpha_composite(ink, (inset, 0))
        image.alpha_composite(cell, (round(x*scale), round(y*scale)))
    return image, len(rendered)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--font', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--scale', type=int, default=8)
    args = ap.parse_args()
    assert 4 <= args.scale <= 16
    report = []
    for game, folder in [('AA', 'main'), ('SH', 'mainta'), ('BT', 'maintt')]:
        effective = {}
        for directory in (['main'] if game == 'AA' else ['main', folder]):
            for package in sorted((args.runtime/directory).glob('*.pk3'), key=lambda p:p.name.lower()):
                if package.name == 'zzzzzzz_AC_Courier.pk3':
                    continue
                with zipfile.ZipFile(package) as z:
                    for name in z.namelist():
                        if name.lower().startswith('fonts/') and name.lower().endswith('.ritualfont'):
                            effective[name.lower()] = z.read(name)
        files, fonts, shaders = {}, [], []
        for name, data in sorted(effective.items()):
            stem = Path(name).stem
            if stem.startswith('marlett'):
                continue  # UI arrows/checkmarks are symbols, not Latin letters.
            image, count = atlas(data.decode('latin1'), args.font, args.scale)
            buffer = io.BytesIO()
            image.save(buffer, format='TGA')
            files[f'gfx/fonts/{stem}.tga'] = buffer.getvalue()
            # High-resolution glyphs need mip filtering when reduced to small
            # HUD text; the old no-mipmap shaders undersample thin strokes.
            shaders.append(f'gfx/fonts/{stem}\n{{\n nopicmip\n {{\n'
                           f' clampmap gfx/fonts/{stem}.tga\n'
                           ' blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n'
                           ' rgbGen global\n alphaGen global\n }\n}\n')
            fonts.append(dict(name=stem, metrics_sha256=digest(data), size=image.size, glyphs=count))
        files['scripts/zzzz_ac_courier.shader'] = ''.join(shaders).encode('ascii')
        output = args.output/folder/'zzzzzzz_AC_Courier.pk3'
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2026, 10, 15, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)
        report.append(dict(game=game, package=str(output), sha256=digest(output.read_bytes()),
                           font_sha256=digest(args.font.read_bytes()), fonts=fonts,
                           metrics_changed=False, colors='existing global tint; black 70% shadow',
                           raster_scale=args.scale))
    (args.output/'package-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps([dict(game=r['game'], fonts=len(r['fonts'])) for r in report]))


if __name__ == '__main__':
    main()
