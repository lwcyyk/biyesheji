# Windows内存API与观测口径审计

2026-11-10。仅读取微软文档、原源码和原始日志；没有新API压力探针或模型运行。所有新观测时窗均为v3设计，旧日志缺项继续null。

|API/SDK对象|设置值 → 读取值|实际约束/统计|可得结论及限制|
|---|---|---|---|
|[EXT](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)|JobMemoryLimit=96MiB → class9读回96MiB|文档定义job可提交的虚拟内存限额；PeakJobMemoryUsed另为峰值字段|commit与WS分列；峰值字段未说明失败请求入账/内部更新顺序|
|[Basic flags](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)|0x2208、ActiveLimit4|活动进程数限制、KILL_ON_CLOSE及Job commit；无breakaway位|字段设置成功不等于异常退出/完整树已校准|
|[Set WS Ex](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsizeex)|min65536/max33554432/flags4|Hard maximum为接口约束；正min不足20页会归一化|v2读回20页相容；历史PeakWS发生在哪个限制窗口仍未知|
|[Get WS Ex](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-getprocessworkingsetsizeex)|min81920/max33554432/flags6|读取当前配置及其强制标志|返回配置不等于测得所有过去时刻的约束，更不认证整树|
|[GetProcessMemoryInfo](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo)|PMC.cb=80，ret检查|输出进程当前及峰值统计；Psapi为K32包装接口|源布局静态正确，无证据因选择Psapi包装而字段变义|
|[PMC_EX](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex)|WS/PeakWS、PrivateUsage/Pagefile及PeakPagefile|当前驻留、驻留峰值、当前private commit、进程生命周期commit峰值是不同量|子释放后和父退出后当前值不能回推分配时刻；无需把Pagefile误解成实际已换出的字节|
|[Query Job](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject)|明确sub.handle、class9/3|NULL会用当前Job，非NULL指明对象|旧代码用明确句柄；v3补实例ID/时间窗/返回长度，实际历史句柄数字未记录|
|[PID_LIST](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_process_id_list)|assigned/returned/PID数组|嵌套时包含子Job进程；数组可变|旧容量8在配置4的所见场景未发现截断；v3仍按returned/assigned及MORE_DATA显式扩容|
|[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)|Create/Assign/继承/关闭|默认CreateProcess子孙在Job，WMI例外；句柄最后关闭才触发KILL_ON_CLOSE|正常源码仅用CreateProcess；父/WD失败及额外持有句柄必须实际校准|

## 1. 当前证据的时窗

|量|原始值/时点|能够支持什么|
|---|---|---|
|测试Job配置|96MiB，首成员关联前|配置早于本sub Job工作负载；不能用“旧成员先占用”作默认解释|
|Job PeakJobMemoryUsed|115167232，worker退出后|OS返回的该字段确实高于配置；不是已记录的“当前Job commit”|
|子PeakWS|33558528，释放后/退出前|进程此前达到的报告峰值；时间定位缺失|
|子当前WS/private|11714560/12951552，释放后|释放后快照，不是五块仍保留时|
|父当前WS/private|32768/77824，退出后|退出后残留统计，不能当活进程实用量|
|树采样WS|最大下界97099776|只给采样下界；进程查询失败或错开时间会降低可见量|

## 2. v3观测协议

新增GetProcessTimes的creation FILETIME用于稳定关联PID；运行时ExitTime未定义，不填写为有效退出时间。每次进程/Job查询保留调用前后monotonic/UTC窗，Job有独立实例ID、名称、创建/设置时间；同一次样本不假装多API原子快照。

子启动记录分为created-suspended、before-limit、after-limit、before-resume、last-live和post-exit。探针记录before-allocation、每次成功后仍持有、失败后仍持有、释放前后。历史Peak字段不做差得到“本时段峰值”；当前WS、PeakWS和private commit仍按SDK名保留。

新增有界VirtualAlloc诊断候选把reserve与commit分开，失败时立即保存GetLastError，再采统计；保留原Python bytearray案例作对照。它能帮助识别分配失败/计账的事件关系，**没有执行就没有机制结论**，即使有限样本复现也不自动成为所有Windows版本的通用定理。

## 3. 根因的可排除与未决项

已读SDK与源码相容于class9/144、PMC80，未发现32位句柄截断；不能把未知直接归因于ctypes布局。v1 min16页与v2进程API20页归一化是精确差异，但缺Job setter的单因素实验。

Job嵌套/句柄流静态相容，实际原日志没有前后PID列表与分配前后统计，所以仅凭字段数值仍无法穷尽错关联、失败预留或内核峰值更新顺序。4KiB与当前页大小相等只是一条线索。此处全部保留UNRESOLVED_MECHANISM。

本轮不修改v2判据来追认PASS。新分类可把解释缺口记为INCONCLUSIVE，但所有必需项均PASS且严格上界闭合之前，整体仍RESOURCE_GATE_FAILED。
