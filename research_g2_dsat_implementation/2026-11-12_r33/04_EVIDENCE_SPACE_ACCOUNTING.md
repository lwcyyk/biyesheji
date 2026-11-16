# 空间计费、预留与容量缺口

原合同计量为13个运行文件的逻辑大小sum(st_size)，包含外部准备的approval receipt；总上限2,097,152字节。物理簇分配、目录和文件元数据开销当前UNKNOWN，另行保留计量边界。

R32实际写入2,075,679字节，余21,473字节。journal为2,056,226字节，suite日志5745字节、COMMAND日志268/0字节、失败receipt8549字节，其余文件逐项见 `R33_EVIDENCE_SPACE_ANALYSIS.json`。journal主要占用为PHASE_ASSERTIONS_FINISHED 640738、TESTS_FINISHED 486619、ORIGIN_CLASSIFIED 374149、ORIGIN_OBSERVED 283485字节。

R32没有为最终文件隔离空间，运行阶段先消费共享额度，随后RESOURCE_AUDIT检查点、MODULE_ORIGINS、RESOURCE_LEDGER、RESULTS依次被预算拒绝。原始文件未被删除或重编码；本轮仅在内存对已有JSON做静态计费。

| 文件 | 旧格式模型字节 | 新编码模型字节 | 新预留上限 | 证据范围 |
|---|---:|---:|---:|---|
| MODULE_ORIGINS.json | 556173 | 81552 | 262144 | complete reconstruction from persisted snapshot fields plus frozen control-flow integrity status |
| RESOURCE_LEDGER.json | 87444 | 9471 | 131072 | known subset only;final meter/RAM/elapsed unavailable |
| RESULTS.json | 892938 | 43372 | 262144 | known subset only;missing final resource and other fields |

MODULE_ORIGINS的556173字节为已存字段与冻结控制流的重建，原文件仍缺失。RESOURCE_LEDGER与RESULTS两行只有已知子集；完整实值和准确实际尺寸保持UNKNOWN。编码尺寸也属于模型测量，压缩对追加内容没有可直接沿用的单调上界。

R32全部609个value经过无损重编码逐项校验，模型journal为817454字节，最大单条31427字节。完整语义摘要索引绑定于空间分析；可复现工具为 `sources/REENCODE_EXISTING_EVIDENCE.py.txt`。这项工作没有执行Runner或测试。

| 未来运行路径 | 隔离额度/字节 |
|---|---:|
| RUN_APPROVAL_RECEIPT.json | 8192 |
| SUITE_INVOCATION_01.json | 8192 |
| TEST_RUNS.json | 65536 |
| COMMAND_stdout.log | 65536 |
| COMMAND_stderr.log | 65536 |
| r33_regression68_001/RUN_START.json | 16384 |
| r33_regression68_001/stdout.log | 65536 |
| r33_regression68_001/EARLY_FAILURE.json | 1048576 |
| r33_regression68_001/RESULTS.json | 262144 |
| r33_regression68_001/MODULE_ORIGINS.json | 262144 |
| r33_regression68_001/RESOURCE_LEDGER.json | 131072 |
| r33_regression68_001/test_metadata.json | 1032 |
| r33_regression68_001/test_request.json | 287 |

额度合计2,000,167字节，保留96,985字节未分配余量。最终三份JSON合计预留655,360字节，失败receipt单独65,536字节。对每个文件k强制size(k)+delta≤cap(k)，同时检查sum(size)+delta≤2MiB。其他文件持续受到各自cap约束，journal和日志无法占用最终文件的独立份额。

代码采用独占创建和最后摘要receipt的逻辑提交，磁盘临时文件为0，重命名和覆盖保持原禁令。逻辑峰值按同时存在的文件逐项计入，包含部分写入文件；内存中的原始/压缩对象没有被当作零RAM成本，原RAM硬限未分配、未来实测待取得。已成功fsync的完整链前缀构成恢复边界，操作系统/硬件崩溃保证保持条件性。

分区总额安全性已经证明，完整负载容量证明尚待完成。静态schema模型中，一条262144字节的构造traceback会形成200165字节编码receipt，超出65536份额。该模型只说明schema与编码规则自身没有给出有限容量结论；尚未证明该trace可由冻结68项产生，因此它没有反驳冻结测试的可行性。

当前状态为R33_EVIDENCE_BUDGET_STATIC_BLOCKED。所缺引理：在明确的冻结68允许执行域中，所有完整journal、来源观测、断言/异常/资源包分别满足上述编码后cap，并在suite启动前取得证书。当前历史样本的装入结果保持其局部范围。
