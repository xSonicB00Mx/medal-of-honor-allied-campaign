"""Native isolated pilot captures. Original saves/runtime are read-only inputs."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--export',action='store_true');ap.add_argument('--bake',type=Path);ap.add_argument('--views',type=Path);ap.add_argument('--uhd',action='store_true');ap.add_argument('--original-engine',action='store_true')
ap.add_argument('--disabled',action='store_true');ap.add_argument('--expect-reject',choices=['lightmap','grid']);ap.add_argument('--lifecycle',action='store_true');ap.add_argument('--stable',action='store_true');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;h=p/'main';h.mkdir(parents=True)
rt=R/'runtime-local/CP09-r1';b=p/'bin';b.mkdir();personal=R/'profiles-local/CP08-r1/user'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
shutil.copy2((rt if a.original_engine else R/'build-local/cp00-r3/RelWithDebInfo')/'openmohaa.exe',b/'openmohaa.exe')
for f in personal.rglob('*.cfg'):
 d=p/f.relative_to(personal);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
d=h/'save/omconfig';d.mkdir(parents=True)
for f in (personal/'main/save/omconfig').glob('quick.*'):shutil.copy2(f,d/('reference'+f.suffix))
if a.bake:
 d=h/'maps/ac_relight';d.mkdir(parents=True)
 for f in a.bake.glob('m3l3.ac*'):shutil.copy2(f,d/f.name)
cmd=['wait 600','loadgame reference','wait 3000','finishloadingscreen','god','notarget','ui_hud 0','set cg_drawviewmodel 0','set ui_crosshair 0','wait 300']
views=json.loads(a.views.read_text()) if a.views else []
for i,v in enumerate(views):
 pos=' '.join(map(str,v['origin']));target=' '.join(map(str,v['target']))
 (h/f'view{i}.scr').write_text(f'''main:
    $player.origin = ( {pos} )
    $player hide
    local.cam = spawn Camera
    local.cam.origin = ( {pos} )
    local.cam.angles = vector_toangles (( {target} ) - local.cam.origin)
    cuecamera local.cam
end
''')
 cmd+=['set paused 0',f'script player exec view{i}.scr','wait 100','set paused 1','wait 500','screenshot silent']
if not views:cmd+=['set paused 1','wait 500','screenshot silent']
extra=[]
if a.lifecycle:
 cmd+=['set paused 0','savegame relight_roundtrip','wait 300','loadgame relight_roundtrip','wait 3500','finishloadingscreen','wait 700','screenshot silent',
       'vid_restart','wait 3500','finishloadingscreen','wait 700','screenshot silent',
       'map m2l1','wait 4500','finishloadingscreen','wait 700','screenshot silent',
       'set r_acLevelRelight 0','loadgame reference','wait 3500','finishloadingscreen','wait 700','screenshot silent']
 extra=['save-load','video-restart','other-map','disabled-reload']
cmd+=['set paused 0','echo AC_RELIGHT_TEST_DONE','quit'];(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840 if a.uhd else 1920,r_customheight=2160 if a.uhd else 1080,com_maxfps=60,com_maxfpsUnfocused=60,r_acLevelRelight=int(bool(a.bake) and not a.disabled),r_acRelightExport=int(a.export),r_acTemporalDebug=0,r_acShadowDebug=0,r_acAODebug=0,r_acObjectMotionBlur=0).items():args+=['+set',k,str(v)]
if a.stable:
 for k in ['r_acTAA','r_acAmbientOcclusion','r_acModelShadows']:args+=['+set',k,'0']
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=150)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_RELIGHT_TEST_DONE' in log
assert not any(e in log for e in ['Script Error','Script file compile error','Unknown command','Invalid event','GL_INVALID','GL_OUT_OF_MEMORY'])
if a.expect_reject:
 assert 'AC_RELIGHT_REJECT '+('invalid grid' if a.expect_reject=='grid' else 'lightmap') in log
 assert ('AC_RELIGHT_APPLIED' in log)==(a.expect_reject=='grid')
 assert 'AC_RELIGHT_GRID' not in log
else:assert 'AC_RELIGHT_REJECT' not in log
if a.export:assert 'AC_RELIGHT_EXPORT triangles=' in log
if a.bake and not a.disabled and not a.expect_reject:assert 'AC_RELIGHT_APPLIED m3l3' in log and 'AC_RELIGHT_GRID' in log
if a.disabled:assert 'AC_RELIGHT_APPLIED' not in log and 'AC_RELIGHT_GRID' not in log
if a.lifecycle:
 assert (h/'save/omconfig/relight_roundtrip.sav').exists()
 # Same-map save loads retain the renderer world; vid_restart rebuilds it.
 # Thus exactly initial load + graphics restart, never a double application.
 assert log.count('AC_RELIGHT_APPLIED m3l3')==2, 'Unexpected sidecar lifetime across map/reload'
images=[]
names=([v['name'] for v in views] or ['save'])+extra
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
 name=names[i];dst=out/f'{name}.png';Image.open(f).save(dst);images.append(str(dst))
assert len(images)==len(names);assert hashes()==before
result=dict(engine_sha256=sha(b/'openmohaa.exe'),personal_files_unchanged=len(before),images=images,relight='AC_RELIGHT_APPLIED' in log,relight_loads=log.count('AC_RELIGHT_APPLIED'),export=str(h/'relight') if a.export else None)
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
