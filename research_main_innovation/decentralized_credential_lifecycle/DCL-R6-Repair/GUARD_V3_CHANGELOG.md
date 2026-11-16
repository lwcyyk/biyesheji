# Guard v3静态修订记录

2026-11-10。位置`D:/毕业设计/DCL-R6-isolated-verification/batch01/versions/v3`。当前为**STATIC_CANDIDATE_NOT_RUN**，校准/导入/语法执行均0。batch01/src仍为v2，v1/v2与原失败未动。v3尚无可认证的启动前包络适配器，正式准入明确关闭。

## 1. 文件与职责

只改guard.py、guard_probe.py、run_batch.py资源入口。f1_model.py、f1_check.py、f4_dp.py、f4_reference.py、compare.py五份业务源码与v2逐字节相同。锁与完整diff见evidence/V3_SOURCE_LOCK.json和三个*.final.diff.txt。第一次发布的静态草稿从其diff恢复，并以原SHA-256验真，保存在v3/drafts/static01；static02亦完整保留，最终静态稿为static03。

|位置|问题与静态修订|安全约束/口径|未来验证|
|---|---|---|---|
|guard.py:77 assert_open_batch|旧入口到期检查前写sessions、缺状态自动建窗 → 先只读检查关闭/到期/根授权，拒自动初始化|历史27和原deadline不改；没有新会话免费额度|复制/重复启动、关闭/到期拒绝且所有历史hash不变|
|guard.py:94/99 strict/formal admission|独立调用run_batch能绕过校准 → 新入口先拒绝未认证平台包络|不接受JSON verified布尔来开放模型；当前适配器未实现，保持显式拒绝|缺凭据/过期/错Job/错代码/不完整校准均拒绝；当前只静态检查|
|guard.py:103 guardian check|WD异常未联动 → 访问/等待入口检查活guardian，异常要求根Job停止|双向失效链需平台接线；当前上下文未绑定，不默许缺guardian|WD退出、controller异常、句柄关闭及日志落盘矩阵|
|guard.py:140 Budget|阻塞锁/短写/中断不确定 → 带deadline的非阻塞重试、短写检查、fsync与预留意图/journal|模糊预留默认停止且占用，不重放/回收；历史格式/已耗27不改|并发、持锁进程死、prepare/write/commit各点中断、额度上限|
|guard.py:204/227 identity/memory|PID复用与退出后值覆盖 → creation FILETIME、查询前后窗、SDK原字段与身份；采样句柄增加SYNCHRONIZE并拒WAIT_FAILED|当前/历史峰值分列；运行时ExitTime未定义则null；查询失败不当死亡|创建、应用限制、Resume、释放前后、退出快照全链|
|guard.py:213/220/239 units/ABI/WS|旧min16页发生归一化但未记页单位 → GetSystemInfo，显式20页min、预期64/144/80布局检查|不把4KiB当容差；API readback仍只是配置证据|实际offset/长度/页单位与SDK比对，Native失败码保存|
|guard.py:251 Job|Job句柄/实例标签缺失，列表固定容量 → 实例/创建时刻、明确峰值名、返回长度、可变PID列表|不把PeakJobMemoryUsed当当前WS；完整成员列表失败即未知/拒绝|嵌套/成员变化/MORE_DATA/错句柄/额外进程|
|guard.py:319/351 launch/wait|日志覆盖和时间混合 → -I -S -B、独占日志、限制前/后/Resume前、last-live/post-exit分列|禁止全局site启动钩子；-S仍不提供启动硬界|审查依赖、每个角色及新增子孙均在前置资源组内|
|guard.py:406/421/428|原整体校准dispatcher易把部分观察用于通过 → 诊断分项与整体准入分开，未证明时INCONCLUSIVE/拒绝|当前calibrate/main保持关闭，不发RESOURCE_GATE_PASS|接通可信平台适配器并补完整调度后才能运行|
|guard_probe.py:6/18/21|缺真正持有时快照 → named Job只读样本、成员检查、分配前后/释放前后|Job查询明确对象，current/peak/time不混合|同一Job/PID身份链及单因素低资源探针|
|guard_probe.py:45|Python异常无底层失败码 → 新增VirtualAlloc reserve/commit分离诊断候选|最大128MiB虚拟预留、1MiB提交步；不将其等同物理压力；未执行|Native返回与立即GetLastError、Job峰值变化的时序鉴别|
|run_batch.py:4/12|模型模块导入前缺资源门；校验遍历缺额度入口 → 先require_formal_admission，对DP/ref输入状态校验预收费|核心函数不改；额外收费保守，不追改历史计数|逐路径收费审计，缓存/参考/变异/重放同账|

## 2. 明确保留的未完成部分

外部启动前资源包络、真实运行时guardian上下文/控制器接线、新平台适配器、完整校准调度与操作系统计账鉴别都尚未完成。当前v3为防止未证准入与改善可观测性的静态修订，不能复制后直接宣称已修好硬界。

本轮只作文本/差异/哈希审查，未启动Python检查语法、未import v3、未试跑探针。因batch01已到期和关闭，当前资源代码的拒绝路径也没有被实际运行验证。RG-2按PARTIAL登记；全部动态性质仍待新范围。

原失败日志、原报告中不充分的3GiB配置推导及所有缺测继续保留，没有用v3说明覆盖历史证据。
