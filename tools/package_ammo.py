"""Align reviewed local Imagegen ammunition sprites to original HUD bounds."""
from pathlib import Path
import io,json,hashlib,zipfile,re
from PIL import Image

root=Path(__file__).resolve().parents[1]
work=root/'generated-local/hud-upscale/ammo'
inventory=json.loads((work/'inventory.json').read_text())
files={};layers=[]
for row in inventory:
 name=row['name']
 # Multiplayer landmine counters are outside the single-player art pass.
 if name.startswith('clip_landmine'):continue
 master_name='clip_pistol' if name=='clip_pistol_small' else name
 source=Image.open(work/'source'/(name+'.png')).convert('RGBA')
 path=work/'generated'/(master_name+'.png')
 master=Image.open(path).convert('RGBA')
 box=master.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
 assert box and source.getchannel('A').getbbox()
 target=tuple(v*8 for v in source.getchannel('A').getbbox())
 canvas=Image.new('RGBA',(source.width*8,source.height*8))
 sprite=master.crop(box).resize((target[2]-target[0],target[3]-target[1]),Image.Resampling.LANCZOS)
 canvas.alpha_composite(sprite,target[:2])
 b=io.BytesIO();canvas.save(b,format='TGA');files[name]=b.getvalue()
 (work/'prepared').mkdir(exist_ok=True);canvas.save(work/'prepared'/(name+'.png'))
 layers.append(dict(name=name,games=row['games'],size=canvas.size,source_bounds=source.getchannel('A').getbbox(),target_bounds=target,master_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
packages=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 selected=[r for r in layers if game in r['games']]
 # Tile bars derive UV extents from the uploaded image dimensions. Compensate
 # the 8x artwork in its shader, retaining the original repetition/count.
 definitions={}
 for base in (['main'] if game=='AA' else ['main',folder]):
  for archive in sorted((root/'runtime-local/CP08-r1'/base).glob('*.pk3'),key=lambda p:p.name.lower()):
   if archive.name=='zzzzzzzz_AC_Ammo.pk3':continue
   with zipfile.ZipFile(archive) as z:
    for entry in z.namelist():
     if not entry.lower().endswith('.shader'):continue
     text=z.read(entry).decode('latin1')
     for row in selected:
      match=re.search(r'(?im)^textures/hud/'+re.escape(row['name'])+r'\s*\{',text)
      if not match:continue
      start=text.index('{',match.start());depth=1;end=start+1
      while depth:
       depth+=(text[end]=='{')-(text[end]=='}');end+=1
      definitions[row['name']]=text[match.start():end]
 shaders=[]
 for row in selected:
  name=row['name']
  if name in ('clip_aa_gun','clip_mine_detector'):continue
  shader=definitions.get(name,f'textures/hud/{name}\n{{\n nopicmip\n {{\n map textures/hud/{name}.tga\n blendFunc blend\n rgbGen global\n alphaGen global\n }}\n}}').replace('\r','')
  assert len(re.findall(r'(?im)^\s*map\s',shader))==1,name
  shader=re.sub(r'(?im)^\s*nomipmaps\s*$', '', shader)
  shader=re.sub(r'(?im)^(\s*map\s+[^\n]+)',r'\1\n        tcMod scale 8 8',shader)
  shaders.append(shader)
 p=work/'packages'/folder/'zzzzzzzz_AC_Ammo.pk3';p.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for row in selected:z.writestr('textures/hud/'+row['name']+'.tga',files[row['name']])
  z.writestr('scripts/zzzz_ac_ammo.shader','\n'.join(shaders))
 packages.append(dict(game=game,package=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),layers=selected))
(work/'packages/package-report.json').write_text(json.dumps(packages,indent=2)+'\n')
print('Packaged',len(layers),'sprites; original HUD layouts and weapon logic unchanged')
