# 三态有界就绪合同与票据门

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

|状态|条件|行为|
|---|---|---|
|STARTING|Type=exec；获准start有正Job且inactive/dead/PID0，或activating/start*；无硬配置错/停止/失效|八项最终凭据不取值或明确未就绪，票据关闭；同一窗口fresh采样|
|READY|两侧active/running，8项实际值全MATCH，实际proc AS/CG与parent限额、身份/boot/version书签通过|生成native观察与私有lease，再复核并放行当前票据|
|FAILED|稳定失配、读取错误/缺字段、错误unit/type、身份变化/退出、boot/锁漂移、STOP/CLOSED、超时/写证失败|保存已取得数据、具体失败ID及raw_error，立即关闭，不继续等待|

[service_readiness.py:74 phase](<../../../DCL-R6-isolated-verification/cr01/src/service_readiness.py>)结合manager.Job和Type/ActiveState/SubState判定exec阶段；当前Job渲染按v255官方实现，使用--all确保空属性仍有明确记录。Job只在已由本流程请求启动、唯一批次单位、无并发特权干预的前提下指示排队，不能授权业务。

独立上界14秒来自原MainPID启动轮询上限，C00/C10从start请求前起共用该上界；有效until=min(start+14,T0+300,stop_at,deadline)。poll参数50ms、样本上限300，每行最多131072B；超过限额或未知状态即失败。取样/持久化成本都在既有窗口内，未追加300秒或新T0。阻塞I/O/调度总延迟保留原条件，不宣称硬实时。

只有原生OS collector可以产生Observation的私有mint，Lease还必须绑定case/unit/PID/starttime/boot/当前锁及pidfd。普通JSON或READY布尔标志无法构造有效lease。[service_readiness.py:311 require_lease](<../../../DCL-R6-isolated-verification/cr01/src/service_readiness.py>)、确认后的再次存活/期限检查及Root ticket摘要绑定组成放行链。

原八项数值完全保持；新增manager单位/类型/User/Group/Tasks/NoNewPrivileges和实际/proc AS/cgroup、parent pids/memory门仅加强证明。单位查询失败、属性缺失、活体UID/GID非法、资源确认错误、错cgroup和已发布终止均不等待。
