# G2-R46：父监督器自身成本与API封装包络

审定依据为冻结Supervisor源码，主工程绝对路径 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_poison28_supervisor.py`。逐调用AST定位见 [sources/API_CALL_SITES.json](sources/API_CALL_SITES.json)；详细成本见 [R46_SUPERVISOR_SELF_COST.json](R46_SUPERVISOR_SELF_COST.json)。本轮实际调用该源码API次数0。

## 前置阶段

`main` 946–952先执行 `PolicyValidator.validate`，随后进入 `supervise`。Python启动、标准库导入、模块/结构定义、路径检查、JSON/摘要核验和DLL导出绑定均发生在Deadline起点前。

在完整准入路径中，`read/document` 有20次控制读取：policy1、approval/resource/runtime三文档3、Runner/Driver/Python/self/manifest5、child packet1、child approval1、child pins8、evidence certificate1。每个控制文件上限2MiB，接受的稳定读取合计≤41943040B。相同源重复读取仍计成本。PE验证增加open1/read2/seek1/close1与70B。

来源目录每项独立open/read/hash/close。设条目数K、稳定字节长度B_i；累计输入为控制实际长度之和+70+ΣB_i。运行时JSON受2MiB约束，成功匹配的每项SHA字符串占至少64输入字节，因此K≤32768；显式文件open/close累计≤21+K≤32789（close界以路径正常完成/上下文收尾为条件）。源码缺少专门的来源累计字节预算，ΣB_i及耗时仍待冻结。

稳定普通文件每次正读取至少前进1字节时，来源read方法调用≤Σ(B_i+1)；若每次非EOF读都取满65536块，可收紧为Σ(⌈B_i/65536⌉+1)。短读取和外部修改分别处理。`read_bytes`在分配后核对长度，受信稳定输入假设若失效，失败路径的分配/读取量还需额外约束。

对于深度为h的既有路径，`checked_path` 138–150会分别执行exists/lstat/is_symlink各h次，末尾is_file/stat各1；`read`再stat1；`verify_source_file`再before/after stat2。policy、child packet、approval的额外checked_path以及两处输出路径检查重复计量。它们是Python方法调用数，底层元数据系统调用次数由实现与缓存决定。

WindowsApi 381–426有WinDLL请求1、导出getattr28及结构检查；加载器隐式I/O、API转发与初始化成本没有进入api.counts。每次封装另有set_last_error/get_last_error，其成本同样单列。

## 成功启动的精确封装调用数

计到首次ResumeThread成功返回，假设全部查询及写入成功、预算与时间足够。

| 阶段 | 调用数 | 推导 |
|---|---:|---|
| Deadline.__init__ | 2 | QPF1+QPC1 |
| ResourceObserver.__init__ | 3 | pseudo handle+PID+GetProcessTimes |
| parent job membership | 1 | IsProcessInJob |
| Output.open | 8 | admit1+NUL1+2*(admit1+CreatePipe1+SetHandleInformation1) |
| ADMITTED | 4 | append admission/prewrite/preflush/prefsync QPC |
| Job.create | 3 | create+set+query readback |
| LAUNCH_INTENT | 4 | append |
| Child.create | 17 | QPC5+Initialize2+Update2+Create1+Close3+membership1+times1+image1+Delete1 |
| CHILD_SUSPENDED | 4 | append |
| initial sample | 10 | admit+tick+two*(IO+memory+memorytick)+two job queries |
| RESOURCE_BEFORE append | 4 | append |
| Child.resume | 3 | admit+membership+ResumeThread |

合计63，其中56次普通标记调用、7次cleanup标记调用（提前关闭三个Child端6次+attribute delete1）。Output.open内还有两次Pipe创建前的QPC准入；它的完整调用数为8。63描述上述路径，不能充当28项suite总需求。

## 全部声明API与可达调用上界

A=`max_api_calls`，S=`max_samples`，D=`max_drain_chunks`；u为主循环wait次数，u≤max(0,S−1)。每个API分量共同受A限制，表中各项无须同时达到上界。

| API | 可达调用上界 | 定位/条件 |
|---|---|---|
| CreateJobObjectW | 1 | Job.create 490-508 |
| SetInformationJobObject | 1 | Job.create 500 |
| AssignProcessToJobObject | 0 in main->supervise reachable graph | Job.assign 510-511 defined, no reachable caller |
| QueryInformationJobObject | 1+2*S+2 | initial readback1; sample <=2S; final accounting<=2 |
| TerminateJobObject | 1 | termination_requested set before call; no retry |
| CloseHandle | 8 | 5 stdio pipe/NUL +2 process/thread +1 Job; at most once per owned name |
| IsProcessInJob | 3 | parent1 + after create1 + before resume1 |
| InitializeProcThreadAttributeList | 2 | size query then initialization |
| UpdateProcThreadAttribute | 2 | HANDLE_LIST and JOB_LIST |
| DeleteProcThreadAttributeList | 1 | finally iff initialized; cleanup=True |
| CreateProcessW | 1 | creation_attempted set before first admission |
| ResumeThread | 1 | single reachable resume call |
| WaitForSingleObject | u+1 <= S | u main waits + at most1 cleanup wait |
| GetExitCodeProcess | 1 | first signaled wait sets exited before code query; future waits omitted |
| TerminateProcess | 1 | fallback only when !member, once flag; mutually exclusive with reachable Job termination |
| GetCurrentProcess | 1 | borrowed pseudo-handle |
| GetCurrentProcessId | 1 | observer init |
| GetProcessTimes | 2 | parent init and created child |
| GetProcessIoCounters | 2*S | one per owner per sample; partial failures reduce |
| K32GetProcessMemoryInfo | 2*S | one per owner per sample |
| QueryPerformanceCounter | A; jointly constrained by all API admissions | Deadline.now callsites; includes cleanup and receipt tail |
| QueryPerformanceFrequency | 1 | Deadline init before QPC start |
| QueryFullProcessImageNameW | 1 | image buffer 32768 WCHAR |
| CreatePipe | 2 | stdout/stderr |
| SetHandleInformation | 2 | readers not inherited |
| CreateFileW | 1 | NUL stdin only |
| PeekNamedPipe | A-32 (loose; all ordinary admissions share ceiling) | drain slots; no separate post-exit slot bound |
| ReadFile | A-32 (loose; all ordinary admissions share ceiling) | drain only, bytes requested <=q |

所有普通封装在调用前要求total<A−32，清理封装要求total<A，随后先增计数再调用，故总获准调用≤A，普通调用次数≤A−32。此为可证明的封装接纳界。28个声明接口中27个在主图可达；`assign`方法没有可达调用。A≥96属于源码安全域要求，完整运行的最小充分A仍未证明。

成功append需要4次QPC。完整双进程/Job sample需要10次封装。一个running Pipe数据槽至多8次，exited槽至多7次；drain至多16D，加生命周期共享的至多一次终止。初始sample也消耗S配额，异常sample可能只产出部分查询。

## 32个清理槽的全生命周期证明

8个自有Win32句柄每个最多一次 `QPC+CloseHandle`，共16；attribute delete1；Job或fallback终止1；一次cleanup wait的两次QPC+wait+exitcode至多4；末次tick1；final append四次QPC；FileIO close准入QPC1。总计28≤32。

提前release_child_ends和attribute delete均已包含在28中；收尾时只尝试尚未尝试的自有句柄。以最后一次普通调用为界，其后剩余cleanup标记调用≤28，因此A−32守卫保留足够的封装槽。调用失败或时限拒绝会保留未知/未关闭状态；该算式只保证调用名额，不保证关闭成功或时延。Python write/flush/fsync/fileno/close与解释器收尾另计。

## 末次receipt的覆盖边界

923行复制 `api.counts` 后，934行最终append还可能执行4次QPC，938行close_file还可能执行1次QPC。最多5个后续封装调用未进入该快照。另有JSON/摘要、write/flush/fileno/fsync、FileIO close、返回判定与解释器退出。

receipt的 `cleanup_status=CLEANUP_UNCONFIRMED`、`receipt_close_confirmation=REQUIRES_EXTERNAL_EXIT_AND_FILE_OBSERVATION` 与source语义一致。它能叙述自身之前的已知前缀；最终落盘与退出尾部需要外部观察。最终receipt写入或关闭失败时，磁盘上可能没有相应错误后缀，内存错误记录不得当作持久事实。

本轮因此可登记 `R46_SUPERVISOR_API_BOUNDS_PROVED=true`，其作用域严格限定为上述源码封装界。全native API次数、全进程I/O、时延和完整内存上界继续未决。
