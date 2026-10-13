"""Rendered command-driven smoke test; explicitly not a completed gameplay test."""
import argparse,json,subprocess,time
from pathlib import Path
from inventory_cp00 import save

ap=argparse.ArgumentParser(); ap.add_argument('game',choices=['AA','SH','BT']); ap.add_argument('--candidate',default='CP00-r1'); ap.add_argument('--engine',type=Path); ap.add_argument('--run-id',default='rendered'); args=ap.parse_args()
if not args.run_id.replace('-','').isalnum(): raise ValueError('Invalid run id')
repo=Path(__file__).resolve().parents[1]; rt=repo/'runtime-local'/args.candidate
num,folder,mapname={'AA':(0,'main','m1l2a'),'SH':(1,'mainta','t1l2'),'BT':(2,'maintt','e1l2')}[args.game]
profile=repo/'profiles-local'/args.candidate/(args.run_id+'-'+args.game)
if profile.exists(): raise ValueError('Preserve prior evidence; select a new run id')
cfgdir=profile/folder; cfgdir.mkdir(parents=True,exist_ok=True)
# OpenMoHAA wait values are milliseconds. finishloadingscreen is the normal
# Continue-button action (cl_ui.cpp), not a mission completion flag.
cfg='\n'.join(['wait 1000',f'map {mapname}',f'which maps/{mapname}.scr','which global/ai.scr','path','wait 3000','finishloadingscreen','wait 5000',f'savegame cp00_{args.game.lower()}','wait 1500',f'loadgame cp00_{args.game.lower()}','wait 2000','finishloadingscreen','wait 3000','screenshot','echo CP00_SAVELOAD_COMMANDS_FINISHED','disconnect','wait 2000','screenshot','echo CP00_MENU_RETURN_COMMAND_FINISHED','quit'])+'\n'
(cfgdir/'cp00-smoke.cfg').write_text(cfg,encoding='ascii')
cmd=[str(args.engine or rt/'openmohaa.exe')]
for key,val in [('com_target_game',str(num)),('fs_basepath',str(rt)),('fs_homepath',str(profile)),('fs_steampath',str(rt)),('fs_gogpath',str(rt)),('fs_microsoftstorepath',str(rt)),('net_enabled','0'),('logfile','2'),('developer','1'),('r_fullscreen','0'),('r_mode','-1'),('r_customwidth','1280'),('r_customheight','960'),('com_maxfps','60'),('com_maxfpsUnfocused','60'),('cl_playintro','0'),('ui_skip_eamovie','1'),('ui_skip_titlescreen','1'),('ui_skip_legalscreen','1')]:
    cmd+=['+set',key,val]
cmd+=['+echo','BUILD_ID='+args.candidate+'-SMOKE-'+args.game,'+exec','cp00-smoke.cfg']
begin=time.time(); proc=subprocess.Popen(cmd,cwd=rt)
print('SMOKE START',args.game,proc.pid,flush=True)
timeout=False
try: proc.wait(timeout=180)
except subprocess.TimeoutExpired:
    timeout=True; proc.terminate(); proc.wait(timeout=15)
logs=list(profile.rglob('qconsole.log')); log=logs[0].read_text(encoding='latin1') if logs else ''
result=dict(game=args.game,map=mapname,exit_code=proc.returncode,timeout=timeout,duration_seconds=round(time.time()-begin,2),active_state='CS_ACTIVE' in log,save_requested=f'Saving to cp00_{args.game.lower()}' in log,load_lines=[l for l in log.splitlines() if 'load' in l.lower() and ('cp00_' in l.lower() or 'done' in l.lower())],commands_finished='CP00_SAVELOAD_COMMANDS_FINISHED' in log,menu_return_command_finished='CP00_MENU_RETURN_COMMAND_FINISHED' in log,screenshots=[p.relative_to(profile).as_posix() for p in profile.rglob('*.tga') if 'screenshots' in p.parts],save_files=[p.relative_to(profile).as_posix() for p in profile.rglob('cp00_*') if p.suffix in ('.sav','.ssv')],note='Command-driven rendered smoke, not manual gameplay or natural level transition.')
result.update(run_id=args.run_id,game_loaded='Game Loaded' in log,resource_origins=[l.split('] ',1)[-1].replace(str(rt),'$RUNTIME') for l in log.splitlines() if 'File "' in l and 'found in' in l])
result['save_files']=[p.relative_to(profile).as_posix() for p in profile.rglob('cp00_*') if p.suffix in ('.sav','.ssv','.tga')]
save(repo/f'checkpoints/CP00/{args.run_id}-{args.game}.json',result); print(json.dumps(result),flush=True)
