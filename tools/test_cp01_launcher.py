"""Exercise actual CMD launchers and shared UI settings in new CP1 user profiles.

Refuses existing user profiles. Finishes with default UI sizes and FOV 90.
"""
import json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parents[1];root=r/'profiles-local/CP01-r1/user'
assert not any(root.rglob('omconfig.cfg')), 'Never overwrite established user settings'
results=[]
expected=dict(ac_ui_auto='1',ac_menu_scale='0.85',ac_hud_scale='1.25',ac_hud_safe='0.9')
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 h=root/game/folder;h.mkdir(parents=True,exist_ok=True)
 commands=['wait 1500',*expected,'cg_fov','echo CP01_LAUNCHER_DONE','wait 500','quit']
 if game=='AA':commands[1:1]=[f'set {k} {v}' for k,v in expected.items()]+['set cg_fov 90','wait 500']
 (h/'launcher-test.cfg').write_text('\n'.join(commands)+'\n')
 args=['cmd.exe','/d','/c',str(r/f'Start-CP01-r1-{game}.cmd'),'+set','r_fullscreen','0','+set','r_mode','-1','+set','r_customwidth','1280','+set','r_customheight','960','+set','cl_playintro','0','+set','ui_console','0','+exec','launcher-test.cfg']
 p=subprocess.run(args,cwd=r,timeout=75,capture_output=True,text=True)
 assert p.returncode==0,(game,p.stdout,p.stderr)
 log=(h/'qconsole.log').read_text(encoding='latin1');assert 'CP01_LAUNCHER_DONE' in log
 observed={k:re.search(r'"'+k+r'" is:\s*"([^"^]*)',log).group(1) for k in expected}
 assert all(float(observed[k])==float(v) for k,v in expected.items()),observed
 results.append(dict(game=game,observed=observed,exit_code=p.returncode))
# Return all newly created user contexts to default UI scale, retaining FOV.
for game,folder in [('BT','maintt'),('AA','main'),('SH','mainta')]:
 h=root/game/folder
 (h/'launcher-test.cfg').write_text('wait 1000\nset ac_ui_auto 1\nset ac_menu_scale 1\nset ac_hud_scale 1\nset ac_hud_safe 1\nset cg_fov 90\nwait 1500\nquit\n')
 p=subprocess.run(['cmd.exe','/d','/c',str(r/f'Start-CP01-r1-{game}.cmd'),'+set','cl_playintro','0','+exec','launcher-test.cfg'],cwd=r,timeout=75,capture_output=True,text=True)
 assert p.returncode==0,(p.stdout,p.stderr)
(r/'checkpoints/CP01/launcher-persistence.json').write_text(json.dumps(dict(passed=True,contexts=results,final_UI='defaults',final_FOV=90,scope='Real root CMD launchers; AA write, SH/BT context inheritance, isolated new user profiles only.'),indent=2)+'\n',encoding='utf-8')
print('PASS: CMD launchers and shared UI preferences AA -> SH -> BT')
