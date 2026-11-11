"""Exercise actual inventory scripts in isolated UHD profiles; preserve user saves."""
from pathlib import Path
import argparse,json,shutil,subprocess
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--installed',action='store_true');args=ap.parse_args()
root=Path(__file__).resolve().parents[1];rt=root/'runtime-local/CP08-r1'
num=['AA','SH','BT'].index(args.game);folder=['main','mainta','maintt'][num]
p=root/'profiles-local/inventory'/args.run;home=p/folder;(home/'probe').mkdir(parents=True,exist_ok=False)
if not args.installed:
    # Expansion packages inherit common artwork, but overlay each used search directory.
    for base in (['main'] if num==0 else ['main',folder]):
        (p/base).mkdir(exist_ok=True)
        shutil.copy2(root/'generated-local/hud-upscale/items/packages'/base/'zzzzzzzz_AC_Inventory.pk3',p/base)
groups=(
    [['binoculars','radio','explosives','camera','battery','bangalores'],
     ['clipboard','gasmask','papers_level1','papers_level2','wirecutters','radio_explosives'],
     ['uniform','uniform_weh','uniform_dak','tigerii_manual','battleplans']]
    if num==0 else [['binoculars','stickybomb','explosives','camera']]
    if num==1 else [['keys','plunger','stickybomb','binoculars','explosives']])
commands=['wait 1000','devmap '+['m2l1','t1l3','e3l1'][num],'wait 6000','finishloadingscreen','set ac_hud_scale 1.66','set developer 0','wait '+('30000' if num==2 else '5000')]
labels=[]
for i,group in enumerate(groups):
    lines=['main:',' $player nodamage',' level.item_total = 0']
    for j in range(1,7):
        lines += [f' level.item[{j}] = NIL',f' huddraw_alpha {20+j} 0',f' huddraw_alpha {30+j} 0']
    for item in group:lines += [f' waitthread global/items.scr::add_item {item} 1 1',' wait 0.1']
    lines += ['end'];(home/'probe'/f'{i}.scr').write_text('\n'.join(lines)+'\n')
    commands += [f'script player exec probe/{i}.scr','wait 2500','screenshot silent'];labels.append(group)
    if i==0:
        if num==0:
            (home/'probe/count.scr').write_text('main:\n waitthread global/items.scr::count_item explosives 3\nend\n')
        elif num==1:
            (home/'probe/count.scr').write_text('main:\n waitthread global/democharge.scr::charge_switch 3 2 0.2 8\nend\n')
        else:
            # BT has chargesN inventory entries, not SH's democharge.scr helper.
            (home/'probe/count.scr').write_text('main:\n waitthread global/items.scr::add_item charges3 1 1\n wait 0.2\n waitthread global/items.scr::remove_item charges3\n waitthread global/items.scr::add_item charges2 1 1\nend\n')
        commands += ['script player exec probe/count.scr','wait 1000','screenshot silent'];labels.append(['counter 3' if num==0 else 'charge counter 3 -> 2'])
        if num==0:
            for value in [12,0]:
                (home/'probe'/f'count{value}.scr').write_text(f'main:\n waitthread global/items.scr::count_item explosives {value}\nend\n')
                commands += [f'script player exec probe/count{value}.scr','wait 800','screenshot silent'];labels.append(['counter '+str(value)])
        if num==1:
            (home/'probe/sticky.scr').write_text('main:\n waitthread global/democharge.scr::sticky_switch 9 8 0.2 2\nend\n')
            commands += ['wait 8500','script player exec probe/sticky.scr','wait 1000','screenshot silent'];labels.append(['sticky counter 9 -> 8'])
    (home/'probe'/f'remove{i}.scr').write_text(f'main:\n waitthread global/items.scr::remove_item {group[-1]}\nend\n')
    commands += [f'script player exec probe/remove{i}.scr','wait 500','screenshot silent'];labels.append(['removed '+group[-1]])
commands+=['ac_hud_scale','echo AC_INVENTORY_CAPTURE_DONE','quit'];(home/'capture.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1,ac_operation=-1,ac_hud_scale=1.66)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
r=subprocess.run(cmd+['+exec','capture.cfg'],cwd=rt,timeout=120)
log=(home/'qconsole.log').read_text(encoding='latin1');assert r.returncode==0 and 'AC_INVENTORY_CAPTURE_DONE' in log
outputs=[]
for i,f in enumerate(sorted((home/'screenshots').glob('*.tga'))):
    im=Image.open(f);assert im.size==(3840,2160)
    out=root/'artifacts-local'/f'HUD-Inventory-{args.game}-{args.run}-{i:02}.png';im.save(out);outputs.append(out.relative_to(root).as_posix())
assert len(outputs)==len(labels)
report=dict(game=args.game,run=args.run,installed=args.installed,width=3840,height=2160,hud_scale=1.66,labels=labels,outputs=outputs,exit_code=r.returncode)
(root/'generated-local/hud-upscale/items'/f'{args.run}-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
