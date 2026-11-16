# R5源码—发行物—部署证据增量

2026-11-10。仅做本地文件/元数据静态读取及公开版本源码访问，原生连接、构建、测试和新增HTTP原生请求0。固定提交`528a0213f01caf70b9f41009cbf7b2f67bdd67ec`，本地HEAD/tag v4.25.0相同，现有稀疏工作树status为空；这描述本地当前副本，发行时工作树另列。

## 1. 官方asset环已补齐

新的[官方展开资产列表](https://github.com/casdoor/casdoor/releases/expanded_assets/v4.25.0)公布Windows x86_64 ZIP摘要`24457f4383e33639d851514ddbb49fcaac85fca630f4736901c14d13a1114b32`，与本地ZIP新核哈希一致；checksum资产摘要`bc81c3e8b21708218cfeea2dec8feb078816938b48cbfcc40ae8d4feea28561a`也与本地561字节checksum文件一致。直接下载链接仍读取失败，页面摘要与本地文件各自记录。exe摘要继续为`ddbab07cbe0a913e3bf3b3fbb09b0a1fa3b4abc5127c6b3156930aa77a37ad5c`，其与ZIP内部exe相同的R4证据保留。

证据[evidence/OFFICIAL_ASSET_MATCH.json](evidence/OFFICIAL_ASSET_MATCH.json)把本地工件连接到官方HTTPS发布元数据。该环达到OFFICIAL_PUBLISHED_DIGEST_MATCH；独立签名认证、完整构建日志和精确编译输入仍有各自责任。

## 2. dirty的具体候选来源得到版本源码支持

固定`.goreleaser.yaml`的before hook除`go mod tidy`，还调用`TestGetVersionInfo`。本轮取得同commit的[system_test.go](https://raw.githubusercontent.com/casdoor/casdoor/528a0213f01caf70b9f41009cbf7b2f67bdd67ec/util/system_test.go)第56–78行及[variable.go](https://raw.githubusercontent.com/casdoor/casdoor/528a0213f01caf70b9f41009cbf7b2f67bdd67ec/util/variable.go)第16–22行（本文一基行号）。该hook会读取Git版本信息并写回tracked的`util/variable.go`三个版本变量，提交中初值为Version=dev、CommitId=unknown、CommitOffset=0。配合固定[system.go](https://raw.githubusercontent.com/casdoor/casdoor/528a0213f01caf70b9f41009cbf7b2f67bdd67ec/util/system.go)的Git tag/HEAD计算，若发行环境可见当前tag且hook成功，预期写为v4.25.0、固定commit及offset0。

这给出能使工作树变dirty的具体、可定位构建步骤。它涉及版本自述，已读函数没有修改刷新/撤销handler。实际发行日志、hook后diff、模块整理差异和全部生成物仍未取得；当前证据不能把发行物的全部dirty集合收缩为这三个字段。对它执行测试会写源码，故本轮仅阅读，未运行hook。

|分类|目前掌握的内容|状态|
|---|---|---|
|已确认配方写入|版本hook向util/variable.go写三个变量|SOURCE_SEMANTICS_CONFIRMED|
|预期版本字段差异|在tag可见/成功hook条件下dev/unknown变为发行版本/commit|BUILD_CORRESPONDENCE_CONDITIONAL；属于条件推导|
|实际发行时全部修改|dirty布尔值存在；完整diff未知|UNRESOLVED|
|可能影响安全语义|handler、driver、filter或依赖如有其他修改均可能改变语义|尚无该类实际修改证据；也未排除|
|已读hook与handler的关系|hook直接写版本变量；源码未见其直接改目标handler|限已读配方/函数，未形成整包等价证明|

## 3. 数据库与事务新投影

[STATIC_DEPLOYMENT_VIEW.json](evidence/STATIC_DEPLOYMENT_VIEW.json)只保存配置白名单和日志计数：driverName=sqlite，DSN为`file:…/casdoor-l1.db?cache=shared`，监听127.0.0.1:18081；配置未列busy_timeout、journal_mode、pool limits或read_uncommitted。本轮主DB头读写格式均1，最后写入者3039003；同路径-wal/-shm文件在该次静态检查中均未发现。2,440,097字节历史日志中PRAGMA/sqlite_version字样计数为0，原始日志未复制。

格式字节与旁文件快照支持当次主文件的rollback格式视图；活跃连接设置、曾经WAL、共享缓存的实际生效及引擎版本继续UNVERIFIED。配置文件存在不证明所有历史进程都加载它。缺关键字也不证明设置从未发生。

固定`object/ormer.go:278–301`直接建立xorm.NewEngine并赋给Engine，选段没有显式pool上限或SQLite PRAGMA。`object/token_oauth_util.go:586–599,705–759`先读/验父，后生成、AddToken，再独立DeleteToken；`object/token.go:256–273`使用Engine.Insert及Engine.ID…Delete，并未包装为跨handler事务。已审session-provider锁保护Get/Set等局部会话字段；它未覆盖完整刷新函数。现有源码副本未显示该路径的whole-handler互斥；未下载的代码、部署代理及dirty差异仍待审。

shared cache及单写者约束不排除“读语句完成→另请求期限化并ACK→原handler新Insert”的串行写交错；连接池只有一连接也可在语句间交错。实际锁、错误/重试和完整handler事务可能改变调度，因此NC1/NC2继续SOURCE_FEASIBLE，DEPLOYMENT_BEHAVIOR_UNVERIFIED。当前未连接DB执行PRAGMA。

## 4. 三级对应裁决

|层|结论|尚需证据|
|---|---|---|
|固定源语义|SOURCE_SEMANTICS_CONFIRMED，限已审调用链/配方|完整未审源/外部依赖按各自范围列出|
|构建对应|BUILD_CORRESPONDENCE_CONDITIONAL，官方asset链加强，dirty有具体版本stamp来源|发行前后diff、go.mod/sum/MVS、生成物和构建日志；或隔离复现|
|实际部署行为|DEPLOYMENT_BEHAVIOR_UNVERIFIED，保留历史有限轨迹原范围|同运行工件的driver/PRAGMA/连接池/锁/入口/并发与接受观测|

未来运行只在新隔离实例：同Go driver连接执行`SELECT sqlite_version()`、`PRAGMA journal_mode`、`PRAGMA busy_timeout`、`PRAGMA read_uncommitted`、`PRAGMA locking_mode`及`PRAGMA compile_options`，保存连接标识/DB路径/时刻。busy_timeout等连接局部值须从实际业务连接或受控同连接观测取得；旁开sqlite3客户端的值无法替代。Go连接池Stats/配置、写事务边界与whole-handler锁需对应观测。命令、构建和权限纳入[R5_NATIVE_EXPERIMENT_GATE.md](R5_NATIVE_EXPERIMENT_GATE.md)，当前未执行。
