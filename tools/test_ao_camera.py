"""Native fixed-position camera rotation regression for AO, isolated profiles.

Diagnostic images share the same scene/camera position. Only yaw/pitch changes;
use these to inspect false darkening of convex edges and camera-relative seams.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from PIL import Image

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('run')
ap.add_argument('--spearhead-save',type=Path,help='Optional read-only SH save input, copied for camera rotation checks')
a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run; out.mkdir(parents=True,exist_ok=False)
rt=R/'runtime-local/CP09-r1'; build=R/'build-local/cp00-r3/RelWithDebInfo'
personal=R/'profiles-local/CP08-r1/user'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(): return {p.relative_to(personal).as_posix():sha(p) for p in personal.rglob('*') if p.is_file()}
before=hashes(); results=[]
angles=[(0,0),(0,-25),(0,25),(-15,0),(15,0)]
scenes=[('m3l2',0,'main'),('m6l3a',0,'main')]
if a.spearhead_save: scenes.append(('sh-save',1,'mainta'))
for level,game,folder in scenes:
    p=R/'profiles-local/CP09'/f'{a.run}-{level}'; h=p/folder; h.mkdir(parents=True,exist_ok=False)
    b=p/'bin'; b.mkdir()
    for f in rt.glob('*.dll'): shutil.copy2(f,b/f.name)
    shutil.copy2(build/'openmohaa.exe',b/'openmohaa.exe')
    (h/'camera.scr').write_text('''main:
    level.ao_cam = spawn Camera
    level.ao_cam.origin = $player.origin + ( 0 0 64 )
    level.ao_angles = $player.viewangles
    level.ao_cam.angles = level.ao_angles
    println ("AO_CAMERA origin=" + level.ao_cam.origin + " angles=" + level.ao_angles)
    $player hide
    cuecamera level.ao_cam
end
''')
    start='map '+level
    if game:
        dst=h/'save/omconfig'; dst.mkdir(parents=True)
        for f in a.spearhead_save.parent.glob(a.spearhead_save.stem+'.*'): shutil.copy2(f,dst/('reference'+f.suffix))
        start='loadgame reference'
    commands=['wait 800',start,'wait 5000','finishloadingscreen','god','wait 1000',
              'script player exec camera.scr','wait 500','ui_hud 0','set ui_crosshair 0',
              'set cg_drawviewmodel 0','set r_acAmbientOcclusion 1','set r_acModelShadows 0']
    for i,(pitch,yaw) in enumerate(angles):
        (h/f'angle{i}.scr').write_text(f'main:\n    level.ao_cam.angles = level.ao_angles + ( {pitch} {yaw} 0 )\nend\n')
        commands += [f'script player exec angle{i}.scr','wait 300','set r_acAODebug 1','wait 200','screenshot silent',
                     'set r_acAODebug 2','wait 200','screenshot silent']
    commands+=['echo AO_CAMERA_DONE','quit']; (h/'camera.cfg').write_text('\n'.join(commands)+'\n')
    args=[str(b/'openmohaa.exe')]
    for k,v in dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,
                    fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,
                    cl_playintro=0,r_fullscreen=0,r_mode=-1,r_customwidth=1600,r_customheight=900,
                    r_fastsky=0,cg_shadows=0,com_maxfps=60,com_maxfpsUnfocused=60,ui_gmbox=0,
                    ui_gmboxspam=0,g_subtitle=0,r_acAODebug=2).items(): args+=['+set',k,str(v)]
    proc=subprocess.run(args+['+exec','camera.cfg'],cwd=b,timeout=90)
    log=(h/'qconsole.log').read_text(encoding='latin1')
    assert proc.returncode==0 and 'AO_CAMERA_DONE' in log
    script_errors=re.findall(r'Script Error[^\r\n]*',log)
    # Direct m6l3a starts lack the preceding level's allied prisoners. Baseline
    # WCR scripts report these four unrelated null death-listeners as well.
    assert not script_errors or (level=='m6l3a' and len(script_errors)==4 and
        all("command 'waitTill' applied to NULL listener" in e for e in script_errors)),script_errors
    assert not any(e in log for e in ['AC AO shader:','AC AO link:','AC AO framebuffer unsupported'])
    costs=[(int(ms),int(e)) for ms,e in re.findall(r'AC_AO_COST ms=(\d+) gl_error=(\d+)',log)]
    assert costs and all(e==0 for _,e in costs)
    imgs=sorted((h/'screenshots').glob('*.tga')); assert len(imgs)==10
    for i,f in enumerate(imgs): Image.open(f).save(out/f'{level}-{i//2}-{"ao" if i%2==0 else "color"}.png')
    results.append(dict(map=level,camera=re.findall(r'AO_CAMERA origin=.*',log),angles=angles,costs_ms=[ms for ms,_ in costs],
                        baseline_map_script_errors=script_errors))
    print('PASS camera rotations',level,flush=True)
assert before==hashes()
(out/'result.json').write_text(json.dumps(dict(engine_sha256=sha(build/'openmohaa.exe'),scenes=results,
                                             personal_files_unchanged=len(before)),indent=2)+'\n')
