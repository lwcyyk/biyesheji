# P之后：L阶段精确需求与最小申请

2026-11-10。Material Passport：NEXT_STAGE_PLAN_ONLY；本文件中的后续命令均未执行。当前P授权已经完整使用；L资源接入/配置、安装和batch02执行仍需匹配的新授权。

## 1. 已可锁定与仍缺字段

|字段|当前可用值|剩余工作|
|---|---|---|
|目标发行版/内核/架构|Ubuntu-24.04；6.18.33.2-microsoft-standard-WSL2；x86_64|新的部署窗口重新绑定boot_id、kernel身份及摘要依据|
|PID1/工具版本|/usr/lib/systemd/systemd；systemd255 (255.4-1ubuntu8.18)|manager真实Version/SystemState、厂商版本与属性支持/有效值|
|资源层级基础|cgroup2；根memory/pids可用且启用；当前init.scope|父slice/祖先读回、权限和限额审计|
|runtime|NATIVE_PYTHON314_UNAVAILABLE（仅两路径）|现有路径发现或确切安装提案，3.14.x/来源/hash/stdlib/loader|
|目标UID|查询root；payload专用UID未知|核查既有专用身份；缺失再申请建用户/组|
|活账路径|候选/var/lib/dcl-r6/batch02，其已观察挂载祖先为ext4|存在/属主/空间/锁/fsync；本阶段未创建|
|单位结构|候选dclr6batch02.slice，所有case/service作其后代|完整单位文本/权限/启动与停止命令锁；命名避免隐式多层slice|
|角色|C集Controller/顺序Worker/预算/日志，C监督线程，W独立Watchdog|最多4task；权限/首入口/全部子孙/崩溃和退出接线|
|外部停止|TCB预置绑定T0/boot_id的停止源，1740秒提前停止|clock、manager定时入口、绝对时间与停止响应的具体设计/校准|
|模型业务|五文件原字节及F1→F4固定顺序|Linux资源API接入、所有收费点/输入/命令摘要|

## 2. 建议先申请 L-R：有限只读补缺

下列是供新许可审阅的具体argv清单。它们超出P的12条范围，**本轮均未执行**。仍固定Ubuntu-24.04，独立argv，无shell组合。先核对工具路径，缺工具或权限只记录并停止依赖项。

```text
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/ls -l /usr/bin/find /usr/bin/getent /usr/bin/apt-cache /usr/bin/df /usr/bin/sha256sum
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /etc/os-release
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/systemctl show --property=Version --property=SystemState
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/systemctl show init.scope --property=ControlGroup --property=TasksMax --property=TasksCurrent --property=MemoryMax
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/getent passwd dcl-r6
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/getent group dcl-r6
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/ls -ld /var/lib /var/lib/dcl-r6
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/df -PT /var/lib
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /sys/fs/cgroup/cgroup.type
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /sys/fs/cgroup/system.slice/cgroup.controllers
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /sys/fs/cgroup/system.slice/cgroup.subtree_control
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/find /usr/local /opt -xdev -type f -name python3.14 -print
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/apt-cache policy python3.14
```

现有runtime搜索严格限`/usr/local`和`/opt`，不随符号链接扩展、不全盘搜索；结果为空只表明该搜索范围。apt-cache只读本地缓存，不更新源、不下载/安装。getent缺条目属于预期发现，不能据此创建账户。system.slice缺路径/文件时保留层级缺口，不写控制文件补齐。

如找到真实native Python，下一份读取锁再绑定该绝对路径的`--version`、sha256sum、stdlib/loader元数据与需要的映像审计命令；当前路径未知，保持该部分未就绪。L-R不包括Python导入、资源探针或模型。

## 3. 依赖/配置的最小变更申请分支

|分支|触发条件|需先准备的具体审阅材料|当前动作|
|---|---|---|---|
|R-PY314|有限发现仍无可核验3.14|准确3.14.x/来源/摘要、目标位置、依赖、下载/构建/安装命令及代理条件|只列需求；不虚构候选包/下载地址|
|R-UID|缺适合专用身份|目标dcl-r6名称、明确UID/GID/账户属性、目录权限和冲突处理|待只读查询后确定数值；当前不建用户|
|R-UNIT|runtime/身份/静态证明足够|父slice与service完整文本/属性/摘要，目标UID，管理命令/控制文件影响，外部停止事件|需具体配置许可；当前不创建单位/目录|
|R-ADAPTER|资源接入获得匹配许可|仅资源三文件的Linux接口实现范围与diff，guard被业务导入的兼容API、账/日志/权限/停止设计|本轮新代码0；不修改业务五文件|
|R-CAL/F|最终合同与全命令锁完整|单批100万/1800秒/AS4条件4GiB，全部C00–C12及F1→F4的精确输入/命令/停止/封存|batch02仍UNAUTHORIZED|

系统manager已经观察到，本轮无“启用systemd”变更需求，也无Docker或其他发行版启动需求。若后续出现新证据再限定范围。当前root查询可作为配置入口线索，实际manager权限与降权策略仍需认证；不自动增加sudo/Polkit改动。

## 4. 资源部署与代码准入

拟议父slice：总TasksMax=4、MemoryMax=4294967296（次级charge保护）；每个service继承父层总任务界并设置LimitAS soft=hard=1073741824，Type=exec、Delegate=no、Restart=no、KillMode=control-group及冻结停止策略。逐case激活并共享单账/绝对deadline。配置属性、初态映像AS、特殊映射和权限封闭缺一项便阻止动态资格。

Envelope原资源程序为Windows接入，v3适配器主动拒绝。未来R-ADAPTER只允许在新的获准范围完成资源三文件接线，五业务文件字节不变，历史版本/失败记录保留。标准库、guard兼容接口、语义导入前准入、计数短写/中断与整组故障联动必须列入审查。单Worker保持F1模型/monitor模块分离及F4 DP/参考语义独立。

主机制IMPLEMENTATION_GATE仍CLOSED。当前没有严格分离实例，也没有新增候选凭据机制的实施资格。验证设施的具体后续工作亦须用户匹配授权；原则认可候选资源合同不生成代码或执行许可。

## 5. 五业务文件原始摘要

|文件|SHA-256|
|---|---|
|f1_model.py|5669c8486d00f56085ef1a69ad7b40c3fc328bd41ae1a8424f1cd68018911d35|
|f1_check.py|1ed89b7da8a03593d49cd91c409e161eb8a118584d8e066423feefbaf6e21645|
|f4_dp.py|a07194f1dbec98efc2932186777f5bdb084012e3d8b5784d9b3c27b6ecbb50c5|
|f4_reference.py|9d1fcbc5752bfe7c6cd0308fb06a838174834dfe0b2f23a75c352418c3047e2b|
|compare.py|3848301c699b5a25a284e5747bb37d38d61ddb144cf49e0506e3ea82a5b7244f|

源锁沿用`DCL-R6-Repair/evidence/V3_SOURCE_LOCK.json`，本轮在行政核对中再次验证。历史batch01仍27次、118.7340827秒、CLOSED_RESOURCE_GATE_FAILED；新P命令耗时独立记录，未打开batch02。

P5=PARTIAL：可以形成如上真实平台驱动的L补缺清单；最终实施/配置/批次命令仍因runtime、UID和接口接线缺失而无法锁定。本文件明确结束P，后续仅依新授权推进。
