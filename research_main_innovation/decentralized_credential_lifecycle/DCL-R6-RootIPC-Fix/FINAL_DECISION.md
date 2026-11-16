# RootIPC-Fix 最终静态裁决

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

**RootIPC-static-1/r4 已完成有限静态修复与冻结；batch06动态执行仍待独立授权。** 本轮未运行C00–C12、C09H、新56、S34、门17或F1/F4；batch06无运行目录/T0/账/单位。

|验收门|裁决|依据及剩余责任|
|---|---|---|
|RI-1 权限根因|PASS_STATIC|batch05源码、真实stat/EACCES、303事务、双流与ZIP互证；原结论保持|
|RI-2 权限修复|CONDITIONAL_PASS|固定Root策略、私有暂存、发布前owner/mode、目录fd/ACL/双目录屏障已实现；真实DAC/失败路径及调度待测|
|RI-3 停止修复|CONDITIONAL_PASS|ready/RPC/父waitpid加入fresh取消，有限回收，ACK/闭合优先级保持；实际总延迟与清理收敛待测|
|RI-4 回归版本|PASS_STATIC|56项/8变异、原测试语义不变、17最终语法、44项host/Linuxhash、完整diff/历史保护与batch06申请已冻结|

原guard.py、c09_handoff.py两份修改，新增3份关联模块；12份程序字节保持，guard中24个预算/资格函数AST保持。原五业务、D2-DP/TRACE-REF、range核心、探针、S34与门17判据保持；输入仅未来命名与锁适配。最终44文件包括17源码、17实际CPython3.12.3缓存、10输入。

56项夹具当前动态0；计费完成路径505，和C09H合计2750≤共同5000硬限，校准硬上界62034≤100000保持。Root额外顺序探针TCB最多1个，下一授权明确接受；实际AS、内存、停止响应及300秒整套可完成性尚未测量。

batch05继续RESOURCE_GATE_FAILED：C00–C08九项PASS、C09H34接受，真实交接NOT_EXERCISED，R37,293、303配对事务、20.928秒payload清空与300.044秒Root结束保留。其531-entry行政包和346-entry原生包逐流核对无差异；历史505研究文件、原source37、各旧工作区/原件和误副本47只读/hash通过，blocked by policy保留。

本轮native13条只含环境读取、语法编译、独立静态目录复制及hash/ACL核对，全部exit0；目标角色正文0、动态故障注入0、systemd/全局资源/实际UID配置修改0、依赖安装0。最终只读检查确认batch06不存在。r1/r2/r3中间静态候选及旧hash保留。

更强的任意恶意同UID预算读路径/账真实性保证仍为UNRESOLVED，当前保持冻结payload与可信Root/内核/存储/调度假设；未修改预算读取核心或扩大安全宣称。新权限/停止行为、真实ACK/waitpid及最终父seal仍需匹配r4的动态证据。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED授予0。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离实例0和IMPLEMENTATION_GATE=CLOSED保持。下一步材料见[batch06申请](BATCH06_EXECUTION_REQUEST.md)。

[权限合同](ROOT_PAYLOAD_PERMISSION_CONTRACT.md)、[停止分析](ROOT_STOP_WAIT_ANALYSIS.md)、[56项计划](ROOT_IPC_REGRESSION_PLAN.md)、[静态检查](STATIC_VERIFICATION_RESULTS.md)、[最终锁](SOURCE_AND_INPUT_LOCK.md)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
