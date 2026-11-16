# 本批反例与证据边界

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**首次因果错误来自运行态phase发布/读取竞态；独立的自动post导入缺陷随后阻断行政收尾。**

|编号|原始证据|裁决|
|---|---|---|
|PTA-RACE-1|停止服务892的journal栈：guard.py:777→c09_handoff.py:207→guard.py:138→startup_lifecycle.py:184，PT_RUNTIME_PHASE_DRIFT；STOP67.121192409|真实并发接线缺陷。私有phase与公开checkpoint由两次持久发布形成，reader逐次读取后要求相等，存在合法过渡被拒绝的调度|
|PTA-STOP-LATCH-2|STOP reason=C09_OR_SUPERVISOR_FAILURE；mr_first_failure先由887锁存LAUNCHER_ERROR/IPC_STOP_REQUEST_DOMINATES|因果触发和首个持久错误槽位分开记录。原槽位字节保持，journal补足因果来源；首次异常精确抛出时刻缺少独立打点|
|PTA-POST-3|冻结只读post命令exit1，startup_lifecycle.py:11 import boot_continuity失败|直接以-I脚本执行时兄弟模块未进入sys.path。host正常入口导入路径与该直接命令不同，静态compile没有覆盖模块装载|
|PTA-QUIESCENCE-4|active入口先返回，独立systemd停止服务仍有后续journal退出见证|自动finalizer应使用真实角色/写者收敛屏障。该批在顶层import处即失败，有界审计分支尚未运行|
|PTA-LABEL-5|摘要绑定的控制路径batch11-r5、正文r3及规则文字r1并存|路径标签一致性缺口；实际代码/JSON/执行锁和运行batch11互相一致，按冻结原件执行，未绑定旧batch10|

RACE精确读取快照未被记录，以下是与原件一致的最小调度：reader取旧READY公开点→writer持久化ARMED私有phase→reader比较新phase而拒绝→writer发布ARMED公开点。最终phase链与公开点均ARMED、intent hash一致，为过渡竞态解释提供支持；具体调度保持推断，后续静态方案需构造可控复现验收。

本轮源码、判据、预算、C09交接和RootIPC语义保持。上述均属于通用验证基础设施缺陷，没有提出新的D1/D2候选机制或原创性分离声明。历史MRA预窗IPC_STATE_MISSING/native失败与CalDiag真实C09证据继续冻结。

[错误与关闭原件](evidence/ACTUAL_RESULTS.json) · [停止服务journal](evidence/JOURNAL_MESSAGE_INDEX.json) · [自动post stderr](evidence/STARTUP_POSTEXIT.stderr.raw) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
