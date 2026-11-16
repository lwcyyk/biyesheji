# WORK守卫与C00结果

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**实际WORK成功，原资源与终态守卫继续保留。** Root在同一真实window中由ARMED/5进入RUNNING/6，随后发放dclr6batch12-c00.service。C00返回PASS，八项主检查及辅助资源比较均MATCH。

运行点committed=true、当前boot/授权/源摘要、phase_record_sha256、initialization_id及counter不可变身份均有持久原件。T0/counter建立在先，当前scheduler身份838与Root state一致；先取得资格再发放服务的路径由冻结launch_one/require_work及实际事件序列支持。

C00当前Payload实际RLIMIT_AS两侧均1GiB，parent TasksMax/pids.max4；实际执行UID999/GID989与NoNewPrivileges等按readiness记录MATCH。C00资格仅属于该测试，不授予完整RESOURCE_GATE_PASS。

非法WORK、旧phase/seq、身份/跨批/终态等测试实际在PT/PF隔离Subject中执行。主执行账、检查点或无关systemd单位未被故意损坏。CLOSED后本批保持关闭；没有继续发放C01、C09、MR或模型。

[八项原始比较](evidence/C00_READINESS_SUMMARY.json) · [112项实际输入与原件定位](evidence/TEST_CASE_RESULTS.json) · [预算完整性](evidence/BUDGET_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
