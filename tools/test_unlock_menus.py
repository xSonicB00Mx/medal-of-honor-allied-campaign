"""Verify locked rows and the growing briefing catalogue in isolated engine profiles."""
import json,re,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];results=[]
for run,state,briefings in [('unlock-fresh-r2','ACPROG2 0 0 - 0 0',[0]),('unlock-partial-r2','ACPROG2 0 0 - 7 0',[0]),('unlock-mid-r2','ACPROG1 127 7 -',[0,1,2,4,5,7]),('unlock-full-r2','ACPROG1 32767 15 -',[0,1,2,4,5,7,8,9,10,12,13,14])]:
 proc=subprocess.run([sys.executable,str(r/'tools/test_level_replay.py'),run,'inspect','--state',state],capture_output=True,text=True,cwd=r)
 assert proc.returncode==0,(proc.stdout,proc.stderr)
 home=r/'profiles-local/level-replay'/run/'main'
 ui=(home/'ui/ac_level_list.urc').read_text();brief=(home/'ui/ac_briefing_room.urc').read_text()
 assert all(f'name "level_{i}"' in ui for i in range(44,53))
 if run!='unlock-full-r2':
  assert 'Start Replay' not in ui and 'ac_level_replay' not in ui
  rows=re.findall(r'resource\s+Label\s*\{[^}]*name "level_\d+"[^}]*\}',ui)
  assert len(rows)==9 and all('LOCKED' in x and 'fgcolor 1 0.25 0.2 1' in x and 'stuffcommand' not in x for x in rows)
 else:assert 'LOCKED' not in ui and 'ac_level_replay 52 2' in ui
 assert [int(x) for x in re.findall(r'name "briefing_(\d+)"',brief)]==briefings
 assert len(re.findall('ac_briefing_replay ',brief))==len(briefings)
 d=json.loads((r/'generated-local'/f'level-replay-{run}.json').read_text());results.append(dict(run=run,briefings=briefings,progress_preserved=d['state_before']==d['state_after'],images=d['images'],engine_sha256=d['engine_sha256']))
 print(run,'PASS',flush=True)
(r/'checkpoints/CP08/unlock-menus-tests.json').write_text(json.dumps(results,indent=2)+'\n')
