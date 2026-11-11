"""Verify collection of the BT health and ammunition drops with ordinary movement."""
from pathlib import Path
import json,re,shutil,subprocess
from inventory_cp00 import sha,save
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP00a-r1'
report=r/'checkpoints/CP00a/cp00a-middle-v2-BT.json';series=json.loads(report.read_text(encoding='utf-8'));assert series['completed'] and not series['errors']
id,model=next((i,m) for i,m in series['steps'][-1]['new_after_death'] if 'mp40' in m)
profile=r/'profiles-local/CP00a-r1/pickup-BT-v3';home=profile/'maintt';assert not profile.exists()
(home/'cp00').mkdir(parents=True);(home/'save/omconfig').mkdir(parents=True)
refs=[]
for ext in ['.sav','.ssv','.tga']:
 source=r/('profiles-local/CP00a-r1/cp00a-middle-v2-BT/maintt/save/omconfig/cp00_after_series'+ext)
 e=next(e for e in series['evidence'] if e['path']==source.relative_to(r).as_posix());assert sha(source)==e['sha256']
 shutil.copy2(source,home/('save/omconfig/cp00_reference'+ext));refs.append(e)
before='main:\n    $player hurt 20\n    $player give models/weapons/mp40.tik\n    $player ammo smg -9999\n    $player use models/weapons/mp40.tik\n    println ("CP00_PICKUP_BEFORE_AMMO " + level.playerammo_smg)\n    println ("CP00_PICKUP_BEFORE_HEALTH " + $player.health)\n    println ("CP00_PICKUP_BEFORE_ORIGIN " + $player.origin)\n    level.cp00_pickup = getentbyentnum DROP_ID\n    if (level.cp00_pickup != NULL)\n    {\n        if (level.cp00_pickup.model == "DROP_MODEL")\n        {\n            println ("CP00_PICKUP_ITEM " + level.cp00_pickup.model + " origin=" + level.cp00_pickup.origin)\n            local.delta = level.cp00_pickup.origin - $player.origin\n            $player.viewangles = vector_toangles local.delta\n            setcvar cp00_pickup_next "exec cp00/walk.cfg"\n        }\n    }\nend\n'
before=before.replace('$player give models/weapons/mp40.tik', '$player takeall\n    $player give models/weapons/mp40.tik').replace('    $player ammo smg -9999\n','').replace('println ("CP00_PICKUP_BEFORE_AMMO " + level.playerammo_smg)', 'println "CP00_INV_BEFORE"\n    $player listinventory\n    println "CP00_INV_END"')
(home/'cp00/before.scr').write_text(before.replace('DROP_ID',str(id)).replace('DROP_MODEL',model),encoding='ascii')
(home/'cp00/after.scr').write_text('main:\n    println "CP00_INV_AFTER"\n    $player listinventory\n    println "CP00_INV_END"\n    println ("CP00_PICKUP_AFTER_HEALTH " + $player.health)\n    println ("CP00_PICKUP_AFTER_ORIGIN " + $player.origin)\n    if (level.cp00_pickup == NULL)\n        println "CP00_PICKUP_ITEM_REMOVED"\n    else\n        println ("CP00_PICKUP_REMAINING_MODEL " + level.cp00_pickup.model)\nend\n',encoding='ascii')
(home/'cp00/walk.cfg').write_text('\n'.join(['screenshot','+forward','wait 950','-forward','wait 700','script player exec cp00/after.scr','wait 300','screenshot','savegame cp00_after_pickup','wait 1000','loadgame cp00_after_pickup','wait 2000','finishloadingscreen','wait 800','script player exec cp00/after.scr','wait 500','echo CP00_PICKUP_DONE','quit'])+'\n',encoding='ascii')
(home/'pickup.cfg').write_text('\n'.join(['set cp00_pickup_next "echo CP00_PICKUP_ABORTED; quit"','wait 1000','loadgame cp00_reference','wait 3000','finishloadingscreen','wait 1000','script player exec cp00/before.scr','wait 500','vstr cp00_pickup_next'])+'\n',encoding='ascii')
settings=dict(com_target_game='2',fs_basepath=str(rt),fs_homepath=str(profile),fs_steampath=str(rt),fs_gogpath=str(rt),fs_microsoftstorepath=str(rt),net_enabled='0',logfile='2',developer='1',cheats='1',r_fullscreen='0',r_mode='-1',r_customwidth='1280',r_customheight='960',com_maxfps='60',com_maxfpsUnfocused='60',cl_playintro='0',ui_console='0',cg_fov='90',skill='1')
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,v]
proc=subprocess.Popen(cmd+['+exec','pickup.cfg'],cwd=rt)
try:proc.wait(timeout=45)
except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=10);raise
log=(home/'qconsole.log').read_text(encoding='latin1')
health_before=re.findall(r'CP00_PICKUP_BEFORE_HEALTH ([0-9.]+)',log);health_after=re.findall(r'CP00_PICKUP_AFTER_HEALTH ([0-9.]+)',log)
result=dict(candidate='CP00a-r1',game='BT',completed='CP00_PICKUP_DONE' in log,exit_code=proc.returncode,health_before=health_before,health_after=health_after,item_removed='CP00_PICKUP_ITEM_REMOVED' in log,records=[l.split('] ',1)[-1] for l in log.splitlines() if 'CP00_PICKUP_' in l],errors=[l.split('] ',1)[-1] for l in log.splitlines() if 'Script Error' in l or 'Unknown command' in l],scope='Normal walking toward the health item dropped in the preceding series. Player takes 20 diagnostic damage and has inventory cleared and is given an MP40 with its normal starting ammunition; normal walking collects original items, no direct item-use callback. Save/load between death and pickup.',reference_save=refs,series_report_sha256=sha(report),visual_check='PENDING',evidence=[dict(path=p.relative_to(r).as_posix(),sha256=sha(p)) for p in sorted(profile.rglob('*')) if p.is_file()])
save(r/'checkpoints/CP00a/pickup-BT-v3.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['evidence','reference_save']},indent=2),flush=True)
assert result['completed'] and proc.returncode==0 and not result['errors']
assert health_before and health_after and result['item_removed']

before_ammo=re.findall(r"CP00_INV_BEFORE[\s\S]*?'smg' : '([0-9]+)'[\s\S]*?CP00_INV_END",log)
after_ammo=re.findall(r"CP00_INV_AFTER[\s\S]*?'smg' : '([0-9]+)'[\s\S]*?CP00_INV_END",log)
assert len(after_ammo)==2 and after_ammo[0]==after_ammo[1]
assert before_ammo and float(after_ammo[0])>float(before_ammo[0])
assert len(health_after)==2 and health_after[0]==health_after[1]
result['ammo_before']=before_ammo;result['ammo_after']=after_ammo;result['passed']=True;result['scope']='Normal walking toward the final MP40 drop; inventory cleared before setup. Real reserve inventory sampled before/after and after process save/load. Health collection verified separately by v2.';save(r/'checkpoints/CP00a/pickup-BT-v3.json',result);print('Ammo pickup:',before_ammo,after_ammo,'Health:',health_before,health_after)
