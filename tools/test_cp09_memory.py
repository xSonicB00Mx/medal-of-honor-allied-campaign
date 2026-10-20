"""Repeated native save/load of a byte copy of the current BT quicksave."""
import argparse
import hashlib
import json
import re
import shutil
import statistics
import subprocess
import time
from pathlib import Path
from cp09_process import tree

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument("run")
a=ap.parse_args()
assert a.run.replace("-","").isalnum()
p=R/"profiles-local/CP09"/a.run
h=p/"maintt"
(h/"save/omconfig").mkdir(parents=True,exist_ok=False)
source=R/"profiles-local/CP08-r1/user/maintt/save/omconfig"
hashes={}
for ext in ("sav","ssv","tga"):
    f=source/("quick."+ext)
    hashes[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
    shutil.copy2(f,h/"save/omconfig"/("reference."+ext))
commands=["wait 800","loadgame reference","wait 5000","finishloadingscreen",
          "set autopaused 0","god","set developer 0"]
for i in range(10):
    commands += ["savegame cp09_roundtrip","wait 400","loadgame cp09_roundtrip",
                 "wait 3000","finishloadingscreen",f"echo CP09_MEMORY_PHASE_{i}","wait 2000",
                 "echo CP09_MEMORY_END"]
commands += ["echo CP09_MEMORY_DONE","quit"]
(h/"probe.cfg").write_text("\n".join(commands)+"\n")
rt=R/"runtime-local/CP08-r1"
settings=dict(com_target_game=2,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,
              fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,
              cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,
              r_customheight=1080,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,
              ac_campaign_mode=0,autopaused=0)
cmd=[str(rt/"openmohaa.exe")]
for k,v in settings.items():cmd+=["+set",k,str(v)]
proc=subprocess.Popen(cmd+["+exec","probe.cfg"],cwd=rt)
known={}
samples={i:[] for i in range(10)}
started=time.monotonic()
try:
    while proc.poll() is None:
        tree(proc.pid,known)
        # Obtain the launched process itself as a child of this harness, once.
        tree(__import__("os").getpid(),known)
        log=(h/"qconsole.log").read_text(encoding="latin1") if (h/"qconsole.log").exists() else ""
        marks=list(re.finditer(r"CP09_MEMORY_(?:PHASE_(\d+)|END)",log))
        active=int(marks[-1][1]) if marks and marks[-1][1] else None
        child=known.get(proc.pid)
        if active is not None and child:
            mem=child.memory()
            if mem:samples[active].append(mem)
        if time.monotonic()-started>150:raise TimeoutError("Save/load stress timeout")
        time.sleep(.2)
finally:
    if proc.poll() is None:proc.terminate()
    proc.wait(timeout=10)
    for child in known.values():child.close()
log=(h/"qconsole.log").read_text(encoding="latin1")
assert proc.returncode==0 and "CP09_MEMORY_DONE" in log
assert log.count("Game Loaded")==11 and log.count("Saving to cp09_roundtrip")==10
assert all(hashlib.sha256((source/n).read_bytes()).hexdigest()==v for n,v in hashes.items())
errors=[l for l in log.splitlines() if any(s in l for s in ("Script Error","Unknown command","AC_SAVE_REJECT","Invalid event"))]
assert not errors,errors
values=[dict(cycle=i,samples=len(s),rss_median=statistics.median(x["rss"] for x in s),
             private_median=statistics.median(x["private"] for x in s)) for i,s in samples.items()]
growth=values[-1]["private_median"]-values[2]["private_median"]
report=dict(passed=True,roundtrips=10,current_save_copy_loaded=True,source_unchanged=True,
            phases=values,private_growth_after_warmup=growth,
            sustained_growth=all(values[i+1]["private_median"]>values[i]["private_median"]+1024*1024 for i in range(2,9)),
            note="Ten reloads only; not proof against all long-session leaks.")
(p/"result.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
