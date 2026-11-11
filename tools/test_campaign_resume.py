"""New campaign, original briefing skip, native quit, cross-context Continue."""
import json,subprocess,time,hashlib,zipfile,atexit
from pathlib import Path
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP08-r1';p=R/'profiles-local/CP08-r1/resume-e2e-r9';assert not p.exists();p.mkdir(parents=True);out=[]
for folder in ['main','mainta','maintt']:
 h=p/folder;h.mkdir();(h/'ac_context_ready.cfg').write_text('set autopaused 0\nwait 4500\nfinishloadingscreen\nset cg_fov 90\n+attack\nwait 500\n-attack\nwait 500\ncg_fov\nac_progress_report\n')
fixture=rt/'main/zzzzzz_AC_resume_probe.pk3';assert not fixture.exists()
with zipfile.ZipFile(fixture,'w') as z:
 original=(R/'generated-local/CP06/inventory/AA/maps/briefing/briefing1.scr').read_text(encoding='latin1')
 assert '$player stufftext "spmap m1l1"' in original
 z.writestr('maps/briefing/briefing1.scr',original.replace('$player stufftext "spmap m1l1"','stuffcmd "spmap m1l1; wait 4000; finishloadingscreen; cg_fov; ac_progress_report; echo AC_NATIVE_STOP; quit"'))
atexit.register(lambda:fixture.unlink(missing_ok=True))
def phase(name,game,action,condition):
 cmd=[str(rt/'openmohaa.exe')]
 settings=dict(com_target_game=game,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,autopaused=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1)
 for k,v in settings.items():cmd+=['+set',k,str(v)]
 proc=subprocess.Popen(cmd+['+wait','1200','+'+action.split()[0]]+action.split()[1:],cwd=rt);events=[];seen=set();start=time.monotonic();ok=False
 while time.monotonic()-start<50:
  time.sleep(.1)
  for f in p.rglob('qconsole.log'):
   for x in f.read_text(encoding='latin1').splitlines():
    if ('AC_' in x or 'cg_fov' in x) and x not in seen:seen.add(x);events.append(x)
  if condition(events) and any('AC_NATIVE_STOP' in x for x in events):ok=True;time.sleep(2);break
 proc.wait(timeout=5)
 out.append(dict(phase=name,passed=ok,events=events,stop='Isolated briefing completion appends loading-screen dismissal, diagnostics and native quit; no gameplay completion claimed'))
 (R/'checkpoints/CP08/resume-e2e.json').write_text(json.dumps(dict(engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),cases=out,state=(p/'ac_progress.dat').read_text()),indent=2)+'\n')
 assert ok,name
phase('new-campaign',0,'ac_mission 0',lambda e:any('AC_MISSION_ENTRY aa_torch m1l1' in x for x in e) and (p/'main/save/omconfig/m1l10000.acmeta').exists())
assert (p/'ac_progress.dat').read_text().split()[1:3]==['0','0']
for f in p.rglob('qconsole.log'):f.rename(f.with_name('new-campaign.log'))
for f in p.rglob('ac_context_ready.cfg'):f.write_text('set autopaused 0\nwait 4500\nfinishloadingscreen\ncg_fov\nac_progress_report\necho AC_NATIVE_STOP\nquit\n')
phase('continue-from-other-context',1,'ac_continue',lambda e:any('AC_SAVE_ACCEPT context=0 map=m1l1' in x for x in e) and any('cg_fov' in x and '90' in x for x in e))
assert (p/'ac_progress.dat').read_text().split()[1:3]==['0','0']
print('New campaign, original briefing skip and cross-context Continue passed.')
