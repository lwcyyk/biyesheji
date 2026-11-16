# ManagerRecovery-static-1/r5源码与输入锁

Material Passport：2026-11-12；最终静态版本；目标运行0。

host工作区D:/毕业设计/DCL-R6-isolated-verification/mr01；未来Linux源包/var/lib/dcl-r6/mr01；阶段A静态规划身份batch10-r5，活账/var/lib/dcl-r6/batch10，slice=dclr6batch10.slice。控制目录DCL-R6-ManagerRecovery-Fix/authorization/batch10-r5。当前这些Linux运行实体、控制回执、T0和预算均未建立。

|最终对象|SHA-256|
|---|---|
|static_manifest.json|e32453a883905db0089e7fd480f43283edeba2d87604407bbea55f4b14c2d395|
|execution_lock.json|a8358f504248377340e86c5d0b79210fd18c7c3207096f9fe7c7e27e4b928c64|

46项＝30 Linux程序＋1 Windows入口＋15输入；source-only无pyc。manager_contract与全部实际程序、输入、原工具/stdlib、slice及argv构成有向摘要链。Windows与native receipt路径从同一个精确identity合同导出，revision、批次、Root/单位/回执及scope同步锁定。

[原42源码](evidence/SOURCE_BEFORE/inputs/static_manifest.json) · [最终46源码](evidence/SOURCE_FINAL_R5/inputs/static_manifest.json) · [逐项实际SHA/字节数](evidence/STATIC_WORKSPACE_LOCK.json) · [完整diff](evidence/FULL_DIFF.patch) · [文件差异索引](evidence/FILE_DIFF_INDEX.json)。

r1/r2/r3/r4候选各有独立源码快照与versions下原锁，保持构造历史；当前所有执行申请仅绑定最终r4。原B09-r1/CalDiag及全部历史工件继续冻结。新原生编译、OS行为、故障和性能状态统一UNRUN；host compile只作静态语法检查。
