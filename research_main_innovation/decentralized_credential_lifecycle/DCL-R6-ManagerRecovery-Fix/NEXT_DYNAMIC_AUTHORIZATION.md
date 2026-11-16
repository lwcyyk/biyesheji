# 新阶段A诊断与后续阶段B条件申请

Material Passport：ManagerRecovery-static-1/r5；REQUEST_ONLY；本轮动态执行授权范围0。

阶段A绑定[最终46项](evidence/STATIC_WORKSPACE_LOCK.json)，manifest `e32453a883905db0089e7fd480f43283edeba2d87604407bbea55f4b14c2d395`，execution_lock `a8358f504248377340e86c5d0b79210fd18c7c3207096f9fe7c7e27e4b928c64`。当前实际批次登记中CalDiag/batch09-r1已CLOSED，新规划为batch10-r5；本轮仅创建host静态包与申请材料。

## 阶段A：有限恢复与自动关闭诊断

请求scope=MR_RECOVERY_DIAGNOSTIC_ONLY：部署45份Linux源/输入，核实际3.12.3/systemd/内核/cgroup/UID/GID/工具及全部摘要；执行冻结单会话/sealed/same-PID/once入口。完成C00、READY64、MR64及原生检查预付、C01–C08、H34/RootIPC56/BC40、真实C09、实例审查和原恢复守卫、C10实际资格。

C10 PASS后调用冻结diagnostic_marker，注入明确的MR_EXPECTED_DIAGNOSTIC_FAILURE返回78，验证关键非零退出自动触发STOP/CLOSED、预算保持、已登记角色回收和单次seal。该预声明故障成功验收应报告EXPECTED_FAILURE_CLOSED及实际退出码78，不能把它视为完整资源资格通过。原生诊断checker还读取真实C10、Root waitpid、首错、关闭/预算原件、Stop与scheduler实际退出；caller_exit_pending由事后审计确认。

阶段A不进入C11/C12、S34、门18或F1/F4；这些项目继续是阶段B完整资格的必需条件。未审查的管理器失败、ACK/身份/预算/原件错误或任何非预期关键失败先停止并保持首错。未确认回收/封存时结果为UNKNOWN，原预算与证据保留。

额外Root故障/不可返回子进程等单独原生失效来源，如本次A仍缺充分证据，应形成新的独立故障诊断批准；闭合后的窗口不自动重跑。64项合成夹具只覆盖有限策略与关闭状态模型。

## 命令、资源及权限

冻结host入口：

```text
python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\mr01\host\windows_entry.py --activate
```

唯一内部调用：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/mr01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch10
```

host使用PYTHONDONTWRITEBYTECODE=1保护source-only包。bootstrap按已验证scope选择锁内带--calibrate-only的Root argv；新MR诊断与自动关闭注入批准位都须明确true。实际授权原文SHA、r4、manager输入及所有锁摘要绑定新回执；当前模板全部批准位false，见[阶段A模板](evidence/PHASE_A_AUTHORIZATION_TEMPLATE.json)。

保持CPY312-UBU24/1、AS4-PAYLOAD/1、总访问1,000,000、总1,800秒、提前1,740、校准300秒/100,000、单进程AS1GiB和Payload父4tasks。继承校准硬62,546＋MR硬1,536=64,082。Root/停止器/查询和既有顺序凭据探针单列TCB；新增持久角色/service为0。Root停止器显式设置既定1GiB AS，systemd资源配置保持。

历史batch09 failed单位仅按输入固定boot、InvocationID、退出状态及Root保护旧CLOSED/结果/收据SHA只读分类；没有reset-failed或旧单位停止操作。发生不匹配时停止预检，记录准确缺项。新关闭权限只作用batch10 slice及受保护当前Root角色身份。源修复、放宽阈值、重置预算/期限、额外窗口、WSL全局配置/重启、下载依赖/外发和误路径操作均排除。

## 阶段B：完整资源资格与F1/F4条件方案

仅在阶段A及必要的独立停止动态证据满足要求、完整时间责任和版本准入已审阅并取得独立授权后推进。阶段B需新的独立身份（规划batch11），先生成对应namespace、精确argv及最终摘要；当前[阶段B条件模板](evidence/PHASE_B_CONDITIONAL_REQUEST.json)明确这些待A后冻结，不能直接用于执行。

阶段B完整顺序保持C00–C12、READY64、MR64/原生恢复审查、BC40、RootIPC56、H34、真实C09、S34、门18、独立原始重算、fresh健康账与当前资源/期限，全部必要条件实际通过后才RESOURCE_GATE_PASS→F1→F4。原五业务、F1八不变量、F4双实现/压缩/G64/变异和重放范围保持。仅对实际完整穷尽指定域授PASS_BOUNDED。

阶段A成功只证明其当批有限范围，已CLOSED的batch10不会向B提供可复用运行资格。任一阶段首个关键失败保留并关闭，模型资格和全链300秒保证均以实际证据裁决。当前TIME_FEASIBILITY_UNRESOLVED。
