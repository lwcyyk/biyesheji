# R27范围与R26授权绑定

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助单文件测试基础设施实现与静态审查；本轮未导入或执行新Runner，未运行--help、测试、SQLite或测试子进程。外部独立复核待取得。

## 实际变更

仅在批准路径新增一个工程Python文件：

`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`

原路径不存在，已在实现前以R27_RUNNER_FILE_LOCK记录。当前文件695行，SHA-256：`a9cb35bcce7d1439f45b2593a16c7fb2884117dd63d515eac7cf40e5d75eda70`。全部修订只落在这一个新文件中；原42份工程源码、3份历史测试、10份fixture和旧Runner修改0。新文件身份与原工程构建身份分别登记。

本轮直接依据R26_MINIMAL_RUNNER_IMPLEMENTATION_REQUEST及本次研究者明确批准实施，未新增候选算法或安全机制。R26历史材料保持其原STATIC_PREFLIGHT_BLOCKED状态；当前R27的新准入记录承接该阻塞。

## 继承证据

完整读取R26全部主稿/结构化材料及R25相关原文，重新核验R26的2045份保护清单、当前42工程文件、24运行时指纹、回归补充源码、原3测试及10fixture。实际R25 54PASS、F24 flush/close真实EINVAL22及P1/P2跨进程见证保持，旧68项历史证据仍按其原构建范围使用。

构建摘要R25=R26=当前：`621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9`。该42文件摘要不包含新测试装配器，完整内容见R27_BUILD_AND_RUNNER_LOCK。解释器路径、关键binary/metadata指纹保持，未安装依赖或建立新venv。

## 读写范围

Runner未来只读R27锁、R26计划/manifest/历史清单、原测试/fixture、R25相关证据、固定Python库及两个D24已锁原文。全部接受执行后的输出固定在`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r26\verification_runs`；当前该验证根、实际运行receipt和新run均未创建。

本轮新增的Markdown/JSON只在当前R27记录根，工程可执行代码仅上述一份Python。预算为静态冻结，ACTUAL_SUITE_RUNS=0。R25额度0继续保持，任何未来68运行都需独立批准。

## 历史T33只读例外

静态检查发现4份历史T33文件是原测试故意保留的硬链接，原内容和链接数均保持。新Runner仅允许这些精确路径在历史核验循环中以historical_read读取，并继续核对原SHA；不开放写入、D24投影、工程源或输出路径例外。

四个路径、hash和静态发现记录见sources/STATIC_FINDING_HISTORICAL_LINKS.json。它修复了新入口对合法历史证据的过度限制，未改变任何历史文件。其余输入、新结果及D24继续严格拒绝硬链接；重解析点一律拒绝。
