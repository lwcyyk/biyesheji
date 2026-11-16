# 四门静态准入

| 门 | 结论 | 范围与责任 |
|---|---|---|
| G1 STORAGE_SAFETY_PROVED | PROVED | 受信源码/运行时、独占输出和FileIO接口前提下，全部受控前缀<=2000167；余96985。 |
| G2 REQUIRED_PAYLOAD_COMPLETE_PROVED | UNPROVEN | W01已揭示结果日志顺序的L0丢失路径，W02有必需DETAILS转移责任，完整联合容量/可用性仍待证。 |
| G3 BOUNDED_EVIDENCE_CONTRACT_APPROVED | CONTRACT_CHANGE_REQUIRED | 37组字段已明确；新增L1引用和L2诊断语义待研究者单独批准。 |
| G4 RUNTIME_ORIGIN_ADMISSION_PROVED | UNRESOLVED | 7项内容变更/5项缺失，版本与字节投影不足以确立原或新批准来源。 |

正式状态R36_STATIC_PREFLIGHT_BLOCKED，R36_FOUR_GATE_STATIC_PREFLIGHT_PASSED=false。P1、P2、P3三个命题及来源门分别登记，G1没有推出其他三门。

13份原证书全部以原ID复核；5项固定/条件schema界保留，8项完整适配待证。41类原异常原ID和原结论完整继承，本轮新增X42—X46，共46类。异常“覆盖”指合同/源码路径已经核对；完整证据和容量全成功继续false。UNSATISFIABLE仅用于全存储不可用时的普适耐久性责任；冻结68的完整字节适配为UNPROVEN。

R35_REGRESSION_COMMAND_LOCK保持原字节、command_executable=false。当前审批阶段没有68/54预算，没有动态导入或执行任何目标代码。源码修改0、依赖修改0、旧来源锁修改0、真实部署0；D1-B1保持部分实现，各真实后续阶段维持独立授权。

R36_NEXT_AUTHORIZATION_REQUEST只申请表示合同的审批。若获批，首先改变G3的纸面语义状态；当前Runner如何满足新schema、W01/W02最小修复、联合容量及运行时来源仍需各自证据与后继授权。批准合同不会自动赋予源码修改或测试权限。
