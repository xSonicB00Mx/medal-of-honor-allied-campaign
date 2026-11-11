"""Register reviewed timer art to native pivots, bounds and tiled UVs."""
from pathlib import Path
import io,json,hashlib,re,zipfile
from PIL import Image

root=Path(__file__).resolve().parents[1];work=root/'generated-local/hud-upscale/timers'
images={};layers=[]
(work/'prepared').mkdir(exist_ok=True)
def master(name):return Image.open(work/'generated'/f'{name}.png').convert('RGBA')
def anchored(im,anchor,scale):
    # Both moving hands and the dial share the original 64,64 pivot (8x).
    return im.transform((1024,1024),Image.Transform.AFFINE,
        (1/scale,0,anchor[0]-512/scale,0,1/scale,anchor[1]-512/scale),Image.Resampling.BICUBIC)
images['stopwatchbase']=anchored(master('stopwatchbase'),(628,670),352/474)
images['stopwatchhand']=anchored(master('stopwatchhand'),(627,955),256/859)
sheet=master('fuse-pair')
for i,name in enumerate(['fusebase','fusebase_shoot']):
    tile=sheet.crop((i*sheet.width//2,0,(i+1)*sheet.width//2,sheet.height))
    box=tile.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();assert box
    source=Image.open(work/'source'/f'{name}.png').convert('RGBA')
    target=tuple(v*8 for v in source.getchannel('A').getbbox())
    canvas=Image.new('RGBA',(1024,512))
    # Register the generated cord socket to the original y=32 centerline.
    canvas.alpha_composite(tile.crop(box).resize((target[2]-target[0],492),Image.Resampling.LANCZOS),target[:2])
    images[name]=canvas
tile=master('fusetile');box=tile.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();assert box
canvas=Image.new('RGBA',(256,512))
canvas.alpha_composite(tile.crop(box).resize((256,44),Image.Resampling.LANCZOS),(0,234))
images['fusetile']=canvas
for name,im in images.items():
    assert im.getchannel('A').getextrema()==(0,255)
    im.save(work/'prepared'/f'{name}.png')
    layers.append(dict(name=name,size=im.size,bounds=im.getchannel('A').getbbox()))
packages=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    selected=['stopwatchbase','stopwatchhand']+([] if game=='AA' else ['fusebase','fusebase_shoot','fusetile'])
    definitions={}
    for base in (['main'] if game=='AA' else ['main',folder]):
        for p in sorted((root/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
            if p.name=='zzzzzzzz_AC_Timers.pk3':continue
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
        shader=re.sub(r'(?im)^\s*nomipmaps\s*$', '',definitions[name].replace('\r',''))
        if name=='fusetile':
            assert len(re.findall(r'(?im)^\s*map\s',shader))==1
            shader=re.sub(r'(?im)^(\s*map\s+[^\n]+)',r'\1\n        tcMod scale 8 8',shader)
        shaders.append(shader)
    p=work/'packages'/folder/'zzzzzzzz_AC_Timers.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for name in selected:
            b=io.BytesIO();images[name].save(b,format='TGA');z.writestr(f'textures/hud/{name}.tga',b.getvalue())
        z.writestr('scripts/zzzz_ac_timers.shader','\n'.join(shaders))
    packages.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),layers=[l for l in layers if l['name'] in selected],pivot=[512,512],masters={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (work/'generated').glob('*.png')}))
(work/'packages/package-report.json').write_text(json.dumps(packages,indent=2)+'\n')
print('Packaged five timer sprites; native animation frames and HUD scripts preserved.')
