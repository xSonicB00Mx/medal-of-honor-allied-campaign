"""Isolated native loadout, presentation and cross-campaign arsenal probes."""
from pathlib import Path
import argparse,json,shutil,subprocess,re,zipfile
from PIL import Image
a=argparse.ArgumentParser();a.add_argument('run');a.add_argument('--game',type=int,default=0);a.add_argument('--case',choices=['menu','arsenal','apply','standard','score','cycle','special','transition','mines','minecontact','retired','models','grenadefx'],default='menu');a.add_argument('--start',type=int,default=0);a.add_argument('--count',type=int,default=12);a.add_argument('--asset-override',type=Path);args=a.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP08-r1';p=r/'profiles-local/loadout'/args.run
p.mkdir(parents=True,exist_ok=False);b=p/'bin';b.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,b/f.name)
for n in ['openmohaa.exe','game.dll','cgame.dll']:shutil.copy2(r/'build-local/cp00-r3/RelWithDebInfo'/n,b/n)
for folder in ['main','mainta','maintt']:
 (p/folder/'probe').mkdir(parents=True)
 for f in (r/'generated-local/loadout/packages'/folder).glob('*.pk3'):shutil.copy2(f,p/folder/f.name)
 (p/folder/'save/omconfig').mkdir(parents=True)
 (p/folder/'save/omconfig/keep.sav').write_bytes(b'PERSONAL SAVE SENTINEL')
state='ACPROG1 32767 15 keep\n';(p/'ac_progress.dat').write_text(state)
h=p/['main','mainta','maintt'][args.game];weapons=json.loads((r/'mod/loadout/weapons.json').read_text())
if args.asset_override:shutil.copy2(args.asset_override,h/'zzzzzzzzzzzzzzzzz_AC_Test.pk3')
settings=dict(com_target_game=args.game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,cheats=1,ui_console=0,r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,com_maxfps=60,com_maxfpsUnfocused=60,cl_playintro=0,ac_campaign_mode=1)
cmd=['set autopaused 0','wait 1200']
if args.case=='retired':settings['ac_loadout_6']=44
if args.case=='menu':
 cmd+=['ac_loadout default','wait 500','ac_ui_report ac_loadout','screenshot silent']
 for slot,id in [(2,'ppsh_smg'),(3,'it_w_breda'),(1,'uk_w_l42a1')]:
  i=next(i for i,w in enumerate(weapons) if w['id']==id)
  cmd+=[f'ac_loadout select {slot} {i+1}','wait 1200','screenshot silent']
 cmd+=['ac_main_menu','wait 500','screenshot silent']
else:
 op,map=[(1,'m2l1'),(7,'t1l2'),(4,'e2l2')][args.game]
 settings.update(ac_operation=op,ac_replay=2 if args.case=='score' else 0 if args.case=='standard' else 1,ac_loadout_authorized=int(args.case not in ['standard','score']),ac_expected_map=map)
 selected=next(i for i,w in enumerate(weapons) if w['id']=='it_w_moschetto')+1
 settings['ac_loadout_2']=selected if args.case in ['apply','standard','score','transition'] else 0
 fixture='main:\n $player nodamage\n $player give models/weapons/thompsonsmg.tik\n $player use models/weapons/thompsonsmg.tik\nend\n'
 (h/'probe/ready.scr').write_text(fixture)
 (h/'probe/empty.scr').write_text('main:\n local.weapon = $player getactiveweap 0\n local.weapon clip_empty\nend\n')
 # Expansion introductions keep weapons holstered while their radio scene runs.
 cmd += [f'map {map}','wait 4500','finishloadingscreen','script player skipcinematic','wait 3000','script player exec probe/ready.scr','wait 45000' if args.game else 'wait 3500']
 if args.case=='arsenal':
  for w in weapons[args.start:args.start+args.count]:
   cmd += [f'echo AC_TEST_WEAPON {w["id"]}',f'script player give {w["model"]}']
   cmd += [f'script player ammo {t} 100' for t in ['pistol','rifle','smg','mg','grenade','agrenade','heavy','shotgun','landmine','smokegrenade','riflegrenade']]
   cmd += [f'script player use {w["model"]}','wait 2100','echo AC_BEFORE','script player state','screenshot silent','+attack','wait 700','-attack','wait 1800','echo AC_AFTER','script player state']
   if w['id']=='m1_garand':cmd+=['script player exec probe/empty.scr','wait 200']
   cmd+=['reload','wait 5000','echo AC_RELOADED','script player state']
 elif args.case=='grenadefx':
  cmd += ['set debugSound 2','set s_show_sounds 1']
  for w in [w for w in weapons if w['slot']==4]:
   cmd += [f'echo AC_GRENADE {w["id"]}', f'script player give {w["model"]}']
   cmd += [f'script player ammo {t} 10' for t in ['grenade','agrenade','smokegrenade']]
   cmd += [f'script player use {w["model"]}','wait 2100','+attack','wait 700','-attack','wait 34000' if w['id']=='it_w_bomba' else 'wait 7000','screenshot silent']
  cmd += ['echo AC_GRENADE_END']
 elif args.case=='models':
  for name in ['fg42','g43','svt_rifle','delisle','it_w_breda','ppsh_smg']:
   model=next(w['model'] for w in weapons if w['id']==name)
   cmd += [f'script player give {model}',f'script player use {model}','wait 2300',f'echo AC_MODEL {name}','set r_uselod 1','wait 200','screenshot silent','set r_uselod 0','wait 200','screenshot silent']
  for name in ['fg42','g43','svt_rifle']:
   choice=next(i+1 for i,w in enumerate(weapons) if w['id']==name)
   cmd += [f'ac_loadout select 1 {choice}','wait 800','screenshot silent']
 elif args.case in ['mines','minecontact']:
  (h/'probe/mine.scr').write_text('main:\n if ($landmine != NULL)\n {\n  println AC_MINE_PRESENT\n  local.pos = $landmine.origin\n  $player.origin = $player.origin + ( 0 128 0 )\n  local.actor = spawn models/human/german_wehrmact_soldier.tik origin local.pos\n  local.actor ai_off\n  local.actor.health = 20\n  waitframe\n  $landmine doTouch local.actor\n  wait 2\n  if (!isalive local.actor)\n   println AC_MINE_KILLED_ACTOR\n }\nend\n')
  if args.case=='minecontact':
   # Exercise the actual broad-phase contact scan used by actor movement.
   probe=h/'probe/mine.scr'
   probe.write_text(probe.read_text().replace('local.actor ai_off', 'local.actor ai_on').replace('$landmine doTouch local.actor','local.actor.origin = local.pos'))
  cmd+=['script player give models/weapons/gr_w_minedetector.tik','script player ammo landmine 10','script player use models/weapons/gr_w_minedetector.tik','wait 2200','+attack','wait 700','-attack','wait 2000','savegame mine','wait 500','loadgame mine','wait 3500','finishloadingscreen','script player exec probe/mine.scr','wait 6500','screenshot silent']
 elif args.case=='special':
  (h/'probe/turret.scr').write_text('main:\n if ($player.turret != NULL)\n {\n  println AC_TURRET_MOUNTED\n }\nend\n')
  cmd += ['script player give models/weapons/kar98_mortar.tik','script player ammo riflegrenade 10','script player use models/weapons/kar98_mortar.tik','wait 2200','echo AC_SECONDARY_BEFORE','script player state','+attacksecondary','wait 300','-attacksecondary','wait 3000','+attack','wait 500','-attack','wait 2200','echo AC_SECONDARY_AFTER','script player state','screenshot silent','script player give models/weapons/mg42carryable.tik','script player use models/weapons/mg42carryable.tik','wait 2200','+attacksecondary','wait 700','-attacksecondary','wait 3000','script player exec probe/turret.scr','screenshot silent','+attack','wait 2000','-attack','screenshot silent','savegame special','wait 500','loadgame special','wait 3500','finishloadingscreen','script player exec probe/turret.scr']
 elif args.case=='transition':
  assert args.game==0
  (h/'probe/transition.scr').write_text('main:\n $player give models/weapons/mp40.tik\n bsptransition m2l2a\nend\n')
  # Leave the command buffer empty so the game's queued gamemap can execute.
  # A test-only hook in the next map schedules verification after its spawn.
  native=''
  for archive in sorted((rt/'main').glob('*.pk3')):
   with zipfile.ZipFile(archive) as z:
    if 'maps/m2l2a.scr' in z.namelist():native=z.read('maps/m2l2a.scr').decode('latin1').replace('\r','')
  native,count=re.subn(r'(?im)^(\s*main:[^\n]*\n)',r'\1 exec probe/after.scr\n',native,count=1);assert count==1
  (h/'maps').mkdir();(h/'maps/m2l2a.scr').write_text(native,encoding='latin1')
  (h/'probe/after.scr').write_text('main:\n println AC_TRANSITION_HOOK\n stuffsrv "exec probe_next.cfg"\nend\n')
  with zipfile.ZipFile(h/'zzzzzzzzzzzzzzzzz_AC_Test.pk3','w') as z:z.writestr('maps/m2l2a.scr',native)
  (h/'probe_next.cfg').write_text('wait 3000\nfinishloadingscreen\nset autopaused 0\nwait 8000\necho AC_NEXT_LEVEL\nscript player state\nac_progress_report\nscreenshot silent\necho AC_LOADOUT_TEST_DONE\nquit\n')
  cmd+=['set g_maxintermission 5','script player state','script player exec probe/transition.scr']
 elif args.case=='cycle':
  (h/'probe/pickup.scr').write_text('main:\n local.w = spawn models/weapons/mp40.tik\n local.w.origin = $player.origin + ( 0 0 16 )\n wait 0.5\n local.w = spawn models/weapons/sten.tik\n local.w.origin = $player.origin + ( 0 0 16 )\n wait 0.5\nend\n')
  cmd += ['script player exec probe/pickup.scr','wait 500']
  for _ in range(4):cmd+=['useweaponclass smg','wait 1800','script player state','screenshot silent']
 else:cmd+=['script player state','screenshot silent','savegame loadout','wait 500','loadgame loadout','wait 3500','finishloadingscreen','script player state','screenshot silent'] if args.case!='score' else ['script player state','screenshot silent']
if args.case=='retired':cmd+=['ac_loadout view 6','wait 500','ac_loadout select 6 44','wait 500','writeconfig retired_verified','screenshot silent']
if args.case!='transition':cmd+=['echo AC_LOADOUT_TEST_DONE','quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
command=[str(b/'openmohaa.exe')]
for k,v in settings.items():command+=['+set',k,str(v)]
proc=subprocess.run(command+['+exec','probe.cfg'],cwd=rt,timeout=300)
log=(h/'qconsole.log').read_text(encoding='latin1')
errors=[s for s in log.splitlines() if re.search(r'Script Error|Invalid event|Unknown command|command not available|TIKI.*[Ee]rror|could not find|[Cc]ouldn.t (?:load|find)|[Mm]issing animation|[Nn]ot found',s)]
for f in (h/'screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
report=dict(case=args.case,game=args.game,exit=proc.returncode,done='AC_LOADOUT_TEST_DONE' in log,errors=errors,events=[s for s in log.splitlines() if 'AC_LOADOUT' in s or 'AC_TEST_WEAPON' in s],progress_unchanged=(p/'ac_progress.dat').read_text()==state)
if args.case=='arsenal':
 checks=[]
 for block in re.split('AC_TEST_WEAPON ',log)[1:]:
  name=block.splitlines()[0]; w=next(w for w in weapons if w['id']==name)
  rows=re.findall(r'AC_WEAPON_STATE model=(\S+) active=1 clip=(-?\d+) reserve=(\d+) secondary=(\d+)',block)
  selected=len(rows)==3 and all(x[0]==w['model'] for x in rows)
  fired=selected and (w['id']=='mg42carryable' or int(rows[1][1])+int(rows[1][2])<int(rows[0][1])+int(rows[0][2]) or int(rows[2][2])<int(rows[0][2]))
  reloaded=selected and (w['slot'] in [4,6] or int(rows[2][1])>=int(rows[0][1]))
  checks.append(dict(weapon=name,selected=selected,fired=fired,reloaded=reloaded,states=rows))
 report['weapons']=checks
if args.case=='grenadefx':
 report['grenade_sounds']={}
 report['grenade_audio_checks']=[]
 for block in re.split('AC_GRENADE ',log)[1:]:
  name=block.splitlines()[0];report['grenade_sounds'][name]=re.findall(r'AC_SOUND_PLAY alias=(\S+) file=(\S+) volume=(\S+)',block)
  expected={'m18_smoke_grenade':'smokegrenade_exp_start','nebelhandgranate':'nebelsmokegrenade_exp_start','rdg-1_smoke_grenade':'rdg1smokegrenade_exp_start','it_w_bombabreda':'smokegrenade_exp_start'}.get(name,'grenade_explode')
  sounds=[(file,float(volume)) for alias,file,volume in report['grenade_sounds'][name] if alias==expected]
  mixed=any(any('OpenAL:' in line and file.lower() in line.lower() and 'vol ' in line for line in block.splitlines()) for file,volume in sounds)
  report['grenade_audio_checks'].append(dict(weapon=name,alias=expected,dispatched=bool(sounds),positive_volume=all(volume>0 for file,volume in sounds),mixed=mixed))
if args.case=='cycle':
 report['cycle']=re.findall(r'AC_WEAPON_STATE model=(\S+) active=1',log)
(p/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
assert proc.returncode==0 and report['done'] and report['progress_unchanged']
if args.case=='arsenal':assert all(x['selected'] and x['fired'] and x['reloaded'] for x in report['weapons']),report['weapons']
if args.case=='cycle':assert report['cycle']==['models/weapons/mp40.tik','models/weapons/sten.tik','models/weapons/thompsonsmg.tik','models/weapons/mp40.tik'],report['cycle']
if args.case=='grenadefx':assert len(report['grenade_audio_checks'])==9 and all(x['dispatched'] and x['positive_volume'] and x['mixed'] for x in report['grenade_audio_checks']),report['grenade_audio_checks']
if args.case=='special':
 assert log.count('AC_TURRET_MOUNTED')==2
 before=log.split('AC_SECONDARY_BEFORE')[1].split('AC_SECONDARY_AFTER')[0]
 after=log.split('AC_SECONDARY_AFTER')[1]
 ammo=lambda s:int(re.search(r'AC_WEAPON_STATE model=models/weapons/kar98_mortar.tik active=1 clip=\d+ reserve=\d+ secondary=(\d+)',s)[1])
 assert ammo(after)<ammo(before)
if args.case=='transition':
 after=log.split('AC_NEXT_LEVEL')[1]
 assert 'map=m2l2a first=0' in log and 'operation=1 replay=1' in after
 assert 'model=models/weapons/mp40.tik' in after and 'model=models/weapons/it_w_moschetto.tik' in after
if args.case in ['mines','minecontact']:assert 'AC_MINE_PRESENT' in log and 'AC_MINE_KILLED_ACTOR' in log and not any('Script Error' in e for e in errors)
for folder in ['main','mainta','maintt']:assert (p/folder/'save/omconfig/keep.sav').read_bytes()==b'PERSONAL SAVE SENTINEL'

if args.case=='retired':
 assert 'AC_LOADOUT_GIVE' not in log
 assert 'AC_WEAPON_STATE model=models/weapons/mg42carryable.tik' not in log
 menu=(h/'ui/ac_loadout.urc').read_text()
 assert 'MG42' not in menu and 'selected=0 custom=0' in log
 assert re.search(r'seta ac_loadout_6 "0"',(h/'configs/retired_verified.cfg').read_text())
