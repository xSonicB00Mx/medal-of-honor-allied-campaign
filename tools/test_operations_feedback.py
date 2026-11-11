"""Isolated Operations UI, context restart and native replay completion regression.
Usage: test_operations_feedback.py menus|replay|finish|hold|baseline unique-run
finish uses an on-foot AA final map and a native bsptransition fixture; it is not
a claim of a complete manual mission playthrough. baseline records existing BT diagnostics.
"""
from pathlib import Path
import sys,shutil,subprocess,time,re,json
from PIL import Image
R=Path(__file__).resolve().parents[1];case=sys.argv[1];p=R/'profiles-local/operations-feedback'/sys.argv[2];p.mkdir(parents=True,exist_ok=False)
rt=R/'runtime-local/CP08-r1';binary=p/'bin';binary.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,binary/f.name)
for n in ['openmohaa.exe','game.dll']:shutil.copy2((rt if case=='baseline' else R/'build-local/cp00-r3/RelWithDebInfo')/n,binary/n)
state='ACPROG1 4095 12 keep\n';(p/'ac_progress.dat').write_text(state)
for folder in ['main','mainta','maintt']:
 h=p/folder;(h/'probe').mkdir(parents=True);(h/'save/omconfig').mkdir(parents=True)
 (h/'save/omconfig/keep.sav').write_bytes(b'PRESERVE')
 (h/'probe/end.scr').write_text('main:\n $player nodamage\n bsptransition ac_campaign_end\nend\n')
 (h/'ac_context_ready.cfg').write_text('wait 6500\nfinishloadingscreen\nset autopaused 0\nset developer 1\necho AC_DIFFICULTY_BEGIN\nskill\ng_skill\nac_progress_report\nscript player exec probe/end.scr\nwait 7000\n+attack\nwait 500\n-attack\nwait 2000\nac_progress_report\nskill\necho AC_FEEDBACK_DONE\nquit\n')
(p/'main/ac_preferences.cfg').write_text('seta skill 1\nseta g_skill 1\n')
cmds=['wait 1000','ac_campaign 0 0 2','wait 700','screenshot silent']
if case in ['replay','baseline']:cmds+=['ac_mission 11']
elif case=='hold':pass
elif case=='finish':cmds=['map m2l3','exec ac_context_ready.cfg']
else:cmds+=['ac_campaign 3 0 0','wait 500','screenshot silent','ac_campaign 8 1 1','wait 500','screenshot silent','ac_level_list','wait 500','screenshot silent','echo AC_FEEDBACK_DONE','quit']
(p/'main/probe.cfg').write_text('\n'.join(cmds)+'\n')
settings=dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,autopaused=0,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1600,r_customheight=900,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1)
if case=='finish':settings.update(com_target_game=0,ac_operation=1,ac_replay=1,ac_expected_map='m2l3',ac_campaign_skill=1,ac_campaign_g_skill=1,skill=2,g_skill=2)
if case=='replay':
 for folder in ['main','mainta','maintt']:
  f=p/folder/'ac_context_ready.cfg';f.write_text(f.read_text().replace('script player exec probe/end.scr','ac_return_main'))
if case=='finish':
 (p/'main/probe/end.scr').write_text('main:\n $player nodamage\n bsptransition briefing/briefing3\nend\n')
if case=='finish':
 f=p/'main/ac_context_ready.cfg';f.write_text(f.read_text().split('script player exec probe/end.scr')[0]+'script player exec probe/end.scr\n')
cmd=[str(binary/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.Popen(cmd+['+exec','probe.cfg'],cwd=rt)
if case=='hold':print('Interactive profile:',p,flush=True);proc.wait(timeout=270);sys.exit()
children=set();text=''
for i in range(150):
 time.sleep(1);text='\n'.join(f.read_text(encoding='latin1') for f in p.glob('*/qconsole.log'))
 children.update(map(int,re.findall(r'AC_CONTEXT_RESTART[^\n]*child=(\d+)',text)))
 if ('AC_REPLAY_COMPLETE' if case=='finish' else 'AC_FEEDBACK_DONE') in text:break
assert ('AC_REPLAY_COMPLETE' if case=='finish' else 'AC_FEEDBACK_DONE') in text
if case=='finish':proc.terminate();proc.wait(timeout=5)
assert (p/'ac_progress.dat').read_text()==state
for folder in ['main','mainta','maintt']:assert (p/folder/'save/omconfig/keep.sav').read_bytes()==b'PRESERVE'
assert not any(x in text for x in ['Unknown command','UI EXCEPTION'])
errors=[x.split('Script Error : ',1)[-1] for x in text.splitlines() if 'Script Error :' in x]
(p/'script-errors.json').write_text(json.dumps(errors))
for f in p.glob('*/screenshots/*.tga'):Image.open(f).save(f.with_suffix('.png'))
if case=='baseline':print('BASELINE',errors);sys.exit()
if case in ['replay','finish']:
 assert ('AC_REPLAY_COMPLETE' if case=='finish' else 'AC_REPLAY_RETURN_MAIN') in text
 segment=text.split('AC_DIFFICULTY_BEGIN',1)[1]
 assert '"skill" is:"2"' in segment
 assert 'replay=1' in segment
 if case=='replay':assert 'replay=0' in segment
else:
 ui=(p/'main/ui/ac_campaign_operations.urc').read_text()
 assert 'Current operation' not in ui and 'Next mission difficulty' in ui
 for block in re.findall(r'resource\s+Button\s*\{([^}]+)\}',ui):
  name=re.search(r'name "([^"]+)"',block)[1];cmd=re.search(r'stuffcommand "([^"]+)"',block)[1]
  if name.startswith(('mission_','marker_','difficulty_','region_')):assert cmd.startswith('ac_campaign '),(name,cmd)
 assert 'rect 24 16 912 34' in (p/'main/ui/ac_level_list.urc').read_text()
print('PASS',case,p,flush=True)
