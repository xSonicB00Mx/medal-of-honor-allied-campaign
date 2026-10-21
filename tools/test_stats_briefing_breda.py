"""Isolated native probes for campaign stats, live AA briefings and mounted Breda."""
from pathlib import Path
import argparse, shutil, subprocess, json, re, hashlib
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('kind',choices=['stats','briefing','breda','ab41']);ap.add_argument('--game',type=int,default=0);ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);a=ap.parse_args()
gun_model='models/vehicles/ab_turret_mini.tik' if a.kind=='ab41' else 'models/statweapons/It_W_Breda_gun.tik'
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/stats-briefing-breda'/a.run;h=p/['main','mainta','maintt'][a.game]
(h/'probe').mkdir(parents=True,exist_ok=False);b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for name in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/name,b/name)
for folder in ['main','mainta','maintt']:
 (p/folder).mkdir(exist_ok=True)
 for f in (r/'generated-local/campaign-stats/packages'/folder).glob('*.pk3'):shutil.copy2(f,p/folder/f.name)
cmd=['wait 1000']
if a.kind=='stats':
 for key,value in dict(ui_HeadShots='100.0',ui_TorsoShots='60.0',ui_LeftArmShots='14.7',ui_GroinShots='4.0',ui_LeftLegShots='5.3',ui_RightArmShots='100.0',ui_RightLegShots='0.0',ui_NumTime='01:23:45',ui_NumComplete='12 / 12',ui_NumShotsFired='12345',ui_NumHits='9876',ui_Accuracy='100.0',ui_PreferredWeapon='Breda',ui_NumHitsTaken='1234',ui_NumEnemysKilled='1234').items():cmd += [f'set {key} "{value}"']
 for menu in ['StatsScreen_Success','StatsScreen_Failed']+(['mission_success_1','mission_success_2','mission_success_3'] if a.game else []):
  cmd += ['hidemenu main 1',f'showmenu {menu} 1','wait 2200',f'ac_ui_report {menu}','screenshot silent',f'hidemenu {menu} 1']
elif a.kind=='briefing':
 for number in range(1,7):cmd += [f'map briefing/briefing{number}','wait 2800','finishloadingscreen','wait 1500','screenshot silent']
else:
 source=r/'profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'
 (h/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:shutil.copy2(source.with_suffix(ext),h/('save/omconfig/reference'+ext))
 fixture='''main:
 $player.health = 10000
 level.ac_gun = spawn models/statweapons/It_W_Breda_gun.tik targetname "ac_breda"
 level.ac_gun.origin = $player.origin + ( 0 0 48 )
 level.ac_gun.angles = $player.angles
 level.ac_gun setPlayerUsable 1
 level.ac_gun maxuseangle 360
 wait .2
 level.ac_gun doUse $player
 wait .5
 local.dir = angles_toforward level.ac_gun.angles
 local.barrel = level.ac_gun gettagposition "tag_barrel"
 level.ac_target = spawn models/human/german_wehrmact_soldier.tik origin (local.barrel + local.dir * 160 - ( 0 0 48 )) targetname "ac_target"
 level.ac_target ai_off
 level.ac_target gravity 0
 level.ac_target.health = 10000
 level.ac_target.enablePain = 0
 level.ac_target.angles = level.ac_gun.angles + ( 0 180 0 )
 wait .5
 println "AC_BREDA_BEGIN"
 for (local.i = 0; local.i < 8; local.i++)
 {
  level.ac_gun shoot
  wait .15
 }
 println ("AC_BREDA_HEALTH=" + level.ac_target.health)
 println "AC_BREDA_END"
end
'''
 (h/'probe/breda.scr').write_text(fixture.replace('models/statweapons/It_W_Breda_gun.tik',gun_model))
 cmd+=['loadgame reference','wait 4000','finishloadingscreen','wait 1500','script player exec probe/breda.scr','wait 1700','screenshot silent','wait 2200','screenshot silent','savegame breda','wait 1000','loadgame breda','wait 3500','finishloadingscreen','wait 800','screenshot silent']
cmd+=['echo AC_PROBE_DONE','quit'];(h/'test.cfg').write_text('\n'.join(cmd)+'\n')
settings=dict(com_target_game=a.game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=int(a.kind in ['breda','ab41']),cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=a.width,r_customheight=a.height,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=0,ac_fx_debug=2,ac_body_wounds=1,ac_world_blood=1,ac_blood_mist=1,g_subtitle=1)
args=[str(b/'openmohaa.exe')]
for key,value in settings.items():args+=['+set',key,str(value)]
proc=subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=120)
log=(h/'qconsole.log').read_text(encoding='latin1');errors=[s for s in log.splitlines() if any(x in s for x in ['Script Error','command not available','Unknown command','Invalid event','Failed to find resource',"Couldn't find menu"])]
report=dict(engine_sha256=hashlib.sha256((b/'openmohaa.exe').read_bytes()).hexdigest(),game_sha256=hashlib.sha256((b/'game.dll').read_bytes()).hexdigest(),kind=a.kind,game=a.game,exit=proc.returncode,done='AC_PROBE_DONE' in log,errors=errors)
if a.kind in ['breda','ab41']:
 hits=re.findall(r'AC_HIT[^\n]+weapon='+re.escape(gun_model)+r'[^\n]+',log,re.I)
 report.update(hits=hits,drops=len(re.findall('AC_DROPS',log)),mist=bool(re.search(r'AC_MIST[^\n]+enabled=1[^\n]+authorized=1',log)),marks='AC_MARK drop' in log,archives=re.findall(r'AC_WOUND_ARCHIVE (save|load) count=(\d+)',log),target_health=re.findall(r'AC_BREDA_HEALTH=([\d.]+)',log))
for f in (h/'screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
assert proc.returncode==0 and report['done'] and not errors
if a.kind in ['breda','ab41']:
 assert len(hits)==(16 if a.kind=='ab41' else 8) and all('group=4' in hit for hit in hits)
 assert report['drops'] and report['mist'] and report['marks']
 count='32' if a.kind=='ab41' else '16'
 assert ('save',count) in report['archives'] and ('load',count) in report['archives']
 if a.kind=='ab41': assert report['target_health']==['7120.000']
