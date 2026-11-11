"""Verify the transition helper exits when its isolated destination process dies."""
import ctypes as c, json, subprocess, sys, time
from ctypes import wintypes as w
from pathlib import Path

r=Path(__file__).resolve().parents[1]
engine=r/'build-local/cp00-r3/RelWithDebInfo/openmohaa.exe'
kernel=c.windll.kernel32
kernel.CreateEventW.argtypes=[c.c_void_p,w.BOOL,w.BOOL,w.LPCWSTR]
kernel.CreateEventW.restype=w.HANDLE
kernel.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD]
kernel.CloseHandle.argtypes=[w.HANDLE]
child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],creationflags=subprocess.CREATE_NO_WINDOW)
ready=kernel.CreateEventW(None,True,False,f'Local\\OpenMOHAA_AC_{child.pid}_ready')
cover=None
try:
    cover=subprocess.Popen([str(engine),'--ac-transition',str(child.pid),'0','0','320','180','0'],creationflags=subprocess.CREATE_NO_WINDOW)
    assert kernel.WaitForSingleObject(ready,5000)==0,'Helper did not paint its window'
    start=time.monotonic()
    child.terminate();child.wait(timeout=5)
    assert cover.wait(timeout=5)==0
    result=dict(painted=True,destination_exit_cleanup=True,cleanup_seconds=time.monotonic()-start)
    output=r/'generated-local/CP09/context-cover-mode-final/failure.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
finally:
    if child.poll() is None:child.terminate();child.wait(timeout=5)
    if cover and cover.poll() is None:cover.terminate();cover.wait(timeout=5)
    kernel.CloseHandle(ready)
