# 内部状态、CLOSED与退出分轴

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**TR-D7=UNKNOWN。** 正常关闭路径仍未生成mr_close_state，原terminal审查和自动行政字段都保持internal UNKNOWN。

|轴|实际结果|
|---|---|
|STOP_REQUEST|正常结束无此文件，未人工补写|
|CLOSED|102.107384106正常原因持久化|
|child退出|当前协调器直接waitpid，raw0/exit0|
|角色/cgroup|原stop_result0/empty；自动和独立审计均确认空|
|预算|3133/3133事务/6266行一致，读取与归档未变|
|native seal|真实COMPLETED233/234|
|行政|自动SEALED249/250|
|内部收据|缺失，保留UNKNOWN；原batch_state仍CALIBRATING，CLOSED支配后续资格|

内部缺件没有被native或行政成功覆盖。原冻结规则允许正常关闭证据完整时封存一个仍含UNKNOWN的真实快照；本批保持该适用范围，没有引入新状态收敛规则或倒填历史。

本批已关闭，claim/T0/R和全部原件保留，不继续旧窗口。新root行政/只读导出进程均结束，人工/外部停止后备0。

[实际状态/退出/停止汇总](evidence/ACTUAL_RESULTS.json) · [原始journal](evidence/JOURNAL_MESSAGE_INDEX.json) · [终态证据](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
