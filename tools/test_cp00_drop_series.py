"""Measure unchanged mission drop behavior using isolated, controlled target series."""
import argparse,json,re,shutil,subprocess
from pathlib import Path
from inventory_cp00 import sha,save
def verify(result, requested_skill):
 assert result['completed'] and result['exit_code']==0 and not result['errors']
 assert result['observed_skill'] and all(float(v)==requested_skill for v in result['observed_skill'])
 for t in result['steps']:
  a,b,c=[t['phases'][p] for p in ['before','dead','corpse']]
  assert a['deaths']==['0'] and b['deaths']==['1'] and c['deaths']==['1']
  assert int(b['stats']['ui_NumEnemysKilled'])==int(a['stats']['ui_NumEnemysKilled'])+1
  assert int(c['stats']['ui_NumShotsFired'])>int(b['stats']['ui_NumShotsFired'])
  assert all(c['stats'][k]==b['stats'][k] for k in ['ui_NumHits','ui_NumEnemysKilled','ui_NumComplete'])
  assert not t['new_after_corpse_fire']

ap=argparse.ArgumentParser()
ap.add_argument('game',choices=['AA','SH','BT'])
ap.add_argument('--run-id',required=True)
ap.add_argument('--verify-only',action='store_true')
ap.add_argument('--skill',type=int,choices=[0,1,2],default=1)
ap.add_argument('--candidate',default='CP00-r4')
ap.add_argument('--fresh-map',choices=['e1l3','e2l2','e3l1'])
args=ap.parse_args();assert args.fresh_map or args.game=='AA' or args.skill==1, 'Nondefault saved-game skill requires separate verification'
assert re.fullmatch(r'[A-Za-z0-9-]+',args.run_id)
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local'/args.candidate
checkpoint='CP00' if args.candidate=='CP00-r4' else 'CP00a'
if args.verify_only:
 verify(json.loads((r/f'checkpoints/{checkpoint}/{args.run_id}-{args.game}.json').read_text(encoding='utf-8')),args.skill)
 print('PASS existing evidence:',args.run_id,args.game,flush=True)
 raise SystemExit(0)
folder,mapname,reference={'AA':('main','m2l1',None),'SH':('mainta','t1l2','profiles-local/CP00-r4/SH/mainta/save/omconfig/t1l20005.sav'),'BT':('maintt','e2l2','profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/save/omconfig/cp00_foot_ready.sav')}[args.game]
if args.fresh_map:
 assert args.game=='BT'
 mapname=args.fresh_map;reference=None
profile=r/f'profiles-local/{args.candidate}/{args.run_id}-{args.game}';home=profile/folder
assert not profile.exists()
refs=[]
if args.game=='BT' and reference:
 ready=json.loads((r/'checkpoints/CP00/r4-bt-foot-e2l2.json').read_text(encoding='utf-8'))
 assert ready['foot_controls_verified'] and ready['completed'] and ready['exit_code']==0
 for ext in ['.sav','.ssv','.tga']:
  source=(r/reference).with_suffix(ext)
  e=next(e for e in ready['evidence'] if e['path']==source.relative_to(r).as_posix());assert sha(source)==e['sha256']
(home/'cp00').mkdir(parents=True)
start='map '+mapname
mode_command=['difficultyEasy','difficultyMedium','difficultyHard'][args.skill]
if reference:
 (home/'save/omconfig').mkdir(parents=True)
 for ext in ['.sav','.ssv','.tga']:
  source=(r/reference).with_suffix(ext);dest=home/('save/omconfig/cp00_reference'+ext);shutil.copy2(source,dest)
  refs.append(dict(path=source.relative_to(r).as_posix(),sha256=sha(source)))
 start='loadgame cp00_reference'
fixture=(r/'tools/cp00_baseline_fixture.scr').read_text(encoding='utf-8')
# Extend snapshots with ownerless items, so carried weapons are not counted as drops.
needle='if ((local.distance < 700) && (local.ent.model != NIL))'
replacement='if ((local.distance < 700) && (local.ent.model != NIL) && (local.ent.owner == NULL))\n                println ("CP00_UNOWNED id=" + local.ent.entnum + " class=" + local.ent.classname + " model=" + local.ent.model + " origin=" + local.ent.origin)\n            if ((local.distance < 700) && (local.ent.model != NIL))'
fixture=fixture.replace(needle,replacement)
(home/'cp00/aim.scr').write_text('main:\n    waitthread cp00/base.scr::aim_corpse\nend\n',encoding='ascii')
(home/'cp00/remove.scr').write_text('main:\n    if (level.cp00_subject != NULL)\n        level.cp00_subject remove\nend\n',encoding='ascii')
(home/'cp00/base.scr').write_text(fixture,encoding='ascii')
def snap(n,phase):
 label=f'step{n}_{phase}'
 (home/f'cp00/{label}.scr').write_text(f'main:\n    waitthread cp00/base.scr::snapshot {label}\nend\n',encoding='ascii')
 return [f'echo CP00_BEGIN_{label}',f'script player exec cp00/{label}.scr','script player stats','wait 200','ui_NumShotsFired','ui_NumHits','ui_NumEnemysKilled','ui_NumComplete',f'echo CP00_END_{label}']
for n in range(1,10):
 gun='Mauser KAR 98K' if n<=6 else 'MP40'
 f=fixture.replace('gun "Mauser KAR 98K"',f'gun "{gun}"').replace('exec cp00/combat.cfg',f'exec cp00/fire{n}.cfg')
 f=f.replace('main:', 'main:\n    if (getcvar(skill) != \"'+str(args.skill)+'\")\n    {\n        println \"CP00_SKILL_MISMATCH\"\n        end\n    }',1)
 (home/f'cp00/spawn{n}.scr').write_text(f,encoding='ascii')
 prepare=[f'echo CP00_STEP_{n}_START','set cp00_next "echo CP00_DROP_ABORTED; quit"',f'script player exec cp00/spawn{n}.scr','wait 1200','script player ammo pistol 100','reload','wait 2000',*snap(n,'before'),'vstr cp00_next']
 (home/f'cp00/step{n}.cfg').write_text('\n'.join(prepare)+'\n',encoding='ascii')
 fire=[*(['+attack','wait 120','-attack','wait 350']*7),*(['reload','wait 2000']+['+attack','wait 120','-attack','wait 350']*7 if args.fresh_map else []),'wait 1600',*snap(n,'dead'),'script player exec cp00/aim.scr','reload','wait 2000',*(['+attack','wait 120','-attack','wait 350']*3),'wait 800',*snap(n,'corpse')]
 if n in (1,6,9):fire+=['screenshot']
 fire+=['script player exec cp00/remove.scr','wait 100']
 if n==5:fire+=['savegame cp00_after_five','wait 1000','loadgame cp00_after_five','wait 3000','finishloadingscreen','wait 1500','skill']
 fire+=([f'exec cp00/step{n+1}.cfg'] if n<9 else ['savegame cp00_after_series','wait 1000','skill','echo CP00_DROP_DONE','quit'])
 (home/f'cp00/fire{n}.cfg').write_text('\n'.join(fire)+'\n',encoding='ascii')
(home/'series.cfg').write_text('\n'.join(['wait 1000',mode_command,start,'wait 3000','finishloadingscreen',('wait 60000' if args.fresh_map else 'wait 3000'),'ai_health_kar','ai_health_mp40points','g_droppeditemlife','skill','which global/loadout.scr',f'which maps/{mapname}.scr',*(['+moveright','wait 700','-moveright','wait 500'] if args.fresh_map else []),'exec cp00/step1.cfg'])+'\n',encoding='ascii')
settings=dict(com_target_game=str(['AA','SH','BT'].index(args.game)),fs_basepath=str(rt),fs_homepath=str(profile),fs_steampath=str(rt),fs_gogpath=str(rt),fs_microsoftstorepath=str(rt),net_enabled='0',logfile='2',developer='1',cheats='1',r_fullscreen='0',r_mode='-1',r_customwidth='1280',r_customheight='960',com_maxfps='60',com_maxfpsUnfocused='60',cl_playintro='0',ui_console='0',cg_fov='90',skill=str(args.skill))
cmd=[str(rt/'openmohaa.exe')]
for k,v in settings.items():cmd+=['+set',k,v]
proc=subprocess.Popen(cmd+['+exec','series.cfg'],cwd=rt)
timed_out=False
try:proc.wait(timeout=390)
except subprocess.TimeoutExpired:timed_out=True;proc.terminate();proc.wait(timeout=10)
log=(home/'qconsole.log').read_text(encoding='latin1');steps=[]
for n in range(1,10):
 phases={}
 for phase in ['before','dead','corpse']:
  label=f'step{n}_{phase}';m=re.search('CP00_BEGIN_'+label+r'(.*?)CP00_END_'+label,log,re.S);part=m.group(1) if m else ''
  items=[dict(id=int(a),kind=b,model=c,origin=d) for a,b,c,d in re.findall(r'CP00_UNOWNED id=(\d+) class=(\S+) model=(\S+) origin=([^\r\n]+)',part) if b not in ['Actor','Player']]
  phases[phase]=dict(stats=dict(re.findall(r'"(ui_\w+)" is:\s*"([^"^]*)',part)),items=items,deaths=re.findall(r'CP00_DEATHS (\d+)',part))
 before={(e['id'],e['model']) for e in phases['before']['items']};dead={(e['id'],e['model']) for e in phases['dead']['items']};corpse={(e['id'],e['model']) for e in phases['corpse']['items']}
 steps.append(dict(step=n,enemy_gun='kar98' if n<=6 else 'mp40',phases=phases,new_after_death=sorted(dead-before),new_after_corpse_fire=sorted(corpse-dead)))
errors=[line.split('] ',1)[-1] for line in log.splitlines() if any(t in line for t in ['Script Error','compile error','was not properly loaded','Unknown command'])]
baseline_warnings=[]
if args.fresh_map=='e2l2':
 baseline_log=(r/'profiles-local/CP00-r4/r4-bt-foot-e2l2/maintt/qconsole.log').read_text(encoding='latin1')
 known="^~^~^ Script Error : invalid waittill prespawn for 'Level'"
 assert baseline_log.count(known)==5
 if errors.count(known)==5:
  baseline_warnings=[known]*5;errors=[e for e in errors if e!=known]
result=dict(baseline_warnings=baseline_warnings,candidate=args.candidate,game=args.game,map=mapname,requested_skill=args.skill,observed_skill=re.findall(r'"skill" is:\s*"([^"^]*)',log),completed='CP00_DROP_DONE' in log,exit_code=proc.returncode,host_timeout=timed_out,scope='Six rifle then three MP40 spawned targets; natural player shots. Mission/actor drop controls and health counter never assigned. Save/load after fifth target. Only player ammo replenished for the diagnostic firing sequence.',steps=steps,errors=errors,reference_save=refs,visual_check='PENDING',engine_sha256=sha(rt/'openmohaa.exe'),wcr_package_fingerprint=json.loads((r/'third_party/wcr/revisions/CP00-r4.json').read_text())['package_fingerprint'],evidence=[dict(path=p.relative_to(r).as_posix(),sha256=sha(p)) for p in sorted(profile.rglob('*')) if p.is_file()])
save(r/f'checkpoints/{checkpoint}/{args.run_id}-{args.game}.json',result)
print(json.dumps(dict(game=args.game,completed=result['completed'],errors=errors,steps=[{k:v for k,v in t.items() if k!='phases'} for t in steps]),indent=2),flush=True)
verify(result,args.skill)
