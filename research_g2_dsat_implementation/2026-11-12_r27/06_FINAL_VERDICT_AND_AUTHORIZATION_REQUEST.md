# R27裁决与一次68项运行申请

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助单文件测试基础设施实现与静态审查；本轮未导入或执行新Runner，未运行--help、测试、SQLite或测试子进程。外部独立复核待取得。

**R27_MINIMAL_RUNNER_IMPLEMENTED；R27_STATIC_PREFLIGHT_PASSED；R27_REGRESSION_COMMAND_READY。** 工程构建保持、单文件入口已落地，34项静态检查通过；当前68项仍NOT_RUN，ACTUAL_SUITE_RUNS=0。

| 状态 | 值 |
|---|---|
| R27_68_TEST_MANIFEST_VERIFIED | TRUE |
| R27_A17_IMPORT_ORDER_STATIC_VERIFIED / R27_D24_PROJECTION_STATIC_VERIFIED | TRUE |
| R27_OUTPUT_ISOLATION_STATIC_VERIFIED / R27_SOURCE_LOCK_VERIFIED | TRUE |
| R27_STATIC_PREFLIGHT_PASSED / R27_STATIC_PREFLIGHT_BLOCKED | TRUE / FALSE |
| R27_RUN_AUTHORIZATION_PENDING | TRUE |
| R27_SUITE_RUNS_ZERO / R27_68_TESTS_NOT_RUN | TRUE |
| D1B1_PARTIAL_IMPLEMENTATION | TRUE |
| D1B1_OFFLINE_CONTRACT_COMPLETE | FALSE |
| D1B2/P1a/P1b/P2/S3-B2/S5 | 继续未授权 |

| 问题 | 回答 |
|---|---|
| Q1 只新增一个Runner？ | 是，唯一工程新增文件为批准路径，现有工程文件修改0。 |
| Q2 原42工程源？ | 全部原字节保持，摘要与R25/R26一致。 |
| Q3 原测试/fixture？ | 3份原测试、10份fixture及原断言保持，逐文件hash核对。 |
| Q4 68身份？ | 完整20A+24H+24D，无重复遗漏，原expected和组内顺序保持。 |
| Q5 装配顺序？ | A1→H1→D1A，D1A模块延迟加载。 |
| Q6 A17如何保证？ | 预检不importcrypto，阶段前屏障和import/exec审计关闭先行crypto/生产模块；原A17不改，无缓存清除或stub。 |
| Q7 D24只两个JSON？ | 是，R26保护清单提供原路径/hash，静态代入验证一致；生成写入和每次读取均检查digest，额外路径拒绝。 |
| Q8 生产白名单？ | 原reader/白名单文件保持；仅D24上下文的测试provider临时映射并恢复。 |
| Q9 输出新根？ | 接受执行后的所有日志、receipt、结果、索引、费用均限R26独立验证根13个固定路径。 |
| Q10 历史写回？ | 未保留历史输出fallback；历史4个T33链接只读核验例外，不具备写权限。 |
| Q11 不改测试可执行？ | 接口与静态控制流条件已建立，具备申请实际执行条件；尚未证明68项动态通过。 |
| Q12 真实命令？ | 已生成存在的Runner及无占位argv，见命令锁；运行仍未授权。 |
| Q13 本轮0次？ | 是，Runner未导入/执行，--help未运行，SQL/key/子进程等运行资源0。 |
| Q14 下一轮可批准？ | 具备按本次最终源码/命令/资源锁独立批准一次68项的静态条件；本轮不执行。 |

## 下一阶段唯一申请

申请对R27_REGRESSION_COMMAND_LOCK固定的入口、当前构建、68身份和资源，独立批准一次完整68项回归。直接调用上限1，自动重跑0，执行原A1/H1/D1A共68项，排除全部54项及整仓发现。运行时源/fixture/命令/预算失配则停止；已启动后失败或部分完成也消耗唯一额度，现场源码修改/第二次调用均不包含在申请中。

新Runner SHA-256：`a9cb35bcce7d1439f45b2593a16c7fb2884117dd63d515eac7cf40e5d75eda70`。原工程摘要：`621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9`。准确命令、工作目录、receipt位置、13路径及资源在两份锁中，当前只提供审查材料和false批准模板，未准备动态目录或实际receipt。

R25_SPECIAL_54=54_PASS继续作为实际基准。未来68项真实通过并核对相同相关工程源/依赖、实际加载来源、原断言/fixture、A17及D24装配语义、预算与历史后，才审查122项联合证据及D1B1合同关闭。新增driver本身不等同于生产工程源变化，也不自动取得联合验收。

本轮新增代码实现和静态复核均为知情模型辅助过程；运行与外部独立核验仍待取得。没有自动开展68/54测试、真实部署、RPC、P1/P2、S3-B2/S5或依赖安装。

本次用户授权第一、九、十一节明确限定静态工作并要求后续运行独立批准，因此本轮止于可审查入口和完整执行申请。
