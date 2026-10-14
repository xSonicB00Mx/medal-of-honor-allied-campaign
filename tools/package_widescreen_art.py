"""Package only visually approved local outpaints, preserving every UI binding."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from functools import lru_cache
from pathlib import Path

from PIL import Image


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
                        if name.lower().startswith('ui/'):
                            entries[name.lower()] = (package, name)

        @lru_cache(maxsize=None)
        def read(name):
            package, entry = entries[name]
            with zipfile.ZipFile(package) as z:
                return z.read(entry)

        modifications, textures, shaders = {}, {}, []
        for row in inventory['assets']:
            asset = row['asset_id']
            if row['game'] != game or asset not in approved:
                continue
            item = approved[asset]
            if item['status'] != 'approved':
                continue
            source = Path(item['file'])
            data = source.read_bytes()
            assert hashlib.sha256(data).hexdigest() == item['sha256'], asset
            texname = 'textures/ac/widescreen/' + re.sub('[^a-z0-9_-]', '_', asset.lower())
            with Image.open(io.BytesIO(data)) as image:
                # Slight model-output size rounding is normalized here, with
                # no changes to the original game texture used in the center.
                image = image.convert('RGB').resize((1536, 864), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                image.save(buffer, format='TGA')
            textures[texname+'.tga'] = buffer.getvalue()
            shader = f'{texname}\n{{\n nomipmaps\n nopicmip\n {{\n clampmap {texname}.tga\n rgbGen global\n alphaGen global\n blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n }}\n}}\n'
            if shader not in shaders:
                shaders.append(shader)
            ui = row['ui']
            targets = [ui] if ui.endswith('.urc') else [
                name for name in entries if name.endswith('.urc')
                and re.search(r'(?mi)^\s*include\s+"?'+re.escape(ui)+r'"?\s*$',
                    read(name).decode('latin1').replace('\r', ''))]
            for target in targets:
                assert not (game == 'BT' and target.startswith('ui/loading_'))
                body = read(target).decode('latin1').replace('\r', '')
                assert re.search(r'(?m)^menu\b', body), target
                assert target not in modifications or modifications[target][0] == texname, target
                modified = re.sub(r'(?m)^(menu[^\n]*\n)',
                    lambda m: m.group(0)+f'widescreenbackground "{texname}"\n', body, count=1)
                # Exact source body remains once the one added directive is removed.
                assert modified.replace(f'widescreenbackground "{texname}"\n', '', 1) == body
                modifications[target] = (texname, modified.encode('latin1'))
        if not modifications:
            continue
        output = args.output/folder/'zzzzzz_AC_Widescreen.pk3'
        output.parent.mkdir(parents=True, exist_ok=True)
        files = {name: value[1] for name, value in modifications.items()}
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
