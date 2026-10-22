"""Native cross-context render handoff probes; isolated profiles and Win32 window coverage."""
import argparse, ctypes as c, hashlib, json, re, shutil, subprocess, time
from ctypes import wintypes as w
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--fullscreen', action='store_true')
ap.add_argument('--mode-switch', action='store_true', help='1280x720 fullscreen instead of native desktop mode')
ap.add_argument('--quick', action='store_true', help='Only AA to SH menu')
a=ap.parse_args()
r=Path(__file__).resolve().parents[1]
rt=r/'runtime-local/CP09-r1'
out=r/'generated-local/CP09'/a.run
out.mkdir(parents=True,exist_ok=False)
bin=out/'bin';bin.mkdir()
for f in rt.glob('*.dll'): shutil.copy2(f,bin/f.name)
engine=r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'
shutil.copy2(engine,bin/engine.name)
user=c.windll.user32; kernel=c.windll.kernel32
callback=c.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
user.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)]
user.GetClassNameW.argtypes=[w.HWND,w.LPWSTR,c.c_int]
user.IsWindowVisible.argtypes=[w.HWND]
user.IsIconic.argtypes=[w.HWND]
kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE
kernel.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD]
kernel.CloseHandle.argtypes=[w.HANDLE]

def windows():
    rows=[]
    @callback
    def visit(hwnd,_):
        name=c.create_unicode_buffer(80);pid=w.DWORD()
        user.GetClassNameW(hwnd,name,80)
        if name.value in ('SDL_app','AlliedCampaignTransition') and user.IsWindowVisible(hwnd) and not user.IsIconic(hwnd):
            user.GetWindowThreadProcessId(hwnd,c.byref(pid))
            rows.append((pid.value,name.value))
        return True
    user.EnumWindows(visit,0)
    return rows

def alive(pid):
    h=kernel.OpenProcess(0x100000,False,pid)
    if not h:return False
    result=kernel.WaitForSingleObject(h,0)==258
    kernel.CloseHandle(h);return result

results=[]
folders=['main','mainta','maintt']
cases=[(0,1,'menu'),(1,2,'menu'),(2,0,'menu'),(0,2,'e2l2'),(2,1,'t1l1'),(1,0,'m2l1')]
for source,target,dest in cases[:1] if a.quick else cases:
    p=r/'profiles-local/context-cover'/a.run/f'{source}-{target}-{dest}'
    for folder in folders:(p/folder).mkdir(parents=True,exist_ok=False)
    (p/folders[source]/'probe.cfg').write_text(f'wait 1500\nac_context {target} {dest}\n')
    (p/folders[target]/'ac_context_ready.cfg').write_text('wait 1800\nfinishloadingscreen\necho AC_COVER_TEST_DONE\nquit\n')
    args=[str(bin/engine.name)]
    settings=dict(com_target_game=source,fs_basepath=rt,fs_homepath=p,fs_steampath=rt,
                  fs_gogpath=rt,fs_microsoftstorepath=rt,net_enabled=0,logfile=2,developer=0,
                  ui_console=0,r_fullscreen=int(a.fullscreen),r_mode=-2 if a.fullscreen and not a.mode_switch else -1,
                  r_customwidth=1280,r_customheight=720,cl_playintro=0,ac_campaign_mode=1,
                  com_maxfps=60,com_maxfpsUnfocused=60)
    for key,value in settings.items():args+=['+set',key,str(value)]
    proc=subprocess.Popen(args+['+exec','probe.cfg'],cwd=rt)
    start=time.monotonic();child=None;events=set();cover_seen=False;gaps=0;samples=0;presented=False
    helper_pids=set()
    while time.monotonic()-start<65:
        logs='\n'.join(f.read_text(encoding='latin1') for f in p.rglob('qconsole.log'))
        match=re.search(r'AC_CONTEXT_RESTART[^\n]+child=(\d+)',logs)
        if match:child=int(match[1])
        events.update(line for line in logs.splitlines() if 'AC_TRANSITION_' in line or 'AC_CONTEXT_RESTART' in line)
        visible=windows()
        covers=[pid for pid,cls in visible if cls=='AlliedCampaignTransition']
        helper_pids.update(covers)
        if covers:cover_seen=True
        if 'AC_TRANSITION_PRESENTED' in logs:presented=True
        # Cover must exist before old window disappears and through the first
        # presented frame. No input or personal profile is touched by this probe.
        if cover_seen and not presented:
            samples+=1
            if not covers and not any(pid in (proc.pid,child) for pid,cls in visible):gaps+=1
        if child and 'AC_COVER_TEST_DONE' in logs and not alive(child):break
        time.sleep(.01)
    else:raise AssertionError('Context did not finish: '+str(p))
    proc.wait(timeout=5)
    time.sleep(.1)
    row=dict(source=source,target=target,destination=dest,fullscreen=a.fullscreen,
             cover_seen=cover_seen,uncovered_samples=gaps,coverage_samples=samples,
             presented=presented,events=sorted(events),helpers_exited=all(not alive(pid) for pid in helper_pids))
    results.append(row)
    (out/'result.json').write_text(json.dumps(dict(engine_sha256=hashlib.sha256(engine.read_bytes()).hexdigest(),cases=results),indent=2))
    print(json.dumps(row),flush=True)
    assert cover_seen and presented and gaps==0 and row['helpers_exited']
    assert any('ready=1' in event for event in events)
print('PASS: selected context directions and cover lifecycle')
