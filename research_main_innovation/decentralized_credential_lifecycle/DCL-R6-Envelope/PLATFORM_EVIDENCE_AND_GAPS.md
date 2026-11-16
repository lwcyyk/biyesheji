# 本机平台证据与部署缺口

2026-11-10。Material Passport：READ_ONLY_PLATFORM_QUERY＋ADMIN_CHECK；新增资源探针、校准、正式模型、Linux shell、平台配置、安装/下载均为 0。

## 1. 已取得的只读事实

|对象|观察与证据|推论边界|
|---|---|---|
|WSL 发行版清单|`wsl.exe --list --verbose` exit0；Ubuntu-24.04（默认）、Ubuntu-22.04、docker-desktop 均 Stopped，Version=2；[记录](evidence/WSL_READONLY_LIST.json)|证明已登记的 WSL2 发行版；活动 Linux 内核/权限仍未观察|
|WSL 组件版本|`wsl.exe --version` exit0；WSL 2.7.14.0，随附 kernel 6.18.33.2-2，WSLg 1.0.73.2，MSRDC 1.2.7214，Windows 10.0.26200.9711；[记录](evidence/WSL_READONLY_VERSION.json)|安装组件元数据；未认证实际运行发行版 kernel/custom override；本地化输出有编码损伤|
|宿主配置|用户 .wslconfig 未发现；effective_runtime_verified=false|缺文件无法认证未来实际 VM 内存/交换限制|
|Docker|固定本地 endpoint `npipe:////./pipe/dockerDesktopLinuxEngine` 的 info exit1，812.0184 ms，未超时，LOCAL_ENGINE_CONNECTION_FAILED；[记录](evidence/DOCKER_READONLY_INFO.json)|只确认此端点查询失败；具体管道/权限/服务原因未留证，不作唯一诊断|
|context/服务只读观察|desktop-linux 指向上述本地管道，无观测到 DOCKER_HOST/CONTEXT 覆盖；com.docker.service=Stopped，WslService=Running|辅助定位，不代表所有可能 engine 均不可用；本项为会话观察，原查询全输出未归档|

Docker 查询只持久化白名单状态/时长/错误分类，原 stderr 172 字节未保存，也未保存 info 代理/敏感配置。由于连接失败，镜像清单未查询。没有执行发行版内部命令，没有启动任何 stopped 环境。

## 2. 明确缺口与最小后续动作

|ID|尚缺证据|下一阶段可审动作（均待授权）|缺口后果|
|---|---|---|---|
|P01|实际 uname/架构、PID1/systemd 版本|仅启动 Ubuntu-24.04，固定只读管理命令|当前 PLATFORM_UNAVAILABLE|
|P02|cgroup v2 mount、memory/pids controller、祖先有效限制|读 mountinfo、cgroup.controllers/subtree_control、相关属性|任务/charge 语义未落地|
|P03|系统 manager 权限、目标 UID、策略封闭|先只读身份/目录属主/管理授权；写权限以日后具体配置许可确认|读到 root 身份也无法替代创建/限制验收|
|P04|原生 Linux Python 3.14 绝对路径/版本/哈希、标准库/动态加载|只检查现有 runtime；缺失则停，另提精确安装申请|Windows Python 禁止作为替代|
|P05|systemd 接口实际支持与有效 LimitAS/TasksMax/kill/clock|固定文档版本对照、未来单位属性读回与入口校准|文档支持≠本机配置生效|
|P06|成功 exec 初始 AS、特殊映射/权限及所有子孙|固定 kernel/runtime 入口路径审计＋获准后的低负载校准|A1/A4 仍条件成立|
|P07|计时含挂起、WSL/宿主暂停及停止响应|实际时钟/启动/退出取证，保留实时性假设|原严格墙钟未闭合|
|P08|本地文件系统持久性、空间、账与镜像权限|Linux 活账目录设计/摘要；仅获准后创建|账/短写故障恢复未验|
|P09|资源三文件 Linux 接口接线|资源范围专门授权后审查，业务五文件 hash 不变|当前八程序无法直接原样运行于新后端|

WSL 官方支持 systemd，但现有已安装发行版的实际启用情况仍需检查：[Microsoft WSL systemd](https://learn.microsoft.com/en-us/windows/wsl/systemd)。任何启用、重启、下载、创建 service/用户/cgroup 都属于后续配置范围；当前保持原环境。

## 3. 历史证据恢复

本轮已复核 Repair 原输出 37 项后锁存其 35 个文件及根导航快照，见 [BASELINE_LOCK](evidence/BASELINE_LOCK.json)。再次复核 batch01 原 62 文件、v3 八文件 static03，未发现 hash 差异；业务五文件 v2/v3 字节一致。原 ZIP SHA-256：

`358778fff25aa3f8354874803e2cc26cbaac1d7d70478e9f0923f9c756559594`

原 ZIP 为 60 项（59 条 manifest 文件＋manifest 本身）。batch01 原资源账为 27 次、118.7340827 秒，deadline=2026-11-10 05:32:39.337 UTC/13:32:39.337 上海，已关闭/到期；F1/F4 正式运行 0。v3 仍为部分静态候选，尚无语法/导入/校准运行。

87 的唯一根因、96 MiB Job peak 差异和 4 KiB WS 差异仍未认证。原子 current 在释放后、父 current 在退出后取得，继续保留该时窗解释。原失败和历史一般证明/外部复核层级均保持，当前行政哈希复核也只登记 ADMIN_CHECK。
