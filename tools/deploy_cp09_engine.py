"""Deploy a tested engine and optional shared options layout with rollback."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from cp09_candidate import R, digest, expected, safe

ap = argparse.ArgumentParser()
ap.add_argument('run', help='Unique backup name; native test report folder')
ap.add_argument('--options-layout', action='store_true', help='Also install the exact options packages from the test report')
ap.add_argument('--game-only', action='store_true', help='Install only the tested game DLL')
ap.add_argument('--cgame', action='store_true', help='Install the matching tested cgame ABI with the engine')
a = ap.parse_args()
assert not (a.game_only and (a.options_layout or a.cgame))
assert re.fullmatch(r'[a-zA-Z0-9-]+', a.run)
report = json.loads((R/'generated-local/CP09'/a.run/'result.json').read_text())
engine = R/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'
assert digest(engine)==report['engine_sha256'], 'Test the exact engine first'
game = engine.with_name('game.dll')
cgame = engine.with_name('cgame.dll')
if a.game_only: assert digest(game)==report['game_sha256'], 'Test the exact game DLL first'
if a.cgame: assert digest(cgame)==report['cgame_sha256'], 'Test the exact cgame DLL first'
assert not subprocess.check_output(['git','diff','HEAD','--','code','mod/ui'],cwd=R), 'Commit tested sources first'
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
updates={'openmohaa.exe':engine}
if a.game_only: updates={'game.dll':game}
if a.cgame: updates['cgame.dll']=cgame
if a.options_layout:
    packages=report['packages']
    assert {row['game'] for row in packages}=={'AA','SH','BT'} and len(packages)==3
    for row in packages:
        src=safe(R,row['package'])
        assert digest(src)==row['sha256'], 'Package changed after test'
        name=src.parent.name+'/'+src.name
        assert src.parent.name in ['main','mainta','maintt'] and src.name=='zzzzzzzzzzzzz_AC_FlinchOptions.pk3'
        with zipfile.ZipFile(src) as z:
            assert z.namelist() in [['ui/ac_scaling.urc'], ['ui/ac_scaling.urc','ui/ac_lighting.urc'], ['ui/ac_scaling.urc','ui/ac_lighting.urc','ui/ac_temporal.urc']]
            assert z.testzip() is None
            for member in z.namelist():
                assert z.read(member)==(R/'mod'/member).read_text().encode('latin1')
        updates[name]=src
    for manifest in manifests:
        assert set(updates).issubset({row['path'] for row in manifest['owned_files']})
files = [['openmohaa.exe','build-manifest.json'],
         ['openmohaa.exe','build-manifest.json','CP09-candidate.json','COMPLETE']]
for names in files:
    names.extend(name for name in updates if name!='openmohaa.exe')
for rt,names in zip(runtimes,files):
    target = backup/rt.name
    target.mkdir(parents=True)
    for name in names:
        (target/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(rt/name,target/name)
        assert digest(target/name)==digest(rt/name)
def save(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n')
try:
    for rt,manifest in zip(runtimes,manifests):
        for name,src in updates.items(): shutil.copy2(src,rt/name)
        manifest.update(source_commit=commit)
        manifest['game_dll_source_commit' if a.game_only else 'engine_source_commit']=commit
        if a.cgame: manifest['cgame_source_commit']=commit
        for row in manifest['owned_files']:
            if row['path'] in updates: row['sha256']=digest(updates[row['path']])
        if a.options_layout:
            manifest['flinch']={**manifest.get('flinch',{}),'batch':a.run,'packages':packages,
                               'provider':'Shared Allied Campaign options layout','upload_allowed':False}
        save(rt/'build-manifest.json',manifest)
    _,_,source_rows = expected(runtimes[0])
    record = json.loads((runtimes[1]/'CP09-candidate.json').read_text())
    record.update(source_commit=commit,engine_source_commit=manifests[1]['engine_source_commit'],checkpoint_source_commit=commit,
                  input_fingerprint=hashlib.sha256(json.dumps(source_rows,sort_keys=True).encode()).hexdigest())
    if a.cgame: record['cgame_source_commit']=commit
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
              rollback=str(backup.relative_to(R)),scope='Engine and options layout; game/cgame/artwork unchanged' if a.options_layout else 'Engine only; game/cgame/assets unchanged')
if a.game_only: result.update(game_sha256=digest(game),scope='Game DLL only; engine/cgame/assets unchanged')
if a.cgame: result.update(cgame_sha256=digest(cgame),scope='Engine and matching cgame; shared options' if a.options_layout else 'Engine and matching cgame')
save(backup.parent/'deployment.json',result)
print(json.dumps(result,indent=2))
