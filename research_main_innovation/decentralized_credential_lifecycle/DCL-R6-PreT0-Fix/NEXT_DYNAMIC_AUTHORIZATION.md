# 下一有限动态验收及后续完整链条件申请

Material Passport：PreT0Recovery-static-1/r3；REQUEST_ONLY；当前动态许可0。

绑定最终51项、manifest `34c9c4642c4ff8c68183845b66f49f1670efa3349ec82e07d80e8bbabfd86ab7`、execution_lock `af8de2c099813d2e3018c6d46b2e95b435c2e75a122d32b73b3f96e3c47b58ec`。新静态规划batch11-r3；原batch10/MRA保持CLOSED、T0/R未初始化的历史事实。

## 阶段A：两个互斥的最小诊断模式

scope=PT_STARTUP_DIAGNOSTIC_ONLY，由批准原文明确选择一个startup_probe_mode。

- **NORMAL_START**：正常预窗ctx/查询/qualify→独占intent→真实T0/state/counter→严格runtime checkpoint→停止器/父资源armed→实际C00→PT64（含9mutant）→关闭和适用的运行态native seal。硬访问1,537，正常完成1,090；不进入READY64/MR64/C09/C10–12/S/门18/模型。
- **PREWINDOW_ABORT**：预窗ctx/健康查询/qualify后，在runtime intent和T0之前注入PT_EXPECTED_PREWINDOW_ABORT，退出77；要求自动STOP/CLOSED、原启动TCB期限内父/child停止、真实无T0/账、native NOT_APPLICABLE，以及host自动post审计/行政manifest/ZIP。不得用人工第二条命令伪装自动成功。

两个模板均未批准：[NORMAL_START](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)、[PREWINDOW_ABORT](evidence/PHASE_A_PREWINDOW_ABORT_AUTHORIZATION_TEMPLATE.json)。它们针对同一个尚未建立实例的互斥选择；首模式关闭后，第二模式需重新冻结下一独立编号/摘要并明确批准，当前不创建额外免费窗口。

共同前置：部署49份Linux源/输入、Root元数据及source-only原生语法，fresh核当前3.12.3/systemd/内核/UID/GID/cgroup/工具；单会话、same-PID exec、sealed与一次认领保持。当前初始静态授权不覆盖任何这些动态动作。

## 精确命令与自动收尾

```text
python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\pt01\host\windows_entry.py --activate
```

唯一active WSL argv：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch11
```

host设置PYTHONDONTWRITEBYTECODE=1。原文SHA、最终r3/两锁、startup输入与模式绑定实际回执；PreT0批准位须true，PREWINDOW_ABORT另需明确注入批准，Full=false。

active结束后，host冻结程序自动再调用锁内只读post-exit命令：同一Ubuntu-24.04、Root、/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/startup_lifecycle.py --post-exit-export。它只审核角色/组空及导出当前原件，不能创建或恢复runtime。Root导出alarm30秒/AS1GiB，host等待上限35秒；这是新增自动行政收尾的严格上界，随本申请单独确认，不延长原120秒启动TCB或任何运行窗口。最多256文件/32MiB行政证据，已关闭文件/日志由host逐流SHA封存。

## 资源、失败和裁决

保持CPY312-UBU24/1、AS4-PAYLOAD/1、总1,000,000访问/1,800秒、校准100,000/300秒、提前1,740、每进程AS1GiB及Payload父4tasks。预窗停止继承原ticket.preflight_deadline（120秒TCB）；不存在运行账时R=null。新PT专项硬1,536，完整继承链硬65,618；原MR/5,000/RANGE20,000等子界不扩。

首次非预期关键错误停止、不现场修改/重跑、保持原claim/对象。进程/应用/native/admin分项裁决；未确认退出为CLEANUP_UNKNOWN，归档失败保留ADMIN_UNRESOLVED，原生不适用时禁止补假state/counter。允许必要的已冻结当前批次停止后备并标明来源；任何额外人工清理不能算自动性质通过。

## 阶段B条件方案

只有两个必要A证据及所需故障/阶段完整性已审查、取得新的独立执行授权与身份/最终摘要后，恢复C00–C09、真实C09、MR64、C10–C12、S34、门18、独立原始重算、fresh账/资源/期限→RESOURCE_GATE_PASS→F1/F4。A中的PT64只覆盖当前有限模型/流程，不能替代完整资源门。

阶段B的编号和源锁须按A实际消耗的身份重新登记；当前只给流程/资源条件，最终namespace/摘要待A后形成。全链300秒仍UNRESOLVED。F2/F3、全局WSL/systemd设置、其他发行版/Docker、依赖下载、真实凭据及外发保持原授权边界。
