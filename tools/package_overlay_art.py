"""Build precise high-resolution optical masks and package reviewed gas-mask art."""
from pathlib import Path
import io,json,hashlib,re,zipfile
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[1];work=root/'generated-local/hud-upscale/overlays'
(work/'prepared').mkdir(exist_ok=True)
names=['zoomoverlay','kartop','karbottom','binocularsoverlay','cameraoverlay']
images={};metrics=[]
for name in names:
    source=np.array(Image.open(work/'source'/f'{name}.png').convert('RGBA'))
    alpha=source[:,:,3].astype(float);pts=[]
    # Fit the 50% boundary away from the aiming lines to an axis-aligned ellipse.
    for y in range(8,248):
        for x in range(8,247):
            if (alpha[y,x]-128)*(alpha[y,x+1]-128)<0:
                pts.append((x+.5+(128-alpha[y,x])/(alpha[y,x+1]-alpha[y,x]),y+.5))
    x,y=np.array(pts).T
    aa,bb,c,d=np.linalg.lstsq(np.column_stack([x*x,y*y,x,y]),np.ones(len(x)),rcond=None)[0]
    cx,cy=-c/(2*aa),-d/(2*bb);k=1+aa*cx*cx+bb*cy*cy
    rx,ry=np.sqrt(k/aa),np.sqrt(k/bb)
    def distance(x,y):return (np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2)-1)*(rx+ry)/2
    yy,xx=np.mgrid[8:248,8:248];dist=distance(xx+.5,yy+.5)
    # Reuse the original soft optical falloff as a one-dimensional profile.
    bins=np.arange(-45,45.5,.5);profile=[]
    for b in bins:
        vals=alpha[8:248,8:248][(dist>=b-.25)&(dist<b+.25)]
        profile.append(np.median(vals) if len(vals) else np.nan)
    valid=np.isfinite(profile);profile=np.interp(bins,bins[valid],np.array(profile)[valid])
    profile=np.maximum.accumulate(profile)
    size=2048;yy,xx=np.mgrid[:size,:size];x=(xx+.5)/8;y=(yy+.5)/8
    a=np.interp(distance(x,y),bins,profile,left=0,right=255)
    # Original geometric reticles: identical center, gap and source-pixel width.
    if name=='zoomoverlay':a=np.where((x>=255)|(y>=255),255,a)
    elif name=='kartop':a=np.where((y>=255)&(x>=25),255,a)
    elif name=='karbottom':a=np.where((x<2)|((y<1)&(x>=25)),255,a)
    out=np.empty((size,size,4),dtype=np.uint8);out[:,:,:3]=source[128,128,:3];out[:,:,3]=np.rint(a).astype(np.uint8)
    images[name]=Image.fromarray(out)
    check=np.array(images[name].resize((256,256),Image.Resampling.BOX))[:,:,3].astype(float)
    delta=float(np.abs(alpha-check).mean())
    assert delta<4,(name,'Optical mask changed too far from original',delta)
    metrics.append(dict(name=name,ellipse=[cx,cy,rx,ry],size=[size,size],mean_alpha_delta=delta,method='analytic ellipse and original optical falloff; exact geometric reticle'))
gas=Image.open(work/'generated/gasmask_overlay.png').convert('RGBA').resize((2048,1024),Image.Resampling.LANCZOS)
assert gas.getpixel((1024,512))[3]<10,'Preserve clear center of gas mask'
assert np.max(np.array(gas)[460:564,940:1108,3])<10,'Preserve clear central aiming area'
images['gasmask_overlay']=gas
metrics.append(dict(name='gasmask_overlay',size=gas.size,method='Built-in Imagegen',master_sha256=hashlib.sha256((work/'generated/gasmask_overlay.png').read_bytes()).hexdigest()))
for name,im in images.items():im.save(work/'prepared'/f'{name}.png')
packages=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    definitions={}
    for base in (['main'] if game=='AA' else ['main',folder]):
        for p in sorted((root/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
            if p.name=='zzzzzzzz_AC_Overlays.pk3':continue
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
    p=work/'packages'/folder/'zzzzzzzz_AC_Overlays.pk3';p.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for name,im in images.items():
            b=io.BytesIO();im.save(b,format='TGA');z.writestr(f'textures/hud/{name}.tga',b.getvalue())
        # Keep original opacity and blending; implicit KAR shaders remain implicit.
        z.writestr('scripts/zzzz_ac_overlays.shader','\n'.join(definitions.values()))
    packages.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),layers=metrics))
(work/'packages/package-report.json').write_text(json.dumps(packages,indent=2)+'\n')
print('Six optical textures packaged; geometric reticles retain native center and widths.')
