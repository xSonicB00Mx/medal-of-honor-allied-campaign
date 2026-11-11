"""Extract release over a separate verified WCR base and smoke-test all games."""
from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile, sys, re, time
from cp09_candidate import R, digest

release=R/'artifacts-local/Allied-Campaign-1.0.1'
archive=release/'Medal-of-Honor-Allied-Campaign-1.0.1-Windows-x64.zip'
dest=R/'generated-local/release-1.0.1-install'
reuse = '--reuse' in sys.argv
finish = '--finish' in sys.argv
if finish: reuse = True
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
assert len(list(dest.glob('*/*.pk3'))) == len([r for r in base if r['path'].endswith('.pk3')]) + 3
updater=lambda: subprocess.run(['cmd.exe','/d','/c','Update-Allied-Campaign.cmd','--quiet'],cwd=dest,check=True,timeout=120)
updater()  # Fresh WCR install, no old packages: safe no-op.
# Exercise a real 1.0.0 -> 1.0.1 migration, not just synthetic fixtures.
old=R/'artifacts-local/Allied-Campaign-1.0.0/Medal-of-Honor-Allied-Campaign-1.0.0-Windows-x64.zip'
with zipfile.ZipFile(old) as z:
    for name in z.namelist():
        if name.endswith('.pk3'): z.extract(name,dest)
assert len(list(dest.glob('*/*_AC_*.pk3')))==68
updater()
updater()  # Repeat is also a no-op.
assert not list(dest.glob('*/*_AC_*.pk3'))
for row in base: assert digest(dest/row['path'])==row['sha256']
for row in manifest['files']: assert digest(dest/row['path'])==row['sha256']
print('Fresh install and real 1.0.0 upgrade passed; WCR/mod hashes verified',flush=True)
results=[]
for game,folder,mapname in [(0,'main','m1l1'),(1,'mainta','t1l1'),(2,'maintt','e2l2')]:
    home=dest/('QA-'+folder); cfg=home/folder/'release-smoke.cfg'; cfg.parent.mkdir(parents=True,exist_ok=reuse)
    (cfg.parent/'release-clearfade.scr').write_text('main:\n clearfade\nend\n')
    cfg.write_text('set autopaused 0\nset cl_paused 0\nset cheats 1\nset thereisnomonkey 1\nwait 1000\nmap '+mapname+'\nwait 30000\nfinishloadingscreen\nscript player exec release-clearfade.scr\nwait 1000\nscreenshot silent\nwait 500\necho AC_RELEASE_SMOKE_COMPLETE\nquit\n')
    args=[str(dest/'openmohaa.exe')]
    for k,v in dict(com_target_game=game,fs_basepath=dest,fs_homepath=home,fs_steampath=dest,
                    fs_gogpath=dest,fs_microsoftstorepath=dest,net_enabled=0,ac_campaign_mode=1,
                    cl_playintro=0,autopaused=0,developer=1,logfile=2,cheats=1,thereisnomonkey=1,com_maxfps=60,com_maxfpsUnfocused=60,r_fullscreen=0,r_mode=-1,
                    r_customwidth=1280,r_customheight=720).items(): args+=['+set',k,str(v)]
    # Compare actual shader enumeration against the unmodified multi-PK3 runtime.
    baseline_home=dest/('baseline-'+folder)
    (baseline_home/folder).mkdir(parents=True,exist_ok=reuse)
    (baseline_home/folder/'baseline.cfg').write_text('wait 1500\necho AC_BASELINE_COMPLETE\nquit\n')
    baseline_args=[str(rt/'openmohaa.exe')]+[str(baseline_home) if a==str(home) else str(rt) if a==str(dest) else a for a in args[1:]]
    if not finish:
        subprocess.run(baseline_args+['+exec','baseline.cfg'],cwd=rt,check=True,timeout=60,
                       stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    baseline_log=(baseline_home/folder/'qconsole.log').read_text(encoding='latin1')
    assert 'AC_BASELINE_COMPLETE' in baseline_log
    if not finish:
        proc=subprocess.run(args+['+exec','release-smoke.cfg'],cwd=dest,timeout=100,
                            stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
        assert proc.returncode==0
    log=(home/folder/'qconsole.log').read_text(encoding='latin1')
    assert 'AC_RELEASE_SMOKE_COMPLETE' in log
    shader_lines=lambda text: re.findall(r"\.\.\.loading '(scripts/[^']+\.shader)'",text)
    assert shader_lines(log) and shader_lines(log)==shader_lines(baseline_log), 'Native shader order changed'
    assert not any(s in log for s in ['VM_Create on game failed','Could not load default.cfg','GLimp_Init() - could not load'])
    shots=list((home/folder/'screenshots').glob('*.tga')); assert shots
    from PIL import Image
    with Image.open(shots[-1]) as image:
        from PIL import ImageStat
        assert max(ImageStat.Stat(image.convert('RGB')).stddev)>3, 'Blank smoke screenshot'
        image.save(release/('smoke-'+folder+'.png'))
    results.append(dict(game=folder,map=mapname,completed=True,screenshot=True))
    print(folder+' launched and rendered from extracted ZIP',flush=True)
# Load the creator's latest save only from a separate copied profile.
copy_home=dest/'save-compatibility'
shutil.copytree(personal,copy_home,dirs_exist_ok=reuse)
(copy_home/'mainta/release-save.cfg').write_text('wait 800\nloadgame t2l30000\nwait 1000\nfinishloadingscreen\nwait 20000\nscreenshot silent\nwait 500\necho AC_SAVE_COMPATIBLE\nquit\n')
save_args=[str(dest/'openmohaa.exe')]
for k,v in dict(com_target_game=1,fs_basepath=dest,fs_homepath=copy_home,fs_steampath=dest,fs_gogpath=dest,
                fs_microsoftstorepath=dest,net_enabled=0,ac_campaign_mode=1,cl_playintro=0,autopaused=0,
                developer=1,logfile=2,com_maxfps=60,com_maxfpsUnfocused=60,r_fullscreen=0,r_mode=-1,
                r_customwidth=1280,r_customheight=720).items(): save_args+=['+set',k,str(v)]
subprocess.run(save_args+['+exec','release-save.cfg'],cwd=dest,check=True,timeout=90,
               stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
save_log=(copy_home/'mainta/qconsole.log').read_text(encoding='latin1')
assert 'AC_SAVE_COMPATIBLE' in save_log and 'AC_SAVE_ACCEPT context=1 map=t2l3' in save_log
assert not any(x in save_log for x in ['Could not load', 'Savegame is from', 'Unknown command'])
errors = [line for line in save_log.splitlines() if 'ERROR:' in line and 'LOCALIZATION ERROR:' not in line]
assert not errors, errors
latest_shot=max((copy_home/'mainta/screenshots').glob('*.tga'),key=lambda p:p.stat().st_mtime)
with Image.open(latest_shot) as im:
    assert max(ImageStat.Stat(im.convert('RGB')).stddev)>3
    im.save(release/'save-compatibility.png')
# Exercise the exact CMD entry point and its automatic update invocation.
launch_home=dest/'AlliedCampaign-User/main';launch_home.mkdir(parents=True,exist_ok=reuse)
(launch_home/'launcher-test.cfg').write_text('wait 1500\necho AC_LAUNCHER_COMPLETE\nquit\n')
subprocess.run(['cmd.exe','/d','/c','Start-Allied-Campaign.cmd','+set','cl_playintro','0','+set','autopaused','0',
                '+set','com_maxfpsUnfocused','60','+set','r_fullscreen','0','+set','r_mode','-1',
                '+set','r_customwidth','1280','+set','r_customheight','720','+exec','launcher-test.cfg'],cwd=dest,check=True,timeout=30)
start=time.monotonic()
while time.monotonic()-start<45:
    logpath=launch_home/'qconsole.log'
    if logpath.exists() and 'AC_LAUNCHER_COMPLETE' in logpath.read_text(encoding='latin1'): break
    time.sleep(.25)
else: raise AssertionError('Portable CMD launcher did not complete')
assert snapshot()==before
report=dict(passed=True,archive_sha256=digest(archive),source_commit=manifest['source_commit'],
            package_files=len(manifest['files']),base_files_verified=len(base),
            personal_files_unchanged=len(before),campaigns=results,legacy_packages_removed=68,
            shader_order_preserved=True,personal_save_copy_loaded=True,portable_launcher_passed=True)
(release/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
