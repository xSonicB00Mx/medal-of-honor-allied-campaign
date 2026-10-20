"""Native Operations labels and cluster navigation in isolated progress fixtures."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from PIL import Image

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--installed', action='store_true')
a = ap.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9-]+', a.run)
rt = R/'runtime-local/CP09-r1'
exe = rt/'openmohaa.exe' if a.installed else R/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'
out = R/'generated-local/CP09'/a.run
assert not out.exists()
out.mkdir(parents=True)
personal = R/'profiles-local/CP08-r1/user'
def hashes():
    return {p.relative_to(personal).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in personal.rglob('*') if p.is_file()}
before = hashes()
roman = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV']
ops = json.loads((R/'mod/campaign/missions.json').read_text())['operations']
# Partial progression exercises single -> cluster transitions and hides locked missions.
cases = [(0,0,0,0), (0,5,5,0), (0,6,6,0), (1,12,12,1), (2,15,11,0), (2,15,14,1)]
results = []
for case, (game, completed, selected, region) in enumerate(cases):
    p = R/'profiles-local/CP09'/f'{a.run}-{case}'
    assert not p.exists()
    h = p/['main','mainta','maintt'][game]
    h.mkdir(parents=True)
    (p/'ac_progress.dat').write_text(f'ACPROG1 {(1<<completed)-1} {completed} -\n')
    (h/'probe.cfg').write_text(f'wait 1200\nac_campaign {selected} {region}\nwait 700\n'
                             'ac_ui_report ac_campaign_operations\nscreenshot silent\nwait 200\necho AC_NUMBERS_DONE\nquit\n')
    cmd = [str(exe)]
    for k,v in dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,
                    fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,
                    r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,
                    cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1).items():
        cmd += ['+set',k,str(v)]
    proc = subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=45)
    log = (h/'qconsole.log').read_text(encoding='latin1')
    assert proc.returncode==0 and 'AC_NUMBERS_DONE' in log
    assert not any(x in log for x in ['UI EXCEPTION','Script Error :',"Couldn't find menu"])
    text = (h/'ui/ac_campaign_operations.urc').read_text()
    widgets = {re.search(r'name "([^"]+)"', b)[1]: b for b in re.findall(r'resource\s+\w+\s*\{([^}]+)\}',text)
               if re.search(r'name "([^"]+)"',b)}
    titles = {k: re.search(r'title "([^"]*)"',v)[1] for k,v in widgets.items()}
    visible = [i for i,o in enumerate(ops) if i<=completed and o['map_region']==region]
    assert {int(k.split('_')[1]) for k in titles if k.startswith('mission_')} == set(visible)
    for i in visible:
        assert titles[f'mission_{i}'].startswith(roman[i]+' '+('> ' if i==selected else ''))
        assert f'stuffcommand "ac_campaign {i} {region}"' in widgets[f'mission_{i}']
    markers = {k:v for k,v in titles.items() if k.startswith('marker_')}
    expected = [
        {'marker_0':'I'},
        {'marker_0':'I','marker_2':'III','marker_3':'IV','marker_4':'V','marker_5':'VI'},
        {'marker_0':'I','marker_2':'III','marker_3':'IV','marker_4':'V','marker_5':'2'},
        {'marker_1':'II','marker_7':'3','marker_10':'XI','marker_12':'XIII'},
        {'marker_0':'I','marker_2':'III','marker_3':'IV','marker_4':'V','marker_5':'2','marker_11':'XII'},
        {'marker_1':'II','marker_7':'3','marker_10':'XI','marker_12':'2','marker_14':'XV'},
    ][case]
    assert markers==expected, (case,markers,expected)
    if case==2:
        assert 'stuffcommand "ac_campaign 5 0"' in widgets['marker_5']
    if case==4:
        assert 'stuffcommand "ac_campaign 6 0"' in widgets['marker_5']
    shots=[]
    for f in (h/'screenshots').glob('*.tga'):
        im=Image.open(f)
        assert im.size==(1920,1080)
        target=out/f'case-{case}.png'
        im.save(target)
        shots.append(str(target.relative_to(R)))
    assert len(shots)==1
    results.append(dict(game=game,completed=completed,selected=selected,region=region,
                        markers=markers,visible=visible,screenshots=shots))
    print('PASS',case,markers,flush=True)
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
    cases=results,personal_files_unchanged=len(before)),indent=2)+'\n')
