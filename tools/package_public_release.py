"""Build a portable WCR overlay from the verified installed mod, never a profile."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
from cp09_candidate import R, digest, expected
from consolidate_release_packages import consolidate

VERSION = '1.0.1'
rt = R/'runtime-local/CP09-r1'
out = R/'artifacts-local'/('Allied-Campaign-'+VERSION)
assert not out.exists(), 'Do not replace a published artifact'
manifest, base, verified = expected(rt)
out.mkdir(parents=True)
stage = out/'payload'
stage.mkdir()
exclude = {'CP09-LOCAL-ONLY.txt', 'CP09-base-inventory.json', 'CP09-candidate.json',
           'Start-AA.cmd', 'Start-SH.cmd', 'Start-BT.cmd', 'Start-Allied-Campaign.cmd',
           'omohaaded.exe', 'launch_openmohaa_base.exe', 'launch_openmohaa_spearhead.exe',
           'launch_openmohaa_breakthrough.exe'}
for row in manifest['owned_files']:
    name = row['path']
    if name in exclude or name.lower().endswith('.pk3'):
        continue
    dest = stage/name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rt/name, dest)
    assert digest(dest) == row['sha256']

consolidation, obsolete = consolidate(rt, stage, manifest['owned_files'])
assert len(obsolete) == 68
with zipfile.ZipFile(R/'artifacts-local/Allied-Campaign-1.0.0/Medal-of-Honor-Allied-Campaign-1.0.0-Windows-x64.zip') as previous:
    previous_manifest = json.loads(previous.read('Allied-Campaign-manifest.json'))
    previous_paks = {r['path']:r['sha256'] for r in previous_manifest['files'] if r['path'].endswith('.pk3')}
    assert previous_paks == {r['path']:r['sha256'] for r in obsolete}, 'Unexpected 1.0.0 baseline'
(out/'consolidation-verification.json').write_text(json.dumps(consolidation, indent=2)+'\n')
update_command = ' '.join(line.strip() for line in (R/'release/update_legacy_packages.ps1').read_text().splitlines()
                          if line.strip() and not line.lstrip().startswith('#'))
assert '"' not in update_command and len(update_command) < 7500
(stage/'Update-Allied-Campaign.cmd').write_bytes(('@echo off\r\nsetlocal\r\nset "AC_RELEASE_ROOT=%~dp0"\r\n'
    'powershell.exe -NoLogo -NoProfile -Command "'+update_command+'"\r\n'
    'if errorlevel 1 goto failed\r\nexit /b 0\r\n:failed\r\n'
    'if /i not "%~1"=="--quiet" pause\r\nexit /b 1\r\n').encode('ascii'))

# App-local redistribution from Visual Studio's designated redist directory.
crt = Path('D:/Visual Studio/2022 Community/VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT')
for dll in crt.glob('*.dll'):
    shutil.copy2(dll, stage/dll.name)
assert (stage/'vcruntime140.dll').exists() and (stage/'msvcp140.dll').exists()
(stage/'Start-Allied-Campaign.cmd').write_bytes(b'''@echo off\r
setlocal\r
cd /d "%~dp0"\r
if not exist "main\\pak0.pk3" goto missing\r
if not exist "mainta\\*.pk3" goto missing\r
if not exist "maintt\\*.pk3" goto missing\r
if not exist "main\\Restoration_AA_Pak1-Main.pk3" goto wcr\r
if not exist "mainta\\Restoration_SH_Pak1-Main.pk3" goto wcr\r
if not exist "maintt\\Restoration_BT_Pak1-Main.pk3" goto wcr\r
call "%~dp0Update-Allied-Campaign.cmd" --quiet\r
if errorlevel 1 goto updatefailed\r
start "" /D "%~dp0." "%~dp0openmohaa.exe" +set com_target_game 0 +set fs_basepath "%~dp0." +set fs_homepath "%~dp0AlliedCampaign-User" +set fs_steampath "%~dp0." +set fs_gogpath "%~dp0." +set fs_microsoftstorepath "%~dp0." +set net_enabled 0 +set ac_campaign_mode 1 +set cl_playintro 1 +set developer 0 +set logfile 1 %*\r
exit /b 0\r
:missing\r
echo Extract this ZIP into your Medal of Honor War Chest game folder.\r
echo Allied Assault, Spearhead and Breakthrough must all be installed.\r
pause\r
exit /b 2\r
:wcr\r
echo War Chest Restored must be installed for all three campaigns first.\r
pause\r
exit /b 3\r
:updatefailed\r
echo The game was not started. Resolve the update message above and try again.\r
pause\r
exit /b 4\r
''')
readme = (R/'release/README.txt').read_bytes()
(stage/'README-Allied-Campaign.txt').write_bytes(readme)
(stage/'CREDITS-Allied-Campaign.txt').write_bytes((R/'release/CREDITS.txt').read_bytes())
(stage/'WCR-BASELINE.json').write_text(json.dumps(json.loads((R/'third_party/wcr/manifest.json').read_text())['modules'], indent=2)+'\n')
commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=R, text=True).strip()
# Include corresponding GPL source, not just a link or developer build files.
subprocess.run(['git','archive','--format=zip','--prefix=allied-campaign-source/',
                '-o', str(stage/'Allied-Campaign-Source.zip'), commit], cwd=R, check=True)
rows = [dict(path=f.relative_to(stage).as_posix(), sha256=digest(f), bytes=f.stat().st_size)
        for f in sorted(stage.rglob('*')) if f.is_file()]
record = dict(version=VERSION, source_commit=commit, engine_source_commit=manifest['engine_source_commit'],
              wcr_package_fingerprint=manifest['wcr_package_fingerprint'], files=rows,
              obsolete_packages=obsolete, consolidation=consolidation)
(stage/'Allied-Campaign-manifest.json').write_text(json.dumps(record, indent=2)+'\n')
archive = out/('Medal-of-Honor-Allied-Campaign-'+VERSION+'-Windows-x64.zip')
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for f in sorted(stage.rglob('*')):
        if f.is_file(): z.write(f,f.relative_to(stage).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for row in rows:
        assert hashlib.sha256(z.read(row['path'])).hexdigest() == row['sha256']
checksum = digest(archive)
(out/'SHA256SUMS.txt').write_text(checksum+'  '+archive.name+'\n')
print(json.dumps(dict(archive=str(archive), bytes=archive.stat().st_size, sha256=checksum, files=len(rows)+1),indent=2))
