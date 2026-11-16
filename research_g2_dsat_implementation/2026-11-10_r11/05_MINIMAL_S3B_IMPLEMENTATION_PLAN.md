# 最小S3-B1方案与后续接线

## 下一轮最小范围

先开发一个Authority可信域内的读取/净化适配器，输出`dsat-authority-read/1`、mode=`AUTHORITY_READONLY_STAGING`。开发和离线验收可独立推进；真实连接调用、解密导出、RPC及Provider读取另设许可。

| 拟新增路径，工程根D:/毕业设计/auth-lifecycle | 责任 |
|---|---|
| src/auth_lifecycle/online_state/dsat_authority_read.py | 纯字段净化/原请求校验；对已初始化reader的一次受锁读取适配；显式scope/来源/缺口 |
| tests/test_dsat_authority_read.py | reader/lock spy及手写状态；权限、隐私、版本、来源、风险与错误行为 |
| tests/fixtures/dsat_authority_read/ | 新合成状态与secret canary，原夹具不动 |
| scripts/run_dsat_authority_read_tests.py | 只运行新测试，记录输入/代码摘要、结果和副作用计数 |

四个目标当前均不存在；本轮未创建这些工程文件。storage/services/migration/Provider、S1/S2/S3-A及其历史测试全部保持。未来输出根拟为`research_g2_dsat_implementation/2026-11-10_r12_b1`，当前未创建。

## 输入输出与读取协议

可信宿主提供已初始化reader、受信认证上下文及允许scope。普通请求只能提出scope，权限由宿主既有授权事实核对；dict中的actor/read_ok/source_confirmed不形成资格。本最小版本没有公开HTTP路由，也不新建用户或grant。

先检查scope/权限/界，再在既有authority.lock下调用read_state一次。该tuple复制后用于全部字段；不调用AuthorityStore构造器、旧call、recover RPC、reconciliation_context、Provider或NativeHTTP。跨进程并发保证只采用单行SELECT的快照点语义，后续变化继续以a/新source检查处理。

输出包含a、可信locator/provenance/时钟域、净化后的grant/request、源引用、处置/window摘要、legacy义务和独立保守视图。缺少稳定instance/o时分别为null与明确gap，不能填0或目录hash伪装已实现。result/disposal引用由授权元数据构造，原生Token和材料私有内容留在源域。

原请求在源内按原digest校验，handle不进入公开导出或错误日志。S1-v1需要原正文，故本阶段固定报告兼容缺口，math_ready=false。原始请求内有handle可在未来获准的私有计算域使用；真实信任入口/新版净化契约需后继审定。本最小动作不承诺完整S1/S2输入或当前Native资格。

## 只读的费用和副作用

read_state经过execute会消耗一次SQL操作额度、日志fsync并读key。未来live调用须显式允许这些既有遥测；world/a/authority_events保持。operation_limit有限时，应在同一锁内保留至少“一次读取+旧调用预检6次操作”的headroom；不足先拒绝，自动重试0。该门只限制适配器自己的读取，实际其他连接/进程及后续业务活性另需部署分析。

第一轮离线测试用reader/lock doubles，不打开SQLite、不加载key、不实例化服务。真实已初始化Authority读调用须另行批准其源scope与秘密域访问，开发授权不会自动包含该动作。

## 未来验收

`S3B_TEST_PLAN.json`共36项均NOT_RUN：33项为B1离线/兼容缺口验收，3项属后续B2真实proof/迁移/旧writer测试。覆盖用户列出的28项，并增加handle摘要、reserved队列、读取额度、synthetic gate、跨scope处置、缺instance、重复provider历史和资源界。

默认输出≤1MiB、scope记录≤4096、每调用读取1次、测试120秒；超过上限安全拒绝，保留incomplete状态。测试需要证明：权限拒绝前不读源；全部私密canary不外泄；每字段来自同一版本；QUEUED/UNKNOWN/迟到/第三源风险保留；缺字段不等于空风险；旧格式与新资格保持区分。

## B2/B3顺序

B2先完成真实权限上下文、保守typed O初始化及全部writer hooks，再实施production codec、独立S3事务入口、持久proposal/object表、进程/schema fence和受控迁移/回归。该阶段需要明确旧文件修改列表及新的执行授权。

B3再完成全部合法证据、托管/写入者、容量/出生代次、持续失活、前沿/接受路径与部署对应。真正原生资格、真实凭据撤销和S5分别管理，数学/条件档案继续保留本地/原生层次。

## 完整费用口径

设S为整加密状态字节，G/R/D/W分别为grant/request/disposal/window数。一次读取解密/JSON需O(S)及外部key访问；净化、origin join和请求重算摘要需扫描相关记录与原正文总字节，规范排序额外O(k log k)，空间包括解密状态S和有界输出。权限不足时仍应先拒绝而非先解密再过滤。

证据适配需扫描/去重全部合法历史，按生产者、代次和tuple连接；E最坏可达|U||I|，既有1MiB/256尝试/256见证/16384边等界须单独检查。后续S1、S2、独立检查、锁等待/CAS、全状态加密、对象/ledger、冲突重准备、备份/迁移、客户端版本与恢复均计费。B1/B2/B3所有实际时延、网络和存储费用当前NOT_MEASURED；R10合成数字不移作生产性能。
