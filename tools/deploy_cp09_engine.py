"""Deploy a tested engine-only fix to the local CP08/CP09 launchers with rollback."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from cp09_candidate import R, digest, expected, safe

ap = argparse.ArgumentParser()
ap.add_argument('run', help='Unique backup name; native test report folder')
a = ap.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9-]+', a.run)
report = json.loads((R/'generated-local/CP09'/a.run/'result.json').read_text())
engine = R/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'
assert digest(engine)==report['engine_sha256'], 'Test the exact engine first'
assert not subprocess.check_output(['git','diff','HEAD','--','code'],cwd=R), 'Commit engine source first'
commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
runtimes = [R/'runtime-local'/name for name in ['CP08-r1','CP09-r1']]
backup = R/'generated-local/CP09'/a.run/'rollback'
assert not backup.exists()
profile = R/'profiles-local/CP08-r1/user'
def profile_hashes():
    return {p.relative_to(profile).as_posix():digest(p) for p in profile.rglob('*') if p.is_file()}
before = profile_hashes()
original = json.loads((R/'generated-local/CP00-r4/input-manifest.json').read_text())
for row in original:
    assert digest(safe(R.parent,row['path']))==row['sha256']
manifests = [expected(rt)[0] for rt in runtimes]
print('Original data and both runtimes verified',flush=True)
files = [['openmohaa.exe','build-manifest.json'],
         ['openmohaa.exe','build-manifest.json','CP09-candidate.json','COMPLETE']]
for rt,names in zip(runtimes,files):
    target = backup/rt.name
    target.mkdir(parents=True)
    for name in names:
        shutil.copy2(rt/name,target/name)
        assert digest(target/name)==digest(rt/name)
def save(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n')
try:
    for rt,manifest in zip(runtimes,manifests):
        shutil.copy2(engine,rt/'openmohaa.exe')
        manifest.update(source_commit=commit,engine_source_commit=commit)
        for row in manifest['owned_files']:
            if row['path']=='openmohaa.exe': row['sha256']=digest(engine)
        save(rt/'build-manifest.json',manifest)
    _,_,source_rows = expected(runtimes[0])
    record = json.loads((runtimes[1]/'CP09-candidate.json').read_text())
    record.update(source_commit=commit,engine_source_commit=commit,checkpoint_source_commit=commit,
                  input_fingerprint=hashlib.sha256(json.dumps(source_rows,sort_keys=True).encode()).hexdigest())
    save(runtimes[1]/'CP09-candidate.json',record)
    for row in manifests[1]['owned_files']:
        if row['path']=='CP09-candidate.json': row['sha256']=digest(runtimes[1]/row['path'])
    save(runtimes[1]/'build-manifest.json',manifests[1])
    (runtimes[1]/'COMPLETE').write_text('CP09-r1\n'+commit+'\n')
    verified = {rt.name:len(expected(rt)[2]) for rt in runtimes}
    assert profile_hashes()==before, 'Personal profile changed'
except BaseException:
    for rt,names in zip(runtimes,files):
        for name in names: shutil.copy2(backup/rt.name/name,rt/name)
    raise
result = dict(source_commit=commit,engine_sha256=digest(engine),verified_files=verified,
              original_files_verified=len(original),personal_files_unchanged=len(before),
              rollback=str(backup.relative_to(R)),scope='Engine only; game/cgame/assets unchanged')
save(backup.parent/'deployment.json',result)
print(json.dumps(result,indent=2))
