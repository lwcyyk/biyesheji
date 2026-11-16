# CalDiag最终裁决

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

**RESOURCE_GATE_FAILED；首次关键错误为恢复入口UNREVIEWED_MANAGER_FAILURE。TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。真实C09及四套前序检查已取得实际证据，完整资源资格仍关闭。**

|最终问题|真实回答|
|---|---|
|1 新执行身份|PASS：batch09-r1/当前boot/源/输入/单位/账/回执/argv完整绑定|
|2 预检及C00|PREFLIGHT_PASS / SAME_BOOT_CONFIRMED / C00_PASS；八字段双侧MATCH|
|3 BootContinuity40|30 PASS＋10 MUTATION_DETECTED；完整恢复连续性仍未完成|
|4 C00–C12|C00–C09全部PASS；C10–C12 UNRUN_AFTER_RESUME_FAILURE|
|5 RootIPC56|48 PASS＋8 MUTATION_DETECTED|
|6 C09H及真实C09|28 PASS＋6 MUTATION_DETECTED；真实HANDOFF_VERIFIED/ACK/waitpid PASS，恢复准入失败|
|7 S1–S9|34项UNRUN_AFTER_RESUME_FAILURE|
|8 门18|原17和新聚合全部UNRUN；健康/13异常/4mutant实际结果null|
|9 原始重算|完成套件的原生独立审核有效，原件SHA一致；全链重算未完成|
|10 全校准耗时|null；C09前缀48.592009253秒，首次失败区间48.699583118–48.738270904秒|
|11 300秒条件|TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE；未取得完整完成实测|
|12 最长观测项|Root套件IPC56 11.392948秒；payload service C09H 7.135260秒，范围及重叠单列|
|13 资源资格|RESOURCE_GATE_PASS=NOT_OBTAINED|
|14 资源/退出|R38,729、1,739事务/3,478行；charged peak观测122.46484375MiB、最大tasks4；补充冻结关闭后角色全空|
|15 新缺陷|恢复manager对预期故障单位拒绝；等待恢复/非零退出未自动关闭，已保存反例|
|16 F1/F4技术条件|尚缺C10–C12/S34/门18/全链资格与时间证据；模型启动0|
|17 下一阶段|先最小静态修复具体恢复/收敛缺陷，再以新身份/锁申请独立校准诊断|

本次入口1次、允许的同父内部恢复尝试1次（成功0）、测试重跑0、源码/判据/权限/上限现场修复0、T0/预算重置0、自动下一批0。初始未关闭的等待态和停止器已取证；随后按本次停止授权调用冻结stop_tree/seal，CLOSED记录在T0+299.567904452采样，持久发布在+299.596399447前完成，清理确认在+299.993796083完成。counter/journal/intent字节保持，最终Payload/Root角色为空、父cgroup不存在。

C00–C09及READY64/IPC56/BC40/H34的通过只归本次实际范围。194项合成/混合回归的原生检查结果为153 PASS＋41 MUTATION_DETECTED；新ledger聚合与S34尚未运行。当前boot、Root4259/start135655、Sender4314/Receiver4318及新scheduler4804的角色时序均保存。额外pidfd精细打点缺口保留FIELD_EVIDENCE_PARTIAL。

F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]，D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持。后续正式模型批次需新明确授权和新当批动态资格，当前已CLOSED窗口保持关闭。

[首次失败及最小修复方向](CALDIAG_COUNTEREXAMPLES.md) · [真实时间裁决](CALDIAG_TIME_FEASIBILITY.md) · [资源核算](CALDIAG_RESOURCE_ACCOUNTING.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
