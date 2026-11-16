# batch03运行时与资源核验
Material Passport：启动前只读实测；RESOURCE_EVIDENCE_INCOMPLETE；实际payload资源边界NOT_EXERCISED。

## 本轮实测身份
|项目|当前观察|证据|
|---|---|---|
|内核/架构|6.18.33.2-microsoft-standard-WSL2 / x86_64|commands/02|
|boot_id|69cd81ea-49c6-44d5-b21e-0949a3c95c41|commands/03|
|Python|3.12.3；/usr/bin/python3.12 hash匹配|commands/01、04|
|systemd|255.4-1ubuntu8.18|commands/05|
|账户|UID999/GID989，补充组仅989|commands/06|
|页大小|4096|commands/07|
|完整文件锁|1266唯一路径全部匹配|commands/01|
|静态目录|/var/lib/dcl-r6为root:989 0750；lc03/src/inputs为root:root0755；所查source/inputs为root:root0644|commands/08|
|既有LC/批02单位|inactive/dead；旧service MainPID0|commands/09|
|本项目已加载运行单位列表|查询输出为空|commands/10|
|既有失败|仅mnt-e.mount|commands/11|

当前boot身份只绑定本次预检记录；尚无运行票据、batch_state、T0、deadline或launcher身份。/proc/uptime的预检读数不充当批次T0。

## 冻结资源合同及当前边界
既定总访问1000000、总墙钟1800秒、1740提前停、cal100000/300、单进程AS1GiB、父TasksMax4、普通AS计费映射条件驻留4GiB保持。瞬态payload的36个属性与14组argv延续BF静态对应清单，当前hash相同；实际batch03单位安装/激活次数0，故这些限制的本批实际内核执行尚待校准。

旧slice的MemorySwapMax显示infinity，旧service为0；这是原模板及既有manager属性的分别观察。拟用payload服务由冻结argv设置MemorySwapMax=0；当前未创建新服务，未据此宣告本批swap资格。AS4-PAYLOAD/1普通映射及特殊内核VMA单列评审的条件范围保持。

本轮11条只读命令包裹耗时之和10.736123秒；该量包括WSL客户端调度/查询开销，既非批次墙钟，也非payload运行时间。批次耗时、payload RSS/charge峰值、CPU时间均N/A。新payload访问/预留发放次数0；原历史32191保持。系统配置写入、单位安装/start/restart、依赖安装、WSL重启或关闭次数均0。

NO_RUNTIME_INITIALIZATION_CHECK记录host/Linux batch03根、批03slice文件及cgroup、lc03/out均缺失。只创建研究证据目录DCL-R6-batch03；运行目录没有初始化，无本批进程需要停止或清理。
