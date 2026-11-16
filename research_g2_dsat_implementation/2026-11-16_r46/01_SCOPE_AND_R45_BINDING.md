# G2-R46：范围与 R45 最终版本绑定

本轮已完成当前对话内的知情模型辅助静态审查、成本推导和文档取证。工程代码保持冻结，操作系统执行验证与外部复核仍待取得。结论为 `R46_STATIC_PREFLIGHT_BLOCKED`。

授权原文：`C:\Users\a1887\.codex\attachments\d6976602-fb28-482c-b86b-6b6ef01ef1a4\Pasted text.txt`。本轮仅审定八类资源的候选及缺口；所有 `approved_maximum=null`，`EXECUTION_AUTHORIZED=false`。

## 读取与绑定

完整读取 R45 的六份报告、全部 JSON 合同、来源定位、源码文本副本与补丁，共29份既有材料；对三个工程文件做全文及 AST 静态核读。阅读记录及每份文件 SHA 位于 [sources/R45_COMPLETE_READ_AND_BINDING.json](sources/R45_COMPLETE_READ_AND_BINDING.json)。工程源码保持以下版本。

| 对象 | 字节 | SHA-256 |
|---|---:|---|
| R41 Runner `scripts/run_dsat_current_build_regressions.py` | 125930 | `245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f` |
| R43 Driver `tests/test_dsat_runner_poison_classification.py` | 59239 | `28e9ccf96f20a634b274f5350e8044da87b33f0c73905448664a68a3c41c67fd` |
| R45 Supervisor `scripts/run_dsat_poison28_supervisor.py` | 53418 | `953d15d7b000b02014062924f80a40d537cba214e17e3459070000f70b8f16d1` |

工程路径均相对 `D:\毕业设计\auth-lifecycle`。R45 的 AMD64 ABI 纸面审核绑定最后一个 SHA；本轮复用其28个签名、11个结构布局结论。`AssignProcessToJobObject` 的接口虽有声明，主执行图通过创建时 JOB_LIST 挂载，实际调用上界为0。未执行 ctypes 布局或任一工程定义。

R45 全局锁 SHA：`47d4e26b0a67d702bb564c4be97cdccb55ba987df5e5f567582f35900642699d`。原28项清单为 R42 的 `R42_28_TEST_MANIFEST.json`，SHA `aaf20e86f733b2eaa7b09254bfaca86b4d23ca69ef4ebf6fc001e11b9db0219d`；所有原 ID 和断言保留，本轮均 `NOT_RUN`。

进一步复用 R44 八类矩阵、产物/来源合同与 T20 桥接申请，以及 R37 逐字段表示批准矩阵。R45 官方接口定位保留于其 `sources/WIN32_SOURCE_REFERENCES.json`；本轮没有新增网页获取或操作系统探测。该记录未保存出版方完整 HTML，其范围仅为已核读 API 语义定位，无法证明本机加载二进制或运行行为。

## 历史保护

审查前继承2561项历史指纹和45份历史 SOURCE_LOCK；追加锁定 R45 的29份交付及 Supervisor，共30项。最终比较口径为2591项记录、46份既有 SOURCE_LOCK，包含5个既有缺失路径。缺失路径的状态保持原样，G4 的历史差异继续待核。末次核对结果见 [sources/HISTORY_AFTER.json](sources/HISTORY_AFTER.json)。本轮 SOURCE_LOCK 单独生成并排除其自身，以最终外部读回摘要作为锁根。

## 操作边界

`SOURCE_MODIFICATIONS=0`、`DRIVER_MODIFICATIONS=0`、`SUPERVISOR_MODIFICATIONS=0`、`NEW_PYTHON_FILES=0`。`JOB_OBJECT_CREATED=0`、`CHILD_CREATED=0`、`RUNTIME_SAMPLING=0`、`ETW_STARTED=0`、`DYNAMIC_TEST_RUNS=0`。

用于文档取证的 PowerShell/标准库静态工具只读取、解析、计算摘要并写入 R46 报告。它们没有导入、执行或复制求值受测函数，没有运行 --help、测试、故障注入、Windows资源API、SQLite、网络服务或密钥操作。文档取证工具的文件写入属于本轮报告生产，不充当将来28项运行的测量值。

全部实际进程/内存/管道/运行字节/耗时指标为 `NOT_MEASURED`。2MiB与120秒保持原约束。机制实现的严格分离门、COL2026暂停、FS23延期及既有淘汰结论均沿用。
