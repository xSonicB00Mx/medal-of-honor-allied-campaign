"""UHD GTAO/shadow stress capture with 16 NPCs and 8 pickups in isolation."""
import argparse, hashlib, json, re, shutil, subprocess
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
(h/'probe.cfg').write_text('''wait 800
map m2l1
wait 4500
finishloadingscreen
wait 600
script player exec crowd.scr
wait 1800
set cg_shadows 0
set r_acModelShadows 0
set r_acAmbientOcclusion 0
wait 1600
screenshot silent
set r_acAmbientOcclusion 1
wait 2000
screenshot silent
set r_acAODebug 1
wait 300
screenshot silent
set r_acAODebug 2
set r_acModelShadows 1
wait 5500
screenshot silent
echo AC_SHADOW_CROWD_DONE
quit
''')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,
               fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,cl_playintro=0,
               r_fullscreen=0,r_mode=-1,r_customwidth=3840,r_customheight=2160,r_fastsky=0,
               ac_hud_scale=1.66,com_maxfps=60,com_maxfpsUnfocused=60,r_acShadowDebug=3,r_acAODebug=2).items():
    args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AC_SHADOW_CROWD_DONE' in log and 'AC_SHADOW_CROWD_READY' in log
assert 'Script Error' not in log
costs=[(int(t),int(e)) for t,e in re.findall(r'AC_SHADOW_COST ms=(\d+) gl_error=(\d+)',log)]
assert costs and all(e==0 for _,e in costs),costs
assert not re.search(r'AC_AO_COST ms=\d+ gl_error=[1-9]',log)
assert 'AC GTAO ready:' in log
draws=[int(n) for n in re.findall(r'AC_SHADOW casters=\d+ drawn=(\d+)',log)]
casters=[int(n) for n in re.findall(r'AC_SHADOW casters=(\d+)',log)]
assert max(casters)>=20,casters # Diffuse-only fallback is intentionally replaced by GTAO.
images=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
    dst=out/f'uhd-{i}.png';Image.open(f).save(dst);images.append(dst.relative_to(R).as_posix())
assert len(images)==4
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),
            resolution=[3840,2160],direct_shadow_drawn_max=max(draws),captured_casters_max=max(casters),synchronized_shadow_pass_ms=[t for t,_ in costs],
            baseline_gl_errors=re.findall(r'AC_SHADOW_SKIPPED enabled=0 gl_error=(\d+)',log),images=images, synchronized_ao_pass_ms=[int(t) for t in re.findall(r'AC_AO_COST ms=(\d+) gl_error=0',log)])
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
