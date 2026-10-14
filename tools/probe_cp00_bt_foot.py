"""Check normal BT foot control and shooting before creating combat fixtures."""
import argparse,json,re,subprocess
from pathlib import Path
from inventory_cp00 import sha,save
ap=argparse.ArgumentParser()
ap.add_argument('--run-id',default='r4-bt-foot-e2l2')
args=ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+',args.run_id)
r=Path(__file__).resolve().parents[1]
rt=r/'runtime-local/CP00-r4';profile=r/'profiles-local/CP00-r4'/args.run_id;home=profile/'maintt'
assert not profile.exists()
(home/'cp00').mkdir(parents=True)
for label in ['before','moved','fired']:
    script='main:\n    println "CP00_FOOT_STAGE LABEL"\n    println ("CP00_ORIGIN " + $player.origin)\n    println ("CP00_HEALTH " + $player.health)\n    println ("CP00_BRIEFOVER " + level.BriefOver)\n    if ($player.vehicle == NULL)\n        println "CP00_NO_VEHICLE"\n    if ($player.turret == NULL)\n        println "CP00_NO_TURRET"\n    local.weapon = $player getactiveweap 0\n    if (local.weapon != NULL)\n        println ("CP00_ACTIVE_WEAPON " + local.weapon.model)\n    else\n        println "CP00_NO_ACTIVE_WEAPON"\nend\n'.replace('LABEL',label)
    (home/f'cp00/{label}.scr').write_text(script,encoding='ascii')
commands=['wait 1000','map e2l2','wait 3000','finishloadingscreen','wait 60000']
def snapshot(label):
    return [f'echo CP00_BEGIN_{label}',f'script player exec cp00/{label}.scr','script player stats','wait 300','ui_NumShotsFired','ui_NumHits','ui_NumEnemysKilled','screenshot',f'echo CP00_END_{label}']
commands+=snapshot('before')+['+moveright','wait 700','-moveright','wait 500']+snapshot('moved')+['+attack','wait 180','-attack','wait 1000']+snapshot('fired')+['savegame cp00_foot_ready','wait 1500','echo CP00_FOOT_PROBE_DONE','quit']
(home/'foot.cfg').write_text('\n'.join(commands)+'\n',encoding='ascii')
settings=dict(com_target_game='2',fs_basepath=str(rt),fs_homepath=str(profile),fs_steampath=str(rt),fs_gogpath=str(rt),fs_microsoftstorepath=str(rt),net_enabled='0',logfile='2',developer='1',cheats='1',r_fullscreen='0',r_mode='-1',r_customwidth='1280',r_customheight='960',com_maxfps='60',com_maxfpsUnfocused='60',cl_playintro='0',ui_console='0',cg_fov='90',skill='1')
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,v]
proc=subprocess.Popen(cmd+['+exec','foot.cfg'],cwd=rt)
timed_out=False
try:proc.wait(timeout=115)
except subprocess.TimeoutExpired:timed_out=True;proc.terminate();proc.wait(timeout=10)
log=(home/'qconsole.log').read_text(encoding='latin1')
stages={}
for label in ['before','moved','fired']:
    m=re.search('CP00_BEGIN_'+label+r'(.*?)CP00_END_'+label,log,re.S)
    part=m.group(1) if m else ''
    origin=re.search(r'CP00_ORIGIN \( ([^)]+) \)',part)
    stages[label]=dict(origin=[float(v) for v in origin.group(1).split()] if origin else None,weapon=re.findall(r'CP00_ACTIVE_WEAPON ([^\r\n]+)',part),no_vehicle='CP00_NO_VEHICLE' in part,no_turret='CP00_NO_TURRET' in part,brief_over='CP00_BRIEFOVER 1' in part,stats=dict(re.findall(r'"(ui_\w+)" is:\s*"([^"^]*)',part)))
result=dict(candidate='CP00-r4',game='BT',map='e2l2',completed='CP00_FOOT_PROBE_DONE' in log,exit_code=proc.returncode,host_timeout=timed_out,stages=stages,visual_check='PENDING',scope='Unmodified map briefing, normal strafe and attack input; no spawned actor, teleports or forced control unlock.',engine_sha256=sha(rt/'openmohaa.exe'),evidence=[dict(path=p.relative_to(r).as_posix(),sha256=sha(p)) for p in sorted(profile.rglob('*')) if p.is_file()])
save(r/f'checkpoints/CP00/{args.run_id}.json',result)
print(json.dumps({k:v for k,v in result.items() if k!='evidence'},indent=2),flush=True)
