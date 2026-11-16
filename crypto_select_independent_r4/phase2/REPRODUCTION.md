# 第二阶段复现与记录

本轮为INFORMED_PHASE2_COMPARISON。第一阶段所有封存文件只读；其14项哈希核验结果在 `PHASE1_INTEGRITY_CHECK.json`。输入读取时间和文件摘要在本阶段 `ACCESS_LOG.jsonl`，待审材料快照元数据在 `PHASE2_INPUT_MANIFEST.json`。

核心文稿依次为：`COMPARISON.md`、`CORE_EQUALITY_REVIEW.md`、`BOUND_REVIEW.md`、`CONSOLIDATED_THEOREM.md`、`FINAL_REVIEW_VERDICT.json`。当前定稿规范化同一个有效位置模拟器，澄清唯一全局b，原算法、理想游戏及计算假设不变。

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\毕业设计\crypto_select_independent_r4\phase2\phase2_checks.py'
```

命令仅用标准库精确算术、输出JSON，不读其它项目文件或调用网络。已运行结果保存在 `FINITE_CHECKS.json`，13项检查通过，含条件均匀性、秩解码、符号抵消、L6/B1有限索引比例、L7原始随机位数、计数上界及失败耦合常数。小例不能替代一般概率空间证明。

`RESULT_HASHES.json` 保存本阶段工件哈希；`PHASE2_SEAL.json` 另存该清单摘要以避免循环自哈希。封存时间来自本地UTC时钟，无外部时间认证。访问日志记录显式研究/结果I/O，不宣称覆盖Python或系统内部的全部依赖读取。

实际复核仍有既有上下文，没有新的无历史模型实例、外部同行或证明助手。候选协议实现、外部联系、邮件和原生AS/RP请求均为0。
