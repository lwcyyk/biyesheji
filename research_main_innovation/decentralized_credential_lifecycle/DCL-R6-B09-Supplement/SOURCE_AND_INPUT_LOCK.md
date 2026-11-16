# B09-AdmissionFix-static-1/r1源码与输入锁

Material Passport：独立静态冻结；2026-11-12；原C00Ready-static-1/r2保持。

host唯一新工作区D:/毕业设计/DCL-R6-isolated-verification/cr09；未来Linux源根/var/lib/dcl-r6/cr09；未来活账根/var/lib/dcl-r6/batch09。当前部署、运行窗口、T0、deadline和预算账建立数均0。

42项＝27 Linux源码＋1 Windows入口＋14输入；无pyc。原工作区完整副本见[SOURCE_BEFORE manifest](evidence/SOURCE_BEFORE/inputs/static_manifest.json)，最终副本见[SOURCE_AFTER manifest](evidence/SOURCE_AFTER/inputs/static_manifest.json)，逐文件实际SHA与字节数见[STATIC_WORKSPACE_LOCK](evidence/STATIC_WORKSPACE_LOCK.json)。

|锁|最终SHA-256|
|---|---|
|static_manifest.json|c7bed9528ea4a6ada08882d02be23dd37c62e8ee79fbb70a9445ddcc361ea127|
|execution_lock.json|fcc70f0d78aefc1ccc1fcc96489a3984417c6b4b7f203c78162c910b64746b81|

相对旧包：16份同路径文件修改，7个新增路径（含slice新文件名），1个旧slice路径只在新工作区更名，19份同路径字节保持。原目录中的旧slice保持。新增程序为batch_identity、ledger_gate、ledger_gate_oracle、ledger_gate_regression；新增输入为batch_identity与ledger_gate_contract。其余修改限命名空间、授权/模式绑定、资格检查及清单/摘要一致性。

全部原始规范、五业务、原探针、RootIPC/C09核心、预算预留语义及资源上限保持相应冻结责任。新版本继承CPY312-UBU24/1与AS4-PAYLOAD/1，原工具/stdlib树摘要保留；当前平台资格仍待未来单会话fresh验证。

新执行锁绑定所有实际未来argv、slice摘要、原生工具摘要、28程序及输入；完整diff见[FULL_DIFF.patch](evidence/FULL_DIFF.patch)，分类与前后SHA见[FILE_DIFF_INDEX](evidence/FILE_DIFF_INDEX.json)。本轮host内存compile没有生成缓存，也没有导入目标模块。

新动态批准模板位于evidence/DYNAMIC_A_AUTHORIZATION_TEMPLATE.json与DYNAMIC_B_AUTHORIZATION_TEMPLATE.json；全部批准位false、原文SHA空。实际控制目录、执行回执及运行产物均尚待新的专项授权。
