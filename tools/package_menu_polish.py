"""Menu-only full-size font metrics and local HD cursor; no changes to HUD fonts."""
from pathlib import Path
import io, json, re, hashlib, zipfile
from PIL import Image, ImageChops
root=Path(__file__).resolve().parents[1];work=root/'generated-local/menu-polish'
im=Image.open(work/'cursor-master.png').convert('RGBA')
box=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
im=im.crop(box).resize((256,256),Image.Resampling.LANCZOS)
im.save(work/'cursor.png');b=io.BytesIO();im.save(b,format='TGA');cursor=b.getvalue()
reports=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    files={'gfx/2d/mouse_cursor.tga':cursor};shaders=[];fonts=[]
    with zipfile.ZipFile(root/'runtime-local/CP08-r1'/folder/'zzzzzzz_AC_Courier.pk3') as z:
        for name in z.namelist():
            if not name.endswith('.ritualfont'):continue
            stem=Path(name).stem
            if not stem.startswith(('facfont-','verdana-','ac-courier-','courier-','handle-','delima-')):continue
            body=z.read(name).decode('ascii')
            files[f'fonts/ac-menu-{stem}.ritualfont']=body.encode('ascii')
            shaders.append(f'gfx/fonts/ac-menu-{stem}\n{{\n nopicmip\n {{\n clampmap gfx/fonts/{stem}.tga\n blendFunc blend\n rgbGen global\n alphaGen global\n }}\n}}')
            fonts.append(stem)
    shaders.append('gfx/2d/mouse_cursor\n{\n nopicmip\n {\n clampmap gfx/2d/mouse_cursor.tga\n blendFunc blend\n rgbGen global\n alphaGen global\n }\n}')
    # Give hover states their own real RGBA images, so deferred/implicit
    # material registration cannot fall back to the opaque missing image.
    with zipfile.ZipFile(root/'runtime-local/CP08-r1'/folder/'zzzzzz_AC_Widescreen.pk3') as z:
        for button in ['quit','back_to_game']:
            base=f'textures/ac/widescreen/{button}_button'
            original=Image.open(io.BytesIO(z.read(base+'.tga'))).convert('RGBA')
            hover=ImageChops.multiply(original,Image.new('RGBA',original.size,(255,209,89,255)))
            b=io.BytesIO();hover.save(b,format='TGA');files[base+'_h.tga']=b.getvalue()
            shaders.append(f'{base}_h\n{{\n nopicmip\n {{\n clampmap {base}_h.tga\n blendFunc blend\n rgbGen global\n alphaGen global\n }}\n}}')
    # Preserve all previously fitted controls from the effective options layout.
    for package in sorted((root/'runtime-local/CP08-r1'/folder).glob('*.pk3')):
        if package.name == 'zzzzzzzzz_AC_MenuPolish.pk3': continue
        with zipfile.ZipFile(package) as z:
            if 'ui/ac_scaling.urc' in z.namelist():
                files['ui/ac_scaling.urc']=z.read('ui/ac_scaling.urc').replace(b'Menu and font size',b'Menu font size')
    files['scripts/zzzz_ac_menu_polish.shader']='\n'.join(shaders).encode('ascii')
    p=work/'packages'/folder/'zzzzzzzzz_AC_MenuPolish.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in files.items():z.writestr(n,data)
    reports.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),menu_font_scale=1.0,fonts=fonts,cursor_size=[256,256]))
(work/'packages/package-report.json').write_text(json.dumps(reports,indent=2)+'\n')
print('Menu-only font aliases and HD cursor packaged.')
