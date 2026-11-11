"""Extract release over a separate verified WCR base and smoke-test all games."""
from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile, sys
from cp09_candidate import R, digest

release=R/'artifacts-local/Allied-Campaign-1.0.0'
archive=release/'Medal-of-Honor-Allied-Campaign-1.0.0-Windows-x64.zip'
dest=R/'generated-local/release-1.0.0-install'
reuse = '--reuse' in sys.argv
assert reuse or not dest.exists()
dest.mkdir(exist_ok=reuse)
rt=R/'runtime-local/CP09-r1'
personal=R/'profiles-local/CP08-r1/user'
snapshot=lambda: {p.relative_to(personal).as_posix():digest(p) for p in personal.rglob('*') if p.is_file()}
before=snapshot()
base=json.loads((rt/'CP09-base-inventory.json').read_text())
for row in base:
    target=dest/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
    if not reuse: shutil.copy2(rt/row['path'],target)
with zipfile.ZipFile(archive) as z:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
    z.extractall(dest)
manifest=json.loads((dest/'Allied-Campaign-manifest.json').read_text())
for row in manifest['files']: assert digest(dest/row['path'])==row['sha256']
for row in base: assert digest(dest/row['path'])==row['sha256']
print('ZIP extracted; all mod files and WCR base hashes verified',flush=True)
results=[]
for game,folder,mapname in [(0,'main','m1l1'),(1,'mainta','t1l1'),(2,'maintt','e2l2')]:
    home=dest/('QA5-'+folder); cfg=home/folder/'release-smoke.cfg'; cfg.parent.mkdir(parents=True)
    (cfg.parent/'release-clearfade.scr').write_text('main:\n clearfade\nend\n')
    cfg.write_text('set autopaused 0\nset cl_paused 0\nset cheats 1\nset thereisnomonkey 1\nwait 1000\nmap '+mapname+'\nwait 30000\nfinishloadingscreen\nscript player exec release-clearfade.scr\nwait 1000\nscreenshot silent\nwait 500\necho AC_RELEASE_SMOKE_COMPLETE\nquit\n')
    args=[str(dest/'openmohaa.exe')]
    for k,v in dict(com_target_game=game,fs_basepath=dest,fs_homepath=home,fs_steampath=dest,
                    fs_gogpath=dest,fs_microsoftstorepath=dest,net_enabled=0,ac_campaign_mode=1,
                    cl_playintro=0,autopaused=0,developer=1,logfile=2,cheats=1,thereisnomonkey=1,com_maxfps=60,com_maxfpsUnfocused=60,r_fullscreen=0,r_mode=-1,
                    r_customwidth=1280,r_customheight=720).items(): args+=['+set',k,str(v)]
    proc=subprocess.run(args+['+exec','release-smoke.cfg'],cwd=dest,timeout=100,
                        stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    log=(home/folder/'qconsole.log').read_text(encoding='latin1')
    assert proc.returncode==0 and 'AC_RELEASE_SMOKE_COMPLETE' in log
    assert not any(s in log for s in ['VM_Create on game failed','Could not load default.cfg','GLimp_Init() - could not load'])
    shots=list((home/folder/'screenshots').glob('*.tga')); assert shots
    from PIL import Image
    with Image.open(shots[-1]) as image:
        from PIL import ImageStat
        assert max(ImageStat.Stat(image.convert('RGB')).stddev)>3, 'Blank smoke screenshot'
        image.save(release/('smoke-'+folder+'.png'))
    results.append(dict(game=folder,map=mapname,exit_code=proc.returncode,screenshot=True))
    print(folder+' launched and rendered from extracted ZIP',flush=True)
assert snapshot()==before
report=dict(passed=True,archive_sha256=digest(archive),source_commit=manifest['source_commit'],
            package_files=len(manifest['files']),base_files_verified=len(base),
            personal_files_unchanged=len(before),campaigns=results)
(release/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
