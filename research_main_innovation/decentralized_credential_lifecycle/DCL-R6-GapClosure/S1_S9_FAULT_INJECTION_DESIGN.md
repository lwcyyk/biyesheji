# 故障注入接口与隔离

Material Passport：BF-static-2/r4；设计、实现和静态审查；动态触发次数0。

## 模式与路径

新钩子只限 CALIBRATING 状态的 RANGE 票据；须有新版本动态授权的 test_mode=RANGE_ONLY/1，并绑定真实源码、执行锁、合同和当前批次。正式 FORMAL 或无票据调用在安全模式入口被拒绝。旧 C11 钩子限制为 C11、四个既定故障值和精确 C11 镜像路径。

真实全局账固定为 batch04/out/visits.bin。夹具账固定为 batch04/out/safety/<case_id>/ledger.bin，cap=8。测试对象在公共核心内执行；生产模式固定访问全局账，测试模式只能访问被冻结 job 的合成账。路径锚定 OUT，拒绝 safety/job 目录符号链接。历史账和主账不接受注入。

## 准确触发

|钩子|真实动作与证据|
|---|---|
|crash|记录 CHECKPOINT/FAULT 与counter/intent快照后，worker真实exit71；父进程记录握手和wait退出|
|short_write|对目标fd实际执行部分os.write，保存returned length及通过fd路径读取的原始短写字节；正常对象拒绝|
|fsync_error|仅合成适配器在指定同步调用处抛OSError(EIO)，记录errno与syscall_invoked=False；测试错误处理路径|
|lost_update|被测合成对象跳过flock，两个actor在读到余额后rendezvous；真实全局计费仍用原锁|
|生命周期|只改变该job的合成lifecycle文件，调用与生产共用的状态/执行锁/初始化检查；真实全局时限始终检查|
|局部越额|只改变测试对象额度判据；语义写入仍由真实全局账预先计费|

fsync EIO为指定适配器故障，当前设计没有声称制造物理介质EIO。S2的“未确认/确认/原子确认未知”按实际调用边界记录，宿主持久化仍依平台合同。

## 被测对象与检查器

range_core承担生产和合成范围事务、幂等事实、派发、claim和局部扣减。range_fixtures只编排固定场景及受限变异；输入JSON没有通用跳过安全检查的入口。所有合法/变异行为均在校准模式、冻结N和合成路径中封闭执行。

range_evidence独立解析原始counter字节、事务日志、持久状态、屏障顺序、操作文件、身份及退出。inspect_job不读取variant/mutant来改变安全断言；check_job只负责将同一违例集合分类为正向通过、指定变异命中或失败。意外违例和恢复始终拒绝。原始短写片段及错误恢复前的残片保留。

故障未触发、触发点错误、进程退出异常、日志短缺或变异未命中均停止，不自动重试job或新批次。预期模糊合成账写CLOSED后拒绝再次使用，不回收信用。主全局账I/O异常继续触发HALTED/STOP_REQUEST；所有测试步骤先从同一真实主账扣费。
