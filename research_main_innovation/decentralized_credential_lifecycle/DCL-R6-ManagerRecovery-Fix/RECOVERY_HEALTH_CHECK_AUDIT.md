# 恢复健康守卫与证据审查

Material Passport：ManagerRecovery-static-1/r5；MR-2=CONDITIONAL_PASS；原生行为UNRUN。

恢复前仍保留完整健康检查。新manager_recovery模块读取两侧failed集合、两次systemd单位快照及Root保护证据；所有查询保存argv、原始双流、退出码、进程和真实时钟。输出/单位数受界，当前集合或实例版本改变即停止恢复。

|退出类型|必须具备的独立依据|
|---|---|
|C06受控时间停止|当批Root PASS、原watchdog expired原件、绑定ticket、活体启动捕获、相同InvocationID/ExecMainPID、signal/9及真实exit时间属性|
|C07预设故障|当批Root PASS、ready身份、绑定ticket/启动实例、exit-code/23，完整boot/源/锁/T0绑定|
|C09交接及controller退出|上述原生单位实例证据，加真实意图ID、持久ACK、Receiver当前活性、Root直接waitpid raw/23、fresh HANDOFF_VERIFIED分类1、结果/收据摘要、原预算和deadline|
|历史已关闭batch09单位|仅固定三个单位，精确旧boot/InvocationID/ExecMainPID/退出状态及Root拥有的CLOSED、case/ticket/ACK/见证等SHA；作为历史关闭事实只读分类|
|其他失败|继续MR_UNREVIEWED_MANAGER_FAILURE，记录精确单位名并关闭|

每个C06/C07/C09单位在发放原ticket前捕获实际MainPID/starttime、InvocationID与启动属性，并将捕获SHA绑定ticket；退出后Root实际结果与该ticket匹配。只凭名字、exit23或PASS字段无法形成完整审查。C09原sender_prepare/ACK/Receiver/waitpid/resume_admission源码保持字节一致，新模块在其前后追加审查与当前责任证书。

等待恢复期间，从受保护HANDOFF_VERIFIED及BOOT_START核对同一Root owner，独立停止器持续检查稳定PID/boot/starttime；恢复后新的scheduler责任由原H.resume_admission原地更新。原预算快照在C09交接后保持不变，因此新检查工作在C09之前预付，恢复期间只扣Root私有检查游标。

新阶段A还需MR诊断批准与明确的关闭故障注入批准；scope与--calibrate-only绑定。公共MR_RECOVERY_REVIEW由Root固定0640发布，真实恢复后才生成。FORMAL导入业务前要求MR合成套件资格及当批真实恢复证书，继承C/BC/RootIPC/H/S/门18和fresh账资格均保留。

历史单位审查保持只读，当前包没有reset-failed或旧单位停止命令。若旧证明/实例不匹配，下一批预检照常失败，保留未决项。当前新ExecMainPID/Code、InvocationID接口与实测时延仍需动态验收。
