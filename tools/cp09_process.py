"""Windows process-tree handles and memory sampling, without extra dependencies."""
import ctypes as C
from ctypes import wintypes as W

K = C.WinDLL("kernel32", use_last_error=True)
P = C.WinDLL("psapi", use_last_error=True)


class Entry(C.Structure):
    _fields_ = [("size", W.DWORD), ("usage", W.DWORD), ("pid", W.DWORD),
                ("heap", C.c_size_t), ("module", W.DWORD), ("threads", W.DWORD),
                ("parent", W.DWORD), ("priority", W.LONG), ("flags", W.DWORD),
                ("exe", W.WCHAR * 260)]


class Memory(C.Structure):
    _fields_ = [("size", W.DWORD), ("faults", W.DWORD)] + [
        (name, C.c_size_t) for name in ("peak", "rss", "peak_pool", "pool",
        "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile", "private")]


K.CreateToolhelp32Snapshot.argtypes = [W.DWORD, W.DWORD]
K.CreateToolhelp32Snapshot.restype = W.HANDLE
K.Process32FirstW.argtypes = [W.HANDLE, C.POINTER(Entry)]
K.Process32NextW.argtypes = [W.HANDLE, C.POINTER(Entry)]
K.CloseHandle.argtypes = [W.HANDLE]
K.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
K.OpenProcess.restype = W.HANDLE
K.GetExitCodeProcess.argtypes = [W.HANDLE, C.POINTER(W.DWORD)]
K.TerminateProcess.argtypes = [W.HANDLE, W.UINT]
P.GetProcessMemoryInfo.argtypes = [W.HANDLE, C.POINTER(Memory), W.DWORD]


def tree(parent, known):
    snap = K.CreateToolhelp32Snapshot(2, 0)
    if snap == W.HANDLE(-1).value:
        return
    rows = []
    try:
        entry = Entry()
        entry.size = C.sizeof(entry)
        ok = K.Process32FirstW(snap, C.byref(entry))
        while ok:
            rows.append((entry.pid, entry.parent, entry.exe))
            ok = K.Process32NextW(snap, C.byref(entry))
    finally:
        K.CloseHandle(snap)
    parents = {parent, *known}
    changed = True
    while changed:
        changed = False
        for pid, ppid, name in rows:
            if ppid in parents and pid not in parents:
                parents.add(pid)
                changed = True
                handle = K.OpenProcess(0x0400 | 0x0010 | 0x0001, False, pid)
                if handle:
                    known[pid] = Process(pid, name, handle)


class Process:
    def __init__(self, pid, name, handle):
        self.pid, self.name, self.handle = pid, name, handle

    def running(self):
        result = W.DWORD()
        return bool(K.GetExitCodeProcess(self.handle, C.byref(result))) and result.value == 259

    def memory(self):
        mem = Memory()
        mem.size = C.sizeof(mem)
        if self.running() and P.GetProcessMemoryInfo(self.handle, C.byref(mem), mem.size):
            return dict(rss=mem.rss, private=mem.private)

    def kill(self):
        if self.running():
            K.TerminateProcess(self.handle, 1)

    def close(self):
        K.CloseHandle(self.handle)
