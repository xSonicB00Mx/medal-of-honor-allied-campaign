"""Sequential real-game runs; never run two renderer instances together."""
import json,subprocess,sys
from pathlib import Path
from validate_wound_run import validate
r=Path(__file__).resolve().parents[1]
cases=[
 ('AA','rear','german_misc_worker',120,['--motion','--lod']),
 ('AA','side','german_misc_worker',60,['--crouch','--lod']),
 ('SH','front','german_winter_type2',60,['--motion']),
 ('SH','rear','german_misc_worker',30,['--lod']),
 ('SH','side','german_misc_worker',60,['--crouch']),
 ('BT','front','Sc_AX_Ital_Inf',30,['--regions','--death']),
 ('BT','rear','german_afrika_private',120,['--motion']),
 ('BT','side','german_misc_worker',60,['--crouch','--lod']),
 ('AA','wall','german_misc_worker',60,['--wall'])]
results=[]
for game,view,model,fps,extra in cases:
 name=f'final-{game}-{view}'
 args=[sys.executable,str(r/'tools/test_body_wounds.py'),game,'--checkpoint','CP05','--run-id',name,'--model',f'models/human/{model}.tik','--one-volley','--facing','front' if view=='wall' else view,'--fps',str(fps),*extra]
 path=r/'checkpoints/CP05'/f'{name}.json'
 if not path.exists():
  with (r/'logs-local'/f'{name}.log').open('w') as log: outcome=subprocess.run(args,cwd=r,stdout=log,stderr=subprocess.STDOUT)
  assert outcome.returncode==0,name
 result=json.loads(path.read_text())
 verified=validate(path,True)
 assert result['patch_budget_exceeded']==0 and result['cache_unavailable']==0,(name,'visual budget/cache')
 # The fixture intentionally disables mist before the later death shot.
 assert all('authorized=1' in m for m in result['mist_events']) and any('enabled=1' in m for m in result['mist_events']), (name,'mist policy')
 assert {int(line.split('group=')[1].split()[0]) for line in result['wounds']}=={1,2,3,4},(name,'weapon coverage')
 results.append(verified);print(json.dumps(verified),flush=True)
 (r/'checkpoints/CP05/matrix.json').write_text(json.dumps(results,indent=2))
