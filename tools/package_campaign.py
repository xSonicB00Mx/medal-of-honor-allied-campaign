"""Generate common mission frontend while preserving all effective WCR menus."""
import json,re,zipfile,hashlib
from pathlib import Path
from inventory_campaign import effective
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP06-r1'
maps=json.loads((R/'generated-local/CP06/inventory/maps.json').read_text())
def widget(name,title,rect,cmd=None):
    return '\nresource\n'+('Button' if cmd else 'Label')+'\n{\n'+f'name "{name}"\ndontlocalize\ntitle "{title}"\nrect {rect}\nfont facfont-20\nfgcolor 0.95 0.89 0.7 1\nbgcolor 0.07 0.085 0.06 0.95\nborderstyle '+('RAISED' if cmd else 'NONE')+'\n'+(f'stuffcommand "{cmd}"\n' if cmd else '')+'}\n'
pages={}
for idx,(game,rows) in enumerate([('AA',maps['AA'][:18]),('AA',maps['AA'][18:]),('SH',maps['SH']),('BT',maps['BT'])]):
    name=['ac_campaign_aa1','ac_campaign_aa2','ac_campaign_sh','ac_campaign_bt'][idx]
    body=f'menu "{name}" 960 540 NONE 0\nvirtualres 1\nfullscreen 1\nbgcolor 0.07 0.085 0.06 1\nborderstyle NONE\n'
    body+=widget('heading','Allied Campaign - Missions','32 18 896 40')
    body+=widget('note','Select a mission. Changing game context briefly restarts the engine.','32 62 896 28')
    for k,title in enumerate(['Allied Assault I','Allied Assault II','Spearhead','Breakthrough']):
        body+=widget('tab'+str(k),title,f'{32+k*226} 102 218 32',f'popmenu 0; ac_campaign {k}')
    for k,row in enumerate(rows):
        # Native map IDs are unambiguous even where localized mission titles collide.
        x=32+(k//9)*452;y=154+(k%9)*34
        body+=widget('mission'+str(k),game+' / '+row['map'],f'{x} {y} 436 30',f'ac_context {dict(AA=0,SH=1,BT=2)[game]} {row["map"]}')
    for k,g in enumerate(['AA','SH','BT']):
        body+=widget('saves'+str(k),g+' saves',f'{32+k*210} 458 198 26',f'ac_context {k} saves')
    body+=widget('back','Back','32 488 180 32','popmenu 0')
    body+=widget('options','Allied Campaign Options','600 488 328 32','ac_ui_options')
    pages['ui/'+name+'.urc']=(body+'end.\n').encode('ascii')
audit=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
    resources=effective(game);package=rt/folder/'zzzzz_AC_Campaign.pk3'
    files=dict(pages);files['ac_context_ready.cfg']=b'// Campaign context is ready.\n'
    provider,original=resources['ui/main.urc'];s=original.decode('latin1')
    s=s.replace('end.',widget('ac_campaign_entry','Allied Campaign','222 444 210 30','ac_campaign')+'end.')
    files['ui/main.urc']=s.encode('latin1')
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    audit.append(dict(game=game,source=provider,source_sha256=hashlib.sha256(original).hexdigest(),package_sha256=hashlib.sha256(package.read_bytes()).hexdigest()))
dest=R/'checkpoints/CP06';dest.mkdir(parents=True,exist_ok=True);(dest/'ui-providers.json').write_text(json.dumps(audit,indent=2)+'\n')
print('Packaged 54 map entries and preserved original main-menu actions.')
