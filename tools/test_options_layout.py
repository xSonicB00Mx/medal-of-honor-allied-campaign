"""Render the shared options and exercise controls, Defaults and Back natively."""
import argparse, hashlib, json, re, shutil, subprocess, zipfile
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--packages-report');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
rt=R/'runtime-local/CP09-r1'
exe=R/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'
source=(R/'mod/ui/ac_scaling.urc').read_text()
packages=(json.loads((R/a.packages_report).read_text())['packages'] if a.packages_report else
          json.loads((R/'generated-local/flinch/packages/package-report.json').read_text()))
defaults=dict(ac_ui_auto=1,ac_menu_scale=1,ac_hud_scale=1,ac_hud_safe=1,ac_blood_mist=1,
              ac_world_blood=1,ac_body_wounds=1,ac_corpse_effects=1,ac_player_flinch_percent=20,
              ac_bt_drop_limits=0,ac_hud_outline=0,r_acModelShadows=1,r_acAmbientOcclusion=1)
personal=R/'profiles-local/CP08-r1/user'
def hashes():
 return {p.relative_to(personal).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in personal.rglob('*') if p.is_file()}
before=hashes();results=[]
for game,(width,height) in enumerate([(1920,1080),(1280,960),(3440,1440)]):
 p=R/'profiles-local/CP09'/f'{a.run}-{game}';assert not p.exists()
 folder=['main','mainta','maintt'][game];h=p/folder;h.mkdir(parents=True)
 for item in packages:
  f=R/item['package'];dst=p/f.parent.name/f.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(f,dst)
 # Only add continuations to the real button commands, so the command buffer drains.
 fixture=source.replace('stuffcommand "popmenu 0"','stuffcommand "popmenu 0; exec back.cfg"')
 fixture=fixture.replace('set r_acAmbientOcclusion 1"','set r_acAmbientOcclusion 1; exec defaults.cfg"')
 with zipfile.ZipFile(h/'zzzzzzzzzzzzzzzzz_AC_OptionsProbe.pk3','w') as z:z.writestr('ui/ac_scaling.urc',fixture)
 scale=min(width/960,height/540);ox=(width-960*scale)/2;oy=(height-540*scale)/2
 def mouse(name,event,x,y,buttons=0):
  return f'widgetcommand {name} {event} {int(ox+x*scale)} {int(oy+y*scale)} {buttons}'
 cmd=['wait 800','ac_main_menu','wait 200','ac_ui_options','wait 400','ac_ui_report ac_scaling','screenshot silent',
      'set ac_menu_scale 0.65','wait 200','ac_ui_report ac_scaling','screenshot silent','set ac_menu_scale 1']
 for name,cv,x,y in [('auto','ac_ui_auto',433,167),('hudOutline','ac_hud_outline',433,331),
                     ('mist','ac_blood_mist',897,166),('worldBlood','ac_world_blood',897,216),
                     ('bodyWounds','ac_body_wounds',897,266),('corpseEffects','ac_corpse_effects',897,316),
                     ('dropLimits','ac_bt_drop_limits',897,431),('modelShadows','r_acModelShadows',897,461),('ambientOcclusion','r_acAmbientOcclusion',433,461)]:
  cmd += [mouse(name,'left_mouse_up',x,y),cv]
 for name,cv,x,y in [('menuSlider','ac_menu_scale',290,210),('hudSlider','ac_hud_scale',290,250),('safeSlider','ac_hud_safe',290,290)]:
  cmd += [mouse(name,'left_mouse_down',x,y,1),mouse(name,'left_mouse_up',x,y),cv]
 cmd += [mouse('playerFlinch','left_mouse_down',260,432,1)]
 for x in range(176,365,4):cmd += [mouse('playerFlinch','left_mousedragged',x,432,1),'ac_player_flinch_percent']
 cmd += [mouse('playerFlinch','left_mouse_up',364,432),'writeconfig changed',
         mouse('reset','left_mouse_down',850,510,1),mouse('reset','left_mouse_up',850,510)]
 (h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
 (h/'defaults.cfg').write_text('wait 200\nwriteconfig restored\nac_ui_report ac_scaling\nscreenshot silent\n'+
     mouse('back','left_mouse_down',80,510,1)+'\n'+mouse('back','left_mouse_up',80,510)+'\n')
 (h/'back.cfg').write_text('wait 200\nac_ui_report main\necho OPTIONS_LAYOUT_DONE\nquit\n')
 args=[str(exe)]
 settings=dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,
               fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cl_playintro=0,ac_campaign_mode=1,
               r_fullscreen=0,r_mode=-1,r_customwidth=width,r_customheight=height,com_maxfps=60,com_maxfpsUnfocused=60)
 settings.update(defaults)
 for k,v in settings.items():args+=['+set',k,str(v)]
 proc=subprocess.run(args+['+exec','probe.cfg'],cwd=rt,timeout=45)
 log=(h/'qconsole.log').read_text(encoding='latin1')
 assert proc.returncode==0 and 'OPTIONS_LAYOUT_DONE' in log and 'AC_UI_CURRENT main' in log
 errors=[s for s in log.splitlines() if any(t in s for t in ['UI EXCEPTION','Unknown command','Invalid event','Failed to find resource'])]
 assert not errors,errors
 roots=re.findall(r'AC_UI_ROOT ac_scaling ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',log)
 assert len(roots)==3 and len(set(roots))==1,roots
 rects=[]
 for name,*values in re.findall(r'AC_UI_CHILD (\S+) ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',log.split('AC_UI_ROOT ac_scaling',1)[1].split('AC_UI_CURRENT',1)[0]):
  x,y,w,t=map(float,values)
  assert x>=0 and y>=0 and x+w<=960*scale+.1 and y+t<=540*scale+.1,(name,values)
  if not name.endswith('Panel'):rects.append((name,x,y,w,t))
 for i,(n,x,y,w,t) in enumerate(rects):
  for m,bx,by,bw,bt in rects[i+1:]:assert min(x+w,bx+bw)-max(x,bx)<=.1 or min(y+t,by+bt)-max(y,by)<=.1,(n,m)
 changed=dict(re.findall(r'seta (ac_\w+|r_acModelShadows|r_acAmbientOcclusion) "([^"]+)"',(h/'configs/changed.cfg').read_text()))
 restored=dict(re.findall(r'seta (ac_\w+|r_acModelShadows|r_acAmbientOcclusion) "([^"]+)"',(h/'configs/restored.cfg').read_text()))
 assert all(float(restored[k])==v for k,v in defaults.items()),restored
 assert all(float(changed[k])!=v for k,v in defaults.items() if k!='ac_player_flinch_percent'),changed
 flinch=[float(v) for v in re.findall(r'"ac_player_flinch_percent" is:"([^" ]+)',log)]
 assert len(flinch)==48 and set(flinch)==set(range(0,101,10)),flinch
 images=[]
 for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
  target=out/f'{folder}-{i}.png';Image.open(f).save(target);images.append(target.relative_to(R).as_posix())
 assert len(images)==3
 results.append(dict(game=game,resolution=[width,height],roots=roots,controls_changed=changed,
                     defaults_restored=True,back_to_main=True,ten_percent_steps=True,overlap_free=True,images=images))
 print('PASS',folder,width,height,flush=True)
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
 packages=packages,cases=results,personal_files_unchanged=len(before)),indent=2)+'\n')
