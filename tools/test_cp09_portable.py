"""Launch the independent candidate and reload a COPY of the user's BT save."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from cp09_process import tree
from cp09_candidate import expected

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument("run")
a=ap.parse_args()
assert a.run.replace("-","").isalnum()
rt=R/"runtime-local/CP09-r1"
expected(rt)
p=R/"profiles-local/CP09"/a.run
p.mkdir(parents=True,exist_ok=False)
for folder in ("main","mainta","maintt"):(p/folder).mkdir()
dest=p/"maintt/save/omconfig";dest.mkdir(parents=True)
original=R/"profiles-local/CP08-r1/user/maintt/save/omconfig"
hashes={}
for ext in ("sav","ssv","tga"):
    f=original/("quick."+ext)
    hashes[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
    shutil.copy2(f,dest/("reference."+ext))
(p/"main/initial.cfg").write_text("wait 1000\npath\nac_campaign\nwait 600\nac_context 2 menu\n")
(p/"maintt/ac_context_ready.cfg").write_text(
    "wait 1000\npath\nloadgame reference\nwait 6000\nfinishloadingscreen\n"
    "ac_progress_report\nscreenshot silent\necho CP09_PORTABLE_DONE\nquit\n")
cmd=[str(rt/"openmohaa.exe")]
for k,v in dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,
               fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,
               developer=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,
               r_customheight=720,cl_playintro=0,com_maxfps=60,
               com_maxfpsUnfocused=60,ac_campaign_mode=0).items():
    cmd+=["+set",k,str(v)]
proc=subprocess.Popen(cmd+["+exec","initial.cfg"],cwd=rt)
known={};start=time.monotonic();logs=""
try:
    while time.monotonic()-start<65:
        tree(proc.pid,known)
        logs="\n".join(f.read_text(encoding="latin1") for f in p.glob("*/qconsole.log"))
        if "CP09_PORTABLE_DONE" in logs:break
        time.sleep(.2)
    else:raise AssertionError("Portable context/save launch did not complete")
    proc.wait(timeout=10)
    time.sleep(1)
finally:
    if proc.poll() is None:proc.terminate()
    for child in known.values():
        child.kill();child.close()
assert "Game Loaded" in logs
assert "AC_CONTEXT_RESTART" in logs
assert "runtime-local/CP08" not in logs.replace("\\","/")
errors=[l for l in logs.splitlines() if any(s in l for s in ("Script Error","Unknown command","Invalid event","AC_SAVE_REJECT"))]
assert not errors,errors
assert all(hashlib.sha256((original/n).read_bytes()).hexdigest()==v for n,v in hashes.items())
expected(rt)
report=dict(passed=True,context_restart=True,current_bt_save_copy_loaded=True,
            original_unchanged=True,no_cp08_runtime_path=True,
            screenshot=[f.relative_to(R).as_posix() for f in p.rglob("shot*.tga")])
(p/"result.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
