# 内存峰值与时限监督合同

## 内存口径

推荐观测指标为目标进程的OS PeakWorkingSetSize，并另记WorkingSetSize、PrivateUsage和提交峰值。Python对象/堆大小、工作集、提交、树合计和退出后持久资源采用不同单位和归属。

[工作集定义](https://learn.microsoft.com/en-us/windows/win32/memory/working-set)覆盖驻留的可分页页，含每进程共享页计数，排除AWE/大页。父子进程各自生命周期峰值之和不等于同时占用峰值；也不能直接作为唯一物理RAM。

[GetProcessMemoryInfo](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo)可按进程句柄查询。活着时成功取得的OS峰值覆盖截至该次查询的历史；末次查询失败或退出后接口不可用时，最后区间仍有未知。Job持续跟踪的提交峰值是另一种指标，不能补成缺失的WS峰值。

[Job内存限制](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)约束提交虚拟内存。[SetProcessWorkingSetSizeEx](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsizeex)支持显式硬最大WS标志，需要SET_QUOTA及相应条件；普通软界可越过。实现须在resume前核对OS支持、实际设置和初始峰值，失败即停止；没有自动提权或默设数值。

数值候选仍为null，当前内存采样0。未来采样检测发现过去超额，与从未超额的硬预防分别管理；父观察器自身内存另计。

## 进程身份和权利

私有unnamed Job持有创建者权限，process/thread句柄来自唯一CreateProcessW；PID只作标签，创建FILETIME和源/镜像绑定进一步核验。只对持有句柄和私有Job操作，不枚举或按旧PID重开/杀进程。

创建时Job列表在Windows10/Server2016起有[公开支持](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)。保持Job handle不被child继承，不打开breakaway；active process limit1对应一个root、target自建child0。已有外层Job/版本不兼容时fail closed。父进程及Job是新增监督开销，均须预算，当前没有实际创建权限。

## 120秒的准确后置条件

沿用120秒。外部QPC锚点应覆盖CreateProcess调用、suspended配置、Python bootstrap、测试、输出、清理和退出。若原120覆盖父子整体，则需更早可信launcher锚点，不能免费增加parent预检或尾部时间。

[QPC文档](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps)说明其包含sleep时间；[WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)现代timeout不包含低功耗时间。每次返回都应重新检查绝对deadline，不能把等待参数直接当完整墙钟保证。

[TerminateProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess)是外部异步请求，pending I/O完成或取消后才能退出。Job终止也按逐进程终止理解。请求、signal、退出值和最终持久证据是不同观察点；当前没有有限调度/终止迟滞证明。

因此“在截止后尽快请求停止”可以设计，“退出及全部取证必在120秒完成”继续UNPROVEN。没有授权额外grace。任何晚返记录为超额/未确认，不被默认为合同内成功。

当前HARD_DEADLINE_ENFORCEMENT_UNAVAILABLE，原因包括项目缺少集成入口以及严格完成保证未证。外部监督规格已形成，监督实现及运行就绪均为false。
