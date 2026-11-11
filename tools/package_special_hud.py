"""Package reviewed local Imagegen objective/marker artwork and a registered heat mask."""
from pathlib import Path
import hashlib, io, json, zipfile
from PIL import Image

root = Path(__file__).resolve().parents[1]
work = root/'generated-local/hud-upscale/special'
(work/'prepared').mkdir(exist_ok=True)
assets = {}
masters = {}
for name in ['directional_arrow', 'emptybox', 'filledbox', 'objectives_backdrop']:
    source = work/'generated'/f'{name}.png'
    masters[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    im = Image.open(source).convert('RGBA')
    if name != 'objectives_backdrop':
        bounds = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
        assert bounds, name
        im = im.crop(bounds).resize((256, 256), Image.Resampling.LANCZOS)
    else:
        im = im.resize((1024, 1024), Image.Resampling.LANCZOS)
    im.save(work/'prepared'/f'{name}.png')
    folder = 'objectives' if name in ['emptybox', 'filledbox'] else 'hud'
    assets[f'textures/{folder}/{name}.tga'] = im

# The existing additive shader expects an opaque red-on-black mask, not red
# RGB with transparent surroundings. Derive coverage from the installed gun's
# alpha so the heat layer follows exactly the new silhouette, including edges.
gun_path = root/'generated-local/hud-upscale/ammo/prepared/clip_aa_gun.png'
gun = Image.open(gun_path).convert('RGBA')
coverage = gun.getchannel('A')
zero = Image.new('L', gun.size, 0)
mask = Image.merge('RGBA', (coverage, zero, zero, Image.new('L', gun.size, 255)))
assert mask.getchannel('R').tobytes() == coverage.tobytes()
mask.save(work/'prepared/red_mask.png')
reports = []
for game, folder in [('AA','main'), ('SH','mainta'), ('BT','maintt')]:
    selected = dict(assets)
    if game != 'AA':
        selected['textures/hud/red_mask.tga'] = mask
        # Verify the technical mask is registered to the artwork actually used.
        with zipfile.ZipFile(root/'runtime-local/CP08-r1'/folder/'zzzzzzzz_AC_Ammo.pk3') as z:
            installed = Image.open(io.BytesIO(z.read('textures/hud/clip_aa_gun.tga'))).convert('RGBA')
            assert installed.tobytes() == gun.tobytes()
    package = work/'packages'/folder/'zzzzzzzz_AC_SpecialHUD.pk3'
    package.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, im in selected.items():
            data = io.BytesIO(); im.save(data, format='TGA'); z.writestr(name, data.getvalue())
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
    reports.append(dict(game=game, package=package.relative_to(root).as_posix(),
        sha256=hashlib.sha256(package.read_bytes()).hexdigest(),
        assets={n:im.size for n,im in selected.items()}, masters=masters,
        gun_master_sha256=hashlib.sha256(gun_path.read_bytes()).hexdigest(),
        shaders='Original definitions preserved, including inverse-alpha marker and additive heat layer'))
(work/'packages/package-report.json').write_text(json.dumps(reports, indent=2)+'\n')
print('Three packages: objective boxes, subtle panel, marker; SH/BT heat mask matches installed gun alpha.')
