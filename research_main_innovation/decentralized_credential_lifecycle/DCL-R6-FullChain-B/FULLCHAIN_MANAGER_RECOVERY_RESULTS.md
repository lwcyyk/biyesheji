# ManagerRecovery恢复与异常路径

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


本轮MR64实际完成0/64、变异检出0/8（状态UNRUN）、RECOVERY_HEALTH_PASS未取得、当前failed-unit集合审查未执行、原生异常关闭未执行。计数0说明运行数量，覆盖结论保持UNRUN。

冻结完整路径在C00后先运行MR64合成有限夹具；真实C09后再通过M.resume完成原生恢复审查。M.health(True)验证handoff事实、审查C06/C07/C09的InvocationID/退出码/时间/身份/收据，随后双读failed-unit集合；已有历史单位按精确关闭证明只读分类，查询失败/陈旧事件/未审查失败继续拒绝。`mnt-e.mount`为既有规则中的固定排除，当前集合尚未读取。

MR64的Subject只维护进程内closed/stop/T0/R等字段；独立oracle读取MR-SIMULATION/1原始轨迹。该层用于分类/幂等/UNKNOWN等有限语义覆盖。真实Root停止、pidfd退出、cgroup清空和native/admin闭合需另有原生证据。

FC-S03的具体见证：guard.py:1099仅在MR_RECOVERY_DIAGNOSTIC_ONLY的C10后调用diagnostic_marker；manager_recovery.py:483–491再次校验scope，写入注入记录并触发预期78退出；协调者仅在该scope/退出78调用diagnostic_report。完整scope通过相同C10位置时继续后续流程，原生诊断分支不可达。

本次第7.4节要求的隔离原生异常路径缺少完整scope中的执行/计费/验收清单。切换诊断scope会提前关闭当前批次；额外批次或修改诊断分支均超出本轮冻结执行路径。下一轮可先静态构造独立的原生异常验收计划，保持第一次失败即关闭及单窗口边界。

历史MR-A被pre-T0故障阻断；TR-A2只证明正常最小路径及封存能力，内部UNKNOWN继续保留。当前internal状态为NOT_CREATED。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[覆盖机器记录](evidence/NATIVE_ANOMALY_COVERAGE.json) · [MR64冻结夹具](evidence/FROZEN_RA_ORIGINALS/inputs/manager_contract.json) · [独立oracle](evidence/FROZEN_RA_ORIGINALS/src/manager_recovery_oracle.py)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
