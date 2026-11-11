import json,zipfile,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];G=R/'generated-local/CP08/geography'
places={}
for archive,member in [('cities15000.zip','cities15000.txt'),('BE.zip','BE.txt'),('IT.zip','IT.txt')]:
 for line in zipfile.ZipFile(G/archive).read(member).decode().splitlines():
  row=line.split('\t');places[row[0]]=row
ids=['2506385','3133880','2473457','2472706','2523119','3179781','3183005','3029241','3029241','3029241','3030300','3182279','2802583','2821164','2950159']
regions=[1,4,1,1,2,2,2,3,3,3,3,2,3,3,5]
data=json.loads((R/'mod/campaign/missions.json').read_text())
for o,id,region in zip(data['operations'],ids,regions):
 row=places[id];o.update(latitude=float(row[4]),longitude=float(row[5]),location_source={'provider':'GeoNames','id':id,'url':'https://www.geonames.org/'+id,'license':'CC BY 4.0','anchor_name':row[1]},map_region=region)
 o['location_precision']='regional anchor; not an exact in-game objective'
 if o['id']=='aa_schmerzen':o['location_precision']='fictional fort; broad Siegfried Line region anchored near Trier'
data['map']={'projection':'Spherical Mercator; WGS84 longitude/latitude; uniform scale, north up','political_borders':False,'front_lines':False,'regions':[
 {'name':'Overview','bounds':[-20,35,30,67]}, {'name':'North Africa','bounds':[-4,14,32,39]},
 {'name':'Italy & Sicily','bounds':[9,18,35.5,46]}, {'name':'Western Europe','bounds':[-7,10,46,53]},
 {'name':'Norway','bounds':[3,18,60,66.5]}, {'name':'Berlin','bounds':[10,17,50.5,54.5]}]}
(G/'missions-with-geography.json').write_text(json.dumps(data,indent=2)+'\n')
# Crop public-domain land polygons to the map's geographic envelope.
def clip(poly,axis,bound,greater):
 out=[]
 if not poly:return out
 for a,b in zip(poly[-1:]+poly[:-1],poly):
  ai=(a[axis]>=bound) if greater else (a[axis]<=bound);bi=(b[axis]>=bound) if greater else (b[axis]<=bound)
  if ai!=bi:
   t=(bound-a[axis])/(b[axis]-a[axis]);out.append([round(a[0]+t*(b[0]-a[0]),5),round(a[1]+t*(b[1]-a[1]),5)])
  if bi:out.append([round(v,5) for v in b])
 return out
polys=[]
for ft in json.loads((G/'land.geojson').read_text())['features']:
 for rings in (ft['geometry']['coordinates'] if ft['geometry']['type']=='MultiPolygon' else [ft['geometry']['coordinates']]):
  p=rings[0]
  for axis,bound,great in [(0,-55,True),(0,70,False),(1,20,True),(1,75,False)]:p=clip(p,axis,bound,great)
  if len(p)>=3:polys.append(p)
(G/'coastlines.json').write_text(json.dumps({'source':'Natural Earth 1:50m land','license':'Public domain','polygons':polys},separators=(',',':'))+'\n')
sources=json.loads((G/'sources.json').read_text())
for c in ['BE','IT']:
 p=G/(c+'.zip');sources.append(dict(file=p.name,url='https://download.geonames.org/export/dump/'+p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
(G/'all-sources.json').write_text(json.dumps(sources,indent=2)+'\n')
print('Prepared 15 sourced regional anchors and',len(polys),'cropped land polygons.')
