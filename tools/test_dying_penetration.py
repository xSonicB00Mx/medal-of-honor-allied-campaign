"""Native weapon queries during an actual actor death animation; isolated fixture."""
import argparse,json,re,subprocess,hashlib,shutil
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--fx',type=int,default=1);ap.add_argument('--paired',action='store_true');ap.add_argument('--pelvis',action='store_true');ap.add_argument('--weapon',default='colt45',choices=['colt45','mp40','kar98','bar']);ap.add_argument('--game',default='AA',choices=['AA','SH','BT']);a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/CP08-r1'/a.run
n,f,src={'AA':(0,'main',None),'SH':(1,'mainta','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':(2,'maintt','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[a.game]
h=p/f;assert not p.exists();(h/'probe').mkdir(parents=True);start='map m2l1'
if src:
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2((r/src).with_suffix(ext),h/('save/omconfig/reference'+ext))
 start='loadgame reference'
s=(r/'tools/cp00_baseline_fixture.scr').read_text().replace('level.cp00_subject ai_off','level.cp00_subject ai_off\n    level.cp00_subject.health = 1')
s=s.replace('models/weapons/colt45.tik',f'models/weapons/{a.weapon}.tik')
s=s.replace('    level.cp00_deaths++','    level.cp00_deaths++\n    self thread penetration')
s+='''
penetration:
    $player.origin = self.origin + ( -60 -60 40 )
    local.rear = spawn models/human/german_wehrmact_soldier.tik targetname "ac_rear"
    local.rear ai_off
    local.rear threatbias ignoreme
    local.rear.health = 10000
    local.rear.angles = self.angles
    local.weapon = $player getactiveweap 0
    local.weapon bulletspread 0 0 0 0
    for (local.i = 0; local.i < 12; local.i++)
    {
        local.aim = self gettagposition "Bip01 Spine2"
        local.aim = local.aim - ( 0 0 8 )
        local.eye = $player.origin + ( 0 0 64 )
        local.dir = vector_normalize (local.aim - local.eye)
        local.rear.origin = local.aim + local.dir * 100 - ( 0 0 50 )
        $player.viewangles = vector_toangles local.dir
        wait 0.05
        println ("AC_DYING_SHOT " + local.i + " front=" + self.health + " rear=" + local.rear.health + " anim=" + self.animname)
        local.weapon shoot
        wait 0.05
        println ("AC_REAR_HEALTH " + local.i + " " + local.rear.health)
    }
    println ("AC_DYING_DONE deaths=" + level.cp00_deaths + " front=" + self.health + " rear=" + local.rear.health)
end
'''
if a.pelvis:s=s.replace('gettagposition "Bip01 Spine2"','gettagposition "Bip01 Pelvis"').replace('local.aim - ( 0 0 8 )','local.aim + ( 0 0 4 )')
if a.paired:
 s=s.replace('        local.weapon shoot','''        local.before = local.rear.health
        setcvar ac_corpse_effects 1
        local.weapon shoot
        local.on = local.before - local.rear.health
        local.before = local.rear.health
        setcvar ac_corpse_effects 0
        local.weapon shoot
        local.off = local.before - local.rear.health
        println ("AC_PAIR_DAMAGE on=" + local.on + " off=" + local.off)
        setcvar ac_corpse_effects 1''')
(h/'probe/base.scr').write_text(s)
commands=['wait 1000',start,'wait 3000','finishloadingscreen','wait 1500','script player exec probe/base.scr','wait 4500','script player ammo '+dict(colt45='pistol',mp40='smg',kar98='rifle',bar='mg')[a.weapon]+' 100','+attack','wait 80','-attack','wait 150','screenshot silent','wait 400','screenshot silent','wait 500','screenshot silent','wait 2000','screenshot silent','echo AC_PROBE_EXIT','quit']
(h/'probe.cfg').write_text('\n'.join(commands)+'\n');cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=n,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_fx_debug=4,ac_corpse_effects=a.fx,ac_blood_mist=a.fx,ac_world_blood=a.fx,ac_body_wounds=a.fx).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=65);log=(h/'qconsole.log').read_text(encoding='latin1')
images=[]
for file in sorted((h/'screenshots').glob('*.tga')):Image.open(file).save(file.with_suffix('.png'));images.append(file.with_suffix('.png').relative_to(r).as_posix())
events=re.findall(r'(?:AC_(?:PAIR_DAMAGE|DYING|REAR_HEALTH|BULLET_PASS|CORPSE|CONTEXT|HIT|WOUND|MIST)|CP00_DEATH_EVENT)[^\r\n]*',log)
errors=[l for l in log.splitlines() if any(t in l for t in ['Script Error','Unknown command','Invalid event','compile error'])]
result=dict(game=a.game,weapon=a.weapon,fx=a.fx,exit=proc.returncode,completed='AC_DYING_DONE' in log,events=events,errors=errors,images=images,binaries={x:hashlib.sha256((rt/x).read_bytes()).hexdigest() for x in ['openmohaa.exe','game.dll','cgame.dll']})
(r/'checkpoints/CP08'/(a.run+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({**result,'events':len(events)}))
assert not errors and proc.returncode==0 and result['completed']
if a.paired:
 pairs=re.findall(r'AC_PAIR_DAMAGE on=([\d.]+) off=([\d.]+)',log)
 assert len(pairs)==12 and all(x==y for x,y in pairs) and any(float(x)>0 for x,y in pairs)
 assert 'AC_BULLET_PASS ' in log and 'AC_CORPSE ' in log
 assert 'AC_DYING_DONE deaths=1 front=0.000' in log
