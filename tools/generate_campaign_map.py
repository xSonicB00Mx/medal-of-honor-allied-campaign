"""Reproducible cartography from sourced polygons; no baked labels or markers."""
import json,math,hashlib,zipfile,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];D=R/'mod/campaign';O=R/'generated-local/CP08/map';O.mkdir(parents=True,exist_ok=True)
data=json.loads((D/'missions.json').read_text());polys=json.loads((D/'coastlines.json').read_text())['polygons'];W,H=560,330;S=4
def merc(lat):return math.degrees(math.log(math.tan(math.pi/4+math.radians(lat)/2)))
def extent(bounds):
 x0,x1,lo,hi=bounds;y0,y1=merc(lo),merc(hi);cx=(x0+x1)/2;cy=(y0+y1)/2;scale=min((W-44)/(x1-x0),(H-40)/(y1-y0));return cx-W/(2*scale),cy-H/(2*scale),scale
def point(lon,lat,ex):x0,y0,s=ex;return (lon-x0)*s,H-(merc(lat)-y0)*s
lines=['/* Generated geographic projection; all labels are native UI widgets. */','#ifndef AC_MAP_H','#define AC_MAP_H','typedef struct {const char *name; float x0,y0,scale;} acMapRegion_t;','static const acMapRegion_t ac_mapRegions[] = {']
for i,reg in enumerate(data['map']['regions']):
 ex=extent(reg['bounds']);lines.append('    {'+json.dumps(reg['name'])+', '+','.join(f'{x:.8f}f' for x in ex)+'},')
 im=Image.new('RGB',(W*S,H*S),(158,170,156));d=ImageDraw.Draw(im)
 for polygon in polys:
  p=[tuple(v*S for v in point(*q,ex)) for q in polygon];d.polygon(p,fill=(205,192,153));d.line(p+[p[0]],fill=(96,105,84),width=2)
 for lon in range(-45,56,5):
  x=point(lon,40,ex)[0]*S;d.line([(x,0),(x,H*S)],fill=(152,155,128),width=1)
 for lat in range(25,71,5):
  y=point(0,lat,ex)[1]*S;d.line([(0,y),(W*S,y)],fill=(152,155,128),width=1)
 # Fine deterministic paper grain; the geometry is untouched.
 import random
 rng=random.Random(1942+i);pix=im.load()
 for y in range(H*S):
  for x in range(W*S):
   n=rng.choice((-2,-1,0,0,0,1,2));pix[x,y]=tuple(max(0,min(255,c+n)) for c in pix[x,y])
 im.save(O/f'region{i}.tga')
lines+=['};','typedef struct {float x,y;int region;} acMapMarker_t;','static const acMapMarker_t ac_mapMarkers[2][15] = {']
audit=[]
for reg in data['map']['regions']:
 ex=extent(reg['bounds']);row=[]
 for o in data['operations']:
  x,y=point(o['longitude'],o['latitude'],ex);row.append('{'+f'{x:.5f}f,{y:.5f}f,{o["map_region"]}'+'}')
 lines.append('    {'+','.join(row)+'},')
lines+=['};','#endif'];(R/'code/client/ac_map.h').write_text('\n'.join(lines)+'\n')
for i,o in enumerate(data['operations']):
 x,y=point(o['longitude'],o['latitude'],extent(data['map']['regions'][o['map_region']]['bounds']));assert 15<x<W-15 and 15<y<H-15
 audit.append(dict(id=o['id'],latitude=o['latitude'],longitude=o['longitude'],region=o['map_region'],pixel=[x,y],source=o['location_source']))
(R/'checkpoints/CP08').mkdir(exist_ok=True)
(R/'checkpoints/CP08/marker-validation.json').write_text(json.dumps(audit,indent=2)+'\n')
shader=''
for i in range(2):shader+=f'ac_map_{i}\n{{\n nopicmip\n nomipmaps\n {{\n map textures/ac_campaign/region{i}.tga\n rgbGen identity\n }}\n}}\n'
(O/'ac_campaign.shader').write_text(shader)
rt=R/'runtime-local/CP08-r1'
for folder in ['main','mainta','maintt']:
 with zipfile.ZipFile(R/'runtime-local/CP07-r1'/folder/'zzzzz_AC_Campaign.pk3') as z:files={n:z.read(n) for n in z.namelist()}
 # Replace the original map/new-game selection action while preserving every other WCR widget.
 main=files['ui/main.urc'].decode('latin1')
 def route(match):
  block=match.group(0)
  if 'name "ac_campaign_entry"' in block:return ''
  if 'name "new game old"' in block or 'name "bigmap"' in block or 'name "briefing"' in block:
   block=re.sub(r'stuffcommand "[^"]*"','stuffcommand "ac_campaign"',block)
  return block
 main=re.sub(r'resource\s+Button\s*\{[^}]*\}',route,main)
 assert 'name "new game old"' in main and 'stuffcommand "ac_campaign"' in main
 files['ui/main.urc']=main.encode('latin1')
 files['scripts/ac_campaign.shader']=shader.encode()
 for i in range(2):files[f'textures/ac_campaign/region{i}.tga']=(O/f'region{i}.tga').read_bytes()
 with zipfile.ZipFile(rt/folder/'zzzzz_AC_Campaign.pk3','w',zipfile.ZIP_DEFLATED) as z:
  for n,b in files.items():z.writestr(n,b)
print('Two 2240 x 1320 map backgrounds; all 15 regional anchors validated.')
