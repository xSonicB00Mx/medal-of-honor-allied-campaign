"""Rasterize local Courier New with natural proportions and matching metrics.

Package local textures, metrics and filtering shaders. Symbol fonts, colors and
text bindings remain untouched. No font file or artwork is committed.
"""
import argparse
import hashlib
import io
import json
import math
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from singleplayer_ui import multiplayer_ui
from hud_weapon_names import expand_static_weapon_names


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atlas(body, font_path, scale):
    """Keep Courier's true advance and aspect; pack fresh cells and metrics."""
    source_height = float(re.search(r'\bheight\s+(\S+)', body)[1])
    indices = list(map(int, re.search(r'indirections\s*\{([^}]+)', body)[1].split()))
    assert len(indices) == 256
    probe = ImageFont.truetype(str(font_path), 256)
    cap = probe.getbbox('H', anchor='ls')
    font = ImageFont.truetype(str(font_path), round(source_height*scale*.65*256/(cap[3]-cap[1])))
    assert font.getname() == ('Courier New', 'Bold')
    w = math.ceil(font.getlength('M'))
    h = round(source_height*scale)
    gap = scale
    columns = (256*scale)//(w+gap)
    rows = math.ceil((max(indices)+1)/columns)
    texture_height = 1 << math.ceil(math.log2(rows*(h+gap)))
    image = Image.new('RGBA', (256*scale, texture_height))
    aspect = image.width/image.height
    locations = []
    for index in range(256):
        slot = index if index<=max(indices) else 0
        locations.append(((slot%columns)*(w+gap)/scale,
                          (slot//columns)*(h+gap)/scale, w/scale, h/scale))
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
        mask = Image.new('L', (w, h))
        ImageDraw.Draw(mask).text((0, round(h*.79)), char, font=font,
                                  fill=255, anchor='ls', stroke_width=0)
        shadow_offset = max(1, round(scale*.6))
        cell = Image.new('RGBA', (w, h))
        shadow = Image.new('RGBA', mask.size, (0, 0, 0, 0))
        shadow.putalpha(mask.point(lambda a: round(a*.7)))
        cell.alpha_composite(shadow, (shadow_offset, shadow_offset))
        ink = Image.new('RGBA', mask.size, (255, 255, 255, 0))
        ink.putalpha(mask)
        cell.alpha_composite(ink)
        x, y, _, _ = locations[index]
        image.alpha_composite(cell, (round(x*scale), round(y*scale)))
    metrics = (f'RitFont\nheight {h/scale:.8f}\naspect {aspect:.8f}\nindirections {{\n'
               + ' '.join(map(str,indices)) + '\n}\nlocations {\n'
               + '\n'.join('{ '+' '.join(f'{v:.8f}' for v in row)+' }' for row in locations)
               + '\n}\n').encode('ascii')
    return image, metrics, len(rendered), w/scale


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
        effective, menus = {}, {}
        for directory in (['main'] if game == 'AA' else ['main', folder]):
            for package in sorted((args.runtime/directory).glob('*.pk3'), key=lambda p:p.name.lower()):
                if package.name == 'zzzzzzz_AC_Courier.pk3':
                    continue
                with zipfile.ZipFile(package) as z:
                    for name in z.namelist():
                        if name.lower().startswith('fonts/') and name.lower().endswith('.ritualfont'):
                            effective[name.lower()] = z.read(name)
                        if name.lower().startswith('ui/') and name.lower().endswith('.urc') and not multiplayer_ui(name.lower()):
                            menus[name.lower()] = z.read(name)
        # Custom menu sizes allow uniform size changes where wider text needs room.
        template = effective['fonts/facfont-20.ritualfont']
        for height in range(10, 18):
            effective[f'fonts/ac-courier-{height}.ritualfont'] = re.sub(
                rb'\bheight\s+\S+', f'height {height}'.encode(), template, count=1)
        files, fonts, shaders = {}, [], []
        for name, data in sorted(effective.items()):
            stem = Path(name).stem
            if stem.startswith('marlett'):
                continue  # UI arrows/checkmarks are symbols, not Latin letters.
            image, metrics, count, advance = atlas(data.decode('latin1'), args.font, args.scale)
            buffer = io.BytesIO()
            image.save(buffer, format='TGA')
            files[f'gfx/fonts/{stem}.tga'] = buffer.getvalue()
            files[name] = metrics
            # High-resolution glyphs need mip filtering when reduced to small
            # HUD text; the old no-mipmap shaders undersample thin strokes.
            shaders.append(f'gfx/fonts/{stem}\n{{\n nopicmip\n {{\n'
                           f' clampmap gfx/fonts/{stem}.tga\n'
                           ' blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n'
                           ' rgbGen global\n alphaGen global\n }\n}\n')
            fonts.append(dict(name=stem, source_metrics_sha256=digest(data), metrics_sha256=digest(metrics), size=image.size, glyphs=count, advance=advance))
        files['scripts/zzzz_ac_courier.shader'] = ''.join(shaders).encode('ascii')
        layout_changes = []
        for name, data in menus.items():
            body = data.decode('latin1').replace('\r', '')
            ammo = name.startswith('ui/hud_ammo_')
            def change(match):
                block = match[0]
                font_size = None
                if match[1].lower() == 'field':
                    font_size = 10  # Full numeric values including six decimals.
                if name == 'ui/controls.urc':
                    if re.search(r'(?mi)^name\s+"?bindlist', block): font_size = 10
                    if 'title "Sensitivity:"' in block: font_size = 10
                if ammo:
                    rect = re.search(r'(?m)^rect\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)',block)
                    if rect:
                        x,y,w,h = map(float,rect.groups())
                        if re.search(r'(?mi)^name\s+"?weaponname',block):
                            w += 100
                        else:
                            x += 100
                        block = block[:rect.start()]+f'rect {x:g} {y:g} {w:g} {h:g}'+block[rect.end():]
                    if re.search(r'(?mi)^name\s+"?(?:ammocount|clipcount)',block): font_size = 14
                    if re.search(r'(?mi)^name\s+"?ammoseperator',block): font_size = 10
                if font_size:
                    block = re.sub(r'(?mi)^font\s+[^\n]+\n?', '', block)
                    block = block[:-1]+f'font ac-courier-{font_size}\n'+'}'
                    if match[1].lower() == 'fakkbindlist':
                        # Filename constructs child labels/buttons immediately.
                        block = block.replace(f'font ac-courier-{font_size}\n', '')
                        block = block.replace('filename ', f'font ac-courier-{font_size}\nfilename ', 1)
                return block
            modified = re.sub(r'(?is)resource\s+(\w+)\s*\{[^{}]*\}',change,body)
            if ammo:
                modified = re.sub(r'(?m)^(menu\s+"[^"]+"\s+)([\d.]+)',
                                  lambda m:m[1]+f'{float(m[2])+100:g}',modified,count=1)
                modified = expand_static_weapon_names(modified)
            if modified != body:
                bindings = lambda s:re.findall(r'(?m)^\s*(?:linkcvar|stuffcommand|playerstat|itemstat|maxplayerstat|addpopup|checked_command|unchecked_command)\b[^\n]*',s)
                assert bindings(modified)==bindings(body),name
                files[name] = modified.encode('latin1')
                layout_changes.append(dict(menu=name,source_sha256=digest(data)))
        output = args.output/folder/'zzzzzzz_AC_Courier.pk3'
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2026, 10, 15, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)
        report.append(dict(game=game, package=str(output), sha256=digest(output.read_bytes()),
                           font_sha256=digest(args.font.read_bytes()), fonts=fonts,
                           metrics_changed=True, proportions='Natural Courier New Bold; no glyph resizing', colors='existing global tint; black 70% shadow',
                           raster_scale=args.scale, layout_changes=layout_changes))
    (args.output/'package-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps([dict(game=r['game'], fonts=len(r['fonts'])) for r in report]))


if __name__ == '__main__':
    main()
