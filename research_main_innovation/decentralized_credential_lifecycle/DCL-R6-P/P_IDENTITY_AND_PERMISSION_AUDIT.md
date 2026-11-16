# P：身份、权限与隔离审查

2026-11-10。Material Passport：命令05的只读身份事实；管理/降权/沙箱配置未执行。

## 1. 已观察身份

`wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/id`返回uid=0(root)、gid=0(root)、groups=0(root)。本次固定argv未带`--user`，因此这次默认执行上下文为root。该事实可以支持后续受信配置入口的候选设计。

只读id无法认证当前namespace中的capabilities、systemd manager控制权限、Polkit规则、文件系统写权限或可创建专用身份。当前没有运行sudo、写测试或单位创建。root查询身份也与未来payload的专用非特权身份分开登记。

## 2. 未来权限需求

|工作|拟议承担者/权限|已知/待决|
|---|---|---|
|创建父slice与service/武装停止事件|受信系统manager入口，root或精确管理授权|root身份已观察；manager控制权限仍需只读接口核验及获准后真实配置|
|AS/pids属性设置|manager在目标exec前应用；限制不可被payload提高|接口静态支持；实际配置/权限尚缺|
|payload执行|专用非特权UID，空capabilities/NoNewPrivileges|UID名称/数值未知，专用账户是否存在未查询|
|日志/预算路径|TCB创建隔离目录；payload仅能写自身账/日志|候选Linux ext4祖先已观察；目录/属主/空间未核|
|外部管理代理封闭|限制systemd/Docker/cron/at/WSLinterop/网络与可写代理路径|mountinfo表明Windows盘可见；有效阻断策略尚缺|
|证据封存导出|组退出后的外部只读复制/摘要|当前仅P报告位于host；未来批次目录未创建|

未来payload以root运行会扩大提高rlimit、迁组及外部代理的可能性；本方案要求专用非特权身份并锁定能力/IPC/文件系统策略。管理入口保留在外部TCB，全部C/W/Worker/预算/日志/probe及后代仍受同一父slice计量。

## 3. 最小后续申请

先授权L的只读身份/目录/管理接口检查，确定是否已有适合UID。若已有身份与所需权限，优先复用经审查的配置；若缺失，另以明确账户名、UID/GID、目录、属主/模式、资源单位和影响范围提出配置申请。当前没有创建用户/组、提升权限、修改Polkit或安装服务。

sudo/Polkit是否需要取决于最终受信Launcher身份与manager授权路径。本轮观察root并未触发额外提权请求；未来的专用payload仍须证明无法控制manager、迁组或提高AS硬限额。[RLIMIT权限语义](https://man7.org/linux/man-pages/man2/getrlimit.2.html)及[systemd代理边界](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.exec.xml)沿用Envelope的官方依据。

P3的管理身份子项为PARTIAL；整体P3因原生Python缺失判FAIL。身份检查完成与资源部署资格分别登记。
