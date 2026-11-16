# MANAGER实际含义与根因

Material Passport：MR-1=PASS_STATIC；依据CalDiag原始轨迹及冻结r1源码；新增运行0。

**错误名称中的MANAGER指systemd的failed-unit集合。** guard._launcher_body使用systemctl list-units --state=failed，逐行仅接受mnt-e.mount。触发谓词涉及服务单位状态；Root协调器、Sender、Receiver和恢复scheduler是另行记录的进程角色。systemd journal管理器记录的_PID=1提供组件来源旁证。

CalDiag C06的受控时间停止、C07的预设exit23、C09交接后的controller停止，分别留下signal/9、exit-code/23、signal/9的failed单位。它们具有当批Root PASS，C09还具有完整持久交接链。恢复前言沿用启动前的严格集合规则，缺少这些预期故障实例的审查/清理语义，因此失败。新的scheduler exit125是该异常的后果。

|假设|证据分类|裁决范围|
|---|---|---|
|H1 预期退出未认可|SOURCE_SUPPORTED、TRACE_SUPPORTED|本批预期failed service/controller实例被拒绝；“必须旧Sender永远存活”并非触发代码|
|H2 C09退出未审查|CONTRADICTED|ACK、Receiver、waitpid及HANDOFF_VERIFIED均已实际完成；缺的是systemd单位实例审查证书|
|H3 旧/竞态快照造成此错误|UNRESOLVED|精确failed查询stdout未落盘；当前证据支持确定性分类缺口，未确认竞态为本轮原因|
|H4 新Root/Manager意外退出触发|CONTRADICTED（触发谓词层）|该谓词读取systemd失败单位，恢复scheduler异常退出发生在抛错之后；其他未采样事件保持范围边界|
|H5 生命周期合并/恢复策略错误|SOURCE_SUPPORTED、TRACE_SUPPORTED|预期故障单位与未审阅故障未分开；恢复前言和非零返回还漏自动关闭|

关闭缺口具有三处组合：前言位于清理try之前；父launcher普通wait返回125直接向外返回，异常清理不执行；C09完成后state清空coordinator_identity，独立停止器只有该身份存在时才检查Owner丢失。初始无CLOSED/seal而Root停止器继续等待的事实与代码吻合。

[H1–H5结构化登记](evidence/ROOT_CAUSE_HYPOTHESES.json) · [真实时间线](MANAGER_FAILURE_TIMELINE.md)。原UNREVIEWED_MANAGER_FAILURE和所有历史失败/预算保留，本轮没有将缺记录的首个单位补写为具体名称。
