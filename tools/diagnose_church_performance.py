"""Isolated latest-save renderer ablation; never writes the personal profile."""
import argparse, hashlib, json, re, shutil, statistics, subprocess
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--walk',type=int,default=0);ap.add_argument('--lighting',action='store_true');ap.add_argument('--paired',action='store_true');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;h=p/'main';h.mkdir(parents=True)
rt=R/'runtime-local/CP09-r1';personal=R/'profiles-local/CP08-r1/user'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes();b=p/'bin';b.mkdir()
for f in list(rt.glob('*.dll'))+[rt/'openmohaa.exe']:shutil.copy2(f,b/f.name)
for f in personal.rglob('*.cfg'):
    dest=p/f.relative_to(personal);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
dest=h/'save/omconfig';dest.mkdir(parents=True)
for f in (personal/'main/save/omconfig').glob('quick.*'):shutil.copy2(f,dest/('reference'+f.suffix))
(h/'position.scr').write_text('main:\n    println ("AC_POSITION " + $player.origin + " angles=" + $player.viewangles)\nend\n')
defaults=dict(r_acTAA=1,r_acObjectMotionBlur=50,r_acModelShadows=1,r_acAmbientOcclusion=1,r_acModelLighting=1,r_acDynamicLighting=1,r_acSoftParticles=1)
stages=[('baseline',{}),('no-blur',dict(r_acObjectMotionBlur=0)),('no-temporal',dict(r_acObjectMotionBlur=0,r_acTAA=0)),('no-shadows',dict(r_acModelShadows=0)),('no-ao',dict(r_acAmbientOcclusion=0)),('no-lighting',dict(r_acModelLighting=0,r_acDynamicLighting=0,r_acSoftParticles=0)),('all-off',dict.fromkeys(defaults,0)),('baseline-repeat',{})]
if a.lighting:stages=[('baseline',{}),('no-model-lighting',dict(r_acModelLighting=0)),('no-dynamic-lighting',dict(r_acDynamicLighting=0)),('baseline-repeat',{}),('no-soft-particles',dict(r_acSoftParticles=0)),('no-dynamic-repeat',dict(r_acDynamicLighting=0)),('baseline-final',{})]
cmd=['wait 800','loadgame reference','wait 4500','finishloadingscreen','god','script player exec position.scr','screenshot silent','set com_speeds 1','wait 200']
if a.walk:cmd+=['echo AC_WALK_BEGIN','+forward',f'wait {a.walk}','-forward','echo AC_WALK_END','wait 500']
cmd+=['script player exec position.scr','screenshot silent']
if a.lighting:cmd+=['wait 5000','set r_acLightingDebug 1']
for label,override in stages:
    cmd += [f'set {k} {v}' for k,v in (defaults|override).items()]
    cmd += ['wait 500',f'echo AC_PERF_BEGIN {label}','wait 2500',f'echo AC_PERF_END {label}','screenshot silent']
if a.paired:
    stages=[('baseline',{}),('no-dynamic-lighting',dict(r_acDynamicLighting=0)),('no-soft-particles',dict(r_acSoftParticles=0))]
    cmd=['wait 800']
    for label,override in stages:
        cmd+=['loadgame reference','wait 4500','finishloadingscreen','god']
        cmd += [f'set {k} {v}' for k,v in (defaults|override).items()]
        cmd+=['set com_speeds 1','set r_acLightingDebug 2','wait 200','+forward','wait 6000','-forward','script player exec position.scr','wait 1500',f'echo AC_PERF_BEGIN {label}','wait 7000',f'echo AC_PERF_END {label}','screenshot silent']
cmd+=['echo AC_CHURCH_DONE','quit'];(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,com_maxfps=0,com_maxfpsUnfocused=0,r_swapInterval=0,r_acTemporalDebug=0,r_acShadowDebug=0,r_acAODebug=0,r_acLightingDebug=0).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=150)
log=(h/'qconsole.log').read_text(encoding='latin1');assert proc.returncode==0 and 'AC_CHURCH_DONE' in log
assert not any(e in log for e in ['Script Error','Script file compile error','Unknown command','Invalid event'])
results={}
for label,_ in stages:
    section=log.split('AC_PERF_BEGIN '+label+'\n',1)[1].split('AC_PERF_END '+label,1)[0]
    rows=re.findall(r'frame:\d+ all:\s*(\d+) sv:\s*(\d+) ev:\s*(\d+) cl:\s*(\d+) gm:\s*(\d+) rf:\s*(\d+) bk:\s*(\d+)',section)
    values=list(zip(*[list(map(int,r)) for r in rows]));assert len(rows)>5
    results[label]={k:dict(median=statistics.median(v),p95=sorted(v)[int(.95*(len(v)-1))],maximum=max(v)) for k,v in zip(['all','sv','ev','cl','gm','rf','bk'],values)}
    results[label]['frames']=len(rows)
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):Image.open(f).save(out/f'{i}.png')
assert hashes()==before
result=dict(stages=results,positions=re.findall(r'AC_POSITION .*',log),engine=sha(rt/'openmohaa.exe'),personal_files_unchanged=len(before),
    measurement='com_speeds CPU wall time including driver waits, not GPU timestamps; combat timing can vary between reloads')
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
