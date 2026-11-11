"""Isolated native MP-entry rejection and real m1l3a Jeep-MG visual-hit probes."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('kind', choices=['menu', 'jeep'])
ap.add_argument('--run', required=True)
ap.add_argument('--game', choices=['AA','SH','BT'], default='AA')
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
runtime = root/'runtime-local/CP08-r1'
profile = root/'profiles-local/singleplayer-jeep'/args.run
assert re.fullmatch('[a-zA-Z0-9-]+', args.run) and not profile.exists()
number, folder = {'AA':(0,'main'),'SH':(1,'mainta'),'BT':(2,'maintt')}[args.game]
home = profile/folder
(home/'probe').mkdir(parents=True)
binary = profile/'bin'
binary.mkdir()
for file in runtime.glob('*.dll'):
    shutil.copy2(file,binary/file.name)
for name in ['openmohaa.exe','game.dll','cgame.dll']:
    shutil.copy2(root/'build-local/cp00-r3/RelWithDebInfo'/name,binary/name)
commands = ['wait 2000']
if args.kind == 'menu':
    commands += ['pushmenu main','wait 500','ac_ui_report main']
    for menu in ['multiplayer','multiplayerstart','mpoptions','joingame','joinnetgame','dm_main','maprotationsetup']:
        commands += [f'pushmenu {menu}','wait 150','ac_ui_report main']
    commands += ['showmenu multiplayer','connect 127.0.0.1','reconnect',
        'ui_startdmmap 1 Free-For-All ui_maplist_ffa','map dm/mohdm1',
        'set g_gametype 1','set sv_maxclients 8','g_gametype','sv_maxclients',
        'ac_ui_report main','screenshot']
else:
    assert args.game == 'AA'
    fixture = '''main:
    $player.health = 10000
    level.playerjeep stop
    level.ac_jeepgun = level.playerjeep queryturretslotentity 0
    println ("AC_JEEP_MODEL=" + level.ac_jeepgun.model)
    level.ac_jeepangles = level.ac_jeepgun.angles
    local.barrel = level.ac_jeepgun gettagposition "tag_barrel"
    local.dir = angles_toforward level.ac_jeepangles
    local.pos = local.barrel + local.dir * 180 - ( 0 0 48 )
    level.ac_target = spawn models/human/german_afrika_private.tik origin local.pos targetname "ac_jeep_target"
    level.ac_target ai_off
    level.ac_target gravity 0
    level.ac_target.health = 2000
    level.ac_target.angles = level.ac_jeepangles + ( 0 180 0 )
    wait 0.5
    println "AC_JEEP_FIRE_BEGIN"
    for (local.i = 0; local.i < 40; local.i++)
    {
        level.playerjeep stop
        $player.viewangles = level.ac_jeepangles
        level.ac_jeepgun psetviewangles level.ac_jeepangles
        level.ac_jeepgun shoot
        println ("AC_JEEP_SHOT health=" + level.ac_target.health)
        wait 0.06
    }
    println "AC_JEEP_FIRE_END"
end
'''
    (home/'probe/jeep.scr').write_text(fixture)
    commands += ['map m1l3a','wait 5000','finishloadingscreen','popmenu 0',
        'set cl_paused 0','unpause','set autopaused 0','wait 1000',
        'script player exec probe/jeep.scr','wait 1000','screenshot',
        'wait 700','screenshot','wait 1800','screenshot','savegame ac_jeep_probe','wait 500']
commands += ['echo AC_SP_JEEP_DONE','quit']
(home/'probe.cfg').write_text('\n'.join(commands)+'\n')
settings = dict(com_target_game=number,fs_basepath=runtime,fs_homepath=profile,
    fs_steampath=runtime,fs_gogpath=runtime,fs_microsoftstorepath=runtime,
    net_enabled=0,logfile=2,developer=int(args.kind=='jeep'),cheats=1,ui_console=0,
    r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,
    com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_fx_debug=2,ac_perf=1)
cmd=[str(binary/'openmohaa.exe')]
for key,value in settings.items():cmd+=['+set',key,str(value)]
proc=subprocess.run(cmd+['+exec','probe.cfg'],cwd=runtime,timeout=100)
log=(home/'qconsole.log').read_text(encoding='latin1')
errors=[line for line in log.splitlines() if any(s in line for s in
    ['Script Error','Unknown command','Invalid event','compile error','Server command overflow'])]
images=[]
for path in sorted((home/'screenshots').glob('*.tga')):
    output=path.with_suffix('.png')
    with Image.open(path) as im:im.save(output)
    images.append(output.relative_to(root).as_posix())
report=dict(kind=args.kind,run=args.run,game=args.game,exit=proc.returncode,
    completed='AC_SP_JEEP_DONE' in log,errors=errors,images=images,
    events=[line for line in log.splitlines() if any(s in line for s in
        ['AC_JEEP_','AC_HIT ','AC_WOUND','AC_CORPSE','AC_MARK','AC_UI_CURRENT','AC_UI_MP_ENTRY','single-player only'])],
    binaries={name:hashlib.sha256((binary/name).read_bytes()).hexdigest() for name in ['openmohaa.exe','game.dll','cgame.dll']})
out=root/'generated-local/singleplayer-jeep'
out.mkdir(exist_ok=True)
(out/(args.run+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(run=args.run,exit=proc.returncode,errors=errors,images=images,events=len(report['events']))))
assert proc.returncode==0 and report['completed'] and not errors
if args.kind=='menu':
    assert len(re.findall('AC_UI_CURRENT main',log))==9
    assert 'AC_UI_MP_ENTRY enabled=0' in log and 'AC_UI_MP_ENTRY enabled=1' not in log
    assert log.count('Allied Campaign is single-player only.')>=12
else:
    assert 'AC_JEEP_MODEL=models/vehicles/jeep_30cal.tik' in log
    assert re.search(r'AC_HIT .*weapon=models/vehicles/jeep_30cal.tik group=4.*entry=1',log)
    assert 'AC_JEEP_FIRE_END' in log
