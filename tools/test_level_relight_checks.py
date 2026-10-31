"""Native opt-out, malformed sidecar and save/map-lifetime regression."""
import argparse,json,shutil,struct,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--bake',type=Path,required=True);a=p.parse_args()
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
views=out/'views.json';views.write_text(json.dumps([dict(name='church',origin=[2800,-2000,-180],target=[2200,-2300,-80])]))
def run(name,*args):
    subprocess.run([sys.executable,str(R/'tools/test_level_relight.py'),a.run+'-'+name,'--views',str(views),'--stable',*map(str,args)],cwd=R,check=True)
    return json.loads((R/'generated-local/CP09'/(a.run+'-'+name)/'result.json').read_text())
reports={}
reports['original']=run('original','--original-engine')
reports['off']=run('off','--bake',a.bake,'--disabled')
def compare(left,right):
    x=np.asarray(Image.open(left),np.int16);y=np.asarray(Image.open(right),np.int16)
    delta=np.abs(x-y)
    # Fog/foliage/temporal sampling can vary with timing. The solid facade is
    # the stable subject, excluding moving NPCs behind the open windows.
    crop=delta[200:800,480:605]
    result=dict(mean=float(delta.mean()),p99=float(np.percentile(delta,99)),facade_mean=float(crop.mean()),facade_max=int(crop.max()))
    assert result['facade_mean']<.6 and result['mean']<1.5,result
    return result
comparisons={'off':compare(reports['original']['images'][0],reports['off']['images'][0])}
for mode in ['wrong-source','short-lightmap','nan-grid','overflow-grid']:
    folder=out/mode;folder.mkdir()
    for f in a.bake.glob('m3l3.ac*'):shutil.copy2(f,folder/f.name)
    name='m3l3.aclm' if mode in ['wrong-source','short-lightmap'] else 'm3l3.acgrid'
    data=bytearray((folder/name).read_bytes())
    if mode=='wrong-source':struct.pack_into('<I',data,4,123)
    elif mode=='short-lightmap':data=data[:8]
    elif mode=='nan-grid':struct.pack_into('<f',data,44,float('nan'))
    else:struct.pack_into('<3i',data,32,0x7fffffff,0x7fffffff,0x7fffffff)
    (folder/name).write_bytes(data)
    reports[mode]=run(mode,'--bake',folder,'--expect-reject','lightmap' if name.endswith('aclm') else 'grid')
    if name.endswith('aclm'):comparisons[mode]=compare(reports['original']['images'][0],reports[mode]['images'][0])
reports['lifecycle']=run('lifecycle','--bake',a.bake,'--lifecycle')
(out/'checks.json').write_text(json.dumps(dict(cases=reports,comparisons=comparisons),indent=2))
print(json.dumps(comparisons,indent=2))
