"""Isolated native corpse shots, persistence and world-blood lifetime evidence."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('game',choices=['AA','SH','BT']);ap.add_argument('--run-id',required=True);ap.add_argument('--map',default='m2l1');ap.add_argument('--model');ap.add_argument('--existing',action='store_true');ap.add_argument('--negative',action='store_true');ap.add_argument('--mist',type=int,default=1);ap.add_argument('--lifetime',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP05a-r1';p=r/'profiles-local/CP05a-r1'/a.run_id
assert re.fullmatch('[A-Za-z0-9-]+',a.run_id) and not p.exists()
n,f,src={'AA':(0,'main',None),'SH':(1,'mainta','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':(2,'maintt','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[a.game]
h=p/f;(h/'probe').mkdir(parents=True);start='map '+a.map
if src:
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2((r/src).with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text().replace('    level.cp00_subject ai_off','    level.cp00_subject ai_off\n    level.cp00_subject.health = 1')
if a.model:
 fixture=fixture.replace('models/human/german_wehrmact_soldier.tik',a.model)
 fixture='\n'.join(l for l in fixture.splitlines() if not any(x in l for x in [' threatbias ',' ai_off',' thread deathwatch','level.cp00_subject.health =']))
 fixture=fixture.replace(' + \" anim=\" + level.cp00_subject.animname','')
 fixture=fixture.replace(' gun "Mauser KAR 98K"','').replace('spawn '+a.model,'spawn Animate model '+a.model)
 fixture=fixture.replace('    level.cp00_subject.origin = level.cp00_target','    level.cp00_subject anim idle\n    level.cp00_subject.origin = level.cp00_target')
if a.existing:
 fixture='main:\n    level.cp00_deaths = 0\n    level.cp00_subject = NULL\n    for (local.i = 1; local.i < 1022; local.i++)\n    {\n        local.e = getentbyentnum local.i\n        if (local.e != NULL)\n        {\n            if (local.e.model == "'+a.model+'")\n            {\n                level.cp00_subject = local.e\n                break\n            }\n        }\n    }\n    level.cp00_base = level.cp00_subject.origin\n    $player give models/weapons/colt45.tik\n    $player use models/weapons/colt45.tik\nend\n\nsnapshot local.label:'+fixture.split('snapshot local.label:',1)[1]
(h/'probe/base.scr').write_text(fixture)
(h/'probe/snapshot.scr').write_text('main:\n'+fixture.split('snapshot local.label:',1)[1].replace('local.label','\"check\"'))
(h/'probe/aim.scr').write_text('main:\n    local.aim = level.cp00_subject gettagposition "Bip01 Spine2"\n    println ("AC_TEST_AIM=" + local.aim)\n    $player.origin = level.cp00_subject.origin + ( -45 -45 35 )\n    $player.viewangles = vector_toangles (local.aim - ($player.origin + ( 0 0 64 )))\nend\n')
(h/'probe/ground.scr').write_text('main:\n    $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 2 )) - ($player.origin + ( 0 0 64 )))\nend\n')
if a.model and ('/static/' in a.model or '/body_' in a.model):
 (h/'probe/aim.scr').write_text((h/'probe/aim.scr').read_text().replace('level.cp00_subject gettagposition \"Bip01 Spine2\"','level.cp00_subject.origin + ( 0 0 10 )'))
commands=['wait 1000',start,'wait 3000','finishloadingscreen','wait 2500','set developer 1','script player exec probe/base.scr','wait 2200','script player ammo pistol 100']
if not a.model:commands+=['echo AC_PHASE_KILL','+attack','wait 80','-attack','wait 1700','screenshot']
commands+=['echo AC_PHASE_CORPSE','script player exec probe/aim.scr','wait 600','screenshot']
for gun,ammo in [('colt45','pistol'),('mp40','smg'),('kar98','rifle'),('bar','mg')]:
 commands += [f'echo AC_GROUP_{gun}',f'script player give models/weapons/{gun}.tik',f'script player use models/weapons/{gun}.tik',f'script player ammo {ammo} 100','wait 1800','script player exec probe/aim.scr','wait 300','+attack','wait 80','-attack','wait 150','screenshot','wait 700']
commands+=['script player exec probe/snapshot.scr','savegame corpse','wait 500','loadgame corpse','wait 3000','finishloadingscreen','wait 700','script player exec probe/aim.scr','wait 500','screenshot','echo AC_PHASE_RELOAD','+attack','wait 80','-attack','wait 500','screenshot','echo AC_PHASE_DISABLED','set ac_corpse_effects 0','wait 300','+attack','wait 80','-attack','wait 700','script player exec probe/snapshot.scr','set ac_corpse_effects 1','script player exec probe/ground.scr','wait 300','screenshot']
if a.lifetime:commands+=['wait 12000','screenshot','wait 14000','screenshot','wait 6000','screenshot']
if a.negative:
 (h/'probe/remove.scr').write_text('main:\n    level.cp00_subject remove\nend\n')
 (h/'probe/occluded.scr').write_text("""main:
    local.eye = $player.origin + ( 0 0 64 )
    local.dirs[1] = ( 1 0 0 )
    local.dirs[2] = ( 0 1 0 )
    local.dirs[3] = ( -1 0 0 )
    local.dirs[4] = ( 0 -1 0 )
    for (local.i = 1; local.i <= 4; local.i++)
    {
        local.goal = local.eye + local.dirs[local.i] * 400
        local.hit = trace local.eye local.goal 1
        local.dist = vector_length (local.hit - local.eye)
        if ((local.dist > 20) && (local.dist < 390))
        {
            level.cp00_subject.origin = local.hit + local.dirs[local.i] * 180 - ( 0 0 8 )
            $player.viewangles = vector_toangles ((level.cp00_subject.origin + ( 0 0 8 )) - local.eye)
            println ("AC_OCCLUDED_READY wall=" + local.hit + " body=" + level.cp00_subject.origin)
            end
        }
    }
end
""")
 commands+=['echo AC_PHASE_OCCLUDED','script player exec probe/occluded.scr','wait 700','+attack','wait 180','-attack','wait 800','screenshot','echo AC_PHASE_REMOVED','script player exec probe/remove.scr','wait 500']
commands+=['ac_ui_options','wait 500','screenshot','set ac_corpse_effects 0','writeconfig omconfig.cfg','echo AC_TEST_DONE','quit'];(h/'test.cfg').write_text('\n'.join(commands)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=960,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_fx_debug=2,ac_world_blood=1,ac_body_wounds=1,ac_blood_mist=a.mist,ac_corpse_effects=1).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','test.cfg'],cwd=rt,timeout=140)
log=(h/'qconsole.log').read_text(encoding='latin1');images=[]
for im in sorted((h/'screenshots').glob('*.tga')):
 out=im.with_suffix('.png');Image.open(im).save(out);images.append(out.relative_to(r).as_posix())
result=dict(game=a.game,map=a.map,model=a.model,completed='AC_TEST_DONE' in log,exit=proc.returncode,binaries={x:hashlib.sha256((rt/x).read_bytes()).hexdigest() for x in ['openmohaa.exe','game.dll','cgame.dll']},images=images,events=re.findall(r'AC_(?:HIT|CORPSE|CONTEXT|MARK|WOUND|PHASE|GROUP)[^\r\n]*',log),deaths=re.findall(r'CP00_DEATH_EVENT[^\r\n]*',log),errors=[l for l in log.splitlines() if any(x in l for x in ['Script Error','Unknown command','Invalid event','compile error'])])
(r/'checkpoints/CP05a'/f'{a.run_id}.json').write_text(json.dumps(result,indent=2))
print(json.dumps({**result,'images':len(images),'events':len(result['events'])}),flush=True)
assert result['completed'] and proc.returncode==0 and not result['errors']
