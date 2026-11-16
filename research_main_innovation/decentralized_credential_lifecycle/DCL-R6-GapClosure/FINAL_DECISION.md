# DCL-R6-GapClosure最终裁决

Material Passport：BF-static-2/r4；有限静态修复完成；2026-11-11；动态验证未执行。

## 实际交付

在独立gc01工作区交付真实代码：修改guard.py，新增公共范围核心、34job夹具驱动和独立原始证据检查器三份资源程序。五业务、runner和原C00–C12探针共7份文件逐字节一致。

S1–S9均有正常/预期故障与指定错误行为的变异见证；S2有三个确认层次，S5有相同/冲突请求，S6包含真实双actor请求屏障，S7保留短写原字节及适配器EIO证据，S8有关闭/过期/boot/锁/重启，S9检查N+1及重复拒绝。所有安全断言对正向与变异对象统一执行，真值来自原始账、屏障、操作文件和退出。意外错误与未声明违例阻断。

新资源门强制13个C结果、34个S正反结果、root原始重算、17项门负向检查与当前全局健康账；FORMAL导入业务前再次核验。缺件/PASS字段伪造/陈旧绑定/变异未检出有明确拒绝路径。旧C11钩子正式模式禁用，新增故障仅作用受锁RANGE合成账。

## Gate

|验收门|状态|实际范围|
|---|---|---|
|GC-1 测试完整性|PASS_STATIC|34job、9责任、11类变异、精确触发点、原始真值和统一oracle已实现/语法通过；动态命中UNRUN|
|GC-2 资源资格门|CONDITIONAL_PASS|强制证据链、17负向检查和再准入已实现；实际拒绝/通过、固定程序/可信root与内核假设待动态证据|
|GC-3 静态安全|CONDITIONAL_PASS|全局/局部界、隔离、无退款、4tasks及300秒合同保持；存储持久性、调度、运行/API行为保留条件|
|GC-4 版本与授权|PASS_STATIC|最终r4源/缓存/输入/argv/hash冻结，旧授权差异和独立下一申请完整|

11源码语法检查及最终变更文件检查通过：guard/fixtures由11覆盖，core/checker由15覆盖。记录的17条WSL检查/编译命令均有原始输出与exit0，目标模块正文执行0。静态控制流/argv核对通过；30项host/Linux工作文件对应。旧候选、错误记录和diff保留，不把中间稿检查当作最终数据。

## 历史与资源

原batch03预检包76项逐流核对；144项BF/batch03研究文件、BF原工作区24项、batch02原件51项和47误副本hash保持。原32191占用与历史失败不改。原batch03没有运行T0/账/运行关闭文件；本次同样没有初始化新运行实体。

新增测试完成路径访问上界19229，RANGE硬限20000；与原校准合计硬限57034≤100000，仍共享300秒。进程结构最多Controller两tasks＋Watchdog＋一个worker=4。墙钟收益、真实fsync耗时、可否完成整套校准以及任一模型性质均尚未测量。

## 当前状态与下一步

RESOURCE_GATE_PASS = NOT_OBTAINED
F1 = UNRUN_RESOURCE_GATE
F4 = UNRUN_RESOURCE_GATE
S1–S9 = UNRUN
batch04 = UNAUTHORIZED_NOT_CREATED
IMPLEMENTATION_GATE = CLOSED
STRICT_SEPARATION_INSTANCES = 0

原授权绑定BF-static-1，新增r4源码与测试需要匹配版本的执行许可。选择独立新批次申请，未创建batch04；[NEXT_EXECUTION_AUTHORIZATION](NEXT_EXECUTION_AUTHORIZATION.md)给出实际摘要、命令、资源、退出和封存范围。批准完整条件流程后，无需再就C12之后的同范围自动F1/F4反复确认。

本轮完成获准静态工作；动态资源资格与模型结果继续保留未运行。D1-PBFT-SEAL/1.1、强G覆盖及原条件裁决保持。

[代码与输入锁](SOURCE_AND_INPUT_LOCK.md)、[测试合同](S1_S9_TEST_CONTRACT.md)、[门规则](RESOURCE_GATE_EVIDENCE_RULES.md)、[静态结果](STATIC_VERIFICATION_RESULTS.md)、[证据索引](EVIDENCE_INDEX.md)、[交付检查](evidence/DELIVERY_CHECK.json)。
