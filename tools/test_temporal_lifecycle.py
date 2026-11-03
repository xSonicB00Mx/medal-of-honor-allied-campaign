"""Native mode changes, map/history resets and the real options entry point."""
import argparse, hashlib, json, re, shutil, subprocess, zipfile
from pathlib import Path
from PIL import Image, ImageStat

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;h=p/'main';h.mkdir(parents=True)
b=p/'bin';b.mkdir();rt=R/'runtime-local/CP09-r1';build=R/'build-local/cp00-r3/RelWithDebInfo'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
personal=R/'profiles-local/CP08-r1/user'
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/n,b/n)
with zipfile.ZipFile(h/'zzzzzzzzzzzzz_AC_FlinchOptions.pk3','w',zipfile.ZIP_DEFLATED) as z:
    for n in ['ac_scaling','ac_temporal']:
        z.writestr('ui/'+n+'.urc',(R/'mod/ui'/f'{n}.urc').read_text().encode('latin1'))
cmd=['wait 800','devmap m2l2a','wait 5000','finishloadingscreen','god','notarget',
     'set r_acTAA 0','set r_acObjectMotionBlur 100','wait 600','screenshot silent',
     'set r_acTAA 1','wait 600','set cg_fov 115','wait 600','screenshot silent',
     'set r_customwidth 640','set r_customheight 480','vid_restart','wait 4000',
     'finishloadingscreen','wait 600','screenshot silent',
     'set r_customwidth 1600','set r_customheight 900','vid_restart','wait 4000',
     'finishloadingscreen','set cg_fov 80','wait 600','screenshot silent',
     'devmap m2l2b','wait 5000','finishloadingscreen','god','wait 800','screenshot silent',
     'pushmenu ac_scaling','wait 500','ac_ui_report ac_scaling','screenshot silent',
     'widgetcommand temporalOptions stuffcommand "pushmenu ac_temporal; exec temporal_page.cfg"',
     'widgetcommand temporalOptions left_mouse_down 1183 188 1',
     'widgetcommand temporalOptions left_mouse_up 1183 188 0']
(h/'temporal_page.cfg').write_text('\n'.join([
     'wait 400','ac_ui_report ac_temporal','screenshot silent',
     'widgetcommand back stuffcommand "popmenu 0; exec finish.cfg"',
     'widgetcommand back left_mouse_down 133 850 1',
     'widgetcommand back left_mouse_up 133 850 0'])+'\n')
(h/'finish.cfg').write_text('wait 200\nac_ui_report ac_scaling\necho AC_TEMPORAL_LIFECYCLE_DONE\nquit\n')
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,
 net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,
 r_customwidth=1600,r_customheight=900,com_maxfps=60,com_maxfpsUnfocused=60,r_fastsky=0,
 r_ext_multisample=0,r_acTemporalDebug=1,ac_campaign_mode=1).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AC_TEMPORAL_LIFECYCLE_DONE' in log
assert log.count('AC temporal ready:')==3
assert 'AC_UI_CURRENT ac_temporal' in log and log.count('AC_UI_CURRENT ac_scaling')==2
assert 'AC_UI_CHILD lightingOptions ' not in log
assert 'AC_UI_CHILD temporalOptions ' in log
assert 'AC lighting ready:' not in log
errors=[l for l in log.splitlines() if any(e in l for e in ['Script Error','Unknown command','Invalid event','AC temporal shader:','AC temporal link:'])]
assert not errors,errors
stats=[list(map(int,m)) for m in re.findall(r'AC_TEMPORAL batches=(\d+) vertices=(\d+) valid=(\d+) overflow=(\d+) ms=(\d+) gl_error=(\d+)',log)]
assert stats and all(s[3]==0 and s[5]==0 for s in stats)
images=[];sizes=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
    im=Image.open(f);assert max(ImageStat.Stat(im).stddev)>5
    dst=out/f'lifecycle-{i}.png';im.save(dst);images.append(dst.relative_to(R).as_posix());sizes.append(im.size)
assert sizes==[(1600,900),(1600,900),(640,480),(1600,900),(1600,900),(1600,900),(1600,900)],sizes
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),
    images=images,sizes=sizes,stats=stats,personal_files_unchanged=len(before)),indent=2))
print('PASS: blur without TAA, live TAA/FOV, 4:3/16:9 resolution changes, map switch, options navigation')
