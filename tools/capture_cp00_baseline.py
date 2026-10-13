"""Controlled live/dead hit fixture on unchanged WCR content, not mission QA."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from inventory_cp00 import sha, save

ap = argparse.ArgumentParser()
ap.add_argument('game', choices=['AA','SH','BT'])
ap.add_argument('--run-id', required=True)
ap.add_argument('--reference-save', type=Path)
ap.add_argument('--weapon', choices=['colt45','mp40','kar98','bar'], default='colt45')
ap.add_argument('--linger-seconds', type=int, default=20)
args = ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9-]+', args.run_id)
assert 1 <= args.linger_seconds <= 30
repo = Path(__file__).resolve().parents[1]
rt = repo/'runtime-local/CP00-r4'
folder,mapname = {'AA':('main','m2l1'),'SH':('mainta','t1l2'),'BT':('maintt','e2l3')}[args.game]
profile = repo/f'profiles-local/CP00-r4/{args.run_id}-{args.game}'
assert not profile.exists()
home=profile/folder
(home/'cp00').mkdir(parents=True)
reference = []
start_command = f'map {mapname}'
if args.reference_save:
    source = (repo/args.reference_save).resolve()
    assert source.is_relative_to(repo/'profiles-local/CP00-r4') and source.suffix == '.sav'
    saves = home/'save/omconfig'
    saves.mkdir(parents=True)
    for extension in ('.sav','.ssv','.tga'):
        original = source.with_suffix(extension)
        dest = saves/('cp00_reference'+extension)
        shutil.copy2(original,dest)
        assert sha(original)==sha(dest)
        reference.append(dict(path=original.relative_to(repo).as_posix(),sha256=sha(original)))
    start_command = 'loadgame cp00_reference'
fixture=(repo/'tools/cp00_baseline_fixture.scr').read_text(encoding='utf-8').replace('models/weapons/colt45.tik',f'models/weapons/{args.weapon}.tik')
(home/'cp00/baseline.scr').write_text(fixture,encoding='ascii')
for label in ('after_shots', 'after_corpse_shots', 'after_delay'):
    (home/f'cp00/{label}.scr').write_text(f'main:\n    waitthread cp00/baseline.scr::snapshot {label}\nend\n',encoding='ascii')
(home/'cp00/aim_corpse.scr').write_text('main:\n    waitthread cp00/baseline.scr::aim_corpse\nend\n',encoding='ascii')
commands=['wait 1000',start_command,'wait 3000','finishloadingscreen','wait 3000',
          'which global/ai.scr','which global/killed.scr','which models/human/german_wehrmact_soldier.tik',
          f'which models/weapons/{args.weapon}.tik','script player exec cp00/baseline.scr',
          'wait 2500','screenshot','savegame cp00_before_combat','wait 500',
          *(['+attack','wait 120','-attack','wait 500'] * 7),'wait 3500',
          'script player exec cp00/after_shots.scr','wait 500','screenshot',
          'script player exec cp00/aim_corpse.scr','+reload','wait 100','-reload','wait 2500',
          *(['+attack','wait 120','-attack','wait 500'] * 3),
          'script player exec cp00/after_corpse_shots.scr','wait 500','screenshot',
          f'wait {args.linger_seconds*1000}','script player exec cp00/after_delay.scr',
          'wait 500','screenshot','savegame cp00_after_combat','wait 1200',
          'echo CP00_BASELINE_DONE','quit']
# Capture genuine player statistics through the server's normal stats event.
expanded=[]
stage_names=iter(('alive','after_shots','after_corpse_shots','after_delay'))
for command in commands:
    if command=='screenshot':
        stage=next(stage_names)
        expanded += ['script player stats','wait 250',f'echo CP00_STATS_BEGIN_{stage}',
                     'ui_NumShotsFired','ui_NumHits','ui_NumEnemysKilled','ui_NumComplete',
                     f'echo CP00_STATS_END_{stage}']
    expanded.append(command)
commands=expanded
(home/'baseline.cfg').write_text('\n'.join(commands)+'\n',encoding='ascii')
settings=dict(com_target_game=str(['AA','SH','BT'].index(args.game)),fs_basepath=str(rt),fs_homepath=str(profile),
              fs_steampath=str(rt),fs_gogpath=str(rt),fs_microsoftstorepath=str(rt),net_enabled='0',logfile='2',
              developer='1',cheats='1',r_fullscreen='0',r_mode='-1',r_customwidth='1280',r_customheight='960',
              com_maxfps='60',com_maxfpsUnfocused='60',cl_playintro='0',skill='1',cg_fov='90')
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items(): cmd+=['+set',k,v]
proc=subprocess.Popen(cmd+['+exec','baseline.cfg'],cwd=rt)
try: proc.wait(timeout=100)
except subprocess.TimeoutExpired:
    proc.terminate();proc.wait(timeout=10);raise
log=(home/'qconsole.log').read_text(encoding='latin1')
records=[line.split('] ',1)[-1] for line in log.splitlines() if 'CP00_' in line]
errors=[line.split('] ',1)[-1] for line in log.splitlines() if any(s in line for s in ('Script Error', 'compile error', 'was not properly loaded'))]
death_counts=re.findall(r'CP00_DEATHS (\d+)',log)
stats={}
for match in re.finditer(r'CP00_STATS_BEGIN_(\w+)\r?\n(.*?)CP00_STATS_END_\1',log,re.S):
    stats[match.group(1)] = dict(re.findall(r'"(ui_\w+)" is:\s*"([^"^]*)',match.group(2)))
result=dict(candidate='CP00-r4',game=args.game,map=mapname,scope='Controlled spawned actor: AI off while alive for repeatable aim, AI on at genuine death to process corpse. Normal player attack input before/after death; not natural mission progression.',
            exit_code=proc.returncode,completed='CP00_BASELINE_DONE' in log,fixture_ready='CP00_FIXTURE_READY' in log,
            script_errors=errors,records=records,visual_check='PENDING',
            reference_save=reference,
            weapon=f'models/weapons/{args.weapon}.tik',linger_seconds=args.linger_seconds,
            death_counts=death_counts,valid_death_sequence=death_counts==['0','1','1','1'],statistics=stats,
            engine_sha256=sha(rt/'openmohaa.exe'),
            engine_source_commit=json.loads((rt/'build-manifest.json').read_text(encoding='utf-8'))['engine_source_commit'],
            wcr_package_fingerprint=json.loads((repo/'third_party/wcr/revisions/CP00-r4.json').read_text(encoding='utf-8'))['package_fingerprint'],
            evidence=[dict(path=p.relative_to(repo).as_posix(),sha256=sha(p)) for p in sorted(profile.rglob('*')) if p.is_file()])
save(repo/f'checkpoints/CP00/{args.run_id}-{args.game}.json',result)
print(args.game,'fixture_ready',result['fixture_ready'],'errors',errors,flush=True)
assert proc.returncode==0 and result['completed'] and result['fixture_ready']
assert result['valid_death_sequence'], 'Invalid controlled death sequence'
