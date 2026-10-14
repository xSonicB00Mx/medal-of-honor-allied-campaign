"""Load every inventoried section independently; do not claim natural playthroughs."""
import hashlib,json,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];rt=R/'runtime-local/CP06-r1'
inventory=json.loads((R/'generated-local/CP06/inventory/maps.json').read_text())
results=[]
for game,rows in inventory.items():
    folder=dict(AA='main',SH='mainta',BT='maintt')[game]
    for row in rows:
        m=row['map'];p=R/'profiles-local/CP06-r1'/('start-'+game+'-'+m);h=p/folder
        if p.exists():continue
        h.mkdir(parents=True)
        (h/'probe.cfg').write_text('\n'.join(['wait 3000','finishloadingscreen','which maps/'+m+'.scr','savegame ac_start','wait 500','echo AC_START_DONE','quit'])+'\n')
        cmd=[str(rt/'openmohaa.exe')]
        for k,v in dict(com_target_game=['AA','SH','BT'].index(game),fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,r_fullscreen=0,r_mode=-1,r_customwidth=1280,r_customheight=720,cl_playintro=0,com_maxfps=60,com_maxfpsUnfocused=60,ac_campaign_mode=1).items():cmd+=['+set',k,str(v)]
        t=time.monotonic()
        try:proc=subprocess.run(cmd+['+map',m,'+exec','probe.cfg'],cwd=rt,timeout=40);rc=proc.returncode
        except subprocess.TimeoutExpired:rc='timeout'
        log=(h/'qconsole.log').read_text(encoding='latin1') if (h/'qconsole.log').exists() else ''
        result=dict(game=game,map=m,exit=rc,commands_completed='AC_START_DONE' in log,save_triplet=all((h/('save/omconfig/ac_start.'+e)).exists() for e in ['sav','ssv','tga','acmeta']),script_errors=[l for l in log.splitlines() if 'Script Error :' in l],seconds=round(time.monotonic()-t,2))
        results.append(result);print(game,m,rc,result['save_triplet'],len(result['script_errors']),flush=True)
        (R/'checkpoints/CP06/map-starts.json').write_text(json.dumps(dict(engine_sha256=hashlib.sha256((rt/'openmohaa.exe').read_bytes()).hexdigest(),results=results,scope='Independent starts only; no natural completion claim'),indent=2)+'\n')
