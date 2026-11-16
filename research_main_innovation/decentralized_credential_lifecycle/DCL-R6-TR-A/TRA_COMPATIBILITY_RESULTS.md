# PT64/PF48兼容回归结果

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

冻结申请要求本轮全量PT64及PF48，合计112项/17变异。本次两套兼容回归执行均0，全部UNRUN_PREFLIGHT_FAILED；25项总变异中另含TR8，均NOT_EXERCISED。

旧batch12的PT55 PASS＋9变异、PF40 PASS＋8变异与R1907保持为历史事实。当前版本source/输入虽与最终r1锁匹配，运行库闭包发生变化，历史动态通过未升级为TerminalRead当前资格。

本轮无测试重跑、无预算账初始化、无附加免费窗口。兼容性回归和真实终态联调需要先完成运行时重新审查及新的独立版本/执行身份授权。

[未执行明细](evidence/UNRUN_CASE_REGISTER.json) · [运行时变化](evidence/RUNTIME_DRIFT_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
