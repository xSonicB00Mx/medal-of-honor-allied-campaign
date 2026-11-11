"""Offline, hash-pinned selective MP1 import. Never writes to the source installation."""
import argparse, hashlib, io, json, zipfile, struct
from pathlib import Path
from PIL import Image
from ras_reader.ras import read_directory,member_bytes

def sha(data): return hashlib.sha256(data).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
 r=Path(__file__).resolve().parents[1];manifest=json.loads((r/'third_party/mp1/manifest.json').read_text())
 expected=next(x['sha256'] for x in manifest['files'] if x['path']=='x_data.ras')
 data=(a.source/'x_data.ras').read_bytes();assert sha(data)==expected,'MP1 source differs from recorded input'
 archive=read_directory(data);assert archive.data_end==len(data)
 names=['data/database/decals/bitmaps/Blood.jpg','data/database/decals/bitmaps/Blood_alpha.jpg']
 selected={n:member_bytes(data,next(e for e in archive.entries if e.path==n)) for n in names}
 rgb=Image.open(io.BytesIO(selected[names[0]])).convert('RGB');alpha=Image.open(io.BytesIO(selected[names[1]])).convert('L');assert rgb.size==alpha.size
 rgba=rgb.convert('RGBA');rgba.putalpha(alpha);converted=io.BytesIO();rgba.save(converted,format='TGA')
 # Original particle frame and its separate alpha are embedded in the local RPS.
 # Decode only this pinned image pair, not the RPS simulation or executable code.
 particle_name='data/database/particles/blood/blood_projectile_trail.rps'
 particle=member_bytes(data,next(e for e in archive.entries if e.path==particle_name))
 assert sha(particle)=='658d9128c7033394383a5bfdfcf0621d69bf5cca9688339ef727e053e966e06b'
 frames=[];particle_records=[]
 for frame in range(16):
  pair=[]
  for ext in ['TGA','PCX']:
   label=f'blood\\splat1\\splat{frame:04d}.{ext}'.encode();assert particle.count(label)==1
   offset=particle.index(label)+len(label);assert particle[offset]==0x13
   size=struct.unpack_from('<H',particle,offset+1)[0];blob=particle[offset+3:offset+3+size]
   im=Image.open(io.BytesIO(blob));im.load();assert im.size==(16,16)
   pair.append(im);particle_records.append(dict(image=label.decode(),sha256=sha(blob),bytes=size))
  im=pair[0].convert('RGBA');im.putalpha(pair[1].convert('L'));blob=io.BytesIO();im.save(blob,format='TGA');frames.append(blob.getvalue())
 shader='''ac/mp1_blood
{
 polygonOffset
 cull none
 {
  map textures/ac/mp1_blood.tga
  blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
  rgbGen vertex
  alphaGen vertex
 }
}
ac/mp1_drop
{
 cull none
 {
  map textures/ac/mp1_drop_00.tga
  blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
  rgbGen entity
  alphaGen entity
 }
}
'''
 shader=shader.replace('map textures/ac/mp1_drop_00.tga','animMap 24 '+' '.join(f'textures/ac/mp1_drop_{i:02d}.tga' for i in range(16)))
 pack=io.BytesIO()
 with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in [('textures/ac/mp1_blood.tga',converted.getvalue()),('scripts/ac_mp1.shader',shader.encode()),*[(f'textures/ac/mp1_drop_{i:02d}.tga',b) for i,b in enumerate(frames)]]:
   info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
 output=a.output.resolve();assert output.is_relative_to((r/'generated-local').resolve()),'Output must be local generated product'
 output.mkdir(parents=True,exist_ok=True);tmp=output/'zzzz_AC_MP1.pk3.tmp';tmp.write_bytes(pack.getvalue());tmp.replace(output/'zzzz_AC_MP1.pk3')
 rgba.save(output/'preview.png')
 report_particle=dict(source=particle_name,sha256=sha(particle),images=particle_records,conversion='Embedded original 16x16 TGA RGB plus PCX alpha; no recoloring/resizing',simulation='Independent bounded collision simulation')
 report=dict(schema=1,source_archive='x_data.ras',source_sha256=expected,reader='tools/ras_reader/PROVENANCE.md',members=[dict(path=n,sha256=sha(b)) for n,b in selected.items()],size=list(rgba.size),alpha_extrema=alpha.getextrema(),conversion='Original RGB JPEG plus separate grayscale alpha, unscaled RGBA TGA. No recoloring.',usage='Small world stains and falling sprites; behavior implemented independently, not a port of the binary RPS simulation.',package_sha256=sha(pack.getvalue()),redistribution='Local only; no MP1 assets in Git',budgets=dict(drops=256,drop_lifetime_ms=2200,world_marks='existing cg_marks_max budget'))
 report['particle_import']=report_particle
 report['usage']='Original MP1 decal for world stains; original MP1 particle image for falling drops.'
 (output/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
