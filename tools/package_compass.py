"""Package reviewed Imagegen compass layers; originals and generated masters stay local."""
from pathlib import Path
import io,json,hashlib,zipfile
from PIL import Image
root=Path(__file__).resolve().parents[1];work=root/'generated-local/hud-upscale/compass'
files={};report=[]
for name in ['compassback','compassface','compassneedle','compassobjarrow','compassobjball']:
 source=Image.open(work/'source'/(name+'.png')).convert('RGBA')
 master_path=work/'generated'/('compassface-r2.png' if name=='compassface' else name+'.png')
 master=Image.open(master_path).convert('RGBA')
 # Ignore almost invisible alpha speckles when aligning the generated sprite.
 box=master.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
 target=tuple(v*8 for v in source.getchannel('A').getbbox())
 canvas=Image.new('RGBA',(source.width*8,source.height*8))
 if name=='compassface':
  # The original alpha is engraved markings, not a filled disk. Its sparse
  # asymmetric bounds must never be used to reshape the rotating artwork.
  # Register the reviewed rose intersection (625,630) to the engine pivot.
  scale=0.61; pivot=(625,630)
  sprite=master.resize((round(master.width*scale),round(master.height*scale)),Image.Resampling.LANCZOS)
  offset=(round(512-pivot[0]*scale),round(512-pivot[1]*scale))
  canvas.alpha_composite(sprite,offset)
  target=canvas.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
 else:
  # Use a circular housing centered on (64,64), not the noisy source bounds.
  if name=='compassback':target=(80,80,944,944)
  sprite=master.crop(box).resize((target[2]-target[0],target[3]-target[1]),Image.Resampling.LANCZOS)
  canvas.alpha_composite(sprite,target[:2])
 b=io.BytesIO();canvas.save(b,format='TGA');files['textures/hud/'+name+'.tga']=b.getvalue()
 (work/'prepared').mkdir(exist_ok=True);canvas.save(work/'prepared'/(name+'.png'))
 report.append(dict(name=name,size=canvas.size,source_bounds=source.getchannel('A').getbbox(),target_bounds=target,master_bounds=box,registration='uniform scale 0.61; rose pivot 625,630 -> 512,512' if name=='compassface' else 'circular housing' if name=='compassback' else 'original bounds',master_sha256=hashlib.sha256(master_path.read_bytes()).hexdigest()))
# Existing shader semantics are retained; only permit mip filtering of HD sprites.
shaders=[]
for name in ['compassback','compassneedle','compassobjball']:
 shaders.append(f'textures/hud/{name}\n{{\n surfaceparm nolightmap\n nopicmip\n {{\n clampmap textures/hud/{name}.tga\n blendFunc blend\n alphaGen oneMinusVertex\n }}\n}}\n')
files['scripts/zzzz_ac_compass.shader']='\n'.join(shaders).encode()
packages=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 p=work/'packages'/folder/'zzzzzzzz_AC_Compass.pk3';p.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in files.items():z.writestr(n,b)
 packages.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),layers=report))
(work/'packages/package-report.json').write_text(json.dumps(packages,indent=2)+'\n')
print('Packaged five layers for AA/SH/BT; damage shader and gameplay unchanged')
