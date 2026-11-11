"""Exercise confirmation and reset in an isolated profile, preserving save sentinels."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--installed', action='store_true')
a = ap.parse_args()
r = Path(__file__).resolve().parents[1]
rt = r/'runtime-local/CP08-r1'
p = r/'profiles-local/operations-reset'/a.run
assert not p.exists()
p.mkdir(parents=True)
binary = rt if a.installed else p/'bin'
if not a.installed:
    binary.mkdir()
    for f in rt.glob('*.dll'): shutil.copy2(f, binary/f.name)
    shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe', binary/'openmohaa.exe')
sentinels = []
for folder in ['main', 'mainta', 'maintt']:
    home = p/folder
    (home/'save').mkdir(parents=True)
    if not a.installed:
        shutil.copy2(r/'generated-local/widescreen/packages'/folder/'zzzzzz_AC_Widescreen.pk3', home/'zzzzzz_AC_Widescreen.pk3')
    f = home/'save/keep_test.sav'
    f.write_bytes(b'ISOLATED SAVE PRESERVATION SENTINEL')
    sentinels.append(f)
(p/'ac_progress.dat').write_text('ACPROG1 7 3 keep_test\n')
before = {str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sentinels}

def run(phase, commands):
    h = p/'main'
    (h/'probe.cfg').write_text('\n'.join(['wait 1600', *commands, 'wait 300', 'echo AC_RESET_TEST_DONE', 'quit'])+'\n')
    cmd = [str(binary/'openmohaa.exe')]
    for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1).items():
        cmd += ['+set',k,str(v)]
    result = subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=45)
    log = (h/'qconsole.log').read_text(encoding='latin1')
    assert result.returncode == 0 and 'AC_RESET_TEST_DONE' in log
    assert not any(x in log for x in ['Unknown command', "Couldn't find menu", 'Invalid event', 'Script Error'])
    (p/(phase+'.log')).write_text(log)
    return log

log = run('cancel', ['pushmenu main','set ui_signshader newgame_sign','wait 700','screenshot silent',
    'ac_reset_progress confirm','ac_campaign','wait 500','screenshot silent',
    'ac_reset_progress','wait 600','ac_ui_report ac_campaign_reset','screenshot silent',
    'popmenu 0','ac_progress_report'])
assert 'AC_RESET_REQUIRES_CONFIRMATION' in log
assert (p/'ac_progress.dat').read_text() == 'ACPROG1 7 3 keep_test\n'
assert 'completed=7 resume=3 slot=keep_test' in log
log = run('confirm', ['ac_campaign','ac_reset_progress','wait 300','ac_reset_progress confirm','wait 700','ac_progress_report','screenshot silent'])
assert 'AC_PROGRESS_RESET saves and preferences preserved' in log
assert (p/'ac_progress.dat').read_text().strip() == 'ACPROG2 0 0 - 0 0'
assert (p/'ac_progress.dat.bak').read_text().strip() == 'ACPROG1 7 3 keep_test'
assert 'name "mission_0"' in (p/'main/ui/ac_campaign_operations.urc').read_text()
assert 'name "mission_1"' not in (p/'main/ui/ac_campaign_operations.urc').read_text()
log = run('restart', ['ac_progress_report'])
assert 'completed=0 resume=0 slot=-' in log
assert before == {str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sentinels}
images = []
for f in sorted((p/'main/screenshots').glob('*.tga')):
    Image.open(f).save(f.with_suffix('.png'))
    images.append(f.with_suffix('.png').relative_to(r).as_posix())
report = dict(run=a.run,installed=a.installed,cancel_preserved=True,confirmation_required=True,
              confirmed_reset=True,restart_persisted=True,saves_unchanged=True,previous_progress_backed_up=True,images=images)
(r/'generated-local'/('operations-reset-'+a.run+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
