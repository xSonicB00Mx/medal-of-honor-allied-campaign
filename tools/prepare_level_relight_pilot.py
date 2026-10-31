"""Prepare two isolated, reversible m3l3 playtest launchers. No regular deployment."""
import argparse,hashlib,json,shutil,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--bake',type=Path,required=True);a=p.parse_args()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
personal=R/'profiles-local/CP08-r1/user';rt=R/'runtime-local/CP09-r1'
before={f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
bin=R/'runtime-local/CP09-Relight-Pilot';bin.mkdir(exist_ok=False)
for f in rt.glob('*.dll'):shutil.copy2(f,bin/f.name)
shutil.copy2(R/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe',bin/'openmohaa.exe')
report=json.loads((a.bake/'bake.json').read_text())
assert report['map']=='m3l3' and report['samples']>=512
assert struct.unpack_from('<4I',(a.bake/'m3l3.aclm').read_bytes())[:2]==(0x314c4341,report['source_fnv'])
launchers=[]
for mode,value in [('Before',0),('After',1)]:
    profile=R/'profiles-local/CP09'/('relight-playtest-'+mode.lower())
    profile.mkdir(parents=True,exist_ok=False)
    for f in personal.rglob('*.cfg'):
        dst=profile/f.relative_to(personal);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst)
    save=profile/'main/save/omconfig';save.mkdir(parents=True)
    for f in (personal/'main/save/omconfig').glob('quick.*'):shutil.copy2(f,save/('relight_reference'+f.suffix))
    sidecar=profile/'main/maps/ac_relight';sidecar.mkdir(parents=True)
    for f in a.bake.glob('m3l3.ac*'):shutil.copy2(f,sidecar/f.name)
    (profile/'main/relight_start.cfg').write_text('wait 800\nloadgame relight_reference\n')
    launcher=R/('Start-CP09-Relight-'+mode+'.cmd')
    args=f'+set com_target_game 0 +set fs_basepath "{rt}" +set fs_homepath "{profile}" +set fs_steampath "{rt}" +set fs_gogpath "{rt}" +set fs_microsoftstorepath "{rt}" +set net_enabled 0 +set cl_playintro 0 +set logfile 2 +set r_acLevelRelight {value} +set r_acRelightExport 0 +exec relight_start.cfg'
    launcher.write_text(f'@echo off\r\npushd "{bin}"\r\n"{bin / "openmohaa.exe"}" {args} %*\r\npopd\r\n',encoding='utf-8')
    launchers.append(dict(mode=mode,launcher=str(launcher),profile=str(profile)))
after={f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
assert before==after
manifest=dict(engine_sha256=sha(bin/'openmohaa.exe'),regular_engine_sha256=sha(rt/'openmohaa.exe'),personal_files_unchanged=len(before),launchers=launchers,
              bake=report,sidecar_sha256={f.name:sha(f) for f in a.bake.glob('m3l3.ac*')})
(bin/'pilot-manifest.json').write_text(json.dumps(manifest,indent=2))
(bin/'README.txt').write_text('''LEVEL LIGHTING PILOT - m3l3 / The Nebelwerfer Hunt

Use Start-CP09-Relight-After.cmd in the workspace for the new lighting.
Use Start-CP09-Relight-Before.cmd for the original lighting.
Each starts the same COPIED save in its own profile. Your regular profile,
campaign progress, settings, engine and original game data are untouched.
Other maps have no relighting sidecar and use their original lighting.

To return to your normal game, close the pilot and use Start-CP09-r1.cmd
(or your usual Allied Campaign launcher). No restore operation is needed.
In the pilot console, r_acLevelRelight 0 followed by vid_restart restores
original lighting. Loading a save in the same map alone may reuse the world.

The pilot is separate from the released runtime. It contains no new game
logic or savegame format. Dynamic weapon lights retain their original path.
''')
print(json.dumps(manifest,indent=2))
