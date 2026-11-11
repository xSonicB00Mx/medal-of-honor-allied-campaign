"""Real single-player weapon shots; isolated profiles and instrumented live targets."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('--run-id',required=True);ap.add_argument('--regions',action='store_true');ap.add_argument('--death',action='store_true');ap.add_argument('--lod',action='store_true');ap.add_argument('--motion',action='store_true');ap.add_argument('--fps',type=int,default=60);ap.add_argument('--model',default='models/human/german_wehrmact_soldier.tik');ap.add_argument('--checkpoint',choices=['CP04','CP05'],default='CP04');ap.add_argument('--wall',action='store_true');ap.add_argument('--quick',action='store_true');ap.add_argument('--facing',choices=['front','rear','side'],default='front');ap.add_argument('--one-volley',action='store_true');ap.add_argument('--crouch',action='store_true');ap.add_argument('--revision',default='r1');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local'/(a.checkpoint+'-'+a.revision);p=r/'profiles-local'/(a.checkpoint+'-'+a.revision)/a.run_id
report=r/'checkpoints'/a.checkpoint
if a.revision!='r1':report=report/a.revision
report.mkdir(parents=True,exist_ok=True)
assert re.fullmatch('[A-Za-z0-9-]+',a.run_id) and not p.exists()
n,f,src={'AA':(0,'main',None),'SH':(1,'mainta','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':(2,'maintt','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[a.game]
h=p/f;(h/'cp00').mkdir(parents=True);start='map m2l1'
if src:
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2((r/src).with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text().replace('level.cp00_subject ai_off','level.cp00_subject ai_off\n    level.cp00_subject.health = 10000')
fixture=fixture.replace('models/human/german_wehrmact_soldier.tik',a.model)
if a.wall: fixture=(r/'tools/cp03_wall_fixture.scr').read_text().replace('models/human/german_wehrmact_soldier.tik',a.model)
fixture += '\n'
if a.facing!='front':
 fixture=fixture.replace('level.cp00_subject ai_off','level.cp00_subject.angles = level.cp00_subject.angles + ( 0 '+str(180 if a.facing=='rear' else 90)+' 0 )\n    level.cp00_subject ai_off')
(h/'cp00/base.scr').write_text(fixture)
commands=['seta ac_fx_debug 2','wait 1000',start,'wait 3000','finishloadingscreen','wait 3000','set ui_console 0','set developer 1','script player exec cp00/base.scr','wait 1500']
for state in ([1] if a.quick or a.one_volley else [0,1]):
 commands += [f'set ac_blood_mist {state}']
 for gun,ammo in ([('colt45','pistol')] if a.quick else [('colt45','pistol'),('mp40','smg'),('kar98','rifle'),('bar','mg')]):
  lateral,height=({'colt45':(12,45),'mp40':(-10,60),'kar98':(5,22),'bar':(0,50)}[gun] if a.regions else (0,50))
  (h/f'cp00/{gun}.scr').write_text(f'main:\n    $player give models/weapons/{gun}.tik\n    $player use models/weapons/{gun}.tik\n    local.left = angles_toleft level.cp00_subject.angles\n    local.aim = level.cp00_subject.origin + local.left * {lateral} + ( 0 0 {height} )\n    $player.viewangles = vector_toangles (local.aim - ($player.origin + ( 0 0 64 )))\nend\n')
  commands += [f'echo CP03_SHOT_{state}_{gun}',f'script player exec cp00/{gun}.scr',f'script player ammo {ammo} 100','wait 2300','+attack','wait 120','-attack','wait 800','+attack','wait 120','-attack','screenshot','wait 800']
commands += ['set ac_blood_mist 0','wait 1500','script player exec cp00/inspect.scr','wait 1000','screenshot','set ac_body_wounds 0','wait 500','screenshot','set ac_body_wounds 1','wait 500','screenshot']
if a.checkpoint=='CP05':
 commands += ['script player exec cp00/rear.scr','wait 700','screenshot','set ac_body_wounds 0','wait 500','screenshot','set ac_body_wounds 1','wait 500','screenshot','script player exec cp00/unrear.scr','wait 500']
if a.motion:
 commands += ['echo AC_TEST_MOTION','script player exec cp00/motion.scr','wait 700','script player exec cp00/inspect.scr','wait 100','screenshot','wait 1100','script player exec cp00/inspect.scr','wait 100','screenshot','script player exec cp00/restore.scr','wait 700','screenshot']
if a.crouch:
 commands += ['echo AC_TEST_CROUCH','script player exec cp00/crouch.scr','wait 500','script player exec cp00/inspect-crouch.scr','wait 100','screenshot','script player exec cp00/stand.scr','wait 1200','script player exec cp00/inspect.scr','wait 100','screenshot']
if a.lod:
 commands += ['echo AC_TEST_LOD','script player exec cp00/far.scr','wait 1200','screenshot','script player exec cp00/inspect.scr','wait 1200','screenshot']
if a.death:
 commands += ['echo AC_TEST_DEATH','script player exec cp00/kill.scr','wait 2300','+attack','wait 120','-attack','wait 1000','screenshot','wait 1500','script player exec cp00/lookdown.scr','wait 500','screenshot']
commands += ['wait 1500','script player exec cp00/lookdown.scr','wait 500','screenshot','savegame cp03_blood','wait 700','loadgame cp03_blood','wait 3000','finishloadingscreen','wait 1000','set developer 1','script player exec cp00/inspect.scr','wait 1000','screenshot','ac_blood_mist','ac_ui_options','wait 500','screenshot','set ac_blood_mist 0','popmenu 1','ac_blood_mist','wait 500','writeconfig omconfig.cfg','wait 200','echo CP03_DONE','quit']
(h/'cp00/lookdown.scr').write_text('main:\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 2 )) - ($player.origin + ( 0 0 64 )))\nend\n')
(h/'cp00/rear.scr').write_text('main:\n    level.cp05_saved_angles = level.cp00_subject.angles\n    level.cp00_subject.angles = level.cp05_saved_angles + ( 0 180 0 )\nend\n')
(h/'cp00/unrear.scr').write_text('main:\n    level.cp00_subject.angles = level.cp05_saved_angles\nend\n')
(h/'cp00/inspect.scr').write_text('main:\n    local.dir = vector_normalize (level.cp00_subject.origin - level.cp00_base)\n    $player.origin = level.cp00_subject.origin - local.dir * 70 + ( 0 0 12 )\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 50 )) - ($player.origin + ( 0 0 64 )))\nend\n')
(h/'cp00/inspect-crouch.scr').write_text((h/'cp00/inspect.scr').read_text().replace('( 0 0 50 )','( 0 0 20 )').replace('* 70','* 100'))
(h/'cp00/motion.scr').write_text('main:\n    level.cp04_angles = level.cp00_subject.angles\n    level.cp00_subject.angles = level.cp04_angles + ( 0 25 0 )\n    level.cp00_subject.enableEnemy = 0\n    level.cp00_subject.enablePain = 0\n    level.cp00_subject ai_on\n    level.cp00_subject anim_scripted walk_bored_forward\n    println (\"AC_TEST_ANIM=\" + level.cp00_subject.animname)\nend\n')
(h/'cp00/restore.scr').write_text('main:\n    level.cp00_subject.angles = level.cp04_angles\n    level.cp00_subject anim idle\n    wait 0.8\n    level.cp00_subject ai_off\n    level.cp00_subject.enablePain = 1\nend\n')
(h/'cp00/crouch.scr').write_text('main:\n    level.cp00_subject.enableEnemy = 0\n    level.cp00_subject.enablePain = 0\n    level.cp00_subject ai_on\n    level.cp00_subject anim_scripted walk_crouch_forward\n    println (\"AC_TEST_CROUCH_ANIM=\" + level.cp00_subject.animname)\nend\n')
(h/'cp00/stand.scr').write_text('main:\n    level.cp00_subject anim idle\n    wait 0.8\n    level.cp00_subject ai_off\n    level.cp00_subject.enablePain = 1\nend\n')
(h/'cp00/far.scr').write_text('main:\n    local.dir = vector_normalize (level.cp00_subject.origin - level.cp00_base)\n    $player.origin = level.cp00_base - local.dir * 420 + ( 0 0 32 )\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 50 )) - ($player.origin + ( 0 0 64 )))\nend\n')
(h/'cp00/kill.scr').write_text('main:\n    level.cp00_subject.health = 1\n    $player give models/weapons/colt45.tik\n    $player use models/weapons/colt45.tik\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 50 )) - ($player.origin + ( 0 0 64 )))\nend\n')
(h/'mist.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=960,com_maxfps=a.fps,com_maxfpsUnfocused=a.fps,cl_playintro=0,ac_fx_debug=2).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','mist.cfg'],cwd=rt,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for image in sorted((h/'screenshots').glob('*.tga')):
 out=image.with_suffix('.png');Image.open(image).save(out);images.append(out.relative_to(r).as_posix())
result=dict(game=a.game,exit=proc.returncode,completed='CP03_DONE' in log,engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cgame_sha256=hashlib.sha256((rt/'cgame.dll').read_bytes()).hexdigest(),images=images,geometry_events=re.findall(r'AC_HIT[^\r\n]+',log),mark_events=re.findall(r'AC_MARK (?:drop|rear)[^\r\n]+',log),mist_events=re.findall(r'AC_MIST[^\r\n]+',log),errors=[l for l in log.splitlines() if any(t in l for t in ['Script Error','Unknown command','Invalid event','compile error','command not available'])],saved_off='seta ac_blood_mist "0"' in (h/'configs/omconfig.cfg').read_text())
(report/f'{a.run_id}.json').write_text(json.dumps(result,indent=2))
result['rendered_mark_fragments']=list(map(int,re.findall(r'AC_MARK_FRAGMENTS (\d+)',log)))
(report/f'{a.run_id}.json').write_text(json.dumps(result,indent=2))
result['wounds']=re.findall(r'AC_WOUND [^\r\n]+',log)
result['received']=re.findall(r'AC_WOUND_RECEIVED[^\r\n]+',log)
result['drawn']=re.findall(r'AC_WOUND_DRAW[^\r\n]+',log)
result['states']=re.findall(r'AC_WOUND_STATE[^\r\n]+',log)
result['archive']=re.findall(r'AC_WOUND_ARCHIVE[^\r\n]+',log)
(report/f'{a.run_id}.json').write_text(json.dumps(result,indent=2))
result['body_blocks']=len(re.findall(r'AC_DROP_BODY_BLOCK status=1',log))
result['rear_body_blocks']=len(re.findall(r'AC_REAR_BODY_BLOCK status=1',log))
result['cache_unavailable']=len(re.findall(r'AC_(?:DROP|REAR)_BODY_BLOCK status=-1',log))
result['patch_budget_exceeded']=log.count('AC_PATCH_BUDGET')
result['intervals']=re.findall(r'AC_INTERVAL[^\r\n]+',log)
result['game_sha256']=hashlib.sha256((rt/'game.dll').read_bytes()).hexdigest()
result['test_conditions']=dict(animation_drive="scripted_no_enemy_follow_camera",crouch=a.crouch,facing=a.facing,fps=a.fps,model=a.model,regions=a.regions,motion=a.motion,lod=a.lod,death=a.death)
(report/f'{a.run_id}.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in result.items()}),flush=True)
assert result['completed'] and proc.returncode==0 and not result['errors'] and result['saved_off'] and len(result['mist_events'])>=(1 if a.quick else 4 if a.one_volley else 8)

if a.checkpoint=='CP05':
 from validate_wound_run import validate
 validate(report/f'{a.run_id}.json',True)
