"""Inventory effective local campaign scripts; original text stays in ignored output."""
import hashlib,json,re,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def effective(game):
    out={}
    for folder in (['main'] if game=='AA' else ['main',{'SH':'mainta','BT':'maintt'}[game]]):
        root=R/'runtime-local/CP05a-r3'/folder
        for p in sorted(root.glob('*.pk3'),key=lambda p:p.name.lower()):
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if n.lower().endswith(('.scr','.urc','.txt','.bsp')):
                        out[n.lower()]=(p.relative_to(R).as_posix(),z.read(n))
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in ('.scr','.urc','.txt','.bsp'):
                out[p.relative_to(root).as_posix().lower()]=(p.relative_to(R).as_posix(),p.read_bytes())
    return out
if __name__=='__main__':
    dest=R/'generated-local/CP06/inventory';dest.mkdir(parents=True,exist_ok=True)
    report={}
    for g in ('AA','SH','BT'):
        files=effective(g);rows=[]
        for n,(p,b) in files.items():
            if n.endswith('.bsp') and re.fullmatch(r'maps/(?:m\dl\d[a-z]?|t\dl\d[a-z]?|e\dl\d[a-z]?)\.bsp',n):
                prefix={'AA':'m','SH':'t','BT':'e'}[g]
                if n[5]!=prefix:continue
                s=files.get(n[:-4]+'.scr',('',b''))
                rows.append(dict(map=n[5:-4],provider=p,script_provider=s[0],sha256=hashlib.sha256(s[1]).hexdigest()))
        report[g]=sorted(rows,key=lambda x:x['map'])
        for n,(p,b) in files.items():
            if n.endswith(('.scr','.urc','.txt')) and (n.startswith(('maps/','briefing/','ui/','global/')) or 'local' in n):
                d=dest/g/n;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b)
    (dest/'maps.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({g:[x['map'] for x in rows] for g,rows in report.items()}))
