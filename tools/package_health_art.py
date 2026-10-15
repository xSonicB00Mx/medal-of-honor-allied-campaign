"""Register the reviewed four-state Imagegen sheet to the original health rectangles."""
from pathlib import Path
import io, json, hashlib, re, zipfile
from PIL import Image

root = Path(__file__).resolve().parents[1]
work = root/'generated-local/hud-upscale/health'
master = work/'generated/health-states.png'
sheet = Image.open(master).convert('RGBA')
names = ['healthback','healthmeter','healthmeterflash','potentialhealthmeter']
files = {}; layers = []
(work/'prepared').mkdir(exist_ok=True)
for i,name in enumerate(names):
    # One column per state; use the opaque body, excluding translucent fringe.
    tile = sheet.crop((round(i*sheet.width/4),0,round((i+1)*sheet.width/4),sheet.height))
    box = tile.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox()
    assert box and box[3]-box[1] > 3*(box[2]-box[0])
    im = tile.crop(box).resize((128,512),Image.Resampling.LANCZOS)
    im.save(work/'prepared'/f'{name}.png')
    b=io.BytesIO(); im.save(b,format='TGA'); files[name]=b.getvalue()
    layers.append(dict(name=name,column=i,bounds=box,size=im.size))
packages=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    selected=names[:3] if game=='AA' else names
    definitions={}
    for base in (['main'] if game=='AA' else ['main',folder]):
        for p in sorted((root/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
            if p.name=='zzzzzzzz_AC_Health.pk3':continue
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if not n.lower().endswith('.shader'):continue
                    text=z.read(n).decode('latin1')
                    for name in selected:
                        match=re.search(r'(?im)^textures/hud/'+name+r'\s*\{',text)
                        if not match:continue
                        start=text.index('{',match.start());end=start+1;depth=1
                        while depth:
                            depth+=(text[end]=='{')-(text[end]=='}');end+=1
                        definitions[name]=text[match.start():end]
    shaders=[]
    for name in selected:
        definition=definitions.get(name,f'textures/hud/{name}\n{{\n nopicmip\n {{\n clampmap textures/hud/{name}.tga\n blendFunc blend\n rgbGen global\n alphaGen global\n }}\n}}')
        shaders.append(re.sub(r'(?im)^\s*nomipmaps\s*$', '',definition.replace('\r','')))
    p=work/'packages'/folder/'zzzzzzzz_AC_Health.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for name in selected:z.writestr(f'textures/hud/{name}.tga',files[name])
        z.writestr('scripts/zzzz_ac_health.shader','\n'.join(shaders))
    packages.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),layers=[l for l in layers if l['name'] in selected],master_sha256=hashlib.sha256(master.read_bytes()).hexdigest()))
(work/'packages/package-report.json').write_text(json.dumps(packages,indent=2)+'\n')
print('Health: four 128x512 layers, original shaders and normalized UV clipping preserved.')
