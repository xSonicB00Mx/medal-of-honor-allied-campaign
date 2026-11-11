"""Package existing SH/BT loading artwork for proportional widescreen zoom.

No AI generation. Source pixels and resulting PK3s stay local and ignored.
The renderer expects a 640x480 source canvas padded, without resizing, to 1024x512.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from PIL import Image, ImageChops


PACKAGE = 'zzzzzzz_AC_LoadingZoom.pk3'
LABEL = re.compile(r'(?is)resource\s+Label\s*\{([^{}]*)\}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = []
    for game, folder, prefix, count in [('SH', 'mainta', 't', 9), ('BT', 'maintt', 'e', 11)]:
        entries = {}
        for directory in ['main', folder]:
            for package in sorted((args.runtime/directory).glob('*.pk3'), key=lambda p: p.name.lower()):
                if package.name == PACKAGE:
                    continue
                with zipfile.ZipFile(package) as z:
                    for name in z.namelist():
                        entries[name.lower()] = (package, name)

        def read(name):
            package, member = entries[name.lower()]
            with zipfile.ZipFile(package) as z:
                return z.read(member)

        files, maps = {}, []
        for ui in sorted(entries):
            if not re.fullmatch(r'ui/loading_' + prefix + r'[1-3]l\d\.urc', ui):
                continue
            original = read(ui)
            text = original.decode('latin1').replace('\r', '')
            canvas = Image.new('RGBA', (640, 480), (0, 0, 0, 255))
            removed, sources = [], []
            for match in LABEL.finditer(text):
                block = match.group(1)
                rect = re.search(r'(?mi)^\s*rect\s+([\d. -]+)', block)
                shader = re.search(r'(?mi)^\s*shader\s+"?([^"\s]+)', block)
                if not rect or not shader:
                    continue
                rect = [int(float(v)) for v in rect.group(1).split()]
                if rect not in [[384, 0, 256, 512], [0, 0, 512, 512]]:
                    continue
                texture = shader.group(1).lower()
                jpg = str(Path(texture).with_suffix('.jpg')).replace('\\', '/')
                if jpg in entries:
                    texture = jpg  # Match the shipped default r_loadjpg=1.
                raw = read(texture)
                with Image.open(io.BytesIO(raw)) as source:
                    layer = source.convert('RGBA').resize(tuple(rect[2:]), Image.Resampling.BICUBIC)
                canvas.alpha_composite(layer, tuple(rect[:2]))
                removed.append(match)
                sources.append(dict(texture=texture, rect=rect, sha256=digest(raw),
                    package=entries[texture][0].relative_to(args.runtime).as_posix()))
            assert len(removed) == 2, (ui, 'Expected exactly two original background labels')
            assert {tuple(s['rect']) for s in sources} == {(384, 0, 256, 512), (0, 0, 512, 512)}
            canvas = canvas.convert('RGB')
            channels = canvas.split()
            mask = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
            bounds = mask.point(lambda value: 255 if value > 20 else 0).getbbox()
            assert bounds and 250 < bounds[3]-bounds[1] < 380, (ui, bounds)
            # Keep two source pixels around the detected picture, including dark
            # feathered edges and the ragged paper border used by Breakthrough.
            crop = [max(0, bounds[0]-2), max(0, bounds[1]-2),
                    min(640, bounds[2]+2), min(480, bounds[3]+2)]
            name = Path(ui).stem.removeprefix('loading_')
            canvas.save(args.output/(game+'-'+name+'-source.png'))
            padded = Image.new('RGB', (1024, 512), 'black')
            padded.paste(canvas)
            buffer = io.BytesIO()
            padded.save(buffer, format='TGA')
            texture = 'textures/alliedcampaign/loadingzoom/'+name+'.tga'
            material = 'ac_loadingzoom/'+name
            files[texture] = buffer.getvalue()
            files['scripts/ac_loadingzoom_'+name+'.shader'] = (
                material+'\n{\n nomipmaps\n nopicmip\n {\n  clampmap '+texture+
                '\n  blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n  rgbGen global\n  alphaGen global\n }\n}\n').encode('ascii')
            stripped = text
            for match in reversed(removed):
                stripped = stripped[:match.start()]+stripped[match.end():]
            directive = 'loadingbackground "'+material+'" '+' '.join(map(str,crop))+'\n'
            first_line, rest = stripped.split('\n', 1)
            overlay = first_line+'\n'+directive+rest
            # Every other directive, particularly loadingbar.txt, remains intact.
            assert overlay.replace(directive, '', 1) == stripped
            assert 'postinclude ui/loadingbar.txt' in overlay
            files[ui] = overlay.encode('latin1')
            maps.append(dict(ui=ui, map=name, source_ui_sha256=digest(original),
                sources=sources, crop=crop, texture_dimensions=[1024,512],
                source_canvas=[640,480], progress_layout_unchanged=True))
        assert len(maps) == count, (game,len(maps))
        destination = args.output/folder/PACKAGE
        destination.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2026, 10, 15, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)
        with zipfile.ZipFile(destination) as z:
            assert z.testzip() is None
        report.append(dict(game=game, package=str(destination), sha256=digest(destination.read_bytes()), maps=maps))
    (args.output/'package-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({row['game']:len(row['maps']) for row in report}))


if __name__ == '__main__':
    main()
