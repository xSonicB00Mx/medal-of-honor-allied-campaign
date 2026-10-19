"""Widen original campaign statistic fields without changing their bindings or art."""
from pathlib import Path
import re, json, zipfile, hashlib

r=Path(__file__).resolve().parents[1]; rt=r/'runtime-local/CP08-r1'
out=r/'generated-local/campaign-stats/packages'; package='zzzzzzzzzzzzzzz_AC_CampaignStats.pk3'
rows=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 files={}
 for base in (['main'] if game=='AA' else ['main',folder]):
  for p in sorted((rt/base).glob('*.pk3'),key=lambda p:p.name.lower()):
   if p.name==package:continue
   with zipfile.ZipFile(p) as z:
    for n in z.namelist():
     if n.startswith(('ui/statsscreen','ui/mission_success_')) and n.endswith(('.urc','.inc')):files[n]=z.read(n)
 changed={}
 for name,data in files.items():
  text=data.decode('latin1').replace('\r','')
  def adjust(match):
   block=match[0]; cvar=re.search(r'(?mi)^\s*linkcvar\s+"?([^"\s]+)',block)
   rect=re.search(r'(?m)^rect\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)',block)
   if not rect:return block
   x,y,w,h=map(float,rect.groups())
   if cvar:
    key=cvar[1].lower()
    if key.startswith(('ui_headshots','ui_torsoshots','ui_leftarmshots','ui_groinshots','ui_leftlegshots')):x,w=144,96
    elif key.startswith(('ui_rightarmshots','ui_rightlegshots')):x,w=400,96
    else:x,w=280,320
   elif 'title "Right Arm:"' in block or 'title "Right Leg:"' in block:x,w=240,152
   elif 'title "Hit Locations Percentage"' in block:w=max(w,480)
   elif x==16 and 40<=y<=240:w=256
   else:return block
   return block[:rect.start()]+f'rect {x:g} {y:g} {w:g} {h:g}'+block[rect.end():]
  modified=re.sub(r'(?is)resource\s+Label\s*\{[^{}]*\}',adjust,text)
  if modified!=text:
   assert re.findall(r'(?mi)^\s*linkcvar.*',modified)==re.findall(r'(?mi)^\s*linkcvar.*',text)
   changed[name]=modified.encode('latin1')
 p=out/folder/package;p.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in changed.items():z.writestr(name,data)
 rows.append(dict(game=game,package=p.relative_to(r).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),menus=list(changed)))
(out/'package-report.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
