# LR：systemd与专用身份权限

2026-11-10。Material Passport：只读manager/单位/身份查询。命令12–21、30为主要证据；没有试写、单位创建/启动/停止、用户创建或Polkit修改。

## 1. manager状态

实际manager接口返回Version=255.4-1ubuntu8.18、SystemState=degraded，默认TasksAccounting/MemoryAccounting=yes、DefaultLimitAS及Soft=infinity。失败清单仅列mnt-e.mount，其LoadState=loaded、ActiveState=failed、Result=exit-code。未读取journal或推断更深层原因；不修复或访问/mnt/e。候选Linux活账位于根ext4，部署前需复核该故障是否仍仅限此范围，任何新增关键失败阻止启动。

当前身份root，manager私有socket为root:root/0700；只读systemctl成功，证明查询接口可访问。实际创建/配置权限未进行写测试；后续以root系统manager入口操作仍须明确授权，payload使用专用非特权身份。

## 2. 官方支持、现有值与未来动作

|属性|255官方支持|本机只读证据|未来部署/验收|
|---|---|---|---|
|LimitAS|每进程soft/hard|默认及journald均infinity|目标exec前1GiB双限、初态映像/继承审计|
|TasksMax/Accounting|pids分层/线程计数|根/system.slice infinity；journald18745；Accounting=yes|独立父slice总4task，逐case整组覆盖|
|MemoryAccounting/Max|charge计量及控制|根/system.slice Max=infinity|4GiB次级charge保护；保留暂超语义|
|KillMode|control-group等|journald=control-group|目标全树退出和失败时序待校准|
|Restart|可配置|journald=always|目标no，禁止意外补窗/重启|
|RuntimeMaxSec|服务运行时限|journald RuntimeMaxUSec=infinity|只能作辅助；T0绝对停止另设|
|Delegate|可配置|system.slice/journald=no|payload不持组管理权，实际权限核验|
|NoNewPrivileges|可配置|journald=yes|目标专用身份+空capabilities+代理封闭|
|User/Group|可配置|当前query root；journald属性为空|目标dcl-r6用户和组待创建|
|文件系统限制|ProtectSystem/Home等|journald=no/no|目标只读runtime/源码，限本批写入，WSL/代理路径屏蔽|

journald只是属性接口样本，未据其值推导本批单位已存在或可配置。其他服务均保持原状。官方来源复用Envelope的systemd.exec/resource-control/service/kill v255；实际厂商补丁与执行语义仍按未来固定配置验证。

## 3. 身份与权限变更需求

getent passwd/group dcl-r6均exit2、无条目。建议L-C审批后创建专用system用户/同名组，使用系统分配的空闲UID/GID，实际数值在创建后锁定；发生既有同名/并发变化则停止核对。无需修改系统默认Python或授予payload sudo。

TCB负责root-owned单位/只读源码/授权manifest，payload只读输入、只写自身out预算/日志。User/Group=dcl-r6，能力集合清空，NoNewPrivileges=yes、Delegate=no、ProtectControlGroups等策略封闭直接迁组与提额；外部manager、D-Bus/cron/at/Docker/WSLinterop等代理入口仍须逐项阻断。

普通UID本身无法证明外部代理全部封闭。Windows盘、WSL驱动/interop入口可见这一历史事实继续有效。候选单位策略及所有访问/故障测试列入L-C与未来batch02；本阶段未配置任何一项。LR-3的权限子项为PARTIAL。
