# T0缺失故障与120秒期限覆盖

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**PREWINDOW_ABORT=UNRUN；T0缺失条件下的真实自动关闭性质仍待验收。**

本批仅运行NORMAL_START。冻结申请把两个A模式绑定到同一未建立实例，首模式认领、创建T0并关闭后，第二模式须新身份、最终摘要与独立授权。本轮没有额外预窗77注入窗口。

|性质|实际覆盖|
|---|---|
|原120秒启动TCB|真实ticket/ctx保存起点65.510243359、deadline185.510243359；初始化T0在起点后1.386606910秒|
|预窗超过120秒时拒绝/停止|UNRUN；本批没有等待或注入到期|
|T0不存在时关键异常自动关闭|UNRUN；本次错误发生在真实T0与预算创建之后|
|PT64的预窗失败/Root失败/账缺失等|0/64；在C00前终止|
|真实77预窗中止与native不适用|UNRUN；实际批次已具备运行对象|
|本批关闭是否早于原预窗deadline|是，但这只说明本批运行态错误的关闭时间，不构成无T0路径通过|

120秒合同和上限保持原样。报告区分“期限真实绑定”“运行态错误自动收敛”“无T0错误动态覆盖”三项。下一独立A所需最小范围见[下一静态审查](NEXT_STATIC_REPAIR_REQUEST.md)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
