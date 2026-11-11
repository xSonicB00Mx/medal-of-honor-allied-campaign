"""Register six reviewed three-state Imagegen sheets to the native weapon bar."""
from pathlib import Path
import io,json,hashlib,re,zipfile
from PIL import Image
import numpy as np

root=Path(__file__).resolve().parents[1];work=root/'generated-local/hud-upscale/weapons'
(work/'prepared').mkdir(exist_ok=True)
images={};layers=[]
for group in ['pistol','rifle','smg','mg','grenade','heavy']:
    master=work/'generated'/f'{group}.png';sheet=Image.open(master).convert('RGBA')
    alpha=np.array(sheet)[:,:,3]
    active=(alpha>200).sum(axis=1)>sheet.width*.1
    changes=np.diff(np.r_[False,active,False].astype(int))
    spans=list(zip(np.where(changes==1)[0],np.where(changes==-1)[0]))
    assert len(spans)==3,(group,spans)
    for row,suffix in enumerate(['','_s','_x']):
        top,bottom=map(int,spans[row]);tile=sheet.crop((0,max(0,top-3),sheet.width,min(sheet.height,bottom+3)))
        box=tile.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox()
        assert box and 1.7<(box[2]-box[0])/(box[3]-box[1])<2.7,(group,row,box)
        im=tile.crop(box).resize((512,256),Image.Resampling.LANCZOS)
        name='weap_'+group+suffix;images[name]=im;im.save(work/'prepared'/f'{name}.png')
        layers.append(dict(name=name,size=im.size,row=row,span=[top,bottom],bounds=box,master_sha256=hashlib.sha256(master.read_bytes()).hexdigest()))
packages=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    definitions={}
    for base in (['main'] if game=='AA' else ['main',folder]):
        for p in sorted((root/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
            if p.name=='zzzzzzzz_AC_WeaponGroups.pk3':continue
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if not n.lower().endswith('.shader'):continue
                    text=z.read(n).decode('latin1')
                    for name in images:
                        m=re.search(r'(?im)^textures/hud/'+name+r'\s*\{',text)
                        if not m:continue
                        start=text.index('{',m.start());end=start+1;depth=1
                        while depth:
                            depth+=(text[end]=='{')-(text[end]=='}');end+=1
                        definitions[name]=text[m.start():end]
    assert set(definitions)==set(images)
    p=work/'packages'/folder/'zzzzzzzz_AC_WeaponGroups.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for name,im in images.items():
            b=io.BytesIO();im.save(b,format='TGA');z.writestr(f'textures/hud/{name}.tga',b.getvalue())
        # Preserve native state pulse and alpha; enable filtering for smaller HUD sizes.
        shaders=[re.sub(r'(?im)^\s*nomipmaps\s*$','',d.replace('\r','')) for d in definitions.values()]
        z.writestr('scripts/zzzz_ac_weapongroups.shader','\n'.join(shaders))
    packages.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),layers=layers))
(work/'packages/package-report.json').write_text(json.dumps(packages,indent=2)+'\n')
print('18 weapon-group states packaged at 512x256; original state shaders preserved.')
