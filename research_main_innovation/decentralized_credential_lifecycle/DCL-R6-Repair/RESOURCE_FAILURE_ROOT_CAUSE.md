# 资源失败根因独立复核

2026-11-10。复核为同会话知情审查，新增运行0。原batch01共62文件及ZIP60项全部核对；59个manifest条目和manifest本身流式验真，摘要仍为358778fff25aa3f8354874803e2cc26cbaac1d7d70478e9f0923f9c756559594。原件保留，证据位置以实际reports/raw/calibration为准，原batch01没有evidence子目录。

## 1. 结论分层

|对象|已确认|尚未确认|
|---|---|---|
|RG-SETUP-1|v1在SetInformationJobObject(class9)返回87，早于AssignProcessToJobObject；v2删除Job WS设置后成功|错误87的唯一内核参数原因|
|RG-MEMORY-2/Job|设96MiB后再关联唯一探针，峰值查询返回109.83203125MiB，MemoryError被捕获|失败请求是否计峰值、暂态计账/内部更新顺序；当前证据不能选定唯一解释|
|RG-MEMORY-2/WS|HardWS读回32MiB、flags6；进程峰值多4096字节|该峰值出现于设置前、设置中、稳态或退出阶段的哪个时点；具体页处理机制|
|观测代码|Python统计先释放所有块，父进程又在退出后覆盖last_memory|这两次当前值都无法还原五块仍驻留时的状态|
|监督体系|控制器自启动早于自身限额；watchdog失败未被控制器持续检查；run_batch可单独调用|原“3GiB推导界”覆盖完整生命周期的证明仍缺|

后四项是可定位的观测/准入缺口。它们不替代Windows内部峰值异常的机制根因，也不构成D1/D2安全反例。

## 2. 错误87的确切调用

v1：CreateJobObjectW创建空Job → EXT.Basic.Flags=0x2209 → MinWS=65536、MaxWS=805306368、ActiveLimit=4、JobMemory=4294967296 → SetInformationJobObject(handle,9,&EXT,sizeof EXT)失败 → 尚未进入job.attach(current)。v2 Flags=0x2208、MinWS/MaxWS留0，其他限制相同；增加错误结构转储后设置成功。

[微软基本限制文档](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)允许列出的标志组合，未在此证据中发现该四bit的明示互斥规则；不能凭猜测宣称WORKINGSET和JOB_MEMORY天然不兼容。Job固定WS范围后成员不能再改范围，解释了v2拆分职责的合理性，不能单独证明首次Set调用为何87。

当前只读页大小4096。v1最小值为16页；[SetProcessWorkingSetSizeEx](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsizeex)会把小于20页的正最小值提升到20页，v2实际读回81920恰为20页。**v2发生最小值归一化可核；Job setter是否因16页拒绝仍是待验证假说**，两API不能直接等同。最大可用物理内存/调用者权限等原时点事实未采集。

旧进程属于其他Job可能影响后续嵌套关联，但首次异常发生于空Job设置，尚未调用进程关联。现有栈排除了“AssignProcessToJobObject返回87”这个解释。原时点调用者Job链/令牌未记录，其他系统约束不作排除性结论。

## 3. ABI与长度静态核对

以已记录AMD64、Windows LLP64及本地ctypes.wintypes源码为前提：DWORD/LONG/BOOL为4字节，SIZE_T/HANDLE/ULONG_PTR为8，LARGE_INTEGER/U64为8，默认对齐8。没有_pack_覆盖。

|结构|关键偏移（字节）|静态预期总长|
|---|---|---:|
|BASIC|Flags16，MinWS24，MaxWS32，ActiveLimit40，Affinity48，Priority56，Scheduling60|64|
|IO_COUNTERS|六个64位计数，连续排列|48|
|EXT|Basic0，Io64，ProcessMemory112，JobMemory120，PeakProcess128，PeakJob136|144|
|PMC_EX|cb0，PageFault4，PeakWS8，WS16，Pagefile56，PeakPagefile64，Private72|80|
|PID_LIST|assigned0，returned4，首个ULONG_PTR8|头8＋8×容量|

class9/144及PMC.cb=80与SDK定义静态一致；API句柄原型均为HANDLE，未发现截成32位的代码。v2成功设置/读取与这些布局相容；v1没有实际sizeof/offsetof转储，当前不登记为一次新的运行ABI校准。v3新增显式预期布局检查，仍未执行。

## 4. Job峰值链

每个calibration循环先创建新的sub Job并设置限额，然后CreateProcess暂停子进程，先确保归根Job，再关联sub Job，设置HardWS，最后Resume。该次memory的sub配置96MiB；wait返回后调用同一sub.info，随后才close。代码没有用NULL句柄查询默认Job，也未把主4GiB Job的统计字段直接写进该sub报告。

因此，**当前源码不支持用“sub Job设置前已有成员”解释其峰值**。峰值查询在退出之后，历史/暂态统计规则仍待核；原日志缺Job实例ID/原生句柄标签和逐分配前后快照，无法运行级穷尽排除错关联或Windows内部计账细节。v3补标识/时间窗，而非替历史补写不存在的数据。

5×16MiB保留、下一次失败和峰值的数值关系只支持设计鉴别实验，不能证明失败请求已经计入峰值。原错误没有Win32分配失败码或Job通知事件；MemoryError也可能由其他分配条件产生。

## 5. 工作集和观测时点

子payload的PrivateUsage=12951552、WS=11714560取于chunks.clear之后；父process_memory的PrivateUsage=77824、WS=32768则取于进程退出后。PeakWS在两处均为33558528。把任一当前值当成仍保留80MiB时的值会形成错误解释。

HARDWS_MAX=4，返回flags6另含MIN_DISABLE=2，读回本身正常。当前4KiB页大小与差值相等，**相等不证明页面取整是原因**。峰值没有重置，限制设置前/后及Resume前均未采集PeakWS，尚无法定位越值事件。也没有证据表明真正的稳态WS上界应自动加一页。

## 6. 已确认的额外代码问题

- guard自己已运行Python及imports后才进Job并设置HardWS，启动窗未被原合成界覆盖；CREATE_SUSPENDED只约束子进程主线程，不限制创建本身的驻留量。
- 控制器等待worker时没有对watchdog退出作必检，无法据现有代码保证watchdog自身故障时及时联停。
- process_alive把OpenProcess失败一律当作已死，权限不足等失败也会得到False；v3改为未知/异常。
- 原主入口在deadline检查前写sessions，缺状态时自动建新计时/计数；没有先拒绝BATCH_CLOSED。run_batch也缺资源准入凭据检查。
- counter写入未核短写、缺中断意图记录；全局/局部共享reserve逻辑正确方向仍需崩溃校准。累计27保持原值。

v3静态修补这些可确认问题；严格启动包络适配器仍未实现，故总资源门保持FAILED，完整原因/保证不写成已闭合。
