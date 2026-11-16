# DCL-R6-Envelope 最终裁决

2026-11-10。Material Passport：资源后端选型、启动/内存条件证明、静态部署与新批次申请。九份要求文档已形成；本轮新增校准/模型/验证代码/平台启动/配置/安装均为 0。

## 1. 选择与停止条件

**选定 C：WSL2 Ubuntu-24.04＋systemd 系统 service；每进程 RLIMIT_AS soft=hard=1 GiB，单批父 slice TasksMax=4。** 同批各校准 service 顺序激活，正式阶段一个 Worker 顺序执行 F1/F4；所有 service 后代共受父 slice 总任务数界。cgroup 内存字段作为次级 charge 保护/诊断。此选择为待批准的 **AS4-PAYLOAD/1**，当前没有可运行的新后端。

原合同结果 A：**E2=UNRESOLVED**。Windows HardWS 的启动前全角色包络与历史峰值窗口尚未闭合；外部 Launcher 责任也需明确。cgroup memory.max 官方允许暂时超限，且 charge 与原 ΣWindows WS 有差异。将后端直接换成 cgroup 无法保留原合同结论。

替代结果 B：明确的 AS/任务数条件定理、边界修订和校准计划已给出。全部受限映像满足 AS≤1 GiB、全部任务≤4、映射覆盖与归属封闭时，payload 驻留和≤4 GiB。固定平台的初始 exec 映像、特殊映射、权限/代理封闭与时钟停止证据仍需认证。该条件证明尚无本机 RESOURCE_GATE_PASS；外部 TCB/pre-exec helper/宿主开销和墙钟响应假设在修订申请中显式列明。

方案搜索在此收敛。新增 v4/guard 版本 0；v3 部分静态候选及主动拒绝入口保持原样。后续只依选定路线的真实平台资格、边界决定和最终冻结锁推进，避免继续同类抽象修补。

## 2. Gate

|Gate|本轮裁决|理由|
|---|---|---|
|E1 方案可行性|CONDITIONAL_PASS|三路线已统一比较，给出具体 C 设计及原合同准确障碍；当前本机部署待核|
|E2 原严格资源证明|UNRESOLVED|原 WS/完整启动/墙钟责任未闭合；替代只有明确前提的静态定理|
|E3 执行架构|STATIC_DESIGN_COMPLETE_CONDITIONAL|角色、父 slice、首入口、全部错误停止与证据边界已列；动态接线尚缺|
|E4 新批次准入|PARTIAL_UNAUTHORIZED|case/资源/停止/结果规格完整；实际 runtime/适配器/全命令摘要待 P 与 L 填齐；batch02 未创建|

RESOURCE_GATE_PASS=未取得；原 RESOURCE_GATE_FAILED 保留；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=空。授权与技术门分别判定，静态通过不授运行资格。

## 3. 实际证据与历史保留

只读管理查询显示：Ubuntu-24.04、Ubuntu-22.04、docker-desktop 全部 Stopped、WSL2；安装组件 WSL2.7.14.0/kernel6.18.33.2-2。该 kernel 是安装元数据，尚无实际发行版运行证据。固定 Docker 本地 Linux engine 管道 info exit1，端点未验证可用。未启动 WSL/Docker，也未核验活动 cgroup/权限/native Python/systemd。

batch01 原 62 文件和 v3 static03 八文件复核一致；原 ZIP 60 项、59 文件 manifest 内容保持，SHA-256 为 `358778fff25aa3f8354874803e2cc26cbaac1d7d70478e9f0923f9c756559594`。原账 27 次、118.7340827 秒，deadline=2026-11-10 05:32:39.337 UTC/13:32:39.337 上海，已关闭/到期。旧剩余不产生新资格。

v3 仅资源三文件历史静态修改、五业务文件 hash 相同；当前无代码修改，也无语法/导入试跑。原 error87、commit/WS 峰值失败及 current 释放/退出时窗原记录均保留。Repair 全文件锁与旧根导航快照另存本轮 BASELINE_LOCK，不重写旧 manifest。

D1-PBFT-SEAL/1.1、D2 条件结论、强 G 覆盖、I1/I2/I3 归档、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED 不变。无新协议反例、一般机器证明或独立外部认证。

## 4. 下一步与授权依据

先审 [BATCH02_AUTHORIZATION_REQUEST](BATCH02_AUTHORIZATION_REQUEST.md)：明确决定是否接受 AS4-PAYLOAD/1 的指标/边界/时间假设，并单独授权仅启动 Ubuntu-24.04 的平台只读 P 阶段。P 后才能填齐真实平台和最终命令锁，提交 batch02 动态许可。若要求原合同全部保持，则记录当前障碍并继续停在 E2 未决分支。

此次保留待批准事项直接来自用户本轮任务§4、§8、§11，涉及新合同、新批次和 stopped 平台的启动；无须重新申请已执行的 batch01 历史范围。当前文件范围内的静态工作已经完成。

交付入口：[README](README.md)、[来源索引](SOURCE_INDEX.json)、[证据索引](EVIDENCE_INDEX.md)、[行政核对](evidence/DELIVERY_CHECK.json)。
