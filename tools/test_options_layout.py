"""Exercise both options pages, their real controls and scoped defaults in AA/SH/BT."""
import argparse, hashlib, json, re, shutil, subprocess, zipfile
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--packages-report');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
rt=R/'runtime-local/CP09-r1';exe=rt/'openmohaa.exe'
sources={n:(R/'mod/ui'/f'{n}.urc').read_text() for n in ['ac_scaling','ac_temporal']}
packages=(json.loads((R/a.packages_report).read_text())['packages'] if a.packages_report else
          json.loads((R/'generated-local/flinch/packages/package-report.json').read_text()))
interface=dict(ac_ui_auto=1,ac_menu_scale=1,ac_hud_scale=1,ac_hud_safe=1,ac_hud_outline=0,ac_player_flinch_percent=20,ac_bt_drop_limits=0)
graphics=dict(r_acTAA=1,r_acObjectMotionBlur=0,r_acAmbientOcclusion=1,r_acModelShadows=1,ac_blood_mist=1,ac_world_blood=1,ac_body_wounds=1,ac_corpse_effects=1)
defaults={**interface,**graphics}
personal=R/'profiles-local/CP08-r1/user'
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def hashes():return {f.relative_to(personal).as_posix():digest(f) for f in personal.rglob('*') if f.is_file()}
before=hashes();results=[]
for case,(game,width,height) in enumerate([(0,1920,1080),(1,1280,960),(2,3440,1440),(0,3840,2160)]):
 p=R/'profiles-local/CP09'/f'{a.run}-{case}';assert not p.exists()
 folder=['main','mainta','maintt'][game];h=p/folder;h.mkdir(parents=True)
 for item in packages:
  f=R/item['package'];assert digest(f)==item['sha256']
  dst=p/f.parent.name/f.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(f,dst)
  with zipfile.ZipFile(f) as z:
   for n,s in sources.items():assert z.read('ui/'+n+'.urc')==s.encode('latin1')
 # Continuations only: all real navigation/default commands run before the test resumes.
 fixtures={n:s.replace('stuffcommand "popmenu 0"','stuffcommand "popmenu 0; exec '+('finish' if n=='ac_scaling' else 'interface_return')+'.cfg"') for n,s in sources.items()}
 fixtures['ac_scaling']=fixtures['ac_scaling'].replace('pushmenu ac_temporal"','pushmenu ac_temporal; exec graphics.cfg"').replace('set ac_bt_drop_limits 0"','set ac_bt_drop_limits 0; exec interface_defaults.cfg"')
 fixtures['ac_temporal']=fixtures['ac_temporal'].replace('set ac_corpse_effects 1"','set ac_corpse_effects 1; exec graphics_defaults.cfg"')
 with zipfile.ZipFile(h/'zzzzzzzzzzzzzzzzz_AC_OptionsProbe.pk3','w') as z:
  for n,s in fixtures.items():z.writestr('ui/'+n+'.urc',s.encode('latin1'))
 scale=min(width/960,height/540);ox=(width-960*scale)/2;oy=(height-540*scale)/2
 def mouse(n,event,x,y,b=0):return f'widgetcommand {n} {event} {int(ox+x*scale)} {int(oy+y*scale)} {b}'
 def click(n,x,y):return [mouse(n,'left_mouse_down',x,y,1),mouse(n,'left_mouse_up',x,y)]
 def drag(n,cv,x0,x1,y):
  commands=[mouse(n,'left_mouse_down',(x0+x1)//2,y,1)]
  for x in range(x0,x1+1,4):commands += [mouse(n,'left_mousedragged',x,y,1),cv]
  return commands+[mouse(n,'left_mouse_up',x1,y)]
 def cfg(n,cmd):(h/(n+'.cfg')).write_text('\n'.join(cmd)+'\n')
 cmd=['wait 800','ac_main_menu','wait 200','ac_ui_options','wait 400','ac_ui_report ac_scaling','screenshot silent',
      'set ac_menu_scale 0.65','wait 200','ac_ui_report ac_scaling','screenshot silent','set ac_menu_scale 1']
 for n,x,y in [('auto',433,215),('hudOutline',433,399),('dropLimits',897,343)]:cmd += [mouse(n,'left_mouse_up',x,y)]
 for n,y in [('menuSlider',260),('hudSlider',306),('safeSlider',352)]:cmd += click(n,290,y)
 cmd += drag('playerFlinch','ac_player_flinch_percent',512,900,256)
 cmd += ['writeconfig interface_changed']+click('temporalOptions',710,113)
 cfg('probe',cmd)
 cmd=['wait 300','writeconfig graphics_entered','set ac_menu_scale 1','wait 200','ac_ui_report ac_temporal','screenshot silent','set ac_menu_scale 0.65','wait 200','ac_ui_report ac_temporal','screenshot silent']
 # Restore the interface font chosen before page navigation (without resetting the page).
 cmd += ['exec font_restore.cfg']
 for n,x,y in [('temporalAA',433,215),('ambientOcclusion',433,275),('modelShadows',433,335),('mist',897,215),('worldBlood',897,275),('bodyWounds',897,335),('corpseEffects',897,395)]:cmd += [mouse(n,'left_mouse_up',x,y)]
 cmd += drag('objectBlur','r_acObjectMotionBlur',48,436,430)
 cmd += ['writeconfig all_changed']+click('reset',850,510)
 cfg('graphics',cmd)
 # Menu slider click above selects .85 in the unchanged-width UI.
 cfg('font_restore',['set ac_menu_scale 0.85'])
 cfg('graphics_defaults',['wait 200','writeconfig graphics_restored','ac_ui_report ac_temporal','screenshot silent']+click('interfaceOptions',240,113))
 cfg('interface_return',['wait 200','ac_ui_report ac_scaling']+click('reset',850,510))
 cfg('interface_defaults',['wait 200','writeconfig restored','ac_ui_report ac_scaling','screenshot silent']+click('back',80,510))
 cfg('finish',['wait 200','ac_ui_report main','echo OPTIONS_LAYOUT_DONE','quit'])
 args=[str(exe)]
 settings=dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,cl_playintro=0,ac_campaign_mode=1,r_fullscreen=0,r_mode=-1,r_customwidth=width,r_customheight=height,com_maxfps=60,com_maxfpsUnfocused=60)
 settings.update(defaults)
 for k,v in settings.items():args+=['+set',k,str(v)]
 with (out/f'{case}-stdout.log').open('w') as stream:proc=subprocess.run(args+['+exec','probe.cfg'],cwd=rt,timeout=75,stdout=stream,stderr=subprocess.STDOUT)
 log=(h/'qconsole.log').read_text(encoding='latin1')
 assert proc.returncode==0 and 'OPTIONS_LAYOUT_DONE' in log and 'AC_UI_CURRENT main' in log
 errors=[s for s in log.splitlines() if any(t in s for t in ['UI EXCEPTION','Unknown command','Invalid event','Failed to find resource'])];assert not errors,errors
 for menu in sources:
  roots=re.findall(r'AC_UI_ROOT '+menu+r' ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',log)
  assert len(roots)>=3 and len(set(roots))==1,(menu,roots)
  for chunk in log.split('AC_UI_ROOT '+menu)[1:]:
   rects=[]
   for name,*values in re.findall(r'AC_UI_CHILD (\S+) ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',chunk.split('AC_UI_CURRENT',1)[0]):
    x,y,w,t=map(float,values);assert x>=0 and y>=0 and x+w<=960*scale+.1 and y+t<=540*scale+.1,(name,values)
    if not name.endswith('Panel'):rects.append((name,x,y,w,t))
   for i,(n,x,y,w,t) in enumerate(rects):
    for m,bx,by,bw,bt in rects[i+1:]:assert min(x+w,bx+bw)-max(x,bx)<=.1 or min(y+t,by+bt)-max(y,by)<=.1,(n,m)
 def settings_at(n):return {k:float(v) for k,v in re.findall(r'seta (\w+) "([0-9.]+)"',(h/f'configs/{n}.cfg').read_text()) if k in defaults}
 first=settings_at('interface_changed');changed=settings_at('all_changed');partial=settings_at('graphics_restored');restored=settings_at('restored')
 assert settings_at('graphics_entered')==first
 assert all(first[k]!=v for k,v in interface.items()),first
 assert all(first[k]==v for k,v in graphics.items()),first
 assert all(changed[k]!=v for k,v in graphics.items()),changed
 assert all(partial[k]==v for k,v in graphics.items()),partial
 assert all(partial[k]==changed[k] for k in interface),partial
 assert all(restored[k]==v for k,v in defaults.items()),restored
 for cv in ['ac_player_flinch_percent','r_acObjectMotionBlur']:
  values=[float(v) for v in re.findall(r'"'+cv+r'" is:"([^" ]+)',log)]
  assert len(values)>90 and set(values)==set(range(0,101,10)),(cv,values)
 images=[]
 for i,f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
  target=out/f'{case}-{folder}-{i}.png';Image.open(f).save(target);images.append(target.relative_to(R).as_posix())
 assert len(images)==6,images
 results.append(dict(game=game,resolution=[width,height],scoped_defaults=True,controls_changed=changed,navigation=True,ten_percent_steps=True,overlap_free=True,images=images))
 print('PASS',folder,width,height,flush=True)
assert hashes()==before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=digest(exe),packages=packages,cases=results,personal_files_unchanged=len(before)),indent=2)+'\n')
