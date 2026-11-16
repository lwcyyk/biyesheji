# DCL-R5最终裁决

2026-11-10，Asia/Shanghai。完成本轮允许的静态研究、纸面审查、验证准入和独立审查输入准备；原工程、历史实验及R1–R4工件保持冻结。R4现有182文件审查包复用，仅对将变化的根目录四份导航/历史文件保存R4副本，锁见[evidence/R4_BASELINE_LOCK.json](evidence/R4_BASELINE_LOCK.json)。

## 1. R5四项Gate

|Gate|结果|依据与边界|
|---|---|---|
|R5-A 关键证明责任|CONDITIONAL_PASS|[主张矩阵](R5_CLAIM_VERIFICATION_MATRIX.md)覆盖P1–P5/D2；展开旧钥/锚/后继签名条件、未登记发送及当前许可的时点边界；外审/机器验证0|
|R5-B 部署证据|PARTIAL|[来源增量](R5_SOURCE_BINARY_DELTA.md)与[缺口表](R5_DEPLOYMENT_GAP_ANALYSIS.md)：官方资产摘要匹配、版本stamp写入证据、SQLite配置/静态视图；实际dirty全集与部署行为未闭合|
|R5-C 验证准入材料|CONDITIONAL_PASS|[F1–F4合同](R5_FORMAL_VERIFICATION_GATE.md)、[T1–T4合同](R5_NATIVE_EXPERIMENT_GATE.md)：域、命令、端点、资源、变异、失败/残留齐列；工具/代码/fixture/授权收据待绑定，执行未授权|
|R5-D 论文与路线|PASS|[路线/贡献裁决](R5_RESEARCH_AND_THESIS_DECISION.md)：A验证优先，B架构工程化保留，C独立创新未启动；强G和真实贡献边界明确|

## 2. P1–P5与D2是否改变

P1在1.1的签名生命周期、稳定共识恢复及可信引导前提内保持条件结论。K1具体展示：退休后旧quorum钥可伪造另一Stop；完整child激活还需治理、新committee签名和引导条件。已pin具体正确child摘要的验证者与只持旧锚者具有不同范围。Stop没有自动到期，长期接纳需要相应长期失陷界或额外已证明机制。

P2登记责任保持继续成立；未登记旁路原生行为的两世界界保留。P3的ReadyState完整对象与ReadyUse/实际执行资格分开，秘密流与Gate/V当前代次/boot仍需部署验收。U2表明先Release、后Revoke、再收到许可并发送的历史仍可能存在；C_local不能直接扩张为撤销后零原生使用。P4安全、最终活性和有界响应依赖分别列出。P5继续保留NC1/NC2、缓存handler、异步审计及C_local/native/effect范围。

D2有限精确模型的累计费用/非空Post/共同策略条件可靠性与完备性保持，完整Markov条件压缩和动态失效范围保持。本轮没有发现满足1.1全部明示模型假设却推翻其唯一历史的反例；新增见证集中在更强旧钥目标、使用时点和部署支持前提。

D1-PBFT-SEAL/1.1继续CONDITIONAL_PROTOCOL_COMPLETE，限纸面范围；当前原生/跨域实际部署和无界连续保证继续待证。

## 3. 源码—二进制新证据

官方expanded-assets公布的Windows ZIP及checksum文件摘要均与本地一致，发行工件字节对应环已补齐。固定配方的TestGetVersionInfo会写tracked util/variable.go，定位出dirty的一项具体候选来源；真实发行前后diff/MVS/生成物和完整日志仍缺，不能断言dirty只有版本字段。

配置确认sqlite及cache=shared，静态主DB头仍指最后写入者3.39.3、读写格式1，当次同路径WAL/SHM文件未发现。历史日志未提供运行PRAGMA/版本值。SOURCE_SEMANTICS_CONFIRMED、BUILD_CORRESPONDENCE_CONDITIONAL、DEPLOYMENT_BEHAVIOR_UNVERIFIED三级对应维持。NC1/NC2继续SOURCE_FEASIBLE，新增实测0。

## 4. S2(T)细化

[S2审查](R5_S2_CONTINUITY_AUDIT.md)保留600秒/1800秒、10逻辑读、20尝试、24预算。额外明确两Gate在T前分别当前ReadyUse/接纳、并发崩溃可有多条UNKNOWN、reserved与charged共同占额度、共享P/网络/DB的服务和故障包络。S2-COLD证明仅有第二台设备仍可能有资格空窗；B-ROT、CUT-ALL/CUT-SHARED保留。满足这些条件的有限配置仍条件可行；共主Q/冷备用可按S1接受暂停。真实独立Q_B/S2部署0。

## 5. 准入与授权

F1–F4已有逐层有限域、初态/转换/性质/公平与变异计划，拟议单批总访问状态10^6、总墙钟30分钟、进程树峰值4GiB；超限INCONCLUSIVE，监督器需能够强制计数/资源界。未来代码、工具版本/摘要和执行授权另绑定。

T1–T4逐端点setup依赖24次、method8次、8份材料的measurement最多20、cleanup40，完整路径最多92次；保留原阶段30/16/28/40共114封顶。T3三材料完整清理需要12次，修订R4每轨迹10次的均分；全局40不变。未用22次容量不许可额外探针/重跑。未来新实例固定拟议端口28451、合成账户/新秘密、独立路径、barrier和scorer/方法观察隔离，冻结18081明确排除。

仍需明确授权：模型/监督器/harness/hook代码、工具/依赖取得、构建/启动、合成账户与原生114范围、同连接SQL观测/备份及外部审稿发送。当前只准备材料，不提出立即执行请求。盲审输入已单独形成[第一阶段包](blind_review/DCL-R5_BLIND_INPUT.zip)，证明/答案在第二阶段提供；外部复核完成0。

## 6. 覆盖、来源与下一步

强G覆盖无变化，I1/I2/I3保持归档，严格分离0、NOVELTY_UNVERIFIED。SC-A2A/Dyno正文缺口SOURCE_UNRESOLVED；本轮没有重复无新入口的宽泛检索。

优先路线A：先独立纸面异议/模型审阅与F1/F4小域验证，再F2/F3；原生构建与隔离条件验收后，按锁定顺序做T1/T4控制及T2/T3并发。架构工程化需部署证据后再准入；另开创新研究当前缺严格输入/必要下界。论文成果定位为条件架构、原生语义与来源审计、可证伪安全分析及验证准入设计。

`IMPLEMENTATION_GATE=CLOSED`；新增机制代码0、机器验证程序0、构建0、native请求0、新实验0、机器证明0、外部审查完成0、外部联系/上传0。行政读取/哈希/JSON/链接/打包与协议验证分列，最终范围见[evidence/DELIVERY_CHECK.json](evidence/DELIVERY_CHECK.json)。
