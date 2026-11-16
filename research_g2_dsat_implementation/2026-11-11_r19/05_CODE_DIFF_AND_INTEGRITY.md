# 代码差异与历史完整性

日期：2026-11-11。范围：研究者本轮明确批准的成熟工程接线与离线验收。证据为本对话内模型辅助实现、实际执行与知情源码复核；外部独立验证待取得。


## 修改边界

本轮仅修改一个既有源文件 `src/auth_lifecycle/online_state/services.py`，新增五个 Python 文件和一个三文件 fixture 子树。完整路径以 `D1A_FILE_LOCK.json` 为准。研究目录中的报告与证据汇编工具仅用于文档取证。

| services.py | SHA-256 |
|---|---|
| 原始源码/原字节快照 | `7cc2321e2623c06848e13d106680887a01bd5635bf417127942a5bac1647be41` |
| 当前源码/最终两域测试版本 | `3bd6f5dd29b5327308c9aa08459e20a704724756ef4801acb4b31716d5a05d03` |

原字节存于 `sources/original/services.py.txt`。修改理由为可选 runtime context、Store 后绑定、listener 元数据和拥有资源清理钩子。原默认路径与 R16 ticket/mount/dispatch 逻辑保留。`sources/CODE.diff` 包含实际完整 diff 和五个新增文件；由于原行尾形式不同，services diff 可能显示较大替换范围，语义顺序另由 D23 AST 检查。

## 核验结果

执行前历史比较 **1441 行匹配**；执行后仅允许 `services.py` 对应的 **9 个来源比较行**映射到新 SHA，其余 **1432 行保持**。9 行来源于多份历史锁中重复引用，实际既有修改文件数为 1。每轮测试前后均核对历史来源和当前 code/input；原 services 快照保持原 SHA。

保护范围覆盖 R16 激活/读宿主模块、原 A1/H1 测试/runner/fixture、R12 B1、R10 S3-A、R07 S1/S2、Controller/Provider、旧 CLOSED/1、migration，以及 R18/参数确认资料。既有 SOURCE_LOCK 和失败日志保留原字节。最终历史复查见 `sources/DELIVERY_QA.json`。

## 新证据固定

- `SOURCE_LOCK.json`：本轮请求授权、代码/输入、最终结果、所有运行及早期失败摘要。
- `CODE_DIFF.json`：逐路径 SHA、行数、原快照、新 fixture 与保护结论。
- `sources/CODE_SYMBOLS.json`：通过 AST 提取的实际入口与行号。
- `D1A_TEST_RUNS.json`：四个完整 suite，加一条预检失败引用；runtime 原索引保持。
- `sources/*_PRE_DELIVERY.json`：本轮中间汇编记录原字节，用于核对最终补充字段。
- `sources/DELIVERY_QA.json`：最终报告/证据清单及摘要，排除自身哈希循环。

生成报告后再次核对六份最终源码，文档汇编未改变已验收工程版本。所有轮次的快照、日志和异常记录保留。哈希仅固定版本；外部独立验证范围仍待取得。
