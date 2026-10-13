"""Create a new, hash-verified CP0 candidate. Never overwrite an existing candidate."""
import argparse, json, re, shutil, subprocess
from pathlib import Path
from inventory_cp00 import sha, save

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline',required=True,type=Path)
    ap.add_argument('--engine',required=True,type=Path)
    ap.add_argument('--openal',required=True,type=Path)
    ap.add_argument('--candidate',default='CP00-r1')
    ap.add_argument('--input-manifest',type=Path)
    args=ap.parse_args(); repo=Path(__file__).resolve().parents[1]
    if not args.candidate.replace('-','').isalnum(): raise ValueError('Invalid candidate name')
    target=repo/'runtime-local'/args.candidate
    if target.exists(): raise ValueError('Candidate already exists; never overwrite')
    source=(args.input_manifest or repo/'generated-local/input-manifest.json').resolve()
    inputs=json.loads(source.read_text(encoding='utf-8'))
    selected=[r for r in inputs if r['path'].split('/')[0] in ('main','mainta','maintt') and not {'save','configs'}.intersection(Path(r['path']).parts)]
    for row in selected:
        if sha(args.baseline/row['path'])!=row['sha256']: raise ValueError('Baseline mismatch: '+row['path'])
    binaries=[p for p in args.engine.iterdir() if p.suffix.lower() in ('.exe','.dll')]
    if not {'openmohaa.exe','game.dll','cgame.dll'}.issubset({p.name for p in binaries}): raise ValueError('Engine build incomplete')
    # The new directory is only usable after its COMPLETE marker is written.
    target.mkdir(parents=True)
    for row in selected:
        dest=target/row['path']; dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(args.baseline/row['path'],dest)
        if sha(dest)!=row['sha256']: raise ValueError('Copied data mismatch: '+row['path'])
    owned=[]
    for p in binaries:
        shutil.copy2(p,target/p.name); owned.append(p.name)
    for src,name in [(repo/'code/thirdparty/libs/win64/SDL2.dll','SDL2.dll'),(args.openal/'bin/Win64/soft_oal.dll','OpenAL64.dll')]:
        shutil.copy2(src,target/name); owned.append(name)
    for src,name in [(repo/'COPYING.txt','OpenMoHAA-COPYING.txt'),(args.baseline/'EULA.txt','Original-EULA.txt')]:
        shutil.copy2(src,target/name); owned.append(name)
    license_dir=target/'licenses/OpenAL'; license_dir.mkdir(parents=True)
    for name in ('COPYING','LICENSE-pffft','readme.txt'):
        shutil.copy2(args.openal/name,license_dir/name)
    owned.extend(p.relative_to(target).as_posix() for p in license_dir.rglob('*') if p.is_file())
    for game,num in [('AA',0),('SH',1),('BT',2)]:
        profile=repo/'profiles-local'/args.candidate/game; profile.mkdir(parents=True)
        # Relative cmd paths keep the workspace movable. Dedicated profiles keep old saves untouched.
        text='@echo off\nsetlocal\ncd /d "%~dp0"\n'
        # FS_CreatePath rejects literal '..' even in otherwise absolute paths.
        # Expand both paths before passing them to the engine; retain portability.
        text+='for %%I in ("%~dp0.") do set "AC_BASE=%%~fI"\n'
        text+=f'for %%I in ("%~dp0..\\..\\profiles-local\\{args.candidate}\\{game}") do set "AC_PROFILE=%%~fI"\n'
        text+='if not exist "COMPLETE" (echo Kandidat unvollstaendig. & pause & exit /b 1)\n'
        text+=f'echo Medal of Honor: Allied Campaign - {args.candidate} - {game}\n'
        text+='start "" "openmohaa.exe" '
        text+=f'+set com_target_game {num} +set fs_basepath "%AC_BASE%" +set fs_homepath "%AC_PROFILE%" '
        text+='+set fs_steampath "%AC_BASE%" +set fs_gogpath "%AC_BASE%" +set fs_microsoftstorepath "%AC_BASE%" +set logfile 2 '
        text+=f'+echo "BUILD_ID={args.candidate}" %*\n'
        (target/f'Start-{game}.cmd').write_text(text,encoding='ascii'); owned.append(f'Start-{game}.cmd')
        (repo/f'Start-{args.candidate}-{game}.cmd').write_text(f'@echo off\ncall "%~dp0runtime-local\\{args.candidate}\\Start-{game}.cmd" %*\n',encoding='ascii')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    header=(args.engine.parent/'generated/q_version.generated.h').read_text()
    engine_commit=re.search(r'#define GIT_REVISION_HASH "([0-9a-f]{40})"',header).group(1)
    if subprocess.check_output(['git','diff',engine_commit,commit,'--','code','cmake','CMakeLists.txt'],cwd=repo):
        raise ValueError('Engine source differs from the built revision')
    manifest=dict(schema=1,build_id=args.candidate,source_commit=commit,engine_source_commit=engine_commit,upstream_commit='a2f340195975f4f042e28a60b62561dd9a0b2700',data_files=len(selected),data_manifest_sha256=sha(source),owned_files=[dict(path=n,sha256=sha(target/n)) for n in sorted(set(owned))],save_schema='Unmodified OpenMoHAA; original save compatibility untested',weapon_policy='No Allied Campaign effects implemented',status='TECHNICAL_TESTS_PENDING')
    data_manifest=repo/'generated-local'/args.candidate/'runtime-data-manifest.json'
    manifest.update(input_manifest=source.relative_to(repo).as_posix(),runtime_data_manifest=data_manifest.relative_to(repo).as_posix(),wcr_package_fingerprint=json.loads((repo/'third_party/wcr/manifest.json').read_text())['package_fingerprint'])
    save(target/'build-manifest.json',manifest)
    save(repo/f'checkpoints/CP00/{args.candidate}-build.json',manifest)
    save(data_manifest,selected)
    (target/'COMPLETE').write_text(args.candidate+'\n',encoding='ascii')
    print('DEPLOYED',target,len(selected),'unchanged data files')

if __name__=='__main__': main()
