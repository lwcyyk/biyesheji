# CalDiag首次失败与基础设施反例

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

|登记|真实见证|性质与边界|
|---|---|---|
|CD-1 恢复manager拒绝|same-PID resume entry已验证；scheduler4804在guard.py:976抛UNREVIEWED_MANAGER_FAILURE、exit125|新恢复准入/执行编排缺陷；实际C06/C07/C09预期故障单位处于failed，Root结果均PASS|
|CD-2 关闭收敛缺口|原父调用返回125后无CLOSED/无seal，状态AWAIT_EXPECTED_RESUME，coordinator和launcher身份均null，external-stop4318仍在|完整控制流未保证非零退出后关闭；本轮观察并保存等待态，随后经授权冻结关闭|

CD-1：原systemd健康检查只接受mnt-e.mount。C06时间停止、C07预设exit23、真实C09停止controller都产生本批failed单位，它们对应当前锁和Root实际PASS。恢复时同一全局谓词将这些状态当作未审阅失败；本轮事后失败列表明确包含c06/c07/c09。精确抛错调用的stdout未落盘，故当时循环最先遇到哪个单位保留UNRECORDED，不用事后顺序填值。

CD-2：健康检查位于_launcher_body清理try之前；父launcher普通wait路径直接返回子进程125，异常清理和“已有CLOSED才seal”的finally均未触发。c09_handoff.observe_exit在HANDOFF_VERIFIED后清空coordinator_identity，external_stop只有该身份存在时才检查Root丢失。两处组合形成已观察的等待空窗。Payload已空、预算保持，资源资格仍关闭，未产生模型业务执行。

本轮按停止授权调用原冻结stop_tree/seal，未修改源、判据、权限或上限，没有重跑、再次激活或新建预算窗。保留初始607与最终612文件及完整命令/时间/账。Native C09真实交接PASS与后续恢复失败分别裁决。

下一静态修复应限制于：按当批受保护结果/原件识别预期故障单位，其他未审阅失败继续拒绝；把恢复前言及普通非零退出纳入关闭收敛；在等待恢复期间保留可监控的Root责任与校准截止。历史失败单位的后续管理也应形成明确、可审阅策略。本轮仅记录这些具体需求，代码保持冻结。

D1/D2正式协议反例0；本轮新增的是验证基础设施的真实控制流反例。batch07具体C00失配仍UNRESOLVED，原条件/强G/严格分离0保持。

[首错原件](evidence/windows_entry.stderr.raw) · [结构化失败证据](evidence/FIRST_FAILURE_AND_CLOSURE_GAP.json) · [初始审计](evidence/POSTRUN_AUDIT.json) · [冻结关闭命令](evidence/CLOSE_FAILED_BATCH.py)。
