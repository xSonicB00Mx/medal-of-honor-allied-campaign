"""Head hits and quicksave persistence in a disposable CP08 profile."""
from pathlib import Path
import argparse,subprocess,shutil,re,json,hashlib
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--game',choices=['AA','SH','BT'],default='AA');ap.add_argument('--head-height',type=int,default=70);ap.add_argument('--head-close',action='store_true');ap.add_argument('--legacy-save',action='store_true');ap.add_argument('--death',action='store_true');ap.add_argument('--candidate',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/wound-regression'/a.run;num=['AA','SH','BT'].index(a.game);h=p/['main','mainta','maintt'][num];(h/'fixture').mkdir(parents=True,exist_ok=False)
runner=rt
if a.candidate:
 runner=p/'runner';runner.mkdir()
 for f in rt.glob('*.dll'):shutil.copy2(f,runner/f.name)
 for n in ['openmohaa.exe','cgame.dll','game.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,runner/n)
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text().replace('level.cp00_subject ai_off','level.cp00_subject ai_off\n    level.cp00_subject.health = 10000\n    level.cp00_subject.enablePain = 0')
(h/'fixture/base.scr').write_text(fixture)
start='devmap m2l1'
if num or a.legacy_save:
 source=r/(['','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'][num])
 if a.legacy_save:source=r/'profiles-local/wound-regression/fixed-aa/main/save/omconfig/quick.sav'
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
cmds=['wait 1500',start,'wait 4000','finishloadingscreen','wait 4000','god','script player exec fixture/base.scr','wait 1800','script player ammo pistol 100']
for height in ([a.head_height] if a.head_close else [50,65,70,75,80,85]):
 (h/f'fixture/aim{height}.scr').write_text(f'main:\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 {height} )) - ($player.origin + ( 0 0 64 )))\nend\n')
 cmds += [f'echo HEAD_TEST_HEIGHT_{height}',f'script player exec fixture/aim{height}.scr','wait 600','+attack','wait 100','-attack','wait 1200']
(h/'fixture/inspect.scr').write_text('main:\n    local.dir = vector_normalize (level.cp00_subject.origin - level.cp00_base)\n    $player.origin = level.cp00_subject.origin - local.dir * 65 + ( 0 0 10 )\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 70 )) - ($player.origin + ( 0 0 64 )))\nend\n')
if a.head_close:
 text=(h/'fixture/inspect.scr').read_text().replace('* 65','* 40')
 (h/'fixture/inspect.scr').write_text(text)
if a.death:
 (h/'fixture/kill.scr').write_text('main:\n    level.cp00_subject.health = 1\nend\n')
 cmds+=['script player exec fixture/kill.scr','script player exec fixture/aim50.scr','wait 600','+attack','wait 100','-attack','wait 3500']
 inspect=(h/'fixture/inspect.scr').read_text().replace('( 0 0 70 )','( 0 0 8 )')
 (h/'fixture/inspect.scr').write_text(inspect)
cmds+=['script player exec fixture/inspect.scr' ,'wait 1000','echo WOUNDS_BEFORE_SAVE','screenshot silent','savegame quick','wait 2200','echo WOUNDS_AFTER_SAVE','screenshot silent','wait 2200','savegame quick','wait 1200','loadgame quick','wait 4000','finishloadingscreen','wait 2200','echo WOUNDS_AFTER_LOAD','screenshot silent','wait 1800','echo WOUND_REGRESSION_DONE','quit']
if a.head_close:
 cmds=cmds[:-2]
 for angle in [35,-70]:
  name='turn'+str(angle)
  (h/f'fixture/{name}.scr').write_text(f'main:\n    level.cp00_subject.angles = level.cp00_subject.angles + ( 0 {angle} 0 )\nend\n')
  cmds += [f'script player exec fixture/{name}.scr','wait 1000','screenshot silent']
 cmds += ['echo WOUND_REGRESSION_DONE','quit']
(h/'test.cfg').write_text('\n'.join(cmds)+'\n')
settings=dict(com_target_game=num,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=0,ac_fx_debug=2,ac_body_wounds=1)
cmd=[str(runner/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','test.cfg'],cwd=rt,timeout=160)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'WOUND_REGRESSION_DONE' in log
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):Image.open(f).save(r/'artifacts-local'/f'Wound-{a.run}-{i}.png')
events=[l for l in log.splitlines() if any(t in l for t in ['AC_HIT ','AC_WOUND_ARCHIVE','AC_WOUND_REMOVED','HEAD_TEST','AC_WOUND id','WOUNDS_','AC_WOUND_OWNER'])]
print('\n'.join(events))

phases=[log.split('WOUNDS_BEFORE_SAVE',1)[1].split('WOUNDS_AFTER_SAVE',1)[0],log.split('WOUNDS_AFTER_SAVE',1)[1].split('Loading game...quick',1)[0],log.split('WOUNDS_AFTER_LOAD',1)[1]]
ids=lambda text:set(re.findall(r'AC_WOUND_DRAW[^\n]*?id=(\d+) branch=(\d+) seed=(\d+)',text))
preserved=bool(ids(phases[0])) and ids(phases[0])==ids(phases[1])==ids(phases[2])
patches=[int(v) for v in re.findall(r'AC_WOUND id=[^\n]*triangles=(\d+)',log)]
errors=[l for l in log.splitlines() if any(e in l for e in ['Script Error','Unknown command','Invalid event','compile error'])]
report=dict(game=a.game,death=a.death,exit=proc.returncode,preserved=preserved,patches=patches,head_projection=re.findall(r'AC_HEAD_PATCH[^\n]+',log),adapted=re.findall(r'AC_PATCH_FIT[^\n]+',log),archive=re.findall(r'AC_WOUND_ARCHIVE[^\n]+',log),errors=errors,binaries={n:hashlib.sha256((runner/n).read_bytes()).hexdigest() for n in ['openmohaa.exe','game.dll','cgame.dll']})
(r/'generated-local'/f'wound-{a.run}.json').write_text(json.dumps(report,indent=2)+'\n')
if a.death:assert 'CP00_DEATH_EVENT count=1' in log
if a.candidate:assert preserved and patches and all(0<n<=256 for n in patches) and not errors,report
print('PERSISTENCE',preserved)
