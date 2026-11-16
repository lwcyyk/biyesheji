# 静态预检与历史回归门

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助源码修订、纸面分支复核与静态取证；动态验证与外部独立复核待取得。

## 本轮静态结果

| 条件 | 状态 |
|---|---|
| OUTPUT_ISOLATION_STATIC_PASSED | TRUE |
| PIPE_EXCEPTION_POLICY_STATIC_PASSED | TRUE |
| HISTORY_INTEGRITY_PASSED | TRUE |
| TEST_RUN_ADMISSION_READY | TRUE，含义为可以申请独立动态批准 |
| AUTHORIZED_FOR_DYNAMIC_RUN | FALSE |
| ACTUAL_RUNS | 0 |
| REMAINING_RUN_BUDGET | 1 |
| 自动重跑 | 0 |

`R24_STATIC_PREFLIGHT.json`含23项具体静态检查，覆盖AST、差异范围、源锁、显式根、独占结果/单次槽位、子进程参数/批准绑定、错误码/主异常、完整收集、54身份、协议保持、历史及资源。PowerShell冻结命令只作AST语法解析，没有执行。

原54 ID、预期、测试文件和五份fixture均保持原字节。原消费协议、grant/journal模式、AuthorityStore、H2会话总量门、Dormant及P2路径保持。本次新增的是测试作业准入和cleanup证据，不能获得真实读取资格。

## 资源与本轮实际

未来单次new54沿用：worker8/并发2、单个观察10秒/累计60秒、文件SQLite104/每case2、state测试key2、TLS材料2、SSLContext2、目录64、路径512、输出64MiB、线程峰值4/创建16。源码保留总观察timer300秒与timeout后5秒wait；OS不可中断I/O仍无法转成硬终止时间保证。

新增每worker一份cleanup JSON，至多8份，在原文件/逻辑字节预算内；没有额外测试、连接、key、TLS、子进程或线程额度。原申请未单列的聚合SQL、RAM字节、聚合锁预算保持未单列；原scope的各具体资源上限继续生效，未借用B2生产预算。

本轮测试SQL、SQLite、worker、key/TLS、锁、网络、P1/P2及真实部署均0；未生成verification_runs，也未安装依赖。临时原始源码快照、diff和报告属于本次明确批准的静态取证材料。

## 68项历史证据的精确资格

R22的24+44实际通过记录绑定R22最终源码，其中runner SHA为`566436a1e4d45e4dfd310e2994f336834dc8c77ffbe65808b0452e94952a367d`，Windows SHA为`0df81f8aba187ac3e4623ee436295e05e15179fc822e8a2d2416348810c91123`。它们与本轮两份新源码不同。

因此现在登记 **CROSS_VERSION_REGRESSION_EVIDENCE**。原历史结果仍有效，当前没有同版本68项运行记录。

| 变化 | 可能受影响性质 | 当前证据 |
|---|---|---|
| runner输出/批准/源锁/命令audit | 路径投影、测试宿主接纳、旧回归入口及输出纪律 | 静态路由证明；原68运行属于旧版 |
| Windows scope根和新测试receipt | 生命周期授权入口、原T52 bootstrap关联 | 业务协议源字节保持；当前运行待取得 |
| 原pipe对象、错误分类和清理留证 | 子进程结束、错误传播、资源计量、诊断文件 | 纸面分支核查；实际清理路径待验证 |
| 额外worker结果完整性门 | 对非预期退出/不完整输出的拒绝 | AST条件检查；当前运行待取得 |

未来一次54项若成功，可支持当前版本54项、F23/F26/T45跨进程保持，以及F24所实际覆盖的清理性质。没有发生的异常分支继续按静态依据陈述；无法据此宣称每一种errno已动态覆盖。

完整D1-B1合同仍需要同版本68项兼容性证据，或经明确审定的完整影响排除证明。本轮未建立足以免除该责任的证明，故默认保留同版本回归需求，执行另外授权。当前R24入口只允许new54；后续68项应另有批准的隔离入口/命令，不在本轮实现或运行。

即使未来54项全部PASS，本轮文件也不预先登记`122/122 SAME_BUILD_PASSED`或`D1B1_OFFLINE_CONTRACT_COMPLETE`。
