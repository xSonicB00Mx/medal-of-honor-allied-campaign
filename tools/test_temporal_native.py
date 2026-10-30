"""Native temporal regression; isolated profiles and hash-protected personal saves."""
import argparse,hashlib,json,re,shutil,subprocess,zipfile
from pathlib import Path
from PIL import Image,ImageStat
import numpy as np
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',type=int,default=0);ap.add_argument('--uhd',action='store_true');ap.add_argument('--msaa',type=int,default=0);a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;folder=['main','mainta','maintt'][a.game];h=p/folder;h.mkdir(parents=True)
b=p/'bin';b.mkdir();rt=R/'runtime-local/CP09-r1';build=R/'build-local/cp00-r3/RelWithDebInfo'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
personal=R/'profiles-local/CP08-r1/user'
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/n,b/n)
packages=[]
for game,f in zip(['AA','SH','BT'],['main','mainta','maintt']):
    zpath=out/'packages'/f/'zzzzzzzzzzzzz_AC_FlinchOptions.pk3';zpath.parent.mkdir(parents=True)
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for n in ['ac_scaling','ac_lighting','ac_temporal']:z.writestr('ui/'+n+'.urc',(R/'mod/ui'/f'{n}.urc').read_text().encode('latin1'))
    dest=p/f/zpath.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(zpath,dest)
    packages.append(dict(game=game,package=zpath.relative_to(R).as_posix(),sha256=sha(zpath)))
start='devmap m2l2a'
if a.game:
    src=personal/'mainta/save/omconfig/quick.sav' if a.game==1 else R/'profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'
    dest=h/'save/omconfig';dest.mkdir(parents=True)
    for f in src.parent.glob(src.stem+'.*'):shutil.copy2(f,dest/('reference'+f.suffix))
    start='loadgame reference'
fixture=(R/'tools/cp00_baseline_fixture.scr').read_text().split('    waitthread snapshot')[0].replace('level.cp00_subject thread deathwatch','level.cp00_subject.health = 10000')
if a.game==0:
    fixture='main:\n    level.cp00_target = ( -4050 -4100 -46 )\n    level.cp00_subject = spawn models/human/german_wehrmact_soldier.tik origin level.cp00_target gun "Mauser KAR 98K"\n    level.cp00_subject ai_off\n    level.cp00_subject.health = 10000\n    $player.origin = ( -4000 -4200 -40 )\n'
fixture+='''    level.tm_item = spawn models/weapons/mp40.tik
    level.tm_item.origin = level.cp00_target + ( 40 0 55 )
    level.tm_item svflags "+broadcast"
    level.tm_cam = spawn Camera
    level.tm_cam.origin = $player.origin + ( 0 0 90 )
    level.tm_cam.angles = vector_toangles (level.cp00_target + ( 0 0 30 ) - level.tm_cam.origin)
    level.tm_angles = level.tm_cam.angles
    $player hide
    cuecamera level.tm_cam
    thread rotate_item
    println AC_TEMPORAL_FIXTURE
end
rotate_item:
    while (1)
    {
        level.tm_item.angles = level.tm_item.angles + ( 0 12 0 )
        wait .02
    }
end
'''
(h/'fixture.scr').write_text(fixture)
(h/'pan.scr').write_text('main:\n    for(local.i = 0;local.i < 120;local.i++)\n    {\n        level.tm_cam.angles = level.tm_cam.angles + ( 0 .25 0 )\n        wait .02\n    }\n    level.tm_cam.angles = level.tm_angles\nend\n')
cmd=['wait 800',start,'wait 5000','finishloadingscreen','god','notarget','wait 500','script player exec fixture.scr','wait 800',
     'set r_acTAA 0','set r_acObjectMotionBlur 0','wait 500','screenshot silent',
     'set r_acTAA 1','wait 1200','screenshot silent',
     'set r_acObjectMotionBlur 100','wait 500','set r_acTemporalDebug 3','wait 100','screenshot silent',
     'script player exec pan.scr','wait 500','screenshot silent','wait 2200',
     'set r_acTemporalDebug 2','wait 200','screenshot silent','set r_acTemporalDebug 1',
     'set com_maxfps 30','wait 500','screenshot silent','set com_maxfps 120','wait 500','screenshot silent','set com_maxfps 60',
     'savegame temporal_check','wait 300','loadgame temporal_check','wait 4000','finishloadingscreen','wait 500','screenshot silent',
     'vid_restart','wait 3500','finishloadingscreen','wait 500','screenshot silent',
     'pushmenu ac_temporal','wait 500','ac_ui_report ac_temporal','screenshot silent','writeconfig temporal_settings']
scale=4 if a.uhd else 1600/960
cmd += [f'widgetcommand temporalAA left_mouse_up {int(868*scale)} {int(146*scale)} 0',
        'widgetcommand objectBlur left_mouse_down '+str(int(795*scale))+' '+str(int(279*scale))+' 1',
        'widgetcommand objectBlur left_mouse_up '+str(int(795*scale))+' '+str(int(279*scale))+' 0',
        'writeconfig temporal_changed',
        f'widgetcommand temporalDefaults left_mouse_down {int(780*scale)} {int(485*scale)} 1',
        f'widgetcommand temporalDefaults left_mouse_up {int(780*scale)} {int(485*scale)} 0',
        'widgetcommand back stuffcommand "exec finish.cfg"',
        f'widgetcommand back left_mouse_down {int(50*scale)} {int(485*scale)} 1',
        f'widgetcommand back left_mouse_up {int(50*scale)} {int(485*scale)} 0']
(h/'finish.cfg').write_text('wait 100\nwriteconfig temporal_defaults\necho AC_TEMPORAL_DONE\nquit\n')
(h/'play.scr').write_text('main:\n    cueplayer\n    $player show\n    $player.viewangles = vector_toangles (level.cp00_target + ( 0 0 45 ) - ($player.origin + ( 0 0 64 )))\n    $player give models/weapons/mp40.tik\n    $player use models/weapons/mp40.tik\nend\n')
idx=cmd.index('savegame temporal_check')
cmd[idx:idx]=['script player exec play.scr','wait 2500','+attack','wait 1200','screenshot silent','wait 300','-attack','reload','wait 400','screenshot silent','wait 1600']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=a.game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,
 net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,
 r_customwidth=3840 if a.uhd else 1600,r_customheight=2160 if a.uhd else 900,com_maxfps=60,com_maxfpsUnfocused=60,
 r_fastsky=0,r_ext_multisample=a.msaa,r_acTemporalDebug=1,ac_campaign_mode=0 if a.game==2 else 1).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=150)
log=(h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AC_TEMPORAL_DONE' in log and 'AC_TEMPORAL_FIXTURE' in log
errors=[l for l in log.splitlines() if any(e in l for e in ['Script Error','Script file compile error','Unknown command','Invalid event','AC temporal shader:','AC temporal link:'])]
assert not errors,errors
stats=[list(map(int,m)) for m in re.findall(r'AC_TEMPORAL batches=(\d+) vertices=(\d+) valid=(\d+) overflow=(\d+) ms=(\d+) gl_error=(\d+)',log)]
assert stats and max(s[1] for s in stats)>0,stats
assert all(s[3]==0 and s[5]==0 for s in stats),stats
assert log.count('AC temporal ready:')>=2
if a.msaa:assert f'AC temporal framebuffer samples: {a.msaa}' in log
content=(h/'configs/temporal_defaults.cfg').read_text(encoding='latin1')
assert 'seta r_acTAA "1"' in content and 'seta r_acObjectMotionBlur "0"' in content
content=(h/'configs/temporal_changed.cfg').read_text(encoding='latin1')
assert 'seta r_acTAA "0"' in content
images=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
    im=Image.open(f);dst=out/f'{folder}-{i}.png';im.save(dst);images.append(dst.relative_to(R).as_posix())
    if i!=4:assert max(ImageStat.Stat(im).stddev)>5,'Blank scene'
assert len(images)==12,len(images)
# The health bar is rendered AFTER the post-pass. Its texture has a tiny
# residual transparency: a black diagnostic backdrop can change up to two
# 8-bit levels, but must never remove, move or blur the green HUD pixels.
original=np.asarray(Image.open(R/images[0]).convert('RGB'))
mask=(original[:,:,1]>150)&(original[:,:,0]<80)&(original[:,:,2]<80)
mask[:int(original.shape[0]*.9),:]=False;mask[:,int(original.shape[1]*.1):]=False
assert mask.sum()>50
for index in [1,4]:
    image=np.asarray(Image.open(R/images[index]).convert('RGB'))
    assert np.max(abs(original[mask].astype(int)-image[mask].astype(int)))<=2,'HUD entered temporal postprocessing'

obj=np.fromfile(h/'temporal-objects.f32',np.float32).reshape((-1,4));motion=np.fromfile(h/'temporal-motion.f32',np.float32).reshape((-1,4))
assert np.isfinite(obj).all() and np.isfinite(motion).all()
moving=(np.linalg.norm(obj[:,:2],axis=1)>1e-5)&(obj[:,3]>0)
assert moving.sum()>20,('No moving object vectors',np.unique(obj[:,3]),stats[-10:])
if a.game==0:
    # The fixed close-up fixture must cover the NPC and rotating pickup,
    # including with MSAA. A few surviving triangles are not a working pass.
    assert (obj[:,3]>0).sum()>len(obj)*.08,'Incomplete object depth coverage'
    assert moving.sum()>len(obj)*.002,'Incomplete moving pickup coverage'
assert np.max(np.abs(obj[obj[:,3]==0,:2]))==0
assert hashes()==before
result=dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),game_sha256=sha(rt/'game.dll'),packages=packages,
 game=folder,images=images,stats=stats,moving_pixels=int(moving.sum()),personal_files_unchanged=len(before))
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS native temporal',folder,'moving_pixels',moving.sum(),'samples',stats[-5:])
