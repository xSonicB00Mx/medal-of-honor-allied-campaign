"""Build local additive cross-campaign weapon resources and the LOADOUT entry.

Original content stays local. Existing weapon gameplay retains native priority;
missing dependencies are imported and restored scope materials are repaired.
"""
from pathlib import Path
import zipfile,re,json,hashlib
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';out=r/'generated-local/loadout/packages'
catalog=json.loads((r/'mod/loadout/weapons.json').read_text())
archives={};indices=[]
for folder in ['main','mainta','maintt']:
 index={}
 for p in sorted((rt/folder).glob('*.pk3'),key=lambda p:p.name.lower()):
  if p.name.endswith('_AC_Loadout.pk3'):continue
  z=archives.setdefault(str(p),zipfile.ZipFile(p))
  for n in z.namelist():
   if not n.endswith('/'):index[n.lower()]=(str(p),n)
 indices.append(index)
union={}
for idx in indices:union.update(idx)
def read(index,n):
 p,m=index[n.lower()];return archives[p].read(m)
def txt(index,n):return read(index,n).decode('latin1').replace('\r','')
def clean(s):return re.sub(r'/\*.*?\*/|//[^\n]*','',s,flags=re.S)
def blocks(s):
 pos=0
 while m:=re.search(r'([^\s{}]+)\s*\{',s[pos:]):
  name=m[1];start=pos+m.end()-1;end=start+1;depth=1
  while depth and end<len(s):
   depth+=(s[end]=='{')-(s[end]=='}');end+=1
  if depth:break
  yield name,s[start:end]
  pos=end
shader_union={}
for idx in indices:
 for n in idx:
  if n.startswith('scripts/') and n.endswith('.shader'):
   for name,body in blocks(clean(txt(idx,n))):shader_union[name.lower()]=(name,body)
def anims(s):
 """Named animation entries, including their event blocks and effective $path."""
 s=clean(s);path='models/human/animation';result={};pos=0
 pattern=re.compile(r'(?m)^\s*(?:\$path\s+(\S+)|([\w-]+)\s+([^\s{}]+\.skc)[^\n]*)')
 while m:=pattern.search(s,pos):
  pos=m.end()
  if m[1]:path=m[1];continue
  end=pos
  while end<len(s) and s[end].isspace():end+=1
  if end<len(s) and s[end]=='{':
   depth=1;end+=1
   while depth and end<len(s):depth+=(s[end]=='{')-(s[end]=='}');end+=1
   pos=end
  result.setdefault(m[2].lower(),[]).append((path,s[m.start():pos].strip()))
 return result
reports=[]
for game,folder in enumerate(['main','mainta','maintt']):
 native=dict(indices[0])
 if game:native.update(indices[game])
 files={};scanned=set();pending=[];materials={}
 native_shaders={}
 for n in native:
  if n.startswith('scripts/') and n.endswith('.shader'):
   native_shaders.update({a.lower():b for a,b in blocks(clean(txt(native,n)))})
 def add(n):
  n=n.lower().strip('"').replace('\\','/')
  if n not in union and n.endswith(('.tga','.jpg','.png')):
   n=next((n.rsplit('.',1)[0]+ext for ext in ['.tga','.jpg','.png'] if n.rsplit('.',1)[0]+ext in union),n)
  if n not in union:return False
  if n not in native and n not in files:files[n]=read(union,n)
  if n not in scanned:pending.append(n)
  return True
 def material(n):
  n=n.lower().strip('"')
  if n in shader_union and n not in native_shaders and n not in materials:
   materials[n]=shader_union[n];scan(materials[n][1])
  else:
   for ext in ['', '.tga','.jpg','.png']:
    if add(n+ext):break
 def scan(s):
  s=clean(s)
  # Absolute resource references and each local filename resolved against all
  # path directives in this definition. No model/weapon source is overwritten.
  paths=re.findall(r'(?im)^\s*\$?path\s+([^\s]+)',s)
  for token in re.findall(r'[\w./$-]+\.(?:tik|txt|scr|skd|skc|spr|wav|mp3|tga|jpg|png)',s,re.I):
   # Sprite model names resolve to extensionless shader names at runtime;
   # they usually have no physical .spr file to follow.
   if token.lower().endswith('.spr'):material(token[:-4])
   if not add(token):
    for base in paths:
     if add(base.rstrip('/')+'/'+token):break
  for sh in re.findall(r'(?im)\b(?:\w*shader|cacheimage|map|clampmap)\s+([^\s{}]+)',s):material(sh)
 for w in catalog:add(w['model'])
 # Retain portable turret resources for existing r1 saves, not loadout selection.
 # The turret derives these filenames in C++, not in its .tik file.
 add("models/weapons/mg42carryable.tik")
 for n in union:
  if n.startswith('models/weapons/mg42portable_placed') and n.endswith('.tik'):add(n)
 files['global/ac_loadout_mine.scr']=(r/'mod/loadout/ac_loadout_mine.scr').read_bytes()
 pending.append('global/ac_loadout_mine.scr')
 # Each expansion names its ammunition HUD after the weapon's display name.
 # Loading the model alone leaves AA's fallback HUD without ammo counters.
 for n in union:
  if n.startswith('ui/hud_ammo_') and n.endswith('.urc'):add(n)
 # Extend inventory metadata without replacing existing item presentations.
 inv='global/inventory.txt';invtext=txt(native,inv)
 have_items=set(re.findall(r'(?im)^\s*item\s+"([^"]+)"',invtext))
 for idx in indices:
  if inv not in idx:continue
  for m in re.finditer(r'(?is)typedef\s+(\w+)\s*\{([^{}]*)\}',clean(txt(idx,inv))):
   for item in re.finditer(r'(?ims)^\s*item\s+"([^"]+)".*?(?=^\s*item\s+"|\Z)',m[2]):
    if item[1] in have_items:continue
    have_items.add(item[1]);invtext+='\ntypedef '+m[1]+'\n{\n'+item[0]+'\n}\n'
 files[inv]=invtext.encode('latin1');pending.append(inv)
 # Universal state table is only used by eligible operation replays.
 for part in ['torso','legs']:
  n='global/mike_'+part+'.st';files['global/ac_loadout_'+part+'.st']=read(union,n);scan(txt(union,n))
 # Add new named animations, retaining all native definitions and their events.
 basefiles=[n for n in union if n.startswith('models/player/base/') and n.endswith('.txt') and '/include' not in n and 'detonator' not in n]
 for n in basefiles:
  if n not in native:add(n);continue
  existing=txt(native,n);have=anims(existing);extra=[]
  for idx in indices:
   if n not in idx:continue
   for name,entries in anims(txt(idx,n)).items():
    if name in have:continue
    have[name]=entries
    for path,entry in entries:extra.append('$path '+path+'\n'+entry)
  if extra:files[n]=(existing+'\nanimations\n{\n'+'\n'.join(extra)+'\n}\n').encode('latin1')
  pending.append(n)
 # Link newly imported third-person animation files into AA/SH base models.
 referenced='\n'.join(txt(native,n) for n in native if n.startswith('models/player/base/') and n.endswith('.txt'))
 extra=[n for n in basefiles if '/anims_' in n and n not in referenced]
 if extra:
  n='models/player/base/include.txt';files[n]=(txt(native,n)+'\n'+'\n'.join('$include '+s for s in extra)+'\n').encode('latin1')
  pending.append(n)
 def drain():
  while pending:
   n=pending.pop()
   if n in scanned:continue
   scanned.add(n)
   if n.endswith(('.tik','.txt','.scr','.spr','.urc')):scan((files[n] if n in files else read(native if n in native else union,n)).decode('latin1'))
 drain()
 # Missing sound aliases are appended to the native table; existing mix intact.
 n='ubersound/ubersound.scr';s=txt(native,n)
 have=set(re.findall(r'(?im)^\s*alias(?:cache)?\s+(\S+)',s));extra=[]
 used='\n'.join((files[k] if k in files else read(native if k in native else union,k)).decode('latin1') for k in scanned if k.endswith(('.tik','.txt','.scr')))
 used=used.lower()
 def weapon_alias(m):
  return m and (m[1].lower() in used or re.sub(r'\d+$','',m[1].lower()) in used or m[2].lower().startswith('sound/weapons/'))
 def portable_alias(line):
  m=re.match(r'\s*alias(?:cache)?\s+(\S+)\s+(\S+)',line)
  if weapon_alias(m):
   line=re.sub(r'\s+maps\s+"[^"]*"','',line,flags=re.I)
   if not re.search(r'\balways\b',line,re.I):line+=' always'
   add(m[2])
  return line
 s='\n'.join(portable_alias(line) for line in s.splitlines())+'\n'
 for idx in indices:
  if n not in idx:continue
  for line in txt(idx,n).splitlines():
   m=re.match(r'\s*alias(?:cache)?\s+(\S+)\s+(\S+)',line)
   # Randomized aliases have numeric suffixes; weapon events use the stem.
   if weapon_alias(m) and m[1] not in have:
    have.add(m[1]);extra.append(portable_alias(line));add(m[2])
 if extra:
  # Alias declarations must precede the script's terminating end statement.
  s=re.sub(r'(?im)^\s*end\s*$', '\n'.join(extra)+'\nend',s,count=1)
 files[n]=s.encode('latin1')
 drain()
 # These restored rifles contain single-sheet scope/receiver geometry that is
 # viewed from its back side in first person. Give only their model surfaces
 # two-sided materials, preserving the native textures, alpha and reflections.
 for weapon in ['fg42','g43','svt_rifle']:
  n='models/weapons/'+weapon+'.tik'
  source=(files[n] if n in files else read(native,n)).decode('latin1')
  def two_sided(m):
   original=m[1].lower();replacement='ac_loadout_twosided_'+original
   body=native_shaders.get(original,shader_union[original][1])
   body=re.sub(r'(?im)^\s*cull\s+\S+[^\n]*','',body)
   body=body.replace('{','{\n cull none',1)
   materials[replacement]=(replacement,body);scan(body)
   return 'shader '+replacement
  source=re.sub(r'\bshader\s+(\w+)',two_sided,source)
  files[n]=source.encode('latin1')
 drain()
 if materials:files['scripts/ac_loadout.shader']='\n'.join(n+'\n'+b for n,b in materials.values()).encode('latin1')
 # Main-menu presentation is shared AA; replace the disabled MP hotspot.
 menu=txt(native,'ui/main.urc')
 (out/folder).mkdir(parents=True,exist_ok=True)
 (out/folder/'main-before.urc').write_text(menu)
 def entry(m):
  if 'pushmenu multiplayer' not in m[0]:return m[0]
  return '''resource
Button
{
name loadout
rect 466 216 140 34
title "LOADOUT"
font facfont-20
fgcolor 1 0.85 0.4 1
bgcolor 0.075 0.095 0.075 0.88
borderstyle RAISED
clicksound "sound/menu/apply.wav"
stuffcommand "ac_loadout"
hovercommand "set ui_signshader 0"
}
'''
 menu=re.sub(r'(?is)resource\s+Button\s*\{[^{}]*\}',entry,menu)
 assert 'stuffcommand "ac_loadout"' in menu
 assert 'pushmenu multiplayer' not in menu
 files['ui/main.urc']=menu.encode('latin1')
 p=out/folder/'zzzzzzzzzzzzzzzz_AC_Loadout.pk3'
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(files.items()):z.writestr(n,b)
 reports.append(dict(game=['AA','SH','BT'][game],package=p.relative_to(r).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),files=len(files),bytes=sum(map(len,files.values()))))
(out/'package-report.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports))
