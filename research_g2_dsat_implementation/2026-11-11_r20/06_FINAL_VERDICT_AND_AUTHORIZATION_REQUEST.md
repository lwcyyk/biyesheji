# 最终裁决与分级授权申请

**D1-B0合同审定完成，形成可审查的D1-B1最小代码与离线测试申请。** 当前工程修改0、项目测试0、部署0。R19的68 PASS继承为历史离线事实，真实服务状态仍为 INSTANCE_RUNNING=false。

## 状态及实际含义

| 状态 | 当前裁决 |
|---|---|
| D1A_IMPLEMENTED / D1A_SYNTHETIC_TESTS_PASSED | 继承R19实际证据 |
| D1B_IDENTITY_CONTRACT_READY | 单机可信SID、实际handle/epoch/实例元组的规格就绪；实际SID与平台验证待取得 |
| D1B_INITIALIZATION_BUDGET_READY | 正常22次SQL、全路径23次wrapper上限等申请已具体化；实际I/O待测 |
| D1B_FAILURE_CLEANUP_SPEC_READY | 全生命周期及28故障责任就绪；测试全NOT_RUN |
| D1B_COMMAND_SPEC_READY | 六操作语义/参数Schema就绪；可执行入口缺失，argv为空 |
| D1B1_READY_FOR_IMPLEMENTATION_REVIEW | 九目标文件锁、新52＋复用68测试、输出和副作用范围明确 |
| D1B1_AUTHORIZATION_PENDING | 本轮无代码/测试执行授权 |
| D1B2_NOT_AUTHORIZED | 后续须依据实际代码、SID、预算和准确argv单独批准 |
| P1A_NOT_AUTHORIZED / P1B_NOT_AUTHORIZED / P2_NOT_AUTHORIZED | 保持 |
| S3B2_NOT_AUTHORIZED / S5_NOT_AUTHORIZED | 保持 |
| SOURCE_OR_REFINEMENT_GAP / TYPED_O_NOT_IMPLEMENTED / O_REVISION_NOT_IMPLEMENTED | 保持；部署接纳无法替代typed O/currentness/global COMPLETE证据 |
| ANALYSIS_ONLY | 本轮实际执行范围 |

READY后缀均限定为合同/预算/审查材料就绪。平台支持、接口实现与部署通过分别核验。

## Q1–Q15

| 问题 | 回答 |
|---|---|
| Q1 距真实启动缺哪些函数？ | LiveDeploymentIssuer/LiveAuthorityContext、实际Windows host provider、OwnedResources、strict seed/fileDB准备、bounded listener loop、prepare/initialize/start/status/stop/recover及父子handle交接。完整拟议符号见文件锁。 |
| Q2 live issuer/provider如何建立？ | 获批bootstrap在生产导入前核对来源/配置/OS与继承资源；provider只读self/owned-child和固定文件handle；进程内opaque部署能力只绑定Dormant，不授P2。 |
| Q3 OS/epoch/Store/会话如何绑定？ | SID＋PID/creation＋image＋root/DB物理ID＋source/config＋新epoch形成运行元组，同一Store/connection/lock引用贯穿。未来P2 envelope再绑定该元组与scope，当前P2固定拒绝。 |
| Q4 单一活动服务？ | 新Authority专用独占lock句柄，从DB打开前持有，经显式句柄交接保持，关闭资源后最后释放；原SingleActive只覆盖Controller。可信主体与同机NTFS前提明确。 |
| Q5 重建/别名/重启重开读？ | 同生命周期只准一Store/连接，R16槽/registry共用；重启和失败后新epoch要求新批准，旧授权无自动恢复。持久防回滚/敌对writer仍有缺口。 |
| Q6 SQLite连接/事务/文件多少？ | 初始化1连接＋Store1连接，最大同时1；准备器显式事务1，正常15＋7＝22次SQL，失败rollback最多1。DB1、WAL/SHM/journal允许3路径；内部VFS/锁次数待测。 |
| Q7 key/TLS如何准备恢复？ | 新state key32B生成/写入/readback各1，加密1、解密0；新TLS RSA2048/cert一次。私有DACL，正常停止保留。recover不读key或DB，内容配对证明待单独批准。 |
| Q8 预检哪些路径/权限/source？ | 批准根/父目录和派生路径、最终path/file-ID/reparse/hardlink、SID/DACL、独占root/lock、Python/依赖来源、完整artifact与有效config digest；实际值在B1/B2取得。 |
| Q9 Store至listener异常谁清理？ | strict ctor先登记connection并在返回前失败时关闭；外层OwnedResources包住注册/Handler/TLS/bind/Ready，先退役context，逐对象关闭，锁最后释放。 |
| Q10 怎样只清理本实例？ | 批准路径＋创建receipt＋实际file-ID＋当前epoch/closed对象条件同时满足。持久自动删除0、临时删除至多3、未知归属保留，foreign kill0。 |
| Q11 崩溃如何识别恢复？ | seed receipt、pending阶段、DB/根物理ID和启动claim共同分类；marker单独无法证明完成。recover仅诊断，无修复/解密/启动；不确定即RECOVERY_REQUIRED。 |
| Q12 入口最小差异？ | 修改services/storage/现launcher三文件，新增live/lifecycle/Windows三模块、新test/runner及fixture树。六语义当前未实现，actual_argv为空。 |
| Q13 B1用例和权限？ | 新52＋原24＋原44＝计划120，分3域；专用输出、公开向量file/memorySQLite、限定8次stub子进程/Win32临时对象。网络/服务/部署根/P1/P2额0。完整限额见TEST_PLAN。 |
| Q14 B2预算和授权？ | 新根/可选新父目录、最多96根内路径，2SQLite连接、22正常SQL、新state/TLS材料、唯一child/单回环listener、至多2客户端和一次拒绝请求、graceful stop。B1后填实际SID/source/argv并独立批准。 |
| Q15 唯一最小下一步？ | 批准D1-B1九目标真实启动代码的离线实现与故障验证，真实部署继续关闭。 |

## 可直接批准的D1-B1范围

申请：按 `D1B_SOURCE_AND_FILE_LOCK.json` 修改3个既有文件、新增5个Python文件及1个fixture树；完成 `D1B_TEST_PLAN.json` 的新52项与原68项分域兼容测试。只写获批工程路径和专用离线输出树，允许受控公开向量文件SQLite、自有临时Win32/stub子进程，以及每次new52至多2套临时测试state/TLS材料与SSLContext加载，保持实际socket、TLS握手和真实Authority服务为0。每suite最多一次范围内修复重跑，失败记录全部保留。

这是一项成熟工程接线申请。原算法创新裁决和严格分离门保持，B1通过也只增加实现与测试证据。

建议批准用语：

> 批准D1-B1九目标代码离线实现及R20冻结的52项新增、68项兼容测试，执行范围和资源上限按D1B_SOURCE_AND_FILE_LOCK.json、D1B_TEST_PLAN.json与D1B_AUTHORIZATION_REQUEST.json。真实部署、P1/P2、S3-B2和S5保持关闭。

结构化申请 `D1B_AUTHORIZATION_REQUEST.json` 当前 `approved=false`。此次材料没有把建议用语登记为已收到授权。

## B2后续条件与唯一动作

B2须等待B1实际实现、故障/兼容结果、真实parser支持、final source snapshot、指定SID/ACL及平台handle核验，随后形成精确初始化/启动/停止argv和副作用申请。真实start调用数仍为0，现有命令锁均不可执行。

**唯一下一动作：批准并执行上述D1-B1限定工程任务。** 成功将补齐真实部署所需的受控代码，并产生决定B2准入的实际证据；身份、资源或清理测试失败时保留具体缺口，继续离线范围，B2保持关闭。

本次独立批准需求直接来自用户R20第十四节：“D1-B1需要独立代码与测试授权。” 本轮第一节将执行范围限定为准入审查，因此当前交付到授权申请为止。
