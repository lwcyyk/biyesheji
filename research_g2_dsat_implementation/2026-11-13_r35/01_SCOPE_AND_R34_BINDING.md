# R35 范围与 R34 绑定

本轮完成单一 Runner 的代码维护与静态审查，最终为 **R35_STATIC_PREFLIGHT_BLOCKED**。suite、单项、目标模块导入、故障注入、测试子进程、SQLite/TLS/密钥创建均为 0。全部本轮取证位于此新目录，运行命名空间尚未创建。

授权来自本轮 R35 全文及 R34 `R34_NEXT_ACTION_REQUEST.json` / `05_FINAL_VERDICT_AND_AUTHORIZATION_REQUEST.md`。R34 申请中的 approved=false 是历史申请状态；用户 R35 正文独立批准了限定代码维护。本轮沿用原异常完整性义务，对受限诊断能否成为接受的替代合同保留待审状态。

唯一改动的既有工程文件为 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`。修改前原字节已保存到 `sources/RUNNER_BEFORE.py.bytes`，随后才改源码；完整补丁为 `sources/RUNNER.patch`。

- 修改前 SHA-256：`5b751f4d6cf654f928d6c0053bab7fbc23caaaa1975a55816968f39aa35237c5`。
- 修改后 SHA-256：`e227b5f3c9a1347474040f64ffe8d71f422b9b0b213610fbeba5589a3c7541a9`。
- 修改/新增方法共 43 项，具体列表与定位在 R35_CODE_DIFF / sources/SOURCE_LOCATION_MAP。范围包括输出生产者、校验、计费、持久化、工作/收尾控制与新命名空间接线。
- 42 工程源码、3 原测试、10 fixture 与源摘要 `621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9` 匹配。来源验证核心方法、D24 投影方法等 AST 保持相同，详见静态安全核对表。

完整读取 R34 的 22 份交付/来源记录；复用13文件、原30异常及历史609条817454字节的限定结论。817454始终是确定历史值，未来完整上界另行审查。原R32仍为68 PASS、native exit1、最终三JSON未保存、失败receipt已存；R33/R34静态阻塞和R25原54 PASS均保持历史定位。

## 新发现：运行时入场漂移

R34原2273项中，2261项入场匹配，12项入场已偏离旧锁，其中5项文件缺失。涉及 python.exe、python312.dll、SQLite两个二进制、CFFI二进制与RECORD、Rust二进制及5份pycparser元数据。精确旧/新SHA和缺失项在 `sources/HISTORY_BEFORE.json`。这些差异在任何本轮源码修改前取得。

新增R34交付保护后共2295条。结束核验：仅授权Runner发生变化，其余条目的字节或缺失状态与入场一致；旧SOURCE_LOCK未改。当前旧运行时匹配门为false。未替换依赖、安装包、恢复环境或重写历史指纹。

原2MiB/13路径/120秒及生产读取白名单、394运行时源码目录、依赖固定值保持。新增R35文件为控制/静态证据；固定运行时原文读取权限沿用原表。研究交付目录大小与运行时13文件计费域分别管理。

本轮属于当前对话内模型辅助静态审查，动态正确性与外部独立核验仍待取得。
