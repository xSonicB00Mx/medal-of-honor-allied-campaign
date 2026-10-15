"""Exercise actual context restarts and conflicting configs in isolated profiles."""
import argparse, json, re, shutil, subprocess, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--run-id', required=True)
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
runtime = root/'runtime-local/CP08-r1'
home = root/'profiles-local/shared-preferences'/args.run_id
assert not home.exists()
binary = home/'bin'
binary.mkdir(parents=True)
for dll in runtime.glob('*.dll'):
    shutil.copy2(dll, binary/dll.name)
shutil.copy2(root/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe', binary/'openmohaa.exe')
folders = ['main', 'mainta', 'maintt']
for folder in folders:
    (home/folder/'configs').mkdir(parents=True)
    (home/folder/'configs/omconfig.cfg').write_text('seta r_gamma "1.1"\nseta s_ambientvolume "0.1"\nbind F7 "+back"\naltbind F8 "+back"\nctrlbind F9 "+back"\n')

common = dict(ac_campaign_mode=1, fs_basepath=runtime, fs_homepath=home,
    fs_steampath=runtime, fs_gogpath=runtime, fs_microsoftstorepath=runtime,
    net_enabled=0, logfile=2, developer=0, cl_playintro=0, config='omconfig.cfg')
def launch(game, script, initial=False):
    cmd = [str(binary/'openmohaa.exe')]
    values = dict(common, com_target_game=game)
    if initial:
        values.update(r_fullscreen=0,r_mode=-1,r_customwidth=960,r_customheight=540,
                      com_maxfps=60,com_maxfpsUnfocused=60)
    for key,value in values.items(): cmd += ['+set',key,str(value)]
    return subprocess.Popen(cmd+['+exec',script],cwd=runtime)

initial = ['wait 600','seta r_gamma 1.25','seta s_ambientvolume 0.37',
    'seta m_pitch -0.022','seta cl_ctrlbindings 1','seta cl_altbindings 0',
    'seta cg_fov 93','seta g_subtitle 0','seta r_picmip 1',
    'bind F7 +forward','altbind F8 +moveleft','ctrlbind F9 +moveright',
    'seta g_lastsave AA_ONLY','seta ui_NumShotsFired_game 123','ac_context 1 menu']
(home/'main/initial.cfg').write_text('\n'.join(initial)+'\n')
for folder,script in {
    'mainta':['wait 600','writeconfig received-aa','r_picmip','cl_ctrlbindings',
              'seta r_gamma 1.4','seta s_ambientvolume 0.63','unbind F7',
              'unaltbind F8','ctrlbind F9 +attack','ac_context 2 menu'],
    'maintt':['wait 600','writeconfig received-sh','seta r_gamma 1.3',
              'seta s_ambientvolume 0.55','seta r_picmip 0','ac_context 0 menu'],
    'main':['wait 600','writeconfig received-bt','echo AC_PREFS_CHAIN_DONE','quit']
}.items():
    (home/folder/'ac_context_ready.cfg').write_text('\n'.join(script)+'\n')
proc = launch(0,'initial.cfg',True)
deadline = time.monotonic()+75
while time.monotonic()<deadline:
    log = home/'main/qconsole.log'
    if log.exists() and 'AC_PREFS_CHAIN_DONE' in log.read_text(encoding='latin1'):
        break
    time.sleep(.2)
else: raise AssertionError('Context chain did not finish')
proc.wait(timeout=5)
time.sleep(1)

def config(folder,name):
    text=(home/folder/'configs'/name).read_text()
    return dict(re.findall(r'^seta (\S+) "(.*)"',text,re.M)),text

checks=[]
for folder,name,gamma,ambient in [('mainta','received-aa.cfg','1.25','0.37'),
    ('maintt','received-sh.cfg','1.4','0.63'),('main','received-bt.cfg','1.3','0.55')]:
    values,text=config(folder,name)
    assert values['r_gamma']==gamma and values['s_ambientvolume']==ambient,(folder,values)
    for key,value in [('m_pitch','-0.022'),('cg_fov','93'),('g_subtitle','0'),('cl_ctrlbindings','1'),('cl_altbindings','0')]:
        assert values[key]==value,(folder,key,values[key])
    if folder=='mainta':
        assert 'bind F7 "+forward"' in text and 'altbind F8 "+moveleft"' in text
        assert 'ctrlbind F9 "+moveright"' in text and values['r_picmip']=='1'
        assert values.get('g_lastsave')!='AA_ONLY' and values.get('ui_NumShotsFired_game')!='123'
    else:
        assert '\nbind F7 ' not in text and '\naltbind F8 ' not in text
        assert 'ctrlbind F9 "+attack"' in text
    checks.append(dict(folder=folder,phase=name,passed=True))

for game,folder in enumerate(folders):
    (home/folder/'restart.cfg').write_text('wait 600\nwriteconfig restarted\necho AC_PREFS_RESTART_DONE\nquit\n')
    launch(game,'restart.cfg').wait(timeout=30)
    values,text=config(folder,'restarted.cfg')
    assert values['r_gamma']=='1.3' and values['s_ambientvolume']=='0.55' and values['r_picmip']=='0'
    assert 'ctrlbind F9 "+attack"' in text and '\nbind F7 ' not in text and '\naltbind F8 ' not in text
    checks.append(dict(folder=folder,phase='fresh-process',passed=True))
shared=(home/'main/ac_preferences.cfg').read_text()
assert 'g_lastsave' not in shared and 'ui_NumShotsFired_game' not in shared
out=root/'generated-local/shared-preferences'
out.mkdir(exist_ok=True)
(out/(args.run_id+'.json')).write_text(json.dumps(dict(checks=checks,passed=True,
    isolated_profile=home.relative_to(root).as_posix(),latched_graphics=True,
    normal_alt_ctrl_bindings=True,removed_bindings=True,mission_state_excluded=True),indent=2)+'\n')
print('PASS: AA -> SH -> BT -> AA, all fresh restarts, latched graphics, controls and state isolation')
