"""Preserve local WCR menus/credits and add campaign completion at credits exit."""
import hashlib,json,zipfile
from pathlib import Path
from inventory_campaign import effective
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP07-r1';audit=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    base=R/'runtime-local/CP06-r1'/folder/'zzzzz_AC_Campaign.pk3'
    with zipfile.ZipFile(base) as z:files={n:z.read(n) for n in z.namelist() if not n.startswith('ui/ac_campaign_')}
    if game in ('AA','BT'):
        provider,data=effective(game)['global/credits.scr'];s=data.decode('latin1')
        needle='$player stufftext "disconnect"';assert s.count(needle)==2
        guard='level.end_level == 1' if game=='AA' else 'level.escaped == 1'
        op=13 if game=='AA' else 11
        addition=f'''if (int (getcvar ac_campaign_mode) == 1 && int (getcvar ac_operation) == {op} && {guard})
{{
    missiontransition ac_campaign_end 1
    end
}}
'''
        merged=s.replace(needle,addition+needle);files['global/credits.scr']=merged.encode('latin1')
        audit.append(dict(game=game,source=provider,source_sha256=hashlib.sha256(data).hexdigest(),changed_sites=2,guard=guard,scope='Only credits completion/skip after actual finale; no airstrike/timer/escape trigger altered'))
    with zipfile.ZipFile(rt/folder/'zzzzz_AC_Campaign.pk3','w',zipfile.ZIP_DEFLATED) as z:
        for n,b in files.items():z.writestr(n,b)
out=R/'checkpoints/CP07';out.mkdir(parents=True,exist_ok=True);(out/'script-integration.json').write_text(json.dumps(audit,indent=2)+'\n')
print('Credits preserved; completion hooks restricted to native completed finales.')
