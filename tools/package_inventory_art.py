"""Package local restored inventory artwork, keeping native HUD rectangles/shaders."""
from pathlib import Path
import io,json,hashlib,re,zipfile
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).resolve().parents[1]
work=root/'generated-local/hud-upscale/items'
rows=json.loads((work/'inventory.json').read_text())
prepared=work/'prepared';prepared.mkdir(exist_ok=True)
font_path=Path('C:/Windows/Fonts/courbd.ttf')
images={};layers=[]
# The binocular texture is a legacy label; its live shader uses binoc3 instead.
# Frames are outside this object-art pass. Booklets/uniforms retain original art
# after provider refusals; do not create misleading stand-ins or altered insignia.
excluded={'item_binoculars','item_empty','item_selected','item_papers1','item_papers2',
          'item_uniform','item_uniform_weh','item_uniform_dak'}

def number_overlay(value,target=None):
    # Typeset actual text rather than asking an image model to invent counters.
    # Natural Courier proportions, original yellow and a small dark outline.
    im=Image.new('RGBA',(512,512));draw=ImageDraw.Draw(im)
    font=ImageFont.truetype(str(font_path),480)
    small=ImageFont.truetype(str(font_path),200)
    assert font.getname()==('Courier New','Bold')
    parts=[('x',small),('9',font),('+',small)] if value=='9+' else [('x',small),(value,font)]
    width=sum(f.getlength(t) for t,f in parts)
    if width>440:
        factor=440/width;font=ImageFont.truetype(str(font_path),round(480*factor));small=ImageFont.truetype(str(font_path),round(200*factor))
        parts=[('x',small),('9',font),('+',small)] if value=='9+' else [('x',small),(value,font)]
        width=sum(f.getlength(t) for t,f in parts)
    x=(512-width)/2
    for text,f in parts:
        draw.text((x+5,442+5),text,font=f,anchor='ls',fill=(0,0,0,180),stroke_width=8,stroke_fill=(0,0,0,180))
        draw.text((x,442),text,font=f,anchor='ls',fill=(255,235,0,255),stroke_width=4,stroke_fill=(0,0,0,255))
        x+=f.getlength(text)
    if target:
        glyphs=im.crop(im.getchannel('A').getbbox())
        scale=min((target[2]-target[0])/glyphs.width,(target[3]-target[1])/glyphs.height)
        glyphs=glyphs.resize((round(glyphs.width*scale),round(glyphs.height*scale)),Image.Resampling.LANCZOS)
        im=Image.new('RGBA',(512,512))
        im.alpha_composite(glyphs,(round((target[0]+target[2]-glyphs.width)/2),round((target[1]+target[3]-glyphs.height)/2)))
    return im

for row in rows:
    name=row['name']
    if name in excluded or name.startswith(('item_number','democharge','stickybomb')):continue
    master_path=work/'generated'/(name+'.png')
    master=Image.open(master_path).convert('RGBA')
    bounds=master.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
    assert bounds and master.getchannel('A').getextrema()[0]==0,name
    target=tuple(v*8 for v in row['bounds'])
    # Uniform fit keeps generated proportions intact; center on original alpha bounds.
    sprite=master.crop(bounds)
    scale=min((target[2]-target[0])/sprite.width,(target[3]-target[1])/sprite.height)
    sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(512,512))
    pos=(round((target[0]+target[2]-sprite.width)/2),round((target[1]+target[3]-sprite.height)/2))
    canvas.alpha_composite(sprite,pos);images[name]=canvas
    layers.append(dict(name=name,games=row['games'],source_bounds=row['bounds'],target_bounds=canvas.getchannel('A').getbbox(),size=canvas.size,master_sha256=hashlib.sha256(master_path.read_bytes()).hexdigest()))

for row in rows:
    name=row['name']
    if name.startswith('item_number'):
        value=name.removeprefix('item_number');value={'9plus':'9+','nil':'!?'}.get(value,value)
        images[name]=number_overlay(value)
    elif name.startswith(('democharge','stickybomb')):
        base='explosives' if name.startswith('democharge') else 'item_stickybomb'
        source=Image.open(work/'source'/(row['key']+'.png')).convert('RGBA')
        mask=Image.new('L',source.size)
        mask.putdata([255 if r>210 and g>210 and b<80 and a>128 else 0 for r,g,b,a in source.get_flattened_data()])
        box=mask.getbbox();assert box,name
        target=(max(0,box[0]-3)*8,max(0,box[1]-3)*8,min(64,box[2]+3)*8,min(64,box[3]+3)*8)
        canvas=images[base].copy();canvas.alpha_composite(number_overlay(name[-1],target));images[name]=canvas
    else:continue
    layers.append(dict(name=name,games=row['games'],size=(512,512),counter=value if name.startswith('item_number') else name[-1]))

for name,im in images.items():im.save(prepared/(name+'.png'))
packages=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    selected=[r for r in layers if game in r['games']];names={r['name'] for r in selected}
    definitions={}
    for base in (['main'] if game=='AA' else ['main',folder]):
        for p in sorted((root/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
            if p.name=='zzzzzzzz_AC_Inventory.pk3':continue
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if not n.lower().endswith('.shader'):continue
                    text=z.read(n).decode('latin1')
                    for match in re.finditer(r'(?im)^textures/hud/[\w/.-]+\s*\{',text):
                        start=text.index('{',match.start());end=start+1;depth=1
                        while depth:
                            depth+=(text[end]=='{')-(text[end]=='}');end+=1
                        definition=text[match.start():end]
                        shader=definition.split('{',1)[0].strip().lower()
                        definitions[shader]=definition
    shaders=[];covered=set()
    for shader,definition in definitions.items():
        textures=set(re.findall(r'(?im)^\s*(?:clampmap|map)\s+textures/hud/([\w-]+)\.tga',definition))
        if not textures.intersection(names):continue
        shaders.append(re.sub(r'(?im)^\s*nomipmaps\s*$', '', definition.replace('\r','')))
        covered.update(textures)
    for name in sorted(names-covered):
        shaders.append(f'textures/hud/{name}\n{{\n nopicmip\n {{\n clampmap textures/hud/{name}.tga\n blendFunc blend\n rgbGen global\n alphaGen global\n }}\n}}')
    p=work/'packages'/folder/'zzzzzzzz_AC_Inventory.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for row in selected:
            b=io.BytesIO();images[row['name']].save(b,format='TGA');z.writestr('textures/hud/'+row['name']+'.tga',b.getvalue())
        z.writestr('scripts/zzzz_ac_inventory.shader','\n'.join(shaders))
    packages.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),layers=selected))
(work/'packages/package-report.json').write_text(json.dumps(packages,indent=2)+'\n')
print('Packaged',len(images),'inventory sprites; fixed HUD rectangles and script logic unchanged')
