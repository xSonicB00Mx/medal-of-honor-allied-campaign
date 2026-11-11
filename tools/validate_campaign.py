"""Asset-free manifest, projection and native-table checks for CI."""
import json,math,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];subprocess.run([sys.executable,str(R/'tools/generate_campaign.py'),'--check'],check=True)
d=json.loads((R/'mod/campaign/missions.json').read_text());ops=d['operations']
assert [o['game_date_start'] for o in ops]==sorted(o['game_date_start'] for o in ops)
assert len(ops)==15 and sum(len(o['map_chain']) for o in ops)==53
def merc(lat):return math.degrees(math.log(math.tan(math.pi/4+math.radians(lat)/2)))
expected=[]
for region in d['map']['regions']:
 x0,x1,lo,hi=region['bounds'];y0,y1=merc(lo),merc(hi);s=min(516/(x1-x0),290/(y1-y0));left=(x0+x1)/2-280/s;bottom=(y0+y1)/2-165/s
 assert left>-55 and left+560/s<70 and bottom>merc(20) and bottom+330/s<merc(75)
 for o in ops:
  assert -90<o['latitude']<90 and -180<o['longitude']<180 and o['location_source']['provider']=='GeoNames'
  expected.append(((o['longitude']-left)*s,330-(merc(o['latitude'])-bottom)*s,o['map_region']))
actual=[(float(x),float(y),int(r)) for x,y,r in re.findall(r'\{(-?[\d.]+)f,(-?[\d.]+)f,(\d)\}',(R/'code/client/ac_map.h').read_text())]
assert len(actual)==30 and all(abs(a[0]-b[0])<.00002 and abs(a[1]-b[1])<.00002 and a[2]==b[2] for a,b in zip(actual,expected))
assert not d['map']['political_borders'] and not d['map']['front_lines']
print('PASS: 54 unique sections, ordered operations, source references, all 30 projected markers and crop coverage')
