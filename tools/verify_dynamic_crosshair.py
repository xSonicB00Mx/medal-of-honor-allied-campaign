"""Check native capture reports against projection and observed live firing."""
from pathlib import Path
import json, math, re, sys
root=Path(__file__).resolve().parents[1]
summary=[]
pattern=r'time=(\d+) code=(\d+) slope=([\d.]+) radius=([\d.]+),([\d.]+) fov=([\d.]+),([\d.]+) viewport=(\d+),(\d+)'
for run in sys.argv[1:]:
    report=json.loads((root/'generated-local/dynamic-crosshair'/f'{run}-test.json').read_text())
    states={k:[[float(x) for x in m.groups()] for line in lines if (m:=re.search(pattern,line))] for k,lines in report['sections'].items()}
    def radius(name):return states[name][-1][3]
    base=radius('standing');assert base>0
    assert max(row[3] for row in states['firing'])>base*1.3
    assert abs(radius('recovery')-base)<.1
    assert abs(radius('stopped')-base)<.1
    assert abs(radius('hud1')-radius('hud166'))<.01
    assert radius('fov90')<radius('fov80')*.9
    assert abs(radius('rifle')-radius('rifle-shot'))<.01
    assert abs(radius('rifle')-radius('rifle-recovered'))<.01
    assert all(row[1]==0 for row in states['projectile'])
    assert abs(radius('save')-radius('loaded'))<.01
    assert not states['hidden'] and not states['legacy']
    # A transition frame can retain the old crosshair while zoom begins.
    assert len(states['scope'])<=2
    projection_error=0
    for rows in states.values():
        for time,code,slope,rx,ry,fx,fy,w,h in rows:
            if not code:continue
            for radius_,size,fov in [(rx,w,fx),(ry,h,fy)]:
                error=abs(radius_-slope*size*.5/math.tan(math.radians(fov)*.5))
                assert error<.01,error
                projection_error=max(projection_error,error)
    samples=[]
    for line in report['sections']['firing']:
        m=re.search(r'range=([\d.]+) sigma=([\d.]+),([\d.]+)',line)
        if m:samples.append([float(x) for x in m.groups()])
    assert len(samples)>=5 and samples[-1][1]>samples[0][1]*1.3
    first=samples[0];slope95=math.sqrt(-2*math.log(.05))*max(first[1:])/first[0]
    assert abs(math.atan(slope95)-math.atan(states['standing'][-1][2]))<.000013
    movement=max(row[3] for row in states['moving'])
    assert movement>base*1.1,('Movement fixture blocked',run,movement,base)
    summary.append(dict(run=run,game=report['game'],installed=report['installed'],resolution=[report['width'],report['height']],standing_radius=base,firing_radius=max(row[3] for row in states['firing']),moving_radius=movement,recovered_radius=radius('recovery'),fov90_radius=radius('fov90'),rifle_radius=radius('rifle'),shot_samples=len(samples),projection_error_pixels=projection_error,binaries=report['binaries'],screenshots=report['outputs']))
print(json.dumps(summary,indent=2))
(root/'generated-local/dynamic-crosshair/verification.json').write_text(json.dumps(summary,indent=2))
