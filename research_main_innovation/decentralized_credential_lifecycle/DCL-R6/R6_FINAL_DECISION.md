# DCL-R6阶段B最终裁决：资源门失败，正式验证未启动

2026-11-10。专项许可已明确取得，八个授权程序已创建，两个源版本和实际运行记录保留。**RESOURCE_GATE_FAILED**。本次阻碍为资源资格，F1/F4状态均为**UNRUN_RESOURCE_GATE**，当前无需重复申请已经批准的同范围许可。

|Gate|实际结果|证据/边界|
|---|---|---|
|R6-B1 资源校准|FAIL|v1 Job初始化返回87；v2正常/计数校准通过，memory峰值断言失败；其余校准停止|
|R6-B2 F1|UNRUN|0次baseline、0次变异/重放，INV1–8均未取得PASS_BOUNDED|
|R6-B3 F4|UNRUN|DP/独立参考/交叉检查/G64均0次，F4-P1–P6未取得PASS_BOUNDED|
|R6-B4 证据完整性|CONDITIONAL_PASS|程序/输入计划/命令/校准/失败/版本与摘要可复查；首轮初始化前峰值缺测、精确树WS峰值null，限制明确保留|

## 1. 资源实际结果

统一计数27次，全部来自校准；从首次控制器启动到v2退出118.7340827秒，未重置30分钟/100万账。v2主Job报告提交峰值145,354,752字节，提交限额4GiB；精确进程树WS峰值未测，采样最大值仅为下界。

失败的memory测试Job设96MiB，报告提交峰值109.83203125MiB；32MiB hard-WS配置下进程峰值为32MiB+4096字节，同时捕获MemoryError。峰值统计可能涉及失败预留/暂态或页面粒度，原因尚未闭合；这些数值不能证明实际整批超过4GiB，也不能支撑当前严格硬界认证。

按用户明确的失败分支，未继续运行独立WS、异常/超时/子树/中断校准，未启动run_batch/F1/F4。所有已记录probe、watchdog和v2控制器PID复查均未发现继续运行。细节与最小修复见[R6_RESOURCE_CALIBRATION_REPORT.md](R6_RESOURCE_CALIBRATION_REPORT.md)。

## 2. 正式安全结论与反例数量

F1实际结论为未运行；F4实际结论为未运行。正式模型反例观察数0，原协议缺陷观察数0，**这不证明缺陷不存在**。实际发现两项资源监督失败记录：首轮初始化错误与后续内存资格断言失败，均不归为D1/D2协议反例。

PASS_BOUNDED性质集合为空。原D1-PBFT-SEAL/1.1纸面CONDITIONAL_PROTOCOL_COMPLETE、D2有限精确模型条件定理保持，无机器依据要求协议升级版本。F1原生/部署/无界精化及F4实现正确性继续待证；LEVEL-3/4/5的协议证据本轮均未新增。

## 3. 工件、许可与下一步

独立目录D:/毕业设计/DCL-R6-isolated-verification/batch01保存八个程序、versions/v1/v2、许可全文/收据、固定批计划、raw/校准/结果JSON及文件锁。[实际机器清单](evidence/stage_B/RUN_RESULTS.json)为研究内投影；源码存在与模型验证完成分列。

最小修复先解决Job峰值计账与hard-WS峰值/舍入上界的指标对应，并给出全进程/子孙的严格合成界；再完整完成剩余资源校准。不能临时改用commit或采样峰值、放宽差值后启动模型。当前batch01已停止，起点/计数保留，后续不可清零扩额。

本轮尚不具备据F1/F4结果推进F2/F3的技术证据；F2/F3及原生验证仍各需独立范围。主机制实现门CLOSED，强G覆盖/I1–I3归档、严格分离0和NOVELTY_UNVERIFIED维持。原生请求、构建、依赖下载/安装、真实账户操作及外发均0，R1–R5冻结工件保持。

阶段A原文及hash已单独封存；下方保留当时的待授权裁决，仅作历史，不代表当前许可状态。

---
# DCL-R6阶段A最终交付与阶段B待授权裁决

2026-11-10，Asia/Shanghai。已完成当前允许的只读预审、工具版本核验、有限规格/协议映射、反例和独立参考合同。阶段B专项许可尚未取得，F1/F4均为UNRUN_PERMISSION；模型/参考/监督程序创建0，实际验证0。本轮提供完整待授权合同，不登记虚构机器证据。

## 1. 四项Gate

|Gate|结果|证据/限定|
|---|---|---|
|R6-A 模型规格|CONDITIONAL_PASS|[F1规格](R6_F1_SPECIFICATION.md)、[F4规格](R6_F4_SPECIFICATION.md)、[对应表](R6_FORMAL_MODEL_MAPPING.md)已明确域/转换/不变量/输入；代码与覆盖对照仍待生成/验证|
|R6-B 机器验证|UNRUN_PERMISSION|[F1结果](R6_F1_RESULTS.md)、[F4结果](R6_F4_RESULTS.md)所有运行值null、执行次数0；未授予PASS_BOUNDED|
|R6-C 证明责任闭合|CONDITIONAL_PASS|旧钥/当前授权/责任/费用条件保持；明确模型自身的非真空性、独立监视/参考和输入完整性责任；真实部署/无界/机器证明仍待证|
|R6-D 后续路线|PASS（决策范围）|先专项许可与资源校准，再F1→F4；F2/F3/原生和工程化继续按独立权限/证据准入|

## 2. 已消除的准备未知项

- 本机真实版本为Corretto Java8u502和Python3.14.0；TLC/Apalache在PATH及已查目录未发现。官方当前TLA+工具需Java11+，现有Java8无法据此认作已就绪TLC环境；未自动下载。
- Windows Job的总提交内存限额与进程树峰值working-set口径分清；轮询内存、堆参数和CPU时间限额不能直接充任本批硬内存/墙钟证明。当前监督器资格未验。
- F1不再用单一current结构充任UniqueChild，也不从同一可能遗漏字段的迁移投影重建RHO真值；独立ghost/多head/Stop历史集合和mutant覆盖已入规格。
- INV3/8按新Release的线性化点限定，保留U2同attempt迟到IO与全部责任。ReadyState归新Q完整对象，ReadyUse/实际业务权限分别校验。K1旧Stop、完整child和可信摘要pin分别建模。
- F4参考按共同动作/观察历史表和具体轨迹直接累计费用，避免复用DP的Post/终态/压缩；世界来源标签与完整Markov状态拆开，防止冗余world键掩盖CE5的错误合并。COST1、空/部分后继、UNKNOWN、非法逐世界策略、真实费用/零步、前缀安全/可见费用及权限状态均有校准。

这些是静态模型审计成果，尚无实测反例或机器通过。R3/R4/R5纸面条件定理未被当前阶段A推翻，协议版本保留1.1。

## 3. 具体待授权范围

[工具/权限文档§5](R6_TOOLCHAIN_AND_PERMISSION.md)给出最小请求：只在`D:/毕业设计/DCL-R6-isolated-verification/batch01`创建八个验证/监督程序及有限输入，沿用已有Python/标准库、无下载；资源校准合格后顺序F1→F4运行baseline、已知变异、独立参考/压缩交叉及证据重放。单批总界仍为100万访问、30分钟、4GiB进程树峰值。资源门无法验收则止于校准；超限INCONCLUSIVE_LIMIT。

写入限于新隔离根及研究目录的结果投影/索引；主系统机制代码、Casdoor构建/原生请求、T1–T4、F2/F3、外部联系/上传均不在此申请内。[执行清单](R6_EXECUTION_MANIFEST.md)列明未来命令和文件，实际工具/程序/输入摘要在生成后绑定；当前许可收据为null。

## 4. 保留的责任与研究定位

F1静态PBFT oracle不证明真实共识实现，F4有限结果不自动证明全原生/无限h/未来效果安全。Casdoor dirty精确对应、缓存handler动态复现、V/Gate/秘密流、NativeCreationCut、历史bearer、实际S2(T)和C_native/C_effect继续待证。原生114请求封顶仍保留为后续计划，当前0新增。

强G覆盖、I1/I2/I3归档、严格分离0和NOVELTY_UNVERIFIED维持。标准状态机/动态规划编码不能直接充任独立原创算法。当前新增证据仍限LEVEL-1/2及行政/工具检查，LEVEL-3/4/5均未新增，REVIEW_READY与无界机器证明未授予。

R5的32个本地工件和原盲审包保持原件；将变化的根目录四文稿保存在revisions/DCL-R5，基线锁见[evidence/R5_BASELINE_LOCK.json](evidence/R5_BASELINE_LOCK.json)。全部历史/原源锁及当前文件核验见[evidence/DELIVERY_CHECK.json](evidence/DELIVERY_CHECK.json)，它们只承担ADMIN_CHECK。

`IMPLEMENTATION_GATE=CLOSED`，`F1=UNRUN_PERMISSION`，`F4=UNRUN_PERMISSION`。当前授权工作已完成，下一步为用户对上述专项范围作独立明确授权。
