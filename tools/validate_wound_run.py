"""Validate actual event/draw/archive logs, including transforms after loading."""
import argparse, json, re
from pathlib import Path

def fields(line):
    return dict(re.findall(r'(\w+)=([^ ]+)', line))

def validate(path, expected_exit=False):
    data=json.loads(path.read_text()); root=Path(__file__).resolve().parents[1]
    assert data['completed'] and data['exit']==0 and not data['errors'], path
    log=(root/Path(data['images'][0]).parent.parent/'qconsole.log').read_text(encoding='latin1')
    expected={}
    for line in data['wounds']:
        f=fields(line)
        if int(f['triangles'])==0: continue
        key=(f['id'],f['branch']); expected[key]=f
        assert float(f['radius'])==(3.5 if int(f['group'])>=3 or int(f['branch']) else 1.8)
        assert 0<=float(f['rotation'])<360 and f['flip'] in ('0,0','0,1','1,0','1,1')
    assert expected and data['received'] and data['drawn']
    for line in data['received']+data['drawn']+data.get('states',[]):
        f=fields(line); e=expected[(f['id'],f['branch'])]
        for key in ('rotation','flip','triangles'): assert f[key]==e[key], (path,key,f,e)
        if 'seed' in f: assert f['seed']==e['seed']
    archive=re.findall(r'AC_WOUND_ARCHIVE (save|load) count=(\d+)',log)
    loads=[int(count) for action,count in archive if action=='load']; assert loads and loads[-1]>0
    saves=[int(count) for action,count in archive if action=='save']; assert saves[-1]==loads[-1]
    after=log.rsplit('AC_WOUND_ARCHIVE load',1)[1]
    record='AC_WOUND_STATE' if data.get('states') else 'AC_WOUND_DRAW'
    restored={(fields(x)['id'],fields(x)['branch']) for x in re.findall(record+r'[^\r\n]+',after)}
    assert len(restored)==loads[-1], (path,restored,loads)
    assert 'AC_WOUND_REMOVED' not in log
    if expected_exit:
        assert any(k[1]=='1' for k in expected)
        for key,e in expected.items():
            if key[1]=='1':
                entry=expected.get((key[0],'0'))
                if entry: assert (entry['seed'],entry['rotation'],entry['flip']) != (e['seed'],e['rotation'],e['flip'])
    else: assert all(k[1]=='0' for k in expected)
    if data.get('test_conditions',{}).get('death'): assert log.count('CP00_DEATH_EVENT count=1')==1
    return dict(run=path.stem,valid_wounds=len(expected),restored=len(restored),stable_transforms=True,exit_checked=expected_exit)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('results',nargs='+',type=Path);ap.add_argument('--exit-wounds',action='store_true');a=ap.parse_args()
    print(json.dumps([validate(p,a.exit_wounds) for p in a.results],indent=2))
