# 完整L0对象清单

以R35原13对象和R38实际写点为基础，新增文件0，新增内容均在原journal和最终JSON中。实际写原语仍为受控exclusive FileIO，经原write前扣费/poison层。

| ID | 文件 | 原配额B | 完整必需尺寸界B | 内容适配状态 |
|---|---|---:|---|---|
| F01 | `RUN_APPROVAL_RECEIPT.json` | 8192 | 8192 | CONDITIONAL |
| F02 | `SUITE_INVOCATION_01.json` | 8192 | 681 | CONDITIONAL |
| F03 | `TEST_RUNS.json` | 65536 | UNPROVEN | UNPROVEN |
| F04 | `COMMAND_stdout.log` | 65536 | UNPROVEN | UNPROVEN |
| F05 | `COMMAND_stderr.log` | 65536 | UNPROVEN | UNPROVEN |
| F06 | `RUN_START.json` | 16384 | 9576 | CONDITIONAL |
| F07 | `stdout.log` | 65536 | UNPROVEN | UNPROVEN |
| F08 | `EARLY_FAILURE.json` | 1048576 | UNPROVEN | UNPROVEN |
| F09 | `RESULTS.json` | 262144 | UNPROVEN | UNPROVEN |
| F10 | `MODULE_ORIGINS.json` | 262144 | UNPROVEN | UNPROVEN |
| F11 | `RESOURCE_LEDGER.json` | 131072 | UNPROVEN | UNPROVEN |
| F12 | `test_metadata.json` | 1032 | 1032 | CONDITIONAL |
| F13 | `test_request.json` | 287 | 287 | CONDITIONAL |

F08已更新为R38的开始/原结果/逐项详情记录、来源快照、组汇总、最终状态与失败链；没有只复制原13项旧记录数。F09/F11/F03含新case状态/确认引用/知识集合/读取观察，所有增加均被纳入清单。

L0包括实际原结果、ID/组/源版本/原预期、检查点/成功前缀、来源身份/拒绝依据、费用/所有权/持久化未知和独立可靠退出观察。OBSERVED_IN_MEMORY、DURABLY_COMMITTED、PERSISTENCE_UNKNOWN保留分别语义；实际退出码由独立调用者观察，native_exit_required只表示验收要求。

每个JSON对象采用实际canonical选项：sort_keys、ensure_ascii=True、紧凑分隔、allow_nan=False、UTF8；ordinary文件加LF，journal逐行加LF，D24保持1032/287原字节。失去L0原值或引用不能降为可选。

9项待确认诊断原责任没有被批准减少。原部分诊断在失败路径实际占用的字节也必须计入相应文件，不能因它不属于核心L0而从物理计费中消失。清单原子瞬态0仅指额外磁盘副本，RAM/内核缓存/物理簇分别管理。

13对象和外部退出边界已枚举；完整域中所有producer负载的适配界仍未取得。
