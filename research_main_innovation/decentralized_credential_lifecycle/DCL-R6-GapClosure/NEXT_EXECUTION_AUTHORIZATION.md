# 下一阶段执行授权差异与具体申请

Material Passport：REVIEWABLE_REQUEST；BF-static-2/r4；当前仅静态授权，以下动态动作均未执行。

## 旧授权覆盖审查

原batch03授权明确以BF-static-1为唯一代码基线，后续测试缺失时资源门关闭，并禁止现场修改冻结版本。新r4包含公共范围核心、34个S1–S9 job、17项资格门负向检查、强制原始证据门与新的manifest/执行锁，原授权无法覆盖这些新hash和执行行为。

batch03原始机器记录只有预检停止：C00–C12/F1/F4均0，T0/counter/运行CLOSED未初始化；没有可沿C09恢复的运行状态。方案A在当前旧授权和新冻结命名下不成立。选择方案B，准备独立batch04申请；本轮没有创建该运行批次。旧T0、账、资格收据及源码均不迁移。

## 申请绑定

版本BF-static-2，freeze_revision=r4。
manifest=4c488e52869d58b14b59721c0cdbd3a068a5fcda256891256c2c9f3e649bf103。
execution_lock=aa9c4a84451a1c5053eb9dd6850254fd7efc5c560889dd017540cc827f5c0e9b。
safety_contract=358cf611aabdc71499723056d51765edc47084b9b7a88102c72a28ab0b1e178a。
四个资源程序和全部业务hash见SOURCE_AND_INPUT_LOCK；输入和所有argv均为实际工件。

主申请scope=CALIBRATE_S1S9_THEN_F1_F4，test_mode=RANGE_ONLY/1。明确授权C00–C12、34个正反job及root独立核查/17项负向门检查全部通过后，同批自动进入冻结F1→F4。授权须接受既有AS4普通映射/特殊内核VMA单列范围及TCB/存储/调度条件。

另有已冻结的校准专用选项：scope=CALIBRATE_S1S9_ONLY，入口和C09恢复均增加--calibrate-only；通过后立即停止并封存。该关闭窗口不用于稍后FORMAL，需独立后续决定。两种scope与命令严格匹配，不能静默切换。

## 资源合同

总访问≤1000000；总墙钟1800秒；1740提前停；cal100000/300共享同一T0。单进程AS1GiB、父sliceTasksMax4、普通payload条件驻留4GiB保持；没有新增账户或依赖。
新增RANGE主账硬限20000；完成路径静态上界19229；与C校准硬界合计≤57034。所有测试、变异、原始核查和门检查均受真实主账/时限约束；单job至多2actor，任意时刻父组最多4tasks。时间可行性未测，无法在300秒完成时按原界停止。

## 确切命令与准备

权威[evidence/execution_lock.json](evidence/execution_lock.json)与[FUTURE_COMMANDS](evidence/FUTURE_COMMANDS.md)逐项列明5条准备命令、15组payload、34条worker模板、external-stop与两种入口/预定恢复。worker只能由RANGE控制器按固定计划调用，operator不独立启动。

完整入口：
~~~text
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/gc01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch04
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/gc01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch04 --resume
~~~

第二条只在预定C09退出23、root结果确认、AWAIT_EXPECTED_RESUME且resume_count=0时执行一次；保留boot/T0/账/deadline。未知退出关闭。

新动态许可后才可创建batch04根/inputs/out、安装拟用slice、verify并daemon-reload。随后写入真实批准原文BATCH04_AUTHORIZATION_TEXT.txt及root拥有的execution_authorization.json，字段含batch_id、scope、profile、limits、真实manifest/执行锁/安全合同hash、test_mode、该次授权原文hash和special_mapping_scope。当前静态任务文本不会充任动态许可。

预检必须重新核验当前kernel/systemd/账户、Python3.12.3/e50d…150f、原31关键文件、journalctl二进制/1224完整树、22源缓存、输入、目录权限及单位36项属性；差异或来源冲突直接拒绝初始化。源码只接受gc01 canonical目录，误路径47副本不参与。

## 输出与停止

未来Linux=/var/lib/dcl-r6/batch04/out，host导出=D:\毕业设计\DCL-R6-isolated-verification\batch04；当前均未创建。按执行锁journal_export_command在停止后立即只读导出当前boot内本批16个服务的journald JSON，保存原始双流；根launcher双流由外层记录器保存。该导出工具已锁hash，当前仅冻结命令。

保存原始journal/counter/intent/facts、34job全部原件、门负向审计、票据、stdout/stderr、时序、模型轨迹和源输入锁，再封存hash/ZIP。

必需case的FAIL/UNRUN/INCONCLUSIVE/MUTATION_NOT_DETECTED、意外故障/恢复、证据缺失、摘要漂移、预算/身份/时间异常均停止；禁止放宽300秒、重置窗口、自动重试或开启其他批次。S2预期模糊合成账永久占用并关闭；真实主账必须健康。F1/F4仅按冻结runner执行，真实基线反例及资源失败按既定规则保存首次输入/轨迹/退出并停止。

批准本申请仍不覆盖F2/F3、T1–T4、Casdoor、主系统代码、依赖安装、WSL重启、误副本清理或对外发送。D1条件裁决、强G覆盖、严格分离0、主机制实现门CLOSED保持。
