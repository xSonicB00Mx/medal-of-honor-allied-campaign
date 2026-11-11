"""Native door, retired choices, HUD outline and persistence regression."""
from pathlib import Path
import json,shutil,subprocess,re,zipfile,sys
reanalyze="--reanalyze" in sys.argv
from PIL import Image
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1'
root=r/'profiles-local/loadout/preferences-r5';root.mkdir(parents=True,exist_ok=reanalyze)
ws=json.loads((r/'mod/loadout/weapons.json').read_text());results=[]
for game,folder in enumerate(['main','mainta','maintt']):
 p=root/folder;p.mkdir(exist_ok=reanalyze);b=p/'bin';b.mkdir(exist_ok=reanalyze)
 for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
 for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
 for base in ['main','mainta','maintt']:
  (p/base).mkdir(exist_ok=reanalyze)
  for kind in ['loadout','flinch']:
   for f in (r/f'generated-local/{kind}/packages'/base).glob('*.pk3'):shutil.copy2(f,p/base/f.name)
 h=p/folder
 (p/'ac_progress.dat').write_text('ACPROG1 32767 15 keep\n')
 # UI button actions append commands to the buffer; let startup drain before
 # continuing assertions. Append only a test continuation to the real command.
 with zipfile.ZipFile(next(h.glob('*_AC_Loadout.pk3'))) as z:menu=z.read('ui/main.urc').decode('latin1')
 assert 'stuffcommand "ac_loadout"' in menu and 'multiplayer_h' in menu
 menu=menu.replace('stuffcommand "ac_loadout"','stuffcommand "ac_loadout; exec stage2.cfg"')
 with zipfile.ZipFile(h/'zzzzzzzzzzzzzzzzz_AC_Probe.pk3','w') as z:z.writestr('ui/main.urc',menu)
 startup=['wait 800','ac_main_menu','wait 300','ac_ui_report main','widgetcommand loadout mouse_entered 690 230 0','wait 100','widgetcommand loadout left_mouse_down 690 230 1','widgetcommand loadout left_mouse_up 690 230 0']
 cmd=['wait 400','ac_ui_report ac_loadout','screenshot silent']
 for i,w in enumerate(ws):
  if not w.get('selectable',True):cmd += [f'set ac_loadout_{w["slot"]} {i+1}',f'ac_loadout view {w["slot"]}',f'ac_loadout_{w["slot"]}',f'ac_loadout select {w["slot"]} {i+1}',f'ac_loadout_{w["slot"]}']
 cmd += ['ac_loadout view 4','wait 300','screenshot silent','ac_ui_options','wait 300','ac_hud_outline','ac_ui_report ac_scaling','widgetcommand hudOutline left_mouse_up 430 470 0','wait 100','ac_hud_outline','writeconfig outline_on','screenshot silent','popmenu 0','popmenu 0','popmenu 0']
 if game==0:
  dest=h/'save/omconfig';dest.mkdir(parents=True,exist_ok=reanalyze)
  for f in (r/'profiles-local/loadout/life-replay-aa-r2/main/save/omconfig').glob('loadout_lifecycle.*'):shutil.copy2(f,dest/f.name)
  cmd+=['loadgame loadout_lifecycle']
 else:cmd += ['map '+['m2l1','t1l2','e2l2'][game]]
 cmd += ['wait 5000','finishloadingscreen','set autopaused 0','script player skipcinematic','wait 45000' if game else 'wait 4000','script player nodamage']
 for name in ['thompsonsmg','ppsh_smg','it_w_breda']:
  cmd += [f'script player give models/weapons/{name}.tik',f'script player use models/weapons/{name}.tik','wait 2200','script player state','set ac_hud_outline 0','wait 100','screenshot silent','set ac_hud_outline 1','wait 100','screenshot silent']
 cmd+=['writeconfig verified','echo PREFERENCES_DONE','quit']
 (h/'test.cfg').write_text('\n'.join(startup)+'\n')
 (h/'stage2.cfg').write_text('\n'.join(cmd)+'\n')
 settings=dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,cl_playintro=0,ui_console=0,ac_campaign_mode=1,ac_replay=1,ac_loadout_authorized=1,ac_operation=[1,7,4][game],r_fullscreen=0,r_mode=-1,r_customwidth=960,r_customheight=540,com_maxfps=60)
 args=[str(b/'openmohaa.exe')]
 for k,v in settings.items():args+=['+set',k,str(v)]
 proc=None if reanalyze else subprocess.run(args+['+exec','test.cfg'],cwd=rt,timeout=100,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 log=(h/'qconsole.log').read_text(encoding='latin1')
 assert (proc is None or proc.returncode==0) and 'PREFERENCES_DONE' in log
 assert 'AC_UI_CURRENT ac_loadout' in log,'door did not open LOADOUT'
 for name in ['thompsonsmg','ppsh_smg','it_w_breda']:
  assert f'AC_WEAPON_STATE model=models/weapons/{name}.tik active=1' in log,name
 values=re.findall(r'"ac_loadout_[46]" is:"([^" ]+)',log);assert len(values)==12 and set(values)=={'0'},values
 values=re.findall(r'"ac_hud_outline" is:"([^" ]+)',log);assert values==['0','1'],values
 menu=(h/'ui/ac_loadout.urc').read_text();assert 'Smoke' not in menu and 'Breda Grenade' not in menu and 'slot_6' not in menu
 for f in (h/'screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
 assert 'seta ac_hud_outline "1"' in (h/'configs/verified.cfg').read_text()
 assert 'seta ac_hud_outline "1"' in (p/'main/ac_preferences.cfg').read_text()
 errors=[l for l in log.splitlines() if any(s in l for s in ['Unknown command','Invalid event','Script Error'])]
 known=[l for l in errors if game==2 and "invalid waittill prespawn for 'Level'" in l]
 assert len(known)<=5 and len(errors)==len(known),errors
 # Restart the same isolated home in a different campaign; shared preference
 # must win without supplying the outline cvar on the command line.
 nextgame=(game+1)%3;nextfolder=['main','mainta','maintt'][nextgame]
 (p/nextfolder/'prefs.cfg').write_text('wait 500\nac_hud_outline\necho PREF_RESTART_DONE\nquit\n')
 restart=list(args);restart[restart.index('com_target_game')+1]=str(nextgame)
 proc2=subprocess.run(restart+['+exec','prefs.cfg'],cwd=rt,timeout=30,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 nextlog=(p/nextfolder/'qconsole.log').read_text(encoding='latin1')
 assert proc2.returncode==0 and 'PREF_RESTART_DONE' in nextlog
 assert re.findall(r'"ac_hud_outline" is:"([^" ]+)',nextlog)==['1']
 results.append(dict(game=folder,door_opened=True,retired_choices_default=True,outline_default_off_checkbox_on=True,persisted=True,known_native_warnings=errors))
 (root/'result.json').write_text(json.dumps(results,indent=2))
 print(folder,'passed',flush=True)
