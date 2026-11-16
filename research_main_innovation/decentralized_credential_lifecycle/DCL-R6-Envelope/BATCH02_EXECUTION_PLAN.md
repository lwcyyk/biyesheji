# batch02 静态执行清单与校准方案

2026-11-10。Material Passport：PLAN_ONLY；AUTHORIZATION=UNAUTHORIZED；全部 actual=null。拟议 host 目录 `D:\毕业设计\DCL-R6-isolated-verification\batch02`，Linux 活账目录 `/var/lib/dcl-r6/batch02`，均未创建。当前 E4=PARTIAL_UNAUTHORIZED：完整 case/停止规格已给出，实际平台/适配程序/命令摘要尚缺。

## 1. 分阶段准入

|阶段|允许范围及结束条件|本轮状态|
|---|---|---|
|P 平台资格|单独批准启动 Ubuntu-24.04，运行下节白名单只读命令；无资源探针/模型/配置|待授权|
|L 静态锁定|根据 P 真实结果确定 UID/runtime/路径/全部属性/内核映射审计；资源三文件平台接入另获匹配授权|缺实际信息；当前无代码变更|
|A 新批次许可|明确接受 AS4-PAYLOAD/1 的边界/计量/时间差异，签定最终命令/摘要和单批预算|UNAUTHORIZED|
|C 动态校准|仅在 A1–A5 前提的部署审计足够后执行下表；关键项均有实际证据|UNRUN|
|F 正式 F1→F4|C 全部通过、收据/锁一致、剩余额度足够、授权明确包括正式模型|UNRUN_RESOURCE_GATE|
|Z 关闭封存|全部 payload/后代退出后核对总账，封存原始字节、结果和 hash|UNRUN|

平台准备的安装/配置/启动开销单列，超出批准的只读命令便停。P 阶段缺 systemd/Python/权限时，先形成具体缺项及配置/安装申请，当前方案没有自动安装或重启授权。Linux 业务语义无需重写，适配范围只限资源接入。

## 2. P 阶段可审命令清单（当前均未执行）

以下每行是独立 argv，无 shell 组合，绑定唯一发行版。首条会启动当前 Stopped 的 Ubuntu-24.04，故须新授权。后续发行版为 Running 才执行；任一失败保存原错误并停止相关依赖检查。

```text
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/uname -r
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/uname -m
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/readlink -f /proc/1/exe
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/systemctl --version
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/id
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/stat -fc %T /sys/fs/cgroup
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /proc/self/mountinfo
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /proc/self/cgroup
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /sys/fs/cgroup/cgroup.controllers
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /sys/fs/cgroup/cgroup.subtree_control
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/cat /proc/sys/kernel/random/boot_id
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/ls -l /usr/bin/python3.14 /usr/local/bin/python3.14
```

这些候选 Python 路径缺失时仅登记缺项；进一步路径发现单列。原生 Python 的 `--version`、sha256sum、stdlib/loader 位置和依赖核对，在发现真实路径后加入最终锁。禁止调用 Windows Python 或自动回退版本。只读命令可能留下正常系统管理痕迹，P 阶段按“启动发行版＋平台只读检查”请求授权。

## 3. L/A 必须冻结的清单

授权收据及修订合同摘要；Windows/WSL/实际 Linux kernel/架构/boot_id；systemd 版本与完整配置文本及摘要；native Python 二进制/stdlib/动态加载依赖标识；八程序及五业务原摘要；完整平台适配 diff；父 slice 与每个 service 的名称/属性/UID/权限策略；所有探针/输入/正式参数/顺序；预置绝对停止事件；账格式和恢复规则；输出目录/文件系统；所有管理、启动、校准、正式、关闭和导出命令逐 argv。

管理指令类别为 systemd-run 创建固定父 slice 下的 service、systemctl show/kill/stop 及只读 cgroup/proc 查询。当前接口入口尚缺 Linux 适配实现，原 `guard.py` 命令无法直接复用；本文不给虚构的可运行新 flag 或未存在脚本。未来最终 COMMAND_LOCK 必须用真实绝对路径与现有 CLI 解析结果填满；任何占位/null 均阻止 A→C。本轮 E4 因这些缺项维持 PARTIAL。

批次启动时在 manager 首次激活之前记录 T0、boot_id 和绝对 deadline。单批 1,000,000 次访问/1,800 秒/AS4-PAYLOAD 条件 4 GiB；所有 case 共用同一全局持久账。建议校准分配软额度 100,000 次/300 秒，全部已包含于总上限；正式阶段使用实际剩余，软预算用尽便停止，不获得第二窗口。

## 4. 完整动态校准矩阵（待执行）

|ID|输入/动作|必须记录/通过条件|立即停止条件|
|---|---|---|---|
|C00 入口|固定系统 manager/父 slice/目标 Python，普通最小入口|启动前 pids 与单位 AS soft/hard；首 exec 映像/限制继承/初始映射审计；全部身份|属性忽略、A1–A5 缺证据、入口不在组|
|C01 正常|C/W 握手、固定有限 probe 正常退出|任务数/身份/AS/账/退出与整组空；RSS/charge 字段分列|日志/账/成员证据缺失|
|C02 AS|已受全局 AS 约束的校准 child 再降低局部 AS 至 96 MiB，1 MiB 步进、逐页触及，有限最多 128 MiB 尝试|每一步持有时映射/驻留/限制；ENOMEM/MemoryError；释放前后和退出分窗；失败留证|无有效全局界、异常增长/子孙遗漏；局部起点仅证明设置后行为|
|C03 映射/共享|小额匿名/文件/共享页、fork/exec 继承，固定 ≤16 MiB 数据|跨进程共享重复 RSS 的记录；初始/继承 AS；特殊映射审计|未审映射/权限、指标转换不明|
|C04 数量|C/W/监督线程占已知 task；受控 child 用尽第 4 槽，尝试第 5 任务|父 slice pids.max=4；拒绝证据、成员/线程清单；总 AS 合成≤4 GiB|组织操作可突破、额外任务成功|
|C05 额度|局部 cap17，串行/并发竞争第 18 次；总账预收费|只授17次；grant 前 durable reserve；拒后无语义处理|任何多授/回滚/新窗口|
|C06 时限|短局部绝对 deadline、sleep/busy/descendant|预先武装 manager 停止源＋C/W；触发/信号/最后活跃/全退出时刻|停止未确认、时钟错域或超出申请保证|
|C07 C 崩溃|固定注入票据，C 异常退出|W/manager 联动、全部后代终止、持久账一致|残留/未知身份/真实总账模糊|
|C08 W 崩溃|W 异常退出，C 正常/忙碌两种有限输入|C 监督/下一grant拒绝；manager 截止兜底；整组退出|失去 W 后继续发放/缺终止证据|
|C09 无响应/Launcher|C 阻塞、Launcher 激活后退出、重复启动请求|预装停止事件独立生效；单次身份；无第二单位/账|Launch 断线导致新免费窗口|
|C10 逃逸|受控 fork/exec、cgroup 迁移/权限提高、外部代理尝试|内核限制/权限拒绝，继承归属；阻断管理 IPC/WSL interop|组外工作或管理权限可得|
|C11 IO/事务|局部已预收费镜像账的短写/fsync/各意图阶段中断|PREPARED/COMMITTED 恢复规则，模糊预留占用、拒绝继续|真实总账或关键日志破坏；整批关闭|
|C12 关闭/错身份|错 batch/过期/closed/错boot_id 的局部收据、正常空组关闭|拒绝前后真实总账不回滚；组空/所有pidfd退出|自动恢复/重复初始化；无需真实重启宿主|

C02 小局部 AS 旨在低成本触发失败，全局 1 GiB 界始终先在；分配/触页迭代设置有限数量，按冻结 probe 访问规则预收费。任何候选/参考/重放/变异语义访问继续原 visit 定义；资源操作的额外计数单列并占总预算预留。所有 planned destructive case 的最大局部操作先预留，总账事务保持清晰。若真实总账遇到模糊状态，则终止整批。

每项需记录 input/command/source/auth hash、预期、actual、退出、时钟、资源与判定。预声明注入导致的预期退出只有在清理/账证据完整时才算 case 通过。下一 case 必须等待前一 service 空组；同一父 slice 持续强制最多 4 tasks；Restart=no。任何关键 FAIL/INCONCLUSIVE 都停止批次，取消后续激活。

Windows 原错误87/commit/WS失败的鉴别不属于 Linux 资格必需项，历史裁决仍失败/未决；如另做 Windows 诊断，另申请其受限路线，避免混入当前批准范围。

## 5. F1/F4 顺序与结果合同

固定业务五文件与原 inputs/batch01.json 语义。F1 原顺序：SMOKE_UNKNOWN、RELEASE_EMPTY、BRANCH_UNKNOWN、9 个原序 mutant、POST_TAKEOVER_B、CHAIN、RECOVERY_ABORT、固定 Key 认证表；原基线/变异 soft visits 为 12,000/8,000。首次反例保留原轨迹并计费独立重放，再区分协议/假设/抽象/实现错误。有限域穷尽且检查/覆盖要求满足时才能 PASS_BOUNDED；soft cutoff/未行使分支单列。

F4：固定夹具→G64，m=0..20、h∈{0,1,2}，压缩开/关/独立参考及逐策略/具体轨迹比较；随后原 10 项 mutant 顺序。DP/参考的 Post/终态/代价/压缩实现保持独立。输入校验和参考/重放全部占总账。任一基线差异/错误即停止保存；未捕获 mutant 记覆盖缺口，阻止相应性质整体通过。

所有任务在剩余访问/时间内执行，超限标 INCONCLUSIVE_LIMIT。缩小域、改参数或重新开始需要新的明确版本/授权，当前授权草案未包含自动缩域重跑。资源资格收据绑定实际源码/输入/runtime/单位配置摘要，只有同锁执行可使用。

## 6. 关闭

T0+1740 秒起停止业务并请求整组终止；绝对 deadline 前确认退出的目标需写明调度/终止假设。若未确认则保存 STOP_UNCONFIRMED，后续停止动作仅限清理，持续登记实际耗时，不制造合格时间窗。

关闭后导出：全局账/预留journal、各 case 的输入/命令/输出/异常、组 current/peak/events 与 RSS 分窗、全部角色/boot_id/时钟/退出、代码/输入/授权锁、模型结果与覆盖、manifest 和 ZIP SHA-256。batch01 原件只读，27 次/118.7340827 秒另列历史失败成本，禁止并入新窗口后消失。
