"""Preserve the effective local WCR options menus, adding one scaling entry.

The regenerated third-party menu bodies stay local. Audit every original command
and cvar binding, so packaging cannot silently remove an existing option.
"""
import argparse,hashlib,json,re,zipfile
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=Path);ap.add_argument('--report-dir',type=Path,default=Path('checkpoints/CP01'));args=ap.parse_args()
 repo=Path(__file__).resolve().parents[1];rows=[]
 for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
  effective={}
  for directory in (['main'] if game=='AA' else ['main',folder]):
   for p in sorted((args.runtime/directory).glob('*.pk3'),key=lambda p:p.name.lower()):
    if p.name.startswith('zzzz_AC_UI'):continue
    with zipfile.ZipFile(p) as z:
     for n in z.namelist():
      if n.lower().startswith('ui/') and n.lower().endswith('.urc'):effective[n.lower()]=(p.relative_to(args.runtime).as_posix(),z.read(n))
  provider,data=effective['ui/options_main.urc'];s=data.decode('latin1').replace('\r','')
  button='''resource
Button
{
name "ac_scaling"
title "HUD / Font Size"
rect 404 438 224 32
font facfont-20
fgcolor 1 0.9 0.65 1
bgcolor 0.08 0.1 0.08 0.95
borderstyle RAISED
stuffcommand "ac_ui_options"
}
'''
  assert s.count('end.')==1
  merged=s.replace('end.',button+'\nend.')
  bindings=lambda t:re.findall(r'(?m)^\s*(?:linkcvar|stuffcommand|addpopup)\s+[^\n]*',t)
  assert all(b in bindings(merged) for b in bindings(s))
  output=args.runtime/folder/'zzzz_AC_UI.pk3'
  with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
   for n,b in [('ui/options_main.urc',merged.encode('latin1')),('ui/ac_scaling.urc',(repo/'mod/ui/ac_scaling.urc').read_text(encoding='utf-8').encode('latin1'))]:
    info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
  inventory=[]
  for n,(provider,b) in sorted(effective.items()):
   body=b.decode('latin1').replace('\r','')
   inventory.append(dict(resource=n,provider=provider,sha256=sha(b),bindings=bindings(body)))
  rows.append(dict(game=game,options_source_sha256=sha(data),package_sha256=sha(output.read_bytes()),preserved_option_bindings=len(bindings(s)),ui_inventory=inventory))
 out=args.report_dir;out.mkdir(parents=True,exist_ok=True)
 (out/'CP01-ui-resource-audit.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
 print([(x['game'],len(x['ui_inventory']),x['preserved_option_bindings']) for x in rows])
if __name__=='__main__':main()
