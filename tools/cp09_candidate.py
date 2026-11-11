"""Offline local candidate from the verified, already merged installation.

This is not a raw-game importer or a redistributable asset package. It preserves
the pinned WCR/BT integration and never reads or copies personal saves.
Interrupted copies remain inactive and may be resumed explicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

R = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def safe(base, relative):
    p = base / relative
    if Path(relative).is_absolute() or ":" in relative or ".." in Path(relative).parts:
        raise ValueError("Unsafe manifest path: "+relative)
    if not p.resolve().is_relative_to(base.resolve()):
        raise ValueError("Escaping manifest path: "+relative)
    for component in [p, *p.parents]:
        if component == base.parent:
            break
        if component.is_symlink() or component.is_junction():
            raise ValueError("Linked installation path")
    return p


def expected(source):
    manifest = json.loads((source/"build-manifest.json").read_text())
    inventory = source/"CP09-base-inventory.json"
    base = json.loads(inventory.read_text()) if inventory.exists() else json.loads((R/manifest["runtime_data_manifest"]).read_text())
    rows = {row["path"]:row["sha256"] for row in base}
    for row in manifest["owned_files"]:
        assert row["path"] not in rows, "Ownership overlaps original data"
        rows[row["path"]] = row["sha256"]
    for name, sha in rows.items():
        path = safe(source, name)
        assert path.is_file() and digest(path)==sha, "Changed or missing source: "+name
    wcr = json.loads((R/"third_party/wcr/manifest.json").read_text())
    assert manifest["wcr_package_fingerprint"]==wcr["package_fingerprint"]
    for row in wcr["modules"]:
        assert rows[row["path"]]==row["sha256"]
    assert "maintt/zzzz_AC_BT_Drops.pk3" in rows, "Incomplete BT integration"
    return manifest,base,rows


def launchers():
    files = {}
    for name, number in (("AA",0),("SH",1),("BT",2)):
        files["Start-"+name+".cmd"] = ('@echo off\r\ncall "%~dp0Start-Allied-Campaign.cmd" '+str(number)+' %*\r\n').encode()
    files["Start-Allied-Campaign.cmd"] = b'''@echo off\r
setlocal\r
if not exist "%~dp0COMPLETE" (echo Incomplete Allied Campaign installation.& exit /b 3)\r
set "GAME=0"\r
if "%~1"=="1" set "GAME=1"\r
if "%~1"=="2" set "GAME=2"\r
start "" /D "%~dp0." "%~dp0openmohaa.exe" +set com_target_game %GAME% +set fs_basepath "%~dp0." +set fs_homepath "%~dp0user" +set fs_steampath "%~dp0." +set fs_gogpath "%~dp0." +set fs_microsoftstorepath "%~dp0." +set net_enabled 0 +set ac_campaign_mode 1 +set cl_playintro 0 +set logfile 2 +set developer 0 +set ui_console 0\r
'''
    return files


def install(source, destination, resume=False, interrupt_after=None):
    source, destination = source.resolve(), destination.absolute()
    allowed=(R/"runtime-local").resolve()
    assert destination.parent.resolve()==allowed and destination.name.startswith("CP09-")
    safe(allowed,destination.name)
    assert source!=destination and not source.is_relative_to(destination)
    manifest,base,rows=expected(source)
    identity=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
    if destination.exists():
        record=json.loads((destination/"CP09-candidate.json").read_text())
        assert record["input_fingerprint"]==identity, "Existing candidate uses different inputs"
        expected(destination)
        assert (destination/"COMPLETE").exists()
        return dict(result="UNCHANGED",files=len(rows),input_fingerprint=identity)
    stage=destination.with_name(destination.name+".staging")
    safe(allowed,stage.name)
    if stage.exists():
        assert resume, "Incomplete stage exists; use --resume after inspection"
        assert json.loads((stage/"CP09-stage.json").read_text())["input_fingerprint"]==identity
    else:
        stage.mkdir()
        (stage/"CP09-stage.json").write_text(json.dumps(dict(input_fingerprint=identity)))
    allowed_names=set(rows)|{"CP09-stage.json"}
    assert all(f.relative_to(stage).as_posix() in allowed_names for f in stage.rglob("*") if f.is_file()), "Unexpected stage files"
    copied=0
    for name, sha in sorted(rows.items()):
        src, dst = safe(source,name), safe(stage,name)
        if not dst.exists() or digest(dst)!=sha:
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dst)
            assert digest(dst)==sha, "Input changed during copy: "+name
            copied+=1
            if interrupt_after is not None and copied>=interrupt_after:
                return dict(result="INTERRUPTED_FOR_TEST",copied=copied,activated=False)
    own={row["path"]:row["sha256"] for row in manifest["owned_files"]}
    extra=launchers()
    extra["CP09-base-inventory.json"]=(json.dumps(base,indent=2)+"\n").encode()
    record=dict(input_fingerprint=identity,source_build=manifest["build_id"],
                source_commit=manifest["source_commit"],engine_source_commit=manifest["engine_source_commit"],
                checkpoint_source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=R,text=True).strip(),
                proprietary_assets=True,upload_allowed=False,natural_playthrough_accepted=False)
    extra["CP09-candidate.json"]=(json.dumps(record,indent=2)+"\n").encode()
    extra["CP09-LOCAL-ONLY.txt"]=(
        "Local Allied Campaign candidate. Contains proprietary game/WCR/MP1 assets: do not upload.\n"
        "Start-Allied-Campaign.cmd starts a NEW independent profile in user/.\n"
        "Existing personal saves are not included or moved. Keep their separate backup.\n"
        "WCR: "+manifest["wcr_package_fingerprint"]+"\n"
        "See OpenMoHAA-COPYING.txt, Original-EULA.txt, MAP-CREDITS.md and source checkpoints/CP09.\n").encode()
    for name,data in extra.items():
        (stage/name).write_bytes(data)
        own[name]=digest(stage/name)
    output={**manifest,"build_id":destination.name,
            "runtime_data_manifest":"CP09-base-inventory.json",
            "owned_files":[dict(path=n,sha256=h) for n,h in sorted(own.items())]}
    (stage/"build-manifest.json").write_text(json.dumps(output,indent=2)+"\n")
    (stage/"CP09-stage.json").unlink()
    expected(stage)
    (stage/"COMPLETE").write_text(destination.name+"\n"+manifest["source_commit"]+"\n")
    stage.rename(destination)
    return dict(result="INSTALLED",files=len(rows),copied=copied,input_fingerprint=identity)


def uninstall(destination):
    allowed=(R/"runtime-local").resolve()
    destination=destination.absolute()
    assert destination.parent.resolve()==allowed and destination.name.startswith("CP09-")
    safe(allowed,destination.name)
    manifest,base,_=expected(destination)
    assert (destination/"CP09-candidate.json").is_file()
    # Verify every owned file before removing any. Preserve base data and user files.
    for row in manifest["owned_files"]:
        safe(destination,row["path"]).unlink()
    for name in ("COMPLETE","build-manifest.json"):
        safe(destination,name).unlink()
    for row in base:
        assert digest(safe(destination,row["path"]))==row["sha256"]
    return dict(result="MOD_REMOVED_BASE_PRESERVED",base_files=len(base))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["install","verify","uninstall"])
    ap.add_argument("destination",type=Path)
    ap.add_argument("--source",type=Path,default=R/"runtime-local/CP08-r1")
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--interrupt-after",type=int)
    args=ap.parse_args()
    if args.action=="install":
        result=install(args.source,args.destination,args.resume,args.interrupt_after)
    elif args.action=="verify":
        m,b,rows=expected(args.destination)
        result=dict(result="VERIFIED",files=len(rows),base_files=len(b),owned_files=len(m["owned_files"]))
    else:
        result=uninstall(args.destination)
    print(json.dumps(result,indent=2))
