"""Native GL1 shadows, copied saves, live options and renderer restart.

All writes go to a new ignored profile/report directory. No personal game is
launched. Screenshots must also be inspected; draw counters alone aren't proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
from PIL import Image

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
a = ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+', a.run)
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
rt = R/'runtime-local/CP09-r1'
personal = R/'profiles-local/CP08-r1/user'
build = R/'build-local/cp00-r3/RelWithDebInfo'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def hashes():
    return {p.relative_to(personal).as_posix():sha(p) for p in personal.rglob('*') if p.is_file()}
before = hashes()
packages = []
source = (R/'mod/ui/ac_scaling.urc').read_text().encode('latin1')
for game,folder in zip(['AA','SH','BT'], ['main','mainta','maintt']):
    p = out/'packages'/folder/'zzzzzzzzzzzzz_AC_FlinchOptions.pk3'
    p.parent.mkdir(parents=True)
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('ui/ac_scaling.urc',source)
    packages.append(dict(game=game,package=p.relative_to(R).as_posix(),sha256=sha(p)))
cases = []
for game,folder in enumerate(['main','mainta','maintt']):
    p = R/'profiles-local/CP09'/f'{a.run}-{folder}'
    h = p/folder
    h.mkdir(parents=True,exist_ok=False)
    b = p/'bin'
    b.mkdir()
    for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
    for name in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/name,b/name)
    for row in packages:
        src=R/row['package']; dst=p/src.parent.name/src.name
        dst.parent.mkdir(exist_ok=True);shutil.copy2(src,dst)
    start='map m2l1'
    if game:
        src = (personal/'mainta/save/omconfig/quick.sav' if game==1 else
               R/'profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')
        dst=h/'save/omconfig';dst.mkdir(parents=True)
        for f in src.parent.glob(src.stem+'.*'):shutil.copy2(f,dst/('reference'+f.suffix))
        start='loadgame reference'
    fixture=(R/'tools/cp00_baseline_fixture.scr').read_text().split('    waitthread snapshot')[0]
    fixture=fixture.replace('level.cp00_subject thread deathwatch','level.cp00_subject.health = 10000')
    fixture+='''    level.shadow_pickup = spawn models/weapons/mp40.tik
    level.shadow_pickup.origin = level.cp00_target + ( 40 0 16 )
    level.shadow_cam = spawn Camera
    level.shadow_cam.origin = $player.origin + ( 0 0 90 )
    level.shadow_cam.angles = vector_toangles (level.cp00_target + ( 0 0 16 ) - level.shadow_cam.origin)
    $player hide
    cuecamera level.shadow_cam
end
'''
    (h/'shadow.scr').write_text(fixture)
    (h/'motion.scr').write_text('''main:
    level.cp00_subject ai_on
    level.cp00_subject.enableEnemy = 0
    level.cp00_subject anim_scripted walk_crouch_forward
    level.shadow_pickup.angles = ( 0 90 0 )
    println AC_SHADOW_MOTION
end
''')
    (h/'freeze.scr').write_text('''main:
    level.cp00_subject ai_off
    println AC_SHADOW_FROZEN
end
''')
    commands=['wait 800',start,'wait 4500','finishloadingscreen','wait 800',
              'script player exec shadow.scr','wait 1600','set cg_shadows 0',
              'set r_acModelShadows 0','wait 300','screenshot silent',
              'set r_acModelShadows 1','wait 500','screenshot silent',
              'script player exec motion.scr','wait 600','screenshot silent',
              'script player exec freeze.scr','savegame shadow_check','wait 500',
              'loadgame shadow_check','wait 4000','finishloadingscreen','wait 800','screenshot silent',
              'vid_restart','wait 3500','finishloadingscreen','wait 800','screenshot silent',
              'ac_ui_options','wait 500','ac_ui_report ac_scaling','screenshot silent',
              # Native checkbox in the 960x540 canvas at 1600x900.
              'widgetcommand modelShadows left_mouse_up 1495 768 0','r_acModelShadows',
              'writeconfig shadow_off','set r_acModelShadows 1','writeconfig shadow_on',
              'echo AC_SHADOW_TEST_DONE','quit']
    (h/'probe.cfg').write_text('\n'.join(commands)+'\n')
    args=[str(b/'openmohaa.exe')]
    settings=dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,
                  fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,
                  cl_playintro=0,r_fullscreen=0,r_mode=-1,r_customwidth=1600,r_customheight=900,
                  com_maxfps=60,com_maxfpsUnfocused=60,r_fastsky=0,r_acShadowDebug=3,r_acAmbientOcclusion=0,ac_campaign_mode=0 if game==2 else 1)
    for k,v in settings.items():args+=['+set',k,str(v)]
    proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=100)
    log=(h/'qconsole.log').read_text(encoding='latin1')
    assert proc.returncode==0 and 'AC_SHADOW_TEST_DONE' in log
    assert 'CP00_PLACEMENT=0' not in log and 'AC_SHADOW_MOTION' in log
    errors=[l for l in log.splitlines() if any(t in l for t in
            ['Script Error','Unknown command','Invalid event','UI EXCEPTION','AC shadows shader:','AC shadows link:'])]
    assert not errors,errors
    assert log.count('AC model shadows ready:')>=2,'Renderer restart failed'
    draws=[int(n) for n in re.findall(r'AC_SHADOW casters=\d+ drawn=(\d+)',log)]
    assert draws and max(draws)>=2,'NPC and pickup missing'
    costs=[(int(ms),int(error)) for ms,error in re.findall(r'AC_SHADOW_COST ms=(\d+) gl_error=(\d+)',log)]
    assert costs and all(error==0 for _,error in costs),costs
    assert 'Loading game...shadow_check' in log
    for name,value in [('shadow_off',0),('shadow_on',1)]:
        assert f'seta r_acModelShadows "{value}"' in (h/f'configs/{name}.cfg').read_text()
    rects=[]
    ui=log.split('AC_UI_ROOT ac_scaling',1)[1].split('AC_SHADOW_TEST_DONE',1)[0]
    for name,*values in re.findall(r'AC_UI_CHILD (\S+) ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',ui):
        x,y,w,t=map(float,values)
        assert x>=0 and y>=0 and x+w<=1600.1 and y+t<=900.1,(name,values)
        if not name.endswith('Panel'):rects.append((name,x,y,w,t))
    assert any(n=='modelShadows' for n,*_ in rects)
    for i,(n,x,y,w,t) in enumerate(rects):
        for m,bx,by,bw,bt in rects[i+1:]:
            assert min(x+w,bx+bw)-max(x,bx)<=.1 or min(y+t,by+bt)-max(y,by)<=.1,(n,m)
    images=[]
    for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
        dst=out/f'{folder}-{i}.png';Image.open(f).save(dst);images.append(dst.relative_to(R).as_posix())
    assert len(images)==6,images
    cases.append(dict(game=folder,drawn_max=max(draws),synchronized_shadow_pass_ms=[ms for ms,_ in costs],
                      renderer_restart=True,save_load=True,live_toggle=True,options_overlap_free=True,images=images))
    print('PASS',folder,'shadow pass ms',[ms for ms,_ in costs],flush=True)
assert hashes()==before,'Personal profile changed'
report=dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),
            game_sha256=sha(rt/'game.dll'),packages=packages,cases=cases,personal_files_unchanged=len(before))
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
