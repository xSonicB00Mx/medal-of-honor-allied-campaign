"""Offline, hash-pinned selective MP1 import. Never writes to the source installation."""
import argparse, hashlib, io, json, zipfile
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
  map textures/ac/mp1_blood.tga
  blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
  rgbGen entity
  alphaGen entity
 }
}
'''
 pack=io.BytesIO()
 with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in [('textures/ac/mp1_blood.tga',converted.getvalue()),('scripts/ac_mp1.shader',shader.encode())]:
   info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
 output=a.output.resolve();assert output.is_relative_to((r/'generated-local').resolve()),'Output must be local generated product'
 output.mkdir(parents=True,exist_ok=True);tmp=output/'zzzz_AC_MP1.pk3.tmp';tmp.write_bytes(pack.getvalue());tmp.replace(output/'zzzz_AC_MP1.pk3')
 rgba.save(output/'preview.png')
 report=dict(schema=1,source_archive='x_data.ras',source_sha256=expected,reader='tools/ras_reader/PROVENANCE.md',members=[dict(path=n,sha256=sha(b)) for n,b in selected.items()],size=list(rgba.size),alpha_extrema=alpha.getextrema(),conversion='Original RGB JPEG plus separate grayscale alpha, unscaled RGBA TGA. No recoloring.',usage='Small world stains and falling sprites; behavior implemented independently, not a port of the binary RPS simulation.',package_sha256=sha(pack.getvalue()),redistribution='Local only; no MP1 assets in Git',budgets=dict(drops=256,drop_lifetime_ms=2200,world_marks='existing cg_marks_max budget'))
 (output/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
