# 日志、归档与资源工作量界

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

**PQ-6相关工作量为PARTIAL；WALL_TIME_BOUND_UNRESOLVED。** 所有数字针对未生效v2的明确局部集合，详见[WORK_BOUND_RECALCULATION.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/WORK_BOUND_RECALCULATION.json)。

|局部操作|最坏次数|字节工作量/条件|
|---|---:|---|
|主日志os.write尝试|263|≤345148；部分写也占用完整预扣槽，禁止整行重试|
|cursor持久更新|522|init1＋bind1＋predebit263＋分类completion256＋poison1；每次≤1198|
|首错摘要|1|≤334；固定一次，无错误追加循环|
|STOP_REQUEST/CLOSED局部发布|2|各≤189；完整回收/MR文件另计|
|以上数据write调用|788|263＋522＋1＋2；≤971216总写入字节|
|文件/目录fsync尝试|1316|263＋2×522＋2（摘要）＋1（初始主log目录）＋3×2（跨目录标记）|
|cursor数据读取|≤522|数据≤625356；另有必要stat/ACL/目录检查，不能把此项当全部syscall次数|
|静止局部集合一次hash pass|1|≤350166输入字节；包括列明的失败staging|
|native ZIP局部raw输入|一份|≤350166；ZIP元数据/压缩膨胀另外计算|
|两个独立archive oracle局部payload|2遍|解压/CRC/hash对应≤700332 payload字节；嵌套ZIP与manifest扫描另计|

971216=345148＋522×1198＋334＋2×189。旧599778/798仅属于较窄的旧cursor/预扣模型；v2新增256笔分类completion，且明确跨目录标记持久责任。因此旧工作表保持历史原样，本轮按新schema和持久顺序重算。

上述工作量还要求全局单次失败/poison责任和失败写不重试；多角色关闭传播及EIO无标记场景的实际强制机制尚待接线证明。故这些数字仅是明确有界调用合同的代数结果。cursor采用紧凑排序JSON＋至多1 LF、同一私有目录原子发布时满足表中界；复用现有BC.Store的紧凑无LF编码会少1字节。若改用RootIPC的indent2编码，必须重新计算cursor及全部工作量，不能直接沿用1198。

在n个给定有界文件总字节B的条件下，流式SHA-256输入量为B；独立核验O(n+B)，排序路径O(n log n)。局部集合至多10个对象（含既有main/STOP/CLOSED、局部新对象和失败staging）。按上一轮F≤1535、ZIP32/无extra/comment/保守descriptor profile，局部头开销H≤22＋10×(92＋2×1535)=31642；ZIP_STORED条件界381808。若另证pinned zlib默认参数满足上一轮compressBound式，deflate条件界382044。该结果依赖格式/压缩库前提，当前未升级或替换压缩实现，完整包需要将其余成员统一计算，不能逐层漏掉ZIP的再复制。

增量数据FD的局部峰值可列为生命周期锁1＋数据FD1；cursor位于同一Root私有目录时另有现有目录FD，跨目录STOP/CLOSED复用RootIPC目录链。完整进程还持有socket、pidfd、输出流、运行库和query子进程资源，当前缺少统一FD常数和实际NOFILE合同。TasksMax4约束任务数量，FD需独立证明。

固定scalar schema使编码输入/结果缓冲有限；1198/1322字节并不等于CPython对象分配峰值。完整观察调用[c09_handoff.py:115](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:115)会执行源/输入hash、trusted/read、unit_show和/proc；[guard.py:718](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:718)捕获PIPE缺前置字节界。native构建[guard.py:1022](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1022)使用整文件read_bytes哈希；post-exit和host helper含z.read整成员物化。1GiB是硬拒绝线，当前未证明所有必要步骤可在其内完成。

访问额：旧完整范围68498保持；若新独立预付256获准，现有项未变时得到68754，再加全部新增测试/适配/核验ΔV。原calibration100000、global1000000及各scope硬额度保持；MR256不可挪用。可选3269＋256=3525≤5000仅在未来明确同context授权后成立，当前不采用隐式合并。

分项裁决：有界授权日志写工作量CONDITIONAL_PROVED；global访问额CONDITIONAL_PROVED（68754仅含已列项）；完整读取/内存/FD为PARTIAL或UNRESOLVED；任意锁等待/反复拒绝请求次数未获统一界。有限fsync调用无法推出300秒必达，完整300秒、terminal5秒、admin30秒及停止时延继续UNRESOLVED。preT0120、全窗1800和stop1740原合同保持。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
