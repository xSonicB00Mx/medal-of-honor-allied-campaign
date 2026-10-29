"""Native lighting regression in an isolated profile, original resources read-only."""
import argparse,hashlib,json,re,shutil,subprocess,zipfile
from pathlib import Path
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('--game',type=int,default=0);a.add_argument('--uhd',action='store_true');a=a.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
p=R/'profiles-local/CP09'/a.run;folder=['main','mainta','maintt'][a.game];h=p/folder;h.mkdir(parents=True)
b=p/'bin';b.mkdir();rt=R/'runtime-local/CP09-r1';build=R/'build-local/cp00-r3/RelWithDebInfo'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
personal=R/'profiles-local/CP08-r1/user'
def hashes():return {f.relative_to(personal).as_posix():sha(f) for f in personal.rglob('*') if f.is_file()}
before=hashes()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','cgame.dll']:shutil.copy2(build/n,b/n)
packages=[]
for game,f in zip(['AA','SH','BT'],['main','mainta','maintt']):
 zpath=out/'packages'/f/'zzzzzzzzzzzzz_AC_FlinchOptions.pk3';zpath.parent.mkdir(parents=True)
 with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
  for name in ['ac_scaling','ac_lighting']:z.writestr('ui/'+name+'.urc',(R/'mod/ui'/f'{name}.urc').read_text().encode('latin1'))
 target=p/f/zpath.name;target.parent.mkdir(exist_ok=True);shutil.copy2(zpath,target)
 packages.append(dict(game=game,package=zpath.relative_to(R).as_posix(),sha256=sha(zpath)))
start='devmap m2l2a'
if a.game:
 src=personal/'mainta/save/omconfig/quick.sav' if a.game==1 else R/'profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav'
 dest=h/'save/omconfig';dest.mkdir(parents=True)
 for f in src.parent.glob(src.stem+'.*'):shutil.copy2(f,dest/('reference'+f.suffix))
 start='loadgame reference'
fixture=(R/'tools/cp00_baseline_fixture.scr').read_text().split('    waitthread snapshot')[0].replace('level.cp00_subject thread deathwatch','level.cp00_subject.health = 10000')
if a.game==0:
 fixture='main:\n    level.cp00_target = ( -4050 -4100 -46 )\n    level.cp00_subject = spawn models/human/german_wehrmact_soldier.tik origin level.cp00_target gun "Mauser KAR 98K"\n    level.cp00_subject ai_off\n    level.cp00_subject.health = 10000\n    $player.origin = ( -4000 -4200 -40 )\n'
fixture+='    level.fx_light = spawn models/weapons/mp40.tik\n    level.fx_light.origin = level.cp00_target + ( 40 -30 65 )\n    level.fx_light svflags "+broadcast"\n    level.fx_light light 1 .3 .08 240\n    level.fx_light lightOn\n    level.fx_cam = spawn Camera\n    level.fx_cam.origin = $player.origin + ( 0 0 90 )\n    level.fx_cam.angles = vector_toangles (level.cp00_target + ( 0 0 30 ) - level.fx_cam.origin)\n    $player hide\n    cuecamera level.fx_cam\n    println AC_FX_READY\nend\n'
(h/'fixture.scr').write_text(fixture)
(h/'cloud.scr').write_text('main:\n    level.fx_cloud = spawn models/emitters/pipe_steam.tik\n    level.fx_cloud.origin = level.cp00_target + ( 30 0 12 )\n    level.fx_cloud anim start\n    println AC_FX_CLOUD\nend\n')
cmd=['wait 800',start,'wait 5000','finishloadingscreen','god','notarget','wait 800',
 'script player exec fixture.scr','wait 800','ui_hud 0','set cg_drawviewmodel 0',
 'set r_acAmbientOcclusion 0','set r_acModelShadows 0','set r_acModelLighting 0','set r_acDynamicLighting 0',
 'wait 300','screenshot silent','set r_acModelLighting 1','set r_acDynamicLighting 1','wait 300','screenshot silent',
 'script player exec cloud.scr','set r_acSoftParticles 0','wait 900','screenshot silent',
 'set r_acSoftParticles 1','wait 900','screenshot silent',
 'set r_acAmbientOcclusion 1','set r_acModelShadows 1','wait 500','screenshot silent',
 'savegame fx_check','wait 300','loadgame fx_check','wait 4000','finishloadingscreen','wait 500','screenshot silent',
 'vid_restart','wait 3500','finishloadingscreen','wait 500','screenshot silent',
 'pushmenu ac_lighting','wait 500','ac_ui_report ac_lighting','screenshot silent',
 'writeconfig fx_settings']
scale=4 if a.uhd else 1600/960
for name,y in [('modelLighting',144),('dynamicLighting',242),('softParticles',340)]:
 cmd += [f'widgetcommand {name} left_mouse_up {int(868*scale)} {int(y*scale)} 0']
cmd += ['wait 100','writeconfig fx_off',
 f'widgetcommand lightingDefaults left_mouse_down {int(772*scale)+5} {int(476*scale)+5} 1',
 f'widgetcommand lightingDefaults left_mouse_up {int(772*scale)+5} {int(476*scale)+5} 0',
 # UI commands append to Cbuf. Queue the verifier behind the actual Defaults
 # action through a second button; an inline quit would run before Defaults.
 'widgetcommand back stuffcommand "exec finish.cfg"',
 f'widgetcommand back left_mouse_down {int(44*scale)+5} {int(476*scale)+5} 1',
 f'widgetcommand back left_mouse_up {int(44*scale)+5} {int(476*scale)+5} 0']
(h/'finish.cfg').write_text('wait 100\nwriteconfig fx_defaults\necho AC_FX_DONE\nquit\n')
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args=[str(b/'openmohaa.exe')]
for k,v in dict(com_target_game=a.game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,
 net_enabled=0,logfile=2,developer=1,cheats=1,thereisnomonkey=1,cl_playintro=0,r_fullscreen=0,r_mode=-1,
 r_customwidth=3840 if a.uhd else 1600,r_customheight=2160 if a.uhd else 900,com_maxfps=60,com_maxfpsUnfocused=60,
 r_fastsky=0,r_acLightingDebug=1,r_acAODebug=2,r_acShadowDebug=3,ac_campaign_mode=0 if a.game==2 else 1).items():args+=['+set',k,str(v)]
proc=subprocess.run(args+['+exec','probe.cfg'],cwd=b,timeout=140)
log=(h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode==0 and 'AC_FX_DONE' in log
errors=[l for l in log.splitlines() if 'LOCALIZATION ERROR:' not in l and any(e in l for e in ['ERROR:','Script Error','Script file compile error','Unknown command','Invalid event','AC lighting shader:','AC AO shader:'])]
assert not errors,errors
assert log.count('AC lighting ready:')>=2
stats=[list(map(int,m)) for m in re.findall(r'AC_LIGHT probes=(\d+) clouds=(\d+) traces=(\d+) blocked=(\d+)',log)]
assert stats and max(s[0] for s in stats)>0 and max(s[1] for s in stats)>0,stats
assert max(s[2] for s in stats)>0,stats
for config,value in [('fx_off',0),('fx_defaults',1)]:
 content=(h/'configs'/(config+'.cfg')).read_text(encoding='latin1')
 for name in ['r_acModelLighting','r_acDynamicLighting','r_acSoftParticles']:
  assert re.search(r'seta '+name+r' "'+str(value)+'"',content),(config,name)
costs=re.findall(r'AC_SHADOW_COST ms=(\d+) gl_error=(\d+)',log)
assert costs and all(int(error)==0 for _,error in costs),costs
images=[]
for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
 dst=out/f'{folder}-{i}.png';Image.open(f).save(dst);images.append(dst.relative_to(R).as_posix())
assert len(images)==8,len(images)
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=sha(build/'openmohaa.exe'),cgame_sha256=sha(build/'cgame.dll'),
 game_sha256=sha(rt/'game.dll'),packages=packages,game=folder,images=images,stats=stats,personal_files_unchanged=len(before)),indent=2)+'\n')
print('PASS',folder,stats[-5:],flush=True)
