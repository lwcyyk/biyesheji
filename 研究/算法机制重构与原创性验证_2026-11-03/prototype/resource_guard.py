"""Per-worker guards. These are not a claim of full product W0 admission latency."""
import os,ctypes
def install():
 if os.name!='nt':return {'platform':os.name,'enforced':False}
 from ctypes import wintypes as W
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 k.GetCurrentProcess.restype=W.HANDLE;proc=k.GetCurrentProcess()
 k.GetProcessAffinityMask.argtypes=[W.HANDLE,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
 process=ctypes.c_size_t();system=ctypes.c_size_t();k.GetProcessAffinityMask(proc,ctypes.byref(process),ctypes.byref(system))
 bits=[i for i in range(64) if process.value&(1<<i)][:4];mask=sum(1<<i for i in bits)
 k.SetProcessAffinityMask.argtypes=[W.HANDLE,ctypes.c_size_t]
 affinity=bool(k.SetProcessAffinityMask(proc,mask))
 class Basic(ctypes.Structure):
  _fields_=[('process_time',ctypes.c_longlong),('job_time',ctypes.c_longlong),('flags',W.DWORD),('minws',ctypes.c_size_t),('maxws',ctypes.c_size_t),('active',W.DWORD),('affinity',ctypes.c_size_t),('priority',W.DWORD),('scheduling',W.DWORD)]
 class IO(ctypes.Structure):_fields_=[(x,ctypes.c_ulonglong) for x in ['readop','writeop','otherop','readbytes','writebytes','otherbytes']]
 class Extended(ctypes.Structure):_fields_=[('basic',Basic),('io',IO),('process_mem',ctypes.c_size_t),('job_mem',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
 k.CreateJobObjectW.argtypes=[ctypes.c_void_p,W.LPCWSTR];k.CreateJobObjectW.restype=W.HANDLE
 job=k.CreateJobObjectW(None,None);info=Extended();info.basic.flags=0x100;info.process_mem=8*1024**3
 k.SetInformationJobObject.argtypes=[W.HANDLE,ctypes.c_int,ctypes.c_void_p,W.DWORD]
 k.AssignProcessToJobObject.argtypes=[W.HANDLE,W.HANDLE]
 mem=bool(k.SetInformationJobObject(job,9,ctypes.byref(info),ctypes.sizeof(info))) and bool(k.AssignProcessToJobObject(job,proc))
 return {'affinity_set':affinity,'logical_cpu_indices':bits,'process_memory_limit_bytes':info.process_mem,'job_memory_guard_set':mem,'scope':'one offline worker, not a dedicated host or native services','job_handle_retained':int(job) if job else None}

def peak_memory():
 if os.name!='nt':return None
 from ctypes import wintypes as W
 class Counters(ctypes.Structure):_fields_=[('cb',W.DWORD),('faults',W.DWORD)]+[(n,ctypes.c_size_t) for n in ['peak_ws','ws','quota_peak_paged','quota_paged','quota_peak_nonpaged','quota_nonpaged','pagefile','peak_pagefile','private']]
 p=ctypes.WinDLL('psapi');k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=W.HANDLE
 c=Counters();c.cb=ctypes.sizeof(c);p.GetProcessMemoryInfo.argtypes=[W.HANDLE,ctypes.c_void_p,W.DWORD]
 return {'peak_working_set_bytes':c.peak_ws,'private_bytes':c.private} if p.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(c),c.cb) else None
