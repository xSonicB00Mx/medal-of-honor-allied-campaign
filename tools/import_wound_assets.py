"""Preserve user PNG artwork; create local unscaled RGBA textures and common materials."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];out=a.output.resolve();assert out.is_relative_to((r/'generated-local').resolve());out.mkdir(parents=True,exist_ok=True)
records=[];package=io.BytesIO();shaders=[]
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for kind,name,expected in [('small','bulletwound_smallCal.png','c9bc4ed8f1c5425f0befb26962e0247fbb766c9340f96bff6cd3d69f4d39ab9f'),('large','bulletwound_highCal.png','1c31acd26a786d535596e81229bf9f96fbb936d2888b26bb4691f52ca6e86e3c')]:
  data=(a.source/name).read_bytes();assert hashlib.sha256(data).hexdigest()==expected
  im=Image.open(io.BytesIO(data));assert im.mode=='RGBA';blob=io.BytesIO();im.save(blob,format='TGA');image_path='textures/ac/wound_'+kind+'.tga'
  info=zipfile.ZipInfo(image_path,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,blob.getvalue())
  shaders.append('ac/wound_'+kind+'\n{\n polygonOffset\n cull none\n {\n  map '+image_path+'\n  blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n  rgbGen lightingSpherical\n  alphaGen vertex\n }\n}\n')
  records.append(dict(source=name,sha256=expected,size=list(im.size),alpha=im.getchannel('A').getextrema(),conversion='Unscaled PNG RGBA to TGA; original colors and alpha retained'))
 info=zipfile.ZipInfo('scripts/ac_wounds.shader',(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,''.join(shaders))
(out/'zzzz_AC_Wounds.pk3').write_bytes(package.getvalue())
report=dict(textures=records,package_sha256=hashlib.sha256(package.getvalue()).hexdigest(),large_profile='One large material for rifle/MG entry and all CP5 exits',assets_in_git=False)
(out/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
