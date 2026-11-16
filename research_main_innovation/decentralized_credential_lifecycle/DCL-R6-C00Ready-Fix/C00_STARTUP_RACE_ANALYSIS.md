# 启动暂态、真实错误和循环等待审查

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

上游systemd v255分别提供MainPID登记和exec完成通知路径：service.c:2198–2205在SERVICE_START登记main pid；3197–3231处理exec-fd事件后进入下一状态。--no-block仅验证/排队。Type=exec的启动完成语义针对成功exec，不等价于应用业务初始化；notify的READY=1属于另一协议。

[v255 service源码](https://raw.githubusercontent.com/systemd/systemd/v255/src/core/service.c)、[v255 service文档](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.service.xml)、[v255 systemd-run文档](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd-run.xml)。本轮查阅公开源码，实际Ubuntu255.4补丁/当前manager没有新查询；不据上游顺序认定batch07某个字段必定处于何值。

原Guard在--no-block后MainPID非零即离开轮询，随即把进程视作最终执行身份。这一屏障缺口已由源码确认。Starting-only消息和782336B的低charged peak支持启动临态假设，因果仍未完成；C00失败不能直接归为竞态、错误资源配置或新协议漏洞。

合法暂态只按manager exec阶段定义：获准start仍排队且无MainPID，或Type=exec处于activating的start/start-pre/start-post。原八项中的最终凭据在exec未确认前不取值，标记NOT_READY；一旦active/running，实际UID/GID、能力、AS或cgroup错误立即FAILED，绝不等待其“变正确”。配置中已确认错误的AS/TasksMax/类型等即使STARTING也失败。

循环依赖审查：controller启动后先等待Root ticket，再做kernel admission/探针。若Root等待依赖ticket的应用ready，双方会死锁。新屏障等待manager认可的exec状态及真实内核身份，不等待应用READY=1、C00.probe或业务访问。READY票据放行后原探针才运行。

[就绪合同](C00_SERVICE_READINESS_CONTRACT.md)、[采样一致性](C00_SNAPSHOT_CONSISTENCY.md)、[公开源码审计](evidence/PUBLIC_SOURCE_AUDIT.json)。
