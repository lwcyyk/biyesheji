# 门18与预算异常聚合

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


门18完成0/18，全部UNRUN_STATIC_ADMISSION；预算聚合完成0/18子例、变异检出0/4，健康控制与13类异常均未执行。本轮无实际预算账，当前真实预算改动0。

现有root_verify_safety在S34原始重算成功后检查当前账健康，再执行gate_negative_cases。原17项覆盖错误status、缺job/raw、hash、绑定、checker与伪造PASS；第18项GATE-LEDGER-ANOMALY强制调用ledger_gate_regression.run_suite。

聚合内部为1个健康控制＋13类异常＋4个mutant，合计18：缺COMMIT、重复COMMIT、pair mismatch、顺序、overflow、batch、boot、sequence gap、截断、lock绑定、foreign journal、digest、缺证据。4项mutant分别吞掉缺COMMIT、累计overflow、batch mismatch和日志digest拒绝。

即时独立oracle逐job核对；整套oracle初审后，Root在run_suite返回与verify_gate_audit处各重新收费18并复读原始字节，完成收费595＋36=631，专项硬cap640。其动态通过及变异检出必须来自真实原件。本轮仅确认强制调用仍存在。

require_formal_admission再次核对门18、聚合资格摘要和当前真实全局账，随后检查真实C09、MR和PreT0资格；受控FORMAL入口与run_batch在语义导入前各调用一次。静态缺口保持RESOURCE_GATE_PASS关闭。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[聚合合同](evidence/FROZEN_RA_ORIGINALS/inputs/ledger_gate_contract.json) · [强制调用摘录](evidence/SOURCE_EXCERPTS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
