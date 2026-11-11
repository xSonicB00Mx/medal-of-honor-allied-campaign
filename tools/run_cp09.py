"""Serial native regression of the installed candidate; isolated test homes only.

Logs and process memory samples stay local. Results distinguish test failure
from acceptance; a scripted boundary never counts as a natural playthrough.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from cp09_process import tree

R = Path(__file__).resolve().parents[1]
RT = R / "runtime-local/CP08-r1"
USER = R / "profiles-local/CP08-r1/user"


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def snapshot(path):
    return {f.relative_to(path).as_posix(): sha(f)
            for f in sorted(path.rglob("*")) if f.is_file()}


def audit():
    manifest = json.loads((RT / "build-manifest.json").read_text())
    counts = {}
    for name, base, rows in [
        ("original", R.parent, json.loads((R / manifest["input_manifest"]).read_text())),
        ("runtime_base", RT, json.loads((R / manifest["runtime_data_manifest"]).read_text())),
        ("runtime_owned", RT, manifest["owned_files"]),
    ]:
        for row in rows:
            assert sha(base / row["path"]) == row["sha256"], (name, row["path"])
        counts[name] = len(rows)
    for name in ("openmohaa.exe", "game.dll", "cgame.dll"):
        assert sha(RT / name) == sha(R / "build-local/cp00-r3/RelWithDebInfo" / name), name
    for folder in ("main","mainta","maintt"):
        packages=list((R/"generated-local/loadout/packages"/folder).glob("*.pk3"))
        assert packages, "Missing LOADOUT test packages"
        for package in packages:
            assert sha(package)==sha(RT/folder/package.name), "Stale LOADOUT test override"
    wcr = json.loads((R / "third_party/wcr/manifest.json").read_text())
    for row in wcr["modules"]:
        assert sha(RT / row["path"]) == row["sha256"], row["path"]
    return dict(counts=counts, build=manifest, wcr=wcr,
                binaries={n: sha(RT / n) for n in ("openmohaa.exe", "game.dll", "cgame.dll")})


def matrix(prefix):
    def case(label, tool, *args):
        return label, [sys.executable, "tools/" + tool + ".py", *args]
    tests = [
        case("metadata", "validate_cp00"),
        case("campaign", "validate_campaign"),
        case("weapon-policy", "generate_weapon_policy", "--check"),
        case("shared-preferences", "test_shared_preferences", "--run-id", prefix+"-prefs"),
        case("score-combat", "test_highscore", prefix+"-score", "--installed"),
        case("score-abort", "test_highscore", prefix+"-abort", "--installed", "--case", "abort"),
        case("operations-finish", "test_operations_feedback", "finish", prefix+"-finish"),
    ]
    for game in ("AA", "SH", "BT"):
        lower = game.lower()
        tests += [
            case("shotgun-"+lower, "test_shotgun_blood", game, prefix+"-pellets-"+lower),
            case("wounds-"+lower, "test_wound_regression", prefix+"-wounds-"+lower,
                 "--game", game, "--candidate"),
            case("drops-"+lower, "test_bt_drop_options", game, prefix+"-drops-"+lower, "--installed"),
            case("menus-"+lower, "test_menu_navigation", game, prefix+"-menus-"+lower,
                 "--installed", "--in-game"),
        ]
    for game, width, height in (("AA",3840,2160), ("SH",1280,960), ("BT",3440,1440)):
        tests.append(case("crosshair-"+game.lower(), "test_dynamic_crosshair", prefix+"-cross-"+game.lower(),
                          "--game",game,"--installed","--width",str(width),"--height",str(height)))
    for op in (13,11,14):
        tests.append(case("finale-"+str(op),"test_campaign_finales",prefix+"-finale-"+str(op),str(op),"--installed"))
    for game in range(3):
        for mode in ("replay","score","new","default","locked"):
            tests.append(case(f"loadout-{game}-{mode}", "test_loadout_lifecycle",
                              f"{prefix}-loadout-{game}-{mode}",mode,"--game",str(game),
                              *(["--baseline-report","checkpoints/CP09/known-bt-e3l3.json"] if game==2 else [])))
    for fx in (0,1):
        tests.append(case("performance-"+str(fx),"test_cp08_mg_performance",
                          prefix+"-perf-"+str(fx),"--fx",str(fx),"--roundtrip"))
    tests.append(case("reload-memory","test_cp09_memory",prefix+"-memory"))
    tests.append(case("portable-candidate","test_cp09_portable",prefix+"-portable"))
    return tests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--only", nargs="+", help="Exact case labels")
    a = ap.parse_args()
    assert a.run.replace("-", "").isalnum()
    tests = matrix(a.run)
    if a.only:
        assert set(a.only) <= {t[0] for t in tests}, "Unknown test"
        tests = [t for t in tests if t[0] in a.only]
    out = R / "generated-local/CP09" / a.run
    out.mkdir(parents=True, exist_ok=False)
    before = snapshot(USER)
    (out/"personal-before.json").write_text(json.dumps(before,indent=2))
    report = dict(run=a.run, source=subprocess.check_output(["git","rev-parse","HEAD"],cwd=R,text=True).strip(),
                  baseline=audit(), tests=[], natural_playthrough=False)
    try:
        for name, command in tests:
            print("START",name,flush=True)
            start=time.monotonic()
            seen={}
            memory=[]
            with (out/(name+".log")).open("w",encoding="utf-8") as log:
                proc=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
                while proc.poll() is None:
                    tree(proc.pid, seen)
                    for child in list(seen.values()):
                        if child.name.lower()=="openmohaa.exe":
                            m=child.memory()
                            if m:
                                memory.append(dict(t=round(time.monotonic()-start,2),pid=child.pid,**m))
                    if time.monotonic()-start > 240:
                        for child in seen.values():
                            child.kill()
                        proc.kill()
                    time.sleep(.25)
                code=proc.wait()
                # A failed harness must never leave one of its own games alive.
                for child in seen.values():
                    deadline=time.monotonic()+3
                    while child.running() and time.monotonic()<deadline:
                        time.sleep(.1)
                    child.kill()
                    child.close()
            (out/(name+"-memory.json")).write_text(json.dumps(memory))
            row=dict(name=name,exit=code,passed=code==0,seconds=round(time.monotonic()-start,2),
                     peak_rss=max((m["rss"] for m in memory),default=None),
                     peak_private=max((m["private"] or 0 for m in memory),default=None))
            report["tests"].append(row)
            (out/"results.json").write_text(json.dumps(report,indent=2))
            print("PASS" if code==0 else "FAIL",name,row["seconds"],flush=True)
    finally:
        report["personal_profile_unchanged"]=before==snapshot(USER)
        report["personal_files"]=len(before)
        report["final_integrity"]=audit()["counts"]
        report["passed"]=all(t["passed"] for t in report["tests"]) and len(report["tests"])==len(tests) and report["personal_profile_unchanged"]
        (out/"results.json").write_text(json.dumps(report,indent=2))
    assert report["passed"], "See per-case local logs; no full pass claimed"


if __name__=="__main__":
    main()
