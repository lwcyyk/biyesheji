# 历史完整性与新证据边界

执行与审查日期：2026-11-12（Asia/Shanghai）。证据类型：本对话内知情模型辅助实际离线运行、源码/日志核对；外部独立核验待取得。

**R25_HISTORY_INTEGRITY_VERIFIED=true。** 前后对照见`sources/PREEXECUTION_AND_HISTORY.json`与`sources/HISTORY_POSTCHECK.json`。

| 保护范围 | 比较文件数 | 结果 |
|---|---:|---|
| R22原交付 | 39 | 原字节保持 |
| R23原交付 | 12 | 原字节保持 |
| R24原交付 | 22 | 原字节保持 |
| R22旧公开运行证据 | 391 | 原字节保持 |
| 既有保护清单 | 1194 | 原字节保持 |

本轮8份指定源码、42份源闭包、5份fixture与准入一致。R22原F24 ERROR堆栈、53PASS1ERROR结果、另外24/44回归、三个旧suite槽、旧TEST_RUNS、SOURCE_LOCK及独立进程见证都未改写。

R24原有静态状态与准入稿的AUTHORIZED_FOR_DYNAMIC_RUN=false保留其形成时事实。本次动态授权通过新增RUN_APPROVAL_RECEIPT单独表达；新增verification_runs为冻结合同批准的新树。两项新增均已事前授权，原73份记录逐字节保持。

原有13份私有合成DB/key/PEM类材料只比较元数据，内容读取和秘密摘要输出0，不从元数据比较推出其字节级验证。新运行也将13份私有文件仅登记路径和长度，公开manifest不给出秘密key或DB摘要。

## 新结果固定

完整运行原文保持在`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs\r24_new54_001`。新TEST_RUNS索引仅含本轮一个结果，RESULTS SHA为`abf9b4f8ec5dc2a0e5518beb6d546c601a09e2e73dbad8a59f918cebb97e571e`。外层stdout/stderr、suite日志、8份cleanup、两独立actor见证和creator journal均列入`sources/RUN_ARTIFACT_MANIFEST.json`，后处理仅读取，未重写原结果。

原批次计数3，新增R24批次计数1；R23/R24静态阶段未算作动态运行。当前总历史实际suite调用4，本轮1，未启用自动重跑。

## 秘密与权限

runner在内存可见新鲜测试秘密时对结果/日志执行扫描，原记录public_sink_scan=CLEAN；后处理再次扫描公开日志/JSON/源码快照的冻结canary，无命中。后处理未读取新鲜key以构造额外泄漏实验，也未输出秘密值/秘密摘要。

真实服务、网络/RPC、真实业务库/key、正式部署根访问、P1a/P1b/P2及S3-B2/S5均0。code modules导入记录单列，不能解释为真实服务启动。OS/VFS更底层监控未额外开展。
