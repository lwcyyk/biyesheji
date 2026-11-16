# 单文件补丁

已有工程文件仅修改 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`。14个既有函数发生差异，其中部分仅为R33命名空间；新增3个辅助函数。函数范围、行号及before/after哈希见 `R33_CODE_DIFF.json`，原始字节与补丁均保存在sources。

| 修复 | 定位 |
|---|---|
| 原生扩展精确键、预算准入 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:165`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:131` |
| 内建模块字典访问与包装身份链 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:95`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:641` |
| 无损证据编码与明文净化 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:244` |
| 统一分文件预算及最终产物编码 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:360`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:373` |
| 原阶段/逐项链保留 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:255` |

字节编码为canonical JSON→内建zlib level9→内建binascii base64。payload同时保存原始字节数与SHA，外层仍为JSON。先扫描未压缩字节中的净化约束，再检查最终写入字节；字段和真实错误语义完整保留。两项codec均属于原解释器内建模块，引用现有解释器/DLL信任；文件读取目录项新增0。

编码模块在受控audit hook启用后的辅助函数内加载，crypto提前导入新增0。所有运行JSON仍独占创建，journal仍为已持有流的追加写入、逐条flush/fsync及序号/摘要链。D24两个原JSON继续以原始字节写入。

21个关键函数AST完全保持，涵盖读取/audit/缓存守卫、文件身份检查、SQL包装、D24投影及恢复、Results.record、错误记录、独立发布和entry收尾。State.preflight、load_group、main、finalize_evidence反向替换R33命名空间后AST相同。原68断言、A17、D24、R16/R22/R25相关生产版本和授权性质保持原合同。

预算合同的full_required_output_bound_proved当前为false。controls命令准入和State构造均设置拒绝门；在容量证明闭合前，EVIDENCE_BUDGET_INSUFFICIENT会阻止进入调用槽、测试、SQLite连接和watchdog阶段。本轮该路径仅静态审查，实际触发次数0。
