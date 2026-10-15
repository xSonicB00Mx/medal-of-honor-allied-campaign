"""Package only visually approved local outpaints, preserving every UI binding."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageOps
from singleplayer_ui import multiplayer_ui


def strip_background(body, layers):
    """Remove only inventoried static image tiles and legacy Voodoo copies."""
    expected = {(layer['shader'].lower(), tuple(layer['rect'])) for layer in layers}
    found = set()
    def replace(match):
        block = match.group(1)
        shader = re.search(r'(?mi)^\s*shader\s+"?([^"\s]+)', block)
        rect = re.search(r'(?mi)^\s*rect\s+([\d. -]+)', block)
        if not shader or not rect:
            return match.group(0)
        key = (shader.group(1).lower(), tuple(float(v) for v in rect.group(1).split()))
        if key in expected:
            found.add(key)
            return ''
        if '/voodoo/' in key[0] and re.search(r'enabledcvar\s+"?ui_voodoo', block):
            return ''
        return match.group(0)
    result = re.sub(r'(?is)resource\s+Label\s*\{([^{}]*)\}', replace, body)
    assert found == expected, ('Missing background tiles', expected - found)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', required=True, type=Path)
    ap.add_argument('--inventory', required=True, type=Path)
    ap.add_argument('--approved', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    inventory = json.loads(args.inventory.read_text(encoding='utf-8'))
    approved = json.loads(args.approved.read_text(encoding='utf-8'))
    report = []
    for game, folder in [('AA', 'main'), ('SH', 'mainta'), ('BT', 'maintt')]:
        entries = {}
        for directory in (['main'] if game == 'AA' else ['main', folder]):
            for package in sorted((args.runtime/directory).glob('*.pk3'), key=lambda p: p.name.lower()):
                if package.name == 'zzzzzz_AC_Widescreen.pk3':
                    continue
                with zipfile.ZipFile(package) as z:
                    for name in z.namelist():
                        entries[name.lower()] = (package, name)

        @lru_cache(maxsize=None)
        def read(name):
            package, entry = entries[name]
            with zipfile.ZipFile(package) as z:
                return z.read(entry)

        modifications, textures, shaders, includes = {}, {}, [], {}
        # Generated lettering only: preserve its alpha over the existing sign.
        sign = Path(__file__).resolve().parents[1]/'generated-local/operations-sign/operations-tilted.png'
        with Image.open(sign) as image:
            assert image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] == 0
            # Ignore near-invisible generator specks when measuring the glyphs.
            bounds = image.getchannel('A').point(lambda v: 255 if v > 32 else 0).getbbox()
            assert bounds
            bounds = (max(0,bounds[0]-8), max(0,bounds[1]-8), min(image.width,bounds[2]+8), min(image.height,bounds[3]+8))
            lettering = ImageOps.contain(image.crop(bounds), (216, 36), Image.Resampling.LANCZOS)
            canvas = Image.new('RGBA', (256,64))
            canvas.alpha_composite(lettering, ((256-lettering.width)//2, 35-lettering.height//2))
            buffer = io.BytesIO(); canvas.save(buffer, format='TGA')
        texname = 'textures/ac/widescreen/operations_sign'
        textures[texname+'.tga'] = buffer.getvalue()
        shaders.append(f'{texname}\n{{\n nomipmaps\n nopicmip\n {{\n clampmap {texname}.tga\n rgbGen global\n alphaGen global\n blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n }}\n}}\n')
        for row in inventory['assets']:
            asset = row['asset_id']
            if row['game'] != game or asset not in approved or multiplayer_ui(row['ui']):
                continue
            item = approved[asset]
            if item['status'] != 'approved':
                continue
            source = Path(item['file'])
            data = source.read_bytes()
            assert hashlib.sha256(data).hexdigest() == item['sha256'], asset
            texname = 'textures/ac/widescreen/' + re.sub('[^a-z0-9_-]', '_', asset.lower())
            with Image.open(io.BytesIO(data)) as image:
                # Normalize model-output rounding without compositing original pixels.
                image = image.convert('RGB').resize((1536, 864), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                image.save(buffer, format='TGA')
            textures[texname+'.tga'] = buffer.getvalue()
            shader = f'{texname}\n{{\n nomipmaps\n nopicmip\n {{\n clampmap {texname}.tga\n rgbGen global\n alphaGen global\n blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n }}\n}}\n'
            if shader not in shaders:
                shaders.append(shader)
            ui = row['ui']
            if not ui.endswith('.urc'):
                includes[ui] = strip_background(read(ui).decode('latin1').replace('\r', ''), row['layers']).encode('latin1')
            targets = [ui] if ui.endswith('.urc') else [
                name for name in entries if name.endswith('.urc')
                and re.search(r'(?mi)^\s*include\s+"?'+re.escape(ui)+r'"?\s*$',
                    read(name).decode('latin1').replace('\r', ''))]
            for target in targets:
                if multiplayer_ui(target):
                    continue
                assert not (game == 'BT' and target.startswith('ui/loading_'))
                body = read(target).decode('latin1').replace('\r', '')
                if ui.endswith('.urc'):
                    body = strip_background(body, row['layers'])
                assert re.search(r'(?m)^menu\b', body), target
                assert target not in modifications or modifications[target][0] == texname, target
                modified = re.sub(r'(?m)^(menu[^\n]*\n)',
                    lambda m: m.group(0)+f'widescreenbackground "{texname}"\n', body, count=1)
                # Exact source body remains once the one added directive is removed.
                assert modified.replace(f'widescreenbackground "{texname}"\n', '', 1) == body
                modifications[target] = (texname, modified.encode('latin1'))
        if game == 'AA':
            for ui in ['ui/medals.urc', 'ui/medals_reset.urc']:
                body = read(ui).decode('latin1').replace('\r', '')
                modified = re.sub(r'(?m)^(menu "[^"]+") 640 480', r'\1 960 540', body)
                modified = modified.replace('virtualres 1', 'virtualres 1\nwidecanvas', 1)
                def widen(match):
                    block = match.group(0)
                    rect = re.search(r'(?m)^rect ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)', block)
                    if not rect:
                        return block
                    x, y, w, h = map(float, rect.groups())
                    # Widen the case/backdrop and dialog masks, not medal icons.
                    stretch = bool(re.search(r'shader "(?:black|medalcaseback)"|name "cancel_', block))
                    nw = w * (1.5 if stretch else 1.125)
                    nx = x * 1.5 if stretch else (x + w/2) * 1.5 - nw/2
                    # Confirmation controls must stay aligned with their panel.
                    if re.search(r'name "(?:yes|no)"', block):
                        nx = 480 + (x - 320) * 1.125
                    return block[:rect.start()] + f'rect {nx:g} {y*1.125:g} {nw:g} {h*1.125:g}' + block[rect.end():]
                modified = re.sub(r'(?is)resource\s+\w+\s*\{[^{}]*\}', widen, modified)
                bindings = lambda s: re.findall(r'(?m)^(?:enabledcvar|hovercommand|stuffcommand|linkcvar).*$', s)
                assert bindings(body) == bindings(modified)
                modifications[ui] = ('', modified.encode('latin1'))
        if game == 'SH':
            # The success slideshow already contains wide paintings. Preserve
            # every timed photo and fade; replace only the two painting widgets.
            for number in range(1, 4):
                ui = f'ui/slideshow{number}.inc'
                old_shader = f'textures/mohmenu/mission{number}stat_1.jpg'
                with Image.open(io.BytesIO(read(old_shader))) as original:
                    canvas = original.convert('RGB').resize((640, 512), Image.Resampling.LANCZOS)
                    channels = canvas.split()
                    mask = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
                    bounds = mask.point(lambda v: 255 if v > 20 else 0).getbbox()
                    assert bounds and bounds[2]-bounds[0] > 600 and 300 < bounds[3]-bounds[1] < 400
                    wide = ImageOps.fit(canvas.crop(bounds), (1536,864), method=Image.Resampling.LANCZOS)
                    buffer = io.BytesIO(); wide.save(buffer, format='TGA')
                texture = f'textures/ac/widescreen/sh-slideshow{number}.tga'
                textures[texture] = buffer.getvalue()
                body = read(ui).decode('latin1').replace('\r', '')
                pattern = r'(?mi)^(\s*shader\s+)"'+re.escape(old_shader)+r'"\s*$'
                modified, count = re.subn(pattern, lambda m: m.group(1)+'"'+texture+'"\nwidescreenpicture\n', body)
                assert count == 2, (ui, count)
                assert re.findall(r'(?m)^fadesequence.*$', body) == re.findall(r'(?m)^fadesequence.*$', modified)
                includes[ui] = modified.encode('latin1')
        if not modifications:
            continue
        output = args.output/folder/'zzzzzz_AC_Widescreen.pk3'
        output.parent.mkdir(parents=True, exist_ok=True)
        files = {name: value[1] for name, value in modifications.items()}
        files.update(includes)
        files.update(textures)
        files['scripts/ac_widescreen.shader'] = ''.join(shaders).encode('ascii')
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2026, 10, 14, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)
        report.append(dict(game=game, package=str(output),
            sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
            menus=sorted(modifications), textures=sorted(textures)))
    (args.output/'package-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([dict(game=r['game'], menus=len(r['menus']), textures=len(r['textures'])) for r in report]))


if __name__ == '__main__':
    main()
