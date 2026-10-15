"""Menu-only 66% font metrics and local HD cursor; no changes to HUD fonts."""
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
            body=re.sub(r'\bheight\s+(\S+)',lambda m:f'height {float(m[1])*.66:.10f}',body)
            start=body.index('locations')
            body=body[:start]+re.sub(r'[-+]?\d+(?:\.\d+)?',lambda m:f'{float(m[0])*.66:.10f}',body[start:])
            files[f'fonts/ac-menu-{stem}.ritualfont']=body.encode('ascii')
            shaders.append(f'gfx/fonts/ac-menu-{stem}\n{{\n nopicmip\n {{\n clampmap gfx/fonts/{stem}.tga\n tcMod scale {1/.66:.12f} {1/.66:.12f}\n blendFunc blend\n rgbGen global\n alphaGen global\n }}\n}}')
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
    files['scripts/zzzz_ac_menu_polish.shader']='\n'.join(shaders).encode('ascii')
    p=work/'packages'/folder/'zzzzzzzzz_AC_MenuPolish.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in files.items():z.writestr(n,data)
    reports.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),menu_font_scale=.66,fonts=fonts,cursor_size=[256,256]))
(work/'packages/package-report.json').write_text(json.dumps(reports,indent=2)+'\n')
print('Menu-only font aliases and HD cursor packaged.')
