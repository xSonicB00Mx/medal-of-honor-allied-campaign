"""Isolated copy of the user's m1l1 save; actual mounted MG42 and native frame timings."""
import argparse, hashlib, json, re, shutil, subprocess, statistics
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--fx',type=int,default=1);ap.add_argument('--debug',type=int,default=0);ap.add_argument('--perf',type=int,default=1);ap.add_argument('--roundtrip',action='store_true');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/CP08-r1'/a.run;h=p/'main'
assert not p.exists();(h/'save/omconfig').mkdir(parents=True);(h/'probe').mkdir()
for ext in ['sav','ssv','tga']:shutil.copy2(r/f'profiles-local/CP08-r1/user/main/save/omconfig/m1l10002.{ext}',h/f'save/omconfig/reference.{ext}')
fixture='''main:
    $player.health = 10000
    if ($mg42guy != NULL)
        $mg42guy remove

    level.perf_deaths = 0
    level.perf_base = $player.origin
    local.dir = angles_toforward $player.angles
    level.perf_target = $player.origin + local.dir * 160
    // Reject placements inside the map. Prefer the viewing direction, then
    // try the four cardinal directions with an actor-sized world trace.
    // Sweep above the slope, then lower the entire actor box onto terrain.
    local.dirs[1] = local.dir
    local.dirs[2] = ( 1 0 0 )
    local.dirs[3] = ( 0 1 0 )
    local.dirs[4] = ( -1 0 0 )
    local.dirs[5] = ( 0 -1 0 )
    level.perf_placement = 0
    for (local.i = 1; local.i <= 5; local.i++)
    {
        local.start = $player.origin + ( 0 0 128 )
        local.goal = local.start + local.dirs[local.i] * 160
        local.hit = trace local.start local.goal 1 ( -16 -16 0 ) ( 16 16 94 )
        local.error = vector_length (local.hit - local.goal)
        if (local.error < 1)
        {
            local.floor = trace local.goal (local.goal - ( 0 0 256 )) 1 ( -16 -16 0 ) ( 16 16 94 )
            local.drop = vector_length (local.goal - local.floor)
            if ((local.drop < 1) || (local.drop >= 255))
                continue
            level.perf_target = local.floor + ( 0 0 2 )
            level.perf_placement = local.i
            break
        }
    }
    println ("CP00_PLACEMENT=" + level.perf_placement)
    if (level.perf_placement == 0)
        end
    local.dir = vector_normalize (level.perf_target - level.perf_base)
    local.dir[2] = 0
    level.perf_angles = vector_toangles local.dir
    $mg42.origin = level.perf_base + local.dir * 40 + ( 0 0 48 )
    $mg42.angles = level.perf_angles
    $mg42 yawCenter level.perf_angles[1]
    $mg42 maxYawOffset 180
    $mg42 maxuseangle 360
    $mg42 setthread mounted
    $mg42 setusable 1
    $mg42 setPlayerUsable 1
    $player.viewangles = level.perf_angles
    $mg42 doUse $player
    wait 0.5
    $mg42 psetviewangles level.perf_angles
    level.perf_pos = level.perf_target
    println ("AC_MG_READY gun=" + $mg42.origin + " angles=" + level.perf_angles + " player=" + $player.origin + " target=" + level.perf_pos)
    level.perf_actor = spawn models/human/german_wehrmact_soldier.tik origin level.perf_pos targetname "ac_perf_actor"
    level.perf_actor ai_off
    level.perf_actor gravity 0
    level.perf_actor.health = 100000
    level.perf_actor.angles = level.perf_angles + ( 0 180 0 )
    level.perf_actor thread deathwatch
    level.perf_deaths = 0
end
mounted:
    println "AC_MG_MOUNTED"
end
deathwatch:
    self waittill death
    self ai_on
    self gravity 1
    level.perf_deaths++
    println ("AC_MG_DEATH " + level.perf_deaths)
end
firephase:
    for (local.i = 0; local.i < 200; local.i++)
    {
        $player.viewangles = level.perf_angles
        $mg42 psetviewangles level.perf_angles
        $mg42 shoot
        if (local.i % 20 == 0)
            println ("AC_MG_SHOT health=" + level.perf_actor.health + " gunangles=" + $mg42.angles + " view=" + $player.viewangles)
        wait 0.06
    }
end
killphase:
    level.perf_actor.health = 1
    for (local.i = 0; local.i < 4; local.i++)
    {
        wait 1.2
        level.perf_actor = spawn models/human/german_wehrmact_soldier.tik origin level.perf_pos targetname "ac_perf_actor"
        level.perf_actor ai_off
    level.perf_actor gravity 0
        level.perf_actor.health = 1
        level.perf_actor.angles = level.perf_angles + ( 0 180 0 )
        level.perf_actor thread deathwatch
    }
end
'''
(h/'probe/mg.scr').write_text(fixture)
for label in ['firephase','killphase']:(h/('probe/'+label+'.scr')).write_text('main:\n    thread '+label+'\nend\n'+fixture.replace('main:', 'setup:', 1))
cmds=['wait 1000','loadgame reference','wait 2500','finishloadingscreen','popmenu 0','set cl_paused 0','unpause','set autopaused 0','wait 1000','script player exec probe/mg.scr','wait 1500','set com_speeds 1','wait 200','echo AC_PERF_BEGIN idle','wait 3000','echo AC_PERF_END idle','echo AC_PERF_BEGIN firing','+attack','script player exec probe/firephase.scr','wait 6000','echo AC_PERF_END firing','echo AC_PERF_BEGIN dying','script player exec probe/killphase.scr','wait 6500','-attack','echo AC_PERF_END dying','set com_speeds 0','screenshot silent','echo AC_MG_DONE','quit']
if a.roundtrip:
 cmds[-2:-2]=['set ac_fx_debug 1','savegame ac_mg_roundtrip','wait 700','loadgame ac_mg_roundtrip','wait 2500','finishloadingscreen','popmenu 0','unpause','wait 1500','screenshot silent']
(h/'probe.cfg').write_text('\n'.join(cmds)+'\n')
cmd=[str(rt/'openmohaa.exe')]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_perf=a.perf,ac_fx_debug=a.debug,ac_corpse_effects=a.fx,ac_blood_mist=a.fx,ac_world_blood=a.fx,ac_body_wounds=a.fx).items():cmd+=['+set',k,str(v)]
proc=subprocess.run(cmd+['+exec','probe.cfg'],cwd=rt,timeout=90)
log=(h/'qconsole.log').read_text(encoding='latin1');stages={}
for name in ['idle','firing','dying']:
 section=log.split('AC_PERF_BEGIN '+name,1)[-1].split('AC_PERF_END '+name,1)[0]
 values=[int(x) for x in re.findall(r'frame:\d+ all:\s*(\d+)',section)]
 gaps=[int(x) for x in re.findall(r'AC_PERF_SNAPSHOT[^\n]*gap=(\d+)',section)]
 pending=[int(x) for x in re.findall(r'AC_PERF_SNAPSHOT[^\n]*pending=(\d+)',section)]
 sizes=[int(x) for x in re.findall(r'AC_PERF_SNAPSHOT[^\n]*bytes=(\d+)',section)]
 ordered=sorted(values)
 stages[name]=dict(snapshots=len(gaps),max_snapshot_gap_ms=max(gaps,default=0),max_pending_commands=max(pending,default=0),max_snapshot_bytes=max(sizes,default=0),frames=len(values),mean_ms=round(sum(values)/max(1,len(values)),2),median_ms=statistics.median(values) if values else None,p95_ms=ordered[int(.95*(len(ordered)-1))] if ordered else None,p99_ms=ordered[int(.99*(len(ordered)-1))] if ordered else None,max_ms=max(values,default=0),over_33ms=sum(v>33 for v in values),over_100ms=sum(v>100 for v in values),measurement="com_speeds CPU wall time; includes driver waits, excludes limiter sleep; not GPU query time")
errors=[l for l in log.splitlines() if any(x in l for x in ['was not properly loaded','Script Error','compile error','unknown command','Unknown command','Invalid event','command not available','Server command overflow','msg overflow'])]
archive=re.findall(r'AC_WOUND_ARCHIVE (save|load) count=(\d+)',log)
if a.roundtrip:assert 'Game Loaded' in log and len(archive)>=2 and archive[-2][0]=='save' and archive[-1][0]=='load' and archive[-2][1]==archive[-1][1]
d=dict(archive=archive,run=a.run,fx=a.fx,exit=proc.returncode,stages=stages,errors=errors[:20],error_count=len(errors),events=[l for l in log.splitlines() if 'AC_MG_' in l],binaries={n:hashlib.sha256((rt/n).read_bytes()).hexdigest() for n in ['openmohaa.exe','game.dll','cgame.dll']})
(r/'checkpoints/CP08'/f'{a.run}.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2));assert proc.returncode==0 and not errors and 'AC_MG_READY' in log and 'AC_MG_DEATH' in log and 'AC_MG_DONE' in log
