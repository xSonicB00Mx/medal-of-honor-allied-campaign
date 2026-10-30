"""Native UHD temporal cost: 16 NPCs, 8 pickups, lights, particles, AO and shadows."""
import argparse, hashlib, json, re, shutil, subprocess, statistics
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;h=p/'main';h.mkdir(parents=True,exist_ok=False)
rt=R/'runtime-local/CP09-r1';build=R/'build-local/cp00-r3/RelWithDebInfo'
b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for name in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/name,b/name)
(h/'crowd.scr').write_text('''main:
    local.forward = angles_toforward $player.angles
    local.left = angles_toleft $player.angles
    for (local.row = 0; local.row < 4; local.row++)
    {
        for (local.col = 0; local.col < 4; local.col++)
        {
            local.pos = $player.origin + local.forward * (180 + local.row * 70) + local.left * (local.col * 55 - 82) + ( 0 0 128 )
            local.pos = trace local.pos (local.pos - ( 0 0 384 )) 1
            local.actor = spawn models/human/german_wehrmact_soldier.tik origin (local.pos + ( 0 0 2 )) gun "Mauser KAR 98K"
            local.actor.angles = $player.angles + ( 0 180 0 )
            local.actor ai_off
            local.actor.health = 10000
            if (local.col < 2)
            {
                local.w = spawn models/weapons/mp40.tik
                local.w.origin = local.pos + local.left * 20 + ( 0 0 16 )
                if (local.row == 1)
                {
                    local.w light 1 .4 .12 300
                    local.w lightOn
                    local.w svflags "+broadcast"
                    local.cloud = spawn models/emitters/pipe_steam.tik
                    local.cloud.origin = local.pos + ( 0 0 8 )
                    local.cloud anim start
                }
            }
        }
    }
    local.cam = spawn Camera
    local.cam.origin = $player.origin + ( 0 0 130 )
    local.cam.angles = vector_toangles ($player.origin + local.forward * 300 - local.cam.origin)
    $player hide
    cuecamera local.cam
    println AC_SHADOW_CROWD_READY
end
''')
cmd=['wait 800','devmap m2l1','wait 4500','finishloadingscreen','god','notarget','wait 600','script player exec crowd.scr','wait 1800','set cg_shadows 0']
for label,taa,blur in [('off',0,0),('taa',1,0),('both',1,100)]:
    cmd += [f'set r_acTAA {taa}',f'set r_acObjectMotionBlur {blur}','wait 300',
            'set com_speeds 1','wait 200',f'echo AC_PERF_BEGIN {label}','wait 4000',f'echo AC_PERF_END {label}','set com_speeds 0','screenshot silent']
cmd += ['echo AC_TEMPORAL_CROWD_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,
               fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,
               r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,r_fastsky=0,
               ac_hud_scale=1.66,com_maxfps=60,com_maxfpsUnfocused=60,r_acShadowDebug=0,r_acAODebug=0,r_acModelShadows=1,r_acAmbientOcclusion=1).items():
    args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AC_TEMPORAL_CROWD_DONE' in log and 'AC_SHADOW_CROWD_READY' in log
assert 'Script Error' not in log
stages={}
for label in ['off','taa','both']:
    section=log.split('AC_PERF_BEGIN '+label,1)[1].split('AC_PERF_END '+label,1)[0]
    values=sorted(map(int,re.findall(r'frame:\d+ all:\s*(\d+)',section)))
    assert len(values)>30
    stages[label]=dict(frames=len(values),median=statistics.median(values),p95=values[int(.95*(len(values)-1))],p99=values[int(.99*(len(values)-1))],maximum=max(values))
images=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
    dst=out/f'uhd-{i}.png';Image.open(f).save(dst);images.append(dst.relative_to(R).as_posix())
assert len(images)==3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),resolution=[3840,2160],stages=stages,images=images,
            measurement='com_speeds CPU wall time including driver waits; not GPU query or present time',npc_count=16,pickup_count=8,lights=2)
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
