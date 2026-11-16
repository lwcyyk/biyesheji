# P：实际运行平台证据

2026-11-10。Material Passport：PLATFORM_READONLY_P；仅按授权执行 12 条独立 argv；资源探针/校准/模型运行 0。P 专项已授权，AS4-PAYLOAD/1 仅获原则接受，batch02 仍 UNAUTHORIZED。

## 1. 原始记录与顺序

授权原文、收据和冻结命令分别见 [授权](evidence/P_AUTHORIZATION_TEXT.txt)、[收据](evidence/P_AUTHORIZATION_RECEIPT.json)、[命令锁](evidence/P_COMMAND_PLAN.json)。本次白名单与 Envelope 计划的 12 条完全一致。每条使用 Windows `ProcessStartInfo.ArgumentList` 直接启动固定 wsl.exe；无 Linux shell、无字符串拼接成 shell 命令、无命令并行、无额外 Linux 查询。

|序号|查询对象|exit|实际输出/结论|
|---|---|---|---|
|01|uname -r|0|6.18.33.2-microsoft-standard-WSL2|
|02|uname -m|0|x86_64|
|03|readlink -f /proc/1/exe|0|/usr/lib/systemd/systemd|
|04|systemctl --version|0|systemd 255 (255.4-1ubuntu8.18)，default-hierarchy=unified|
|05|id|0|uid=0(root) gid=0(root) groups=0(root)|
|06|stat cgroup 文件系统|0|cgroup2fs|
|07|当前 mountinfo|0|cgroup2 rw/nsdelegate；根 ext4；Windows盘为9p/DrvFS；hugetlbfs存在|
|08|当前进程 cgroup|0|0::/init.scope|
|09|根 controllers|0|cpuset cpu io memory hugetlb pids rdma|
|10|根 subtree_control|0|cpu memory pids|
|11|boot_id|0|原值本地保存，本文省略唯一标识|
|12|两个固定 Python3.14 路径的 ls|2|两路径均报告 No such file or directory|

[P_COMMAND_RESULTS](evidence/P_COMMAND_RESULTS.json)保存每条精确 argv、开始/结束时间、单调耗时、退出码、stdout/stderr、原始字节文件摘要、输出解释与权限范围。`evidence/commands/NN.stdout.txt`、`NN.stderr.txt`为重定向流原始字节，metadata 为 `NN.result.json`。

## 2. 运行环境判断

uname 的实际 release 带 microsoft-standard-WSL2，结合已冻结管理清单中该发行版 Version=2，支持“Ubuntu-24.04 的指定查询实际运行于 WSL2 内核”。此前 Envelope 的安装组件 kernel6.18.33.2-2 只是元数据；本轮首次取得此发行版内部 release。

PID1 的实际可执行文件单独由命令03观察为 systemd。命令04提供工具版本和编译特性，二者合用支持 systemd 作为下一阶段的候选系统 manager。版本输出仍无法认证 manager D-Bus 权限、所有 service 属性有效值或厂商补丁的完整行为。

实际 systemd 主版本255与 Envelope采用的官方v255文档相符。255.4-1ubuntu8.18 是本机工具报告的发行修订；未读取其二进制摘要/发行包源码/运行中 manager 版本属性，后续仍需锁定。编译输出含 +SECCOMP、+APPARMOR，-BPF_FRAMEWORK；这些是构建能力标签，尚无已应用沙箱策略证据。

12次输出是顺序的分时观测，只有命令11读取一次 boot_id。跨命令同一启动代次、配置稳定性与原子快照均保留为后续锁定责任。当前没有业务 payload，也没有从首条目标指令生效的资源包络实例。

## 3. 警告与编码

全部12条均收到 WSL 原生警告：检测到 localhost 代理配置，未镜像到 NAT WSL。命令01–11仍返回0，命令12的失败由两个缺失路径明确解释。当前本地只读检查无需网络；本轮保持代理/WSL配置原样，后续下载方案须单独考虑此环境条件。

原生 WSL stderr 为 UTF-16LE；命令12在其后拼接 UTF-8 的 Linux ls 错误。已按原字节边界解码，保留初次错误编码视图 `01.initial-decode.json`、`12.initial-decode.json`及更正说明；没有重跑命令。原始流摘要始终按未经改写的字节计算。

## 4. 时间与已知运行状态

命令窗口：08:40:45.7746418–08:43:28.9637533 UTC，即16:40:45.7746418–16:43:28.9637533 上海。12条命令单调耗时之和21.1719751秒，首命令开始至末命令结束的墙钟跨度163.1891115秒（含命令间审查）。这些数值分别描述执行耗时和查询窗口，未计作整个文档编制时间，也未占用尚未启动的 batch02 时间窗。

Ubuntu-24.04在获准命令执行期间已实际运行。末次命令后的即时 Running/Stopped 状态未另行查询；本轮没有 shutdown、terminate、额外 list 查询或主动停止。其他发行版和Docker的当前状态亦未追加检查；本轮未请求启动它们。

Gate P1=PASS_STATIC，含义为平台只读证据审查完整。RESOURCE_GATE_PASS 继续 NOT_OBTAINED。
