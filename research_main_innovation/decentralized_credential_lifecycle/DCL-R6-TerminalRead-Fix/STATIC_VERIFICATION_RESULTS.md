# 静态验收结果与动态缺口

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

|检查|范围与结果|
|---|---|
|41程序语法|主机AST、3.12文法及内存compile通过；目标导入/执行0，无pyc|
|活动/终态调用分流|28静态断言通过；终态闭包无G.state/root_checkpoint或写入、创建、预算、服务动作|
|身份/window/预算|同namespace/源/执行锁/回执/原boot；精确原window；counter/intent/journal闭合核验|
|终态安全|固定Root原件只读、counter→phase锁顺序、5秒读取/2秒获取/512次；正常工作守卫保持|
|native前置|原退出等待后读取并记录活态拒绝；native_ready和实际ZIP完成分别处理|
|兼容性|13程序字节、70成员AST、完整RootIPC/MR AST保持；host两文件字节保持；PT64/PF48 jobs相同|
|TR40/oracle|32safe/8mutant输入配对、唯一ID、最多4帧、stdlib独立参考与目标类别静态检查；动态0|
|资源|TR完成681/硬960；正常A完成2588/硬3649；完整硬67730≤100000|
|历史|预锁7768文件，PFA/PF静态/PreT0-A旧包逐流核验；旧native UNRESOLVED/internal UNKNOWN/admin成功保持|
|本轮原生动作|WSL0、部署/服务/Launcher0、T0/R=null、PT/PF/TR/模型/参考运行0|

TR-G1=PASS_STATIC；TR-G2=CONDITIONAL_PASS；TR-G3=PARTIAL；TR-G4=PASS_STATIC。已定位直接前置阻断并建立分流；实际Native读取/锁/IO/归档、跨boot和全链300秒可行性仍待新授权验证。

只读扫描不产生模型搜索访问或新的运行资格，R不debit；读取属于有界行政IO，最长5秒/固定文件与journal上界。原finalizer30/35秒、256文件/32MiB界保持，新增case/报告占用的实际归档大小仍须下一批核验；遇上界直接失败并保留未决，不放宽既有限额。

[机器结果](evidence/STATIC_RESULT.json) · [控制流/只读闭包](evidence/SYNTAX_CONTROL_FLOW_READONLY_CHECK.json) · [资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json) · [最终摘要链](evidence/FINAL_BINDING_REVIEW.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
