"""Exercise independent live effect switches and a policy-excluded shotgun."""
import hashlib,json,re,subprocess,shutil
from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP05-r1';p=r/'profiles-local/CP05-r1/options';h=p/'main'
assert not p.exists();(h/'cp00').mkdir(parents=True)
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text().replace('german_wehrmact_soldier','german_misc_worker').replace('level.cp00_subject ai_off','level.cp00_subject ai_off\n    level.cp00_subject.health = 10000')
(h/'cp00/base.scr').write_text(fixture)
cases=[('ALL',1,1,1,'colt45','pistol'),('WORLD',0,1,0,'colt45','pistol'),('BODY',0,0,1,'colt45','pistol'),('MIST',1,0,0,'colt45','pistol'),('NONE',0,0,0,'colt45','pistol'),('SHOTGUN',1,1,1,'shotgun','shotgun')]
commands=['seta ac_fx_debug 2','wait 1000','map m2l1','wait 3000','finishloadingscreen','wait 3000','set developer 1','script player exec cp00/base.scr','wait 1500']
for name,mist,world,body,gun,ammo in cases:
 (h/f'cp00/{name}.scr').write_text(f'main:\n    $player give models/weapons/{gun}.tik\n    $player use models/weapons/{gun}.tik\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 50 )) - ($player.origin + ( 0 0 64 )))\n    println ("AC_OPTION_HEALTH_{name}=" + level.cp00_subject.health)\nend\n')
 commands += [f'seta ac_blood_mist {mist}',f'seta ac_world_blood {world}',f'seta ac_body_wounds {body}','wait 2400',f'echo AC_OPTION_BEGIN_{name}',f'script player exec cp00/{name}.scr',f'script player ammo {ammo} 100','wait 2300','+attack','wait 120','-attack','wait 2500','screenshot',f'echo AC_OPTION_END_{name}']
commands+=['seta ac_blood_mist 0','seta ac_world_blood 0','seta ac_body_wounds 0','writeconfig omconfig.cfg','wait 300','echo AC_OPTIONS_DONE','quit']
(h/'options.cfg').write_text('\n'.join(commands)+'\n')
settings=dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=960,com_maxfps=60,cl_playintro=0)
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','options.cfg'],cwd=rt,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_OPTIONS_DONE' in log
assert not any(t in log for t in ('Script Error','Unknown command','Invalid event'))
results=[]
for name,mist,world,body,gun,ammo in cases:
 part=log.split(f'AC_OPTION_BEGIN_{name}',1)[1].split(f'AC_OPTION_END_{name}',1)[0]
 marks=re.findall(r'AC_MARK (?:drop|rear)[^\r\n]*',part);wounds=re.findall(r'AC_WOUND id=[^\r\n]*',part);clouds=re.findall(r'AC_MIST[^\r\n]*',part)
 assert clouds,(name,'no actual hit')
 if name=='SHOTGUN':
  assert not marks and not wounds and 'AC_HIT' not in part
  assert all('enabled=0' in x and 'authorized=0' in x for x in clouds)
 else:
  assert bool(wounds)==bool(body) and bool(marks)==bool(world),(name,wounds,marks)
  assert all(f'enabled={mist}' in x and 'authorized=1' in x for x in clouds),(name,clouds)
 results.append(dict(case=name,marks=marks,wounds=wounds,clouds=clouds))
config=(h/'configs/omconfig.cfg').read_text()
assert all(f'seta {c} "0"' in config for c in ('ac_blood_mist','ac_world_blood','ac_body_wounds'))
# A separate process reads the archived values before any override.
shutil.copy2(h/'qconsole.log',h/'options-first-process.log')
(h/'restart.cfg').write_text('ac_blood_mist\nac_world_blood\nac_body_wounds\necho AC_RESTART_DONE\nquit\n')
restart=subprocess.run(cmd+['+exec','restart.cfg'],cwd=rt,timeout=30)
restartlog=(h/'qconsole.log').read_text(encoding='latin1')
assert restart.returncode==0 and 'AC_RESTART_DONE' in restartlog
assert all(float(re.search(r'"'+c+r'" is:\s*"([^"^]*)',restartlog).group(1))==0 for c in ('ac_blood_mist','ac_world_blood','ac_body_wounds')),restartlog[-2500:]
images=[]
for im in sorted((h/'screenshots').glob('*.tga')):
 out=im.with_suffix('.png');Image.open(im).save(out);images.append(out.relative_to(r).as_posix())
result=dict(complete=True,cases=results,persisted_after_process_restart=True,images=images,binaries={f:hashlib.sha256((rt/f).read_bytes()).hexdigest() for f in ('openmohaa.exe','cgame.dll','game.dll')})
(r/'checkpoints/CP05/options.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)
