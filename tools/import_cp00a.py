"""Offline, hash-pinned semantic merge of the supplied BT patch into local WCR.

Third-party script bodies and generated diffs stay in ignored local directories.
No network, extraction, downloads, or execution of archive members.
"""
import argparse, difflib, hashlib, json, re, zipfile
from pathlib import Path

PATCH_SHA = 'd4122611afec4bb317eef1026f256cd0e1aa87fc85268218ceb19df71fb225fd'
def sha(data): return hashlib.sha256(data).hexdigest()
def text(data): return data.decode('latin1').replace('\r\n','\n').replace('\r','\n')
def ammo(s, prefix):
    return dict(re.findall(r'(?m)^\s*'+re.escape(prefix)+r'\s+(\w+)\s+(\d+)', s))
def blocks(s):
    matches=list(re.finditer(r'(?:else )?if\s*\(\s*level.script == "maps/(e\dl\d).scr"\s*\)',s))
    return {m[1]:(m.start(), matches[i+1].start() if i+1<len(matches) else s.index('level.loadout_script_run = 1',m.end())) for i,m in enumerate(matches)}
def merge(n, b, p, w):
    decisions=[]; result=w
    if n in ('global/giveall.scr','global/givenewweapons.scr'):
        old,new=ammo(b,'ammo'),ammo(p,'ammo')
        for k,v in new.items():
            if old.get(k)!=v:
                result,count=re.subn(r'(?m)^(\s*ammo\s+'+k+r'\s+)\d+',lambda m:m[1]+v,result)
                assert count==1,(n,k,count)
                decisions.append(dict(rule='patch_ammo_limit',ammo=k,value=int(v)))
    elif n=='global/loadout.scr':
        bb,pb,wb=blocks(b),blocks(p),blocks(w)
        for mapname,(start,end) in sorted(wb.items(),key=lambda i:i[1][0],reverse=True):
            section=w[start:end]; old=ammo(b[slice(*bb[mapname])],'$player ammo');new=ammo(p[slice(*pb[mapname])],'$player ammo')
            # Only values actually changed/added by the supplied patch override WCR.
            # Retain restored weapons, inventory carryover, AI, grenades and aliases.
            for k,v in new.items():
                if old.get(k)==v:continue
                section,count=re.subn(r'(?m)^(\s*\$player ammo\s+'+k+r'\s+)\d+',lambda m:m[1]+v,section)
                assert count<=1,(mapname,k)
                if count==0:
                    pos=section.rfind('}')
                    section=section[:pos]+'\t$player ammo '+k+' '+v+'\n\t'+section[pos:]
                decisions.append(dict(map=mapname,rule='patch_loadout_ammo',ammo=k,value=int(v)))
            # The patch removes global inhibitions, and enables each mission.
            section=re.sub(r'(level\.nodrop(?:health|weapons)\s*=\s*)1',r'\g<1>0',section)
            result=result[:start]+section+result[end:]
        # Preserve WCR's entry label (missing in supplied patch) and record save policy.
        result=result.replace('main:', 'main:\n\tlevel.ac_bt_drops_revision = 1',1)
        decisions.append(dict(rule='retain_WCR_weapons_and_story_state_enable_drops',save='Old in-level saves require mission restart; no replay/migration of deaths.'))
    else:
        # Map drop flag changes, including already equivalent WCR changes.
        for flag in ('nodrophealth','nodropweapons'):
            pattern=r'(?m)^(\s*level\.'+flag+r'\s*=\s*)1'
            if re.search(pattern,b) and re.search(pattern.replace('*)1','*)0'),p):
                result,count=re.subn(pattern,r'\g<1>0',result)
                decisions.append(dict(rule='enable_'+flag,changed_assignments=count))
        if n=='maps/e1l4.scr':
            # Two actual pistol-ammo changes. Keep WCR award names and restored logic.
            old=list(re.finditer(r'(?m)^\s*\$player ammo pistol\s+(\d+)',b))
            new=list(re.finditer(r'(?m)^\s*\$player ammo pistol\s+(\d+)',p))
            wmatches=list(re.finditer(r'(?m)^(\s*\$player ammo pistol\s+)(\d+)',result))
            assert len(old)==len(new)==len(wmatches)==2
            for a,c,m in reversed(list(zip(old,new,wmatches))):
                if a[1]!=c[1]:result=result[:m.start(2)]+c[1]+result[m.end(2):]
            decisions.append(dict(rule='patch_pistol_ammo',values=[int(m[1]) for m in new]))
        if n in ('maps/e1l4.scr','maps/e3l4.scr'):
            decisions.append(dict(rule='exclude_unrelated_old_medal_names_preserve_WCR'))
        if n=='maps/e3l2.scr':decisions.append(dict(rule='patch_only_changes_comments_no_behavior'))
    assert '<<<<<<<' not in result
    return result,decisions

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path);ap.add_argument('--baseline',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    source=args.source.read_bytes();assert sha(source)==PATCH_SHA,'Unrecognized patch; no output activated'
    assert args.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]/'generated-local'),'Output must be local generated data'
    rows=[];products={};diffs={}
    with zipfile.ZipFile(args.source) as patch,zipfile.ZipFile(args.baseline/'maintt/pak1.pk3') as base,zipfile.ZipFile(args.baseline/'maintt/Restoration_BT_Pak1-Main.pk3') as wcr:
        assert patch.testzip() is None
        names=[n for n in patch.namelist() if not n.endswith('/')]
        assert len(names)==10
        for n in names:
            assert not Path(n).is_absolute() and '..' not in Path(n).parts and '\\' not in n
            b,p,w=base.read(n),patch.read(n),wcr.read(n)
            merged,decisions=merge(n,text(b),text(p),text(w));data=merged.encode('latin1')
            rows.append(dict(resource=n,base_sha256=sha(b),patch_sha256=sha(p),wcr_sha256=sha(w),merged_sha256=sha(data),decisions=decisions))
            if merged!=text(w):products[n]=data
            diffs[n]=''.join(difflib.unified_diff(text(w).splitlines(True),merged.splitlines(True),fromfile='WCR/'+n,tofile='CP00a/'+n))
    args.output.mkdir(parents=True,exist_ok=True)
    temp=args.output/'bt-merge.tmp'
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in sorted(products.items()):
            info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    target=args.output/'zzzz_AC_BT_Drops.pk3';temp.replace(target)
    for n,d in diffs.items():(args.output/(n.replace('/','_')+'.diff')).write_text(d,encoding='utf-8',newline='\n')
    manifest=dict(schema=1,revision=1,patch_sha256=PATCH_SHA,output_sha256=sha(target.read_bytes()),files=rows,active_resources=sorted(products),old_save_policy='Restart mission; original saves not modified. No retroactive drops.')
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(package=str(target),sha256=manifest['output_sha256'],resources=len(products))))
if __name__=='__main__':main()
