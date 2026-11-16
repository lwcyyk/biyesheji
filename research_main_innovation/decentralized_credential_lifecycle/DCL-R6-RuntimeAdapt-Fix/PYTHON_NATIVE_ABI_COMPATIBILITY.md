# CPython与原生ABI兼容条件

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

**静态必要ABI条件满足，运行行为仍CONDITIONAL_PASS。** 当前CPython为3.12.3-1ubuntu0.17，执行文件SHA与旧e50d468e…锁完全相同，PT_INTERP=/lib64/ld-linux-x86-64.so.2，其实际目标为已审查加载器。

原1241对象中66个ELF入口进行只读解析，递归解析114个当前对象。DT_NEEDED均可解析，GNU version needs无未满足组。systemd-core所需SD_SHARED通过父systemd/systemd-analyze直接装载的唯一同SONAME共享库解析，初始未处理该link-map上下文的结果和精化证据均保留。

实际只读Python进程/proc/self/maps中的loader/libc/libm路径、device/inode与当前磁盘对象相符，未观察到deleted映射。LD_PRELOAD/LD_LIBRARY_PATH/LD_AUDIT为空，/etc/ld.so.preload不存在；配置、cache及六个文件身份均记录。它是当前查询进程的证据，不能借作未来业务服务PID的加载证明。

libc导出setrlimit/getrlimit/prlimit、clock_gettime/flock/fsync/open/pread64/pwrite64/waitpid/syscall等需要接口。系统d255.4-1ubuntu8.18、原kernel6.18.33.2-microsoft-standard-WSL2、cgroup v2及UID999/GID989保持观察值一致。RLIMIT_AS/cgroup/TasksMax行为、信号/退出、seal与资源时延仍须新C00及后续原生证据。

静态图按实际RPATH/RUNPATH/本机cache和父已加载SONAME条件解析；它未执行目标ELF或解析全部重定位/运行时dlopen行为。原Kernel/Manager信任及无并发特权运行时更新前提继续保留，全部动态兼容性及完整300秒可行性UNRESOLVED。

[ELF完整图与缺项检查](evidence/ELF_ABI_AUDIT.json) · [原始初图](evidence/ELF_ABI_AUDIT_INITIAL.json) · [当前映射与环境](evidence/RUNTIME_DISCOVERY.json) · [最终基本环境](evidence/FINAL_PLATFORM_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
