# 双次取样、身份锚与一致性前提

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

不存在跨systemd、procfs和cgroup的共同原子状态版本。源码使用有限书签和双次收集：unit前读→pidfd/identity锚→proc及parent读→unit后读→proc及parent后读→PID/boot/FD再检查；READY要求全部值符合原约束，两个manager版本及目标身份一致。

manager版本含InvocationID、StateChangeTimestampMonotonic和关键属性的原值；后者只作不透明版本比较，不与BOOTTIME相减。pidfd防止把退出/复用的新PID当作原目标，PID/starttime/boot在采样内与相邻样本均检查；非零MainPID及Invocation改变失败。合法PID0→assigned或STARTING→active只生成新轮次NOT_READY，不拼接成READY。

进程credentials/status为同一proc文件读，实际AS/cgroup及parent限额单独双读；任何稳定不符、退出或读取失败直接终止。lease确认再次进行完整采样，票据写前再核存活/期限/停止，Root票据绑定证书摘要。

一致性前提：冻结controller在ticket前只等待，不自行改变凭据/资源；无并发特权代码/单位/成员更改。两侧相等无法完全排除特权ABA、瞬时资源迁移或读后立刻退出，这些继续CONDITIONAL，原服务内kernel admission和完整资源门仍需fresh检查。源码不把八个时刻的匹配无条件宣称同一原子快照。

当前采样和pidfd均未实际执行；后续动态许可需记录这些书签与未知窗口。[原生collector](<../../../DCL-R6-isolated-verification/cr01/src/service_readiness.py>)、[静态检查](evidence/STATIC_CHECKS.json)。
