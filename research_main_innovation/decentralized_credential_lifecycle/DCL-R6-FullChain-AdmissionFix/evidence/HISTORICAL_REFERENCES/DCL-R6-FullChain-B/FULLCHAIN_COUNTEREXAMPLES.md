# 静态见证与研究证据边界

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


|标识|可构造输入/轨迹|度量与触发|结论|
|---|---|---|---|
|FC-S01|冻结完整scope，六个C00后必需套件全部完成且保留原件|至少312常规文件>行政cap256|成功轨迹与自动行政导出合同冲突|
|FC-S02|相同原件集由guard.seal按冻结逻辑打包|至少313 ZIP成员>终态reader cap257|生成后的native包与终态接受合同冲突|
|FC-S03|scope=CALIBRATE_S1S9_THEN_F1_F4，C10成功|诊断注入分支scope条件为False|本次必需原生异常路径缺覆盖|

前两项共享同一312路径构造，属于两个合同位置的容量矛盾；第三项属于任务覆盖缺口。全部结论由静态源码与锁定输入导出，实际运行反例数量0、协议反例数量0。

这些见证针对验证基础设施。当前最强通用方法G与D1/D2间的严格分离实例仍为0；这批静态见证没有形成新的候选机制分离声明。研究实现门保持CLOSED。

UNKNOWN边界：历史TR-A2 mr_close_state缺失而internal UNKNOWN原样保存；当前internal字段NOT_CREATED；正式M.formal_gate需要MR_QUALIFICATION和MR_RECOVERY_REVIEW，当前材料缺失。当前资源门保持未取得。

后续最小工作为独立静态修复：完整输出规模/容量/字节/时间证明与终态/admin一致化；原生异常验收执行清单与隔离/计费/退出/接受条件；完成摘要重冻结后再决定新的动态身份。当前授权已按照静态失败分支结束，追加修复与重跑均为0。

[路径构造](evidence/SEAL_CAPACITY_STATIC_WITNESS.json) · [覆盖构造](evidence/NATIVE_ANOMALY_COVERAGE.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
