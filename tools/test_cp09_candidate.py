"""Transactional local installation/rollback regression; no game launch or saves."""
import json
from pathlib import Path
from cp09_candidate import R, install, uninstall, expected, digest

target=R/"runtime-local/CP09-install-test-r1"
source=R/"runtime-local/CP08-r1"
assert not target.exists() and not target.with_name(target.name+".staging").exists()
out=R/"generated-local/CP09/install-r1"
out.mkdir(parents=True,exist_ok=False)
results=[]
results.append(install(source,target,interrupt_after=25))
assert not target.exists()
assert not (target.with_name(target.name+".staging")/"COMPLETE").exists()
results.append(install(source,target,resume=True))
manifest,base,rows=expected(target)
before={name:digest(target/name) for name in rows}
results.append(install(source,target))
assert before=={name:digest(target/name) for name in rows}
# Unknown user files and saves survive an uninstall. Changed owned files cause
# a refusal before any deletion, then restoring the exact bytes allows rollback.
save=target/"user/main/save/omconfig/sentinel.sav"
save.parent.mkdir(parents=True)
save.write_bytes(b"DISPOSABLE PROFILE SENTINEL")
owned=target/"Start-AA.cmd"
original=owned.read_bytes()
owned.write_bytes(original+b"rem edited\n")
try:
    uninstall(target)
except AssertionError:
    results.append(dict(result="CHANGED_OWNED_FILE_REFUSED"))
else:
    raise AssertionError("Modified installation was removed")
assert (target/"openmohaa.exe").exists()
owned.write_bytes(original)
results.append(uninstall(target))
assert save.read_bytes()==b"DISPOSABLE PROFILE SENTINEL"
assert not (target/"openmohaa.exe").exists()
assert all(digest(target/row["path"])==row["sha256"] for row in base)
expected(source)
report=dict(passed=True,steps=results,source_unchanged=True,user_sentinel_preserved=True,
            base_files=len(base),scope="Already merged local runtime, not arbitrary raw-game/WCR import")
(out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
