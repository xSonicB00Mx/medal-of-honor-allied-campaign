"""Unified save catalog, ordering, duplicate slots and native cross-context loads.
Only copies are opened; source profile files are hash-checked afterwards.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, struct, subprocess, time
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('run');a=ap.parse_args()
r=Path(__file__).resolve().parents[1];rt=r/'runtime-local/CP09-r1'
out=r/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
profile=r/'profiles-local/unified-saves'/a.run
source=r/'profiles-local/CP08-r1/user'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p.relative_to(source).as_posix():digest(p) for p in source.rglob('*') if p.is_file()}
bin=out/'bin';bin.mkdir()
for f in rt.glob('*.dll'):shutil.copy2(f,bin/f.name)
engine=r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe';shutil.copy2(engine,bin/engine.name)
folders=['main','mainta','maintt'];fixtures=[]
for folder in folders:
    choices=sorted((source/folder/'save/omconfig').glob('*.ssv'))
    choices=[p for p in choices if p.with_suffix('.acmeta').exists() and b'briefing' not in p.with_suffix('.acmeta').read_bytes()]
    assert choices,folder
    fixtures.append(choices[0])

def seed(name,many=False):
    p=profile/name
    for game,folder in enumerate(folders):
        h=p/folder/'save/omconfig';h.mkdir(parents=True,exist_ok=False)
        for ext in ['.sav','.ssv','.tga','.acmeta']:
            f=fixtures[game].with_suffix(ext)
            if f.exists():shutil.copy2(f,h/('shared'+ext))
        data=bytearray((h/'shared.ssv').read_bytes());struct.pack_into('<i',data,4,1700000000+game*60)
        (h/'shared.ssv').write_bytes(data)
    if many:
        h=p/'main/save/omconfig';data=bytearray((h/'shared.ssv').read_bytes())
        for i in range(11):
            struct.pack_into('<i',data,4,1600000000+i)
            data[12:76]=(b'Long save title with "quotes" and \\slashes / 1234567890123456789').ljust(64,b'\0')[:64]
            (h/f'older_{i}.ssv').write_bytes(data);(h/f'older_{i}.sav').write_bytes(b'UI fixture only')
        (h/'truncated.ssv').write_bytes(b'bad');(h/'truncated.sav').write_bytes(b'bad')
        wrong=bytearray(data);wrong[2]=2
        (h/'wrong_game.ssv').write_bytes(wrong);(h/'wrong_game.sav').write_bytes(b'bad')
    return p

def launch(p,commands):
    (p/'main/test.cfg').write_text('\n'.join(commands)+'\n')
    args=[str(bin/engine.name)]
    values=dict(com_target_game=0,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,fs_gogpath=rt,
                fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=1,ui_console=0,
                r_fullscreen=0,r_mode=-1,r_customwidth=1920,r_customheight=1080,
                cl_playintro=0,ac_campaign_mode=1,com_maxfps=60,com_maxfpsUnfocused=60)
    for k,v in values.items():args+=['+set',k,str(v)]
    return subprocess.Popen(args+['+exec','test.cfg'],cwd=rt)

catalog=seed('catalog',True)
proc=launch(catalog,['wait 1400','ac_campaign','wait 400','ac_ui_report ac_campaign_operations',
                     'ac_saves','wait 500','ac_ui_report ac_saved_games','screenshot silent',
                     'ac_saves page 1','wait 500','screenshot silent','echo AC_CATALOG_DONE','quit'])
assert proc.wait(timeout=45)==0
log=(catalog/'main/qconsole.log').read_text(encoding='latin1')
rows=re.findall(r'AC_SAVE_LIST index=(\d+) game=(\d+) time=(\d+) slot=(\S+)',log)
assert len(rows)==14,rows
assert [int(x[2]) for x in rows]==sorted([int(x[2]) for x in rows],reverse=True)
assert [(x[1],x[3]) for x in rows[:3]]==[('2','shared'),('1','shared'),('0','shared')]
urc=(catalog/'main/ui/ac_campaign_operations.urc').read_text()
assert 'Saved Games' in urc and 'AA saves' not in urc and 'BT saves' not in urc
assert 'Script Error' not in log and 'Unknown command' not in log
for f in (catalog/'main/screenshots').glob('*.tga'):Image.open(f).save(f.with_suffix('.png'))
cases=[]
for game in range(3):
    p=seed(f'load-{game}')
    done='wait 1600\nfinishloadingscreen\necho AC_UNIFIED_LOAD_DONE\nquit\n'
    for folder in folders:(p/folder/'ac_context_ready.cfg').write_text(done)
    proc=launch(p,['wait 1200','ac_saves',f'ac_saves select {2-game}','ac_saves_load',
                   'wait 1800','finishloadingscreen','echo AC_UNIFIED_LOAD_DONE','quit'])
    deadline=time.monotonic()+70
    while time.monotonic()<deadline:
        target=p/folders[game]/'qconsole.log'
        text=target.read_text(encoding='latin1') if target.exists() else ''
        if 'AC_UNIFIED_LOAD_DONE' in text:break
        time.sleep(.1)
    else:raise AssertionError('Load timed out '+str(game))
    proc.wait(timeout=10);time.sleep(.5)
    text=target.read_text(encoding='latin1')
    assert f'AC_SAVE_ACCEPT context={game}' in text,text[-4000:]
    assert 'Game Loaded' in text and 'AC_SAVE_REJECT' not in text
    if game:assert 'AC_TRANSITION_PRESENTED' in text
    cases.append(dict(game=game,accepted=True,loaded=True,slot='shared'))
    print('Loaded shared slot in campaign',game,flush=True)
after={p.relative_to(source).as_posix():digest(p) for p in source.rglob('*') if p.is_file()}
assert before==after,'Personal profile changed'
report=dict(engine_sha256=digest(engine),catalog=rows,loads=cases,personal_files_unchanged=len(before))
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: chronological catalog, separate identical slots, paging, all three native loads')
