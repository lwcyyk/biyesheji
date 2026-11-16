# R30裁决与唯一最小审批任务

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助真实离线调用及只读证据审查；工程源/Runner/测试/fixture修改0，自动重跑与额外测试0；独立外部核验待取得。

**原68项断言全部实际通过，完整回归入口退出1。D1-B1离线合同暂不关闭。** 唯一执行额度已用，未修改代码或补跑。

| 状态 | 值/范围 |
|---|---|
| R30_STATIC_ADMISSION_PASSED / R30_SINGLE_SUITE_EXECUTED | TRUE |
| R30_68_TEST_ASSERTIONS_PASSED | TRUE，20/24/24，原日志与EARLY计数互证 |
| R30_68_REGRESSION_PASSED | FALSE，含完整来源/资源收尾的合同口径 |
| R30_PYC_IMPORT_FALLBACK_VERIFIED | FALSE，功能恢复已见但逐probe记录缺件 |
| R30_A17_IMPORT_ORDER_VERIFIED / R30_D24_PROJECTION_VERIFIED | TRUE，本次实际正例范围 |
| R30_RESOURCE_BUDGET_SATISFIED | FALSE，完整actual meter缺件；未观察到超额 |
| R30_HISTORY_INTEGRITY_VERIFIED | TRUE |
| R30_122_JOINT_EVIDENCE_ACCEPTED / D1B1_OFFLINE_CONTRACT_COMPLETE | FALSE |
| D1B1_PARTIAL_IMPLEMENTATION / SOURCE_OR_REFINEMENT_GAP | TRUE，gap为harness来源分类/持久化 |
| D1B2_AUTHORIZATION_PENDING / REAL_DEPLOYMENT_NOT_RUN | TRUE |
| P1a/P1b/P2/S3-B2/S5 | 保持未授权 |

| 问题 | 回答 |
|---|---|
| Q1 执行前提？ | 全部冻结核验匹配，17组事前检查通过。动态暴露后置来源模型/收尾持久化缺口。 |
| Q2 只一次？ | 是，唯一固定Runner调用，native退出1，额度剩余0，自动重跑0。 |
| Q3 argv？ | 实际包装与RUN_START均与R29逐项相同。 |
| Q4 缓存回退？ | 功能性导入恢复且所有原模块/CLI用例通过；逐探测path/mode/SHA记录未落盘，完整PYC动态审计未验收。 |
| Q5 未批准读取拒绝？ | 冻结guard保持，未临时放宽；直接拒绝meter缺件，未另注入负例，因此保留动态覆盖限制。 |
| Q6 A17？ | 实际原A17执行ok，R30_A17_IMPORT_ORDER_VERIFIED=true，原断言/缓存策略保持。 |
| Q7 D24？ | 实际ok、双目标SHA与原文匹配、readerhash保持；恢复由达到phase_finished的with控制流支持，negative/failure分支静态范围。 |
| Q8 三组结果？ | A1 20PASS、H1 24PASS、D1A24PASS。 |
| Q9 68统计？ | 断言PASS68，其余FAIL/ERROR/SKIP/BLOCKED/NOT_RUN全0；框架后置错误单列。 |
| Q10 全部资源预算？ | 可见时间/输出/文件等界内；完整SQL/连接/线程/RAM meter未持久化，不能给完整budget验收。 |
| Q11 历史？ | 2146份保护文件前后匹配，代码/Runner/测试/fixture修改0，R25/R28/R29原字节保持。 |
| Q12 联合条件？ | 断言层54+68均通过；依赖来源、逐probe和资源/最终receipt审计缺失，联合accepted=false。 |
| Q13 离线合同完成？ | 当前D1B1_PARTIAL_IMPLEMENTATION。缺post-D1A来源分类的确切身份与完整来源/计量/结果文件。 |
| Q14 唯一下一项？ | 独立批准仅该Runner的依赖来源分类和失败证据持久化修复及新命名空间静态冻结，保持原工程/测试；后续运行另批。 |

## 最小已定位缺陷

原68完成后，origins_snapshot要求有__file__的所有所选依赖同时具备相同spec.origin。该谓词失败；原始日志没有module name/file/origin值，无法确定具体模块。来源值在全轮验证后才append，异常使partial snapshot遗失；收尾又在保存meter/RESULTS前重做来源核验，可再次阻断最终输出。现有EARLY保持首条错误，后续实值未补造。

原生扩展派生子模块可能具有不同元数据形态，只能作为待核线索。静态源码看到cryptography从_rust导出_openssl/openssl，当前没有证据将任何特定模块确认为本轮触发者，不能整体放行missing-origin或吞异常。

## 下一阶段唯一申请

详见sources/MINIMAL_RUNNER_FIX_REQUEST.json，approved=false。限定现有Runner一个文件：在判断前捕获完整来源字段与expected pins；仅对可证明绑定到已锁父扩展对象/二进制的具体派生模块采用明确规则；其他异常仍失败。无法证明具体分类时保留来源阻塞。

同时修复失败持久化顺序：已有meter/cache/projection/partial-origin/68rows即使审查失败也保留，RESULTS体现真实非零和未完成义务，不在输出阶段用同一校验异常再次截断所有证据。继续使用有界13路径/2MiB；新增资源另批。

旧R29run/receipt/slot全部保留。建议新记录根2026-11-12_r31、新验证根其下verification_runs、run ID r31_regression68_001；当前仅提案，未创建。该阶段只实现和静态核验，动态测试0；以后任何新68调用须独立授权。

不修改42工程源、3原测试、10fixture、生产reader、原54证据或历史SOURCE_LOCK。最终实际运行及所有联合条件满足后，才审查D1B1离线关闭。当前不启动D1-B2、P1/P2或其他真实阶段。
