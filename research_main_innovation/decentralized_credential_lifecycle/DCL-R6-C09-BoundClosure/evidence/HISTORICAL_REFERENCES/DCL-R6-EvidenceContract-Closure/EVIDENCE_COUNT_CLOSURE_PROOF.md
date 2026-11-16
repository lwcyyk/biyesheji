# 数量闭包与保守上界证明

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


在锁定程序/输入、受控ROOT封闭写入域、Restart=no、一次激活/最多一次C09恢复、固定演员/线程和首错展开的前提下，得到保守源级包络：K≤4450。该值由以下互斥路径族及临时对象族相加推导，当前运行未产生这些文件。

|路径族|槽位上界|来源|
|---|---:|---|
|FLAT_INPUTS|60|RootIPC allowed fixed names, public Store targets, auth2, lifecycle locks,16 ticket/result pairs|
|BOOT_FIXED|41|All fixed private Store.put targets, six locks/three append logs and phase/start/review names|
|BOOT_SUITE_ROWS|370|PT64/PF48/TR40/RA32/READY64/MR64 =312; BC40; ledger descriptor18|
|NATIVE_READINESS_SAMPLES|602|C00/C10 each sample_cap300 plus one lease confirmation; 2*(300+1)|
|IPC_AND_WAITPID|141|Scenario-specific IPC files/wait context/shadow,56 raw cases,2 scheduler waitpids,c09 append log. Nonregular link slot conservatively included.|
|C09H_RAW|238|Sum actual frozen events204 plus34 per-job oracle files|
|LEDGER_NATIVE_SPECIMENS|53|18*3 minus one deliberately absent intent|
|CONTROLLER_FILES|128|16 no-restart services times eight fixed suffixes|
|PROBES_AND_GLOBAL_BUDGET|33|global budget3/global facts3/STOP1/ready4/child pairs6/shared1/C05 local3/C11 mirrors12|
|S34_NAMED|406|Per frozen scenario table, traces/ledger/registry/checker/worker/barrier/snapshot/partial files|
|MODEL_FILES|196|F1 31 plus F4 164 plus mutable summary1|
|PAYLOAD_FIXED_TEMP|1555|2*759 non-core atomic target slots (including12 rendezvous files) +31 shared global-intent writers +6 global fact owner/claim writers|
|S_CORE_TEMP|144|3*48 actor slots: current intent, retained intent, fact temp. No double counting with G.atomic non-core targets.|
|BOOT_RANDOM_TEMP|341|3 prepare audits+2 activation updates+2 entry+2 child+1 before-seal+1 resume+6 scheduler+7 phases+256 credit updates+4 failed callers+3*abort16+seal7+2 public qualifiers|
|ROOT_RANDOM_TEMP|96|3 expected IPC staged faults+4 ordinary first Root failures+4*abort16+2*7 ordinary stop calls+7 seal manifest attempts+4 seal-error writes|
|DYNAMIC_STOP_FILES|46|stop_result/event at most2 per stop_tree call; C_stop=23=abort16+coordinator4+external1+C09_1+normal1|
|合计K|4450|保守联合包络，未声称为可同时达到的最小精确最大值|

源级封闭性：固定目标的覆盖写增加文件内容版本，不增加成员；G.atomic的临时名由目标＋固定PID/TID决定；S34最多48个实际actor。intent临时件移入mutant_retained后可在原路径重建，因此每actor计当前intent、保留intent、fact三个槽位。G.atomic另计并发rendezvous的12个目标及其临时件，避免遗漏。Root随机临时名按有界调用次数计，未按随机值空间臆造容量。

关闭调用展开：C_abort≤2×3＋2×4＋2=16（两个scheduler每个最多fail/两层异常；两个协调阶段每个最多四层关闭责任；external两层）；abort内部无递归abort。C_stop≤16＋4＋1＋1＋1=23；动态stop_event/result每次≤2，共46；STOP/CLOSED/first_failure/close_state/external_closing为最多5个固定异常目标，已在固定族计入。C_seal_attempt≤1＋2＋2＋1＋1=7。随机BC临时件341及Root publish临时件96按这些调用配额逐项界定。未成功停止/未确认回收继续UNKNOWN，文件上界本身不推导关闭成功。

1082的构成逐项为312回归raw＋238 C09H事件/oracle＋56 IPC raw＋40 BC raw＋170个S34最低原件＋71个预算异常原件＋195模型输入/输出。1083再加入一个native manifest。该下界去重后1082条路径互异；后来增加的上界族只为尚未覆盖的文件类型、可选分支和临时件提供包络，图中schema节点不再作为额外文件计入。

层级固定点：以K表示排除native manifest/ZIP的运行原件，native ZIP成员=K＋1；native封存后行政运行原件=K＋2；行政最终ZIP再加10 host侧件、4 source lock及1 manifest，为K＋17。故完整成功轨迹：原件1082≤K≤4450，native成员1083…4451，行政导出原件1084…4452，行政ZIP成员1099…4467。原用户1082行政下界仍成立，精细层级表达揭示额外两份native封存文件。

现有256/257接受集合中的完整成功轨迹为空；上述区间描述源产物/拟议容量包络，未声称旧守卫接受。全范围、额外外部写入者或自动重试若改变，当前上界失去适用性，需重算。新增测试集合J时按新增固定目标、actor/临时对象、Root调用上界和封存侧件作并集，再求相同分层固定点；同路径更新不重复加算。

字节/工作量仍为EVIDENCE_MAX_BOUND_UNRESOLVED：C09 PENDING退出见证循环反复向一个固定日志追加记录，源码没有记录数/字节配额，访问上限也未给此循环收费。固定时间截止没有提供单操作最短耗时公理。故可构造任意n次PENDING的合同模型前缀，文件数恒定而日志字节/读验工作增长；此处未声称物理机器能在固定时间实际完成任意n。

602条就绪记录各≤131072，独立逐条上限组合已允许78905344字节，高于32MiB；实际是否达到该组合待测，单项cap无法推出总量保证。完整RAW单文件/总字节/构建与验收期限继续未闭合。4450属于带明确前提的人工源级证明，算式/AST/hash已核对，尚无CPython/内核完整语义机械证明。

[最终算式与S34逐job表](evidence/FINAL_COUNT_CLOSURE_CALCULATION.json) · [原始1082路径](evidence/HISTORICAL_REFERENCES/DCL-R6-FullChain-AdmissionFix/evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json) · [待闭合日志规则](evidence/FINITE_FIXED_POINT.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
