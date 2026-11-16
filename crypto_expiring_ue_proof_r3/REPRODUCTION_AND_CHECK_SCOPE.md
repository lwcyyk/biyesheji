# 离线复现与检查范围

本轮输出目录为 `D:\毕业设计\crypto_expiring_ue_proof_r3\`。历史文件、R2 脚本和 PDF 保持只读；源码仓库未修改。

## 复现

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$pythonExe = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe 'D:\毕业设计\crypto_expiring_ue_proof_r3\finite_math_audit.py'
& $pythonExe 'D:\毕业设计\crypto_expiring_ue_proof_r3\verify_artifacts.py'
```

两个命令都只输出 JSON。第一个调用冻结的 R2 数学工具，并对 λ=4 的树、标签差、范围差、孩子代次和窗口作 17 项新检查。原始输入、预期、实际值及 8 项 R2 复用结果见 `FINITE_MATH_RESULTS.json`。第二个检查历史哈希、新工件及声明一致性，输出见 `VALIDATION_RESULT.json`。

`R2_INTEGRITY_RECHECK.json` 记录本轮只读运行 R2 工件校验器的结果；它保持原轮的分母和检查类型。

## 证明与检查的层次

- **原文直接核对**：所锁定 TCC PDF、重放读取的既有原图和逐页文本；结构侧车只核对文件/页数结构。
- **本轮手工证明**：R3-RANGE 的全子树表示限制、右孩子一般代次公式、根残因子及更新配对残因子、带前提的正确性不变量。
- **继承数学结果**：R2-LOCAL 的同轨迹模拟和 R2-EXP 条件攻击；本轮明确其实际来源缺项和完整密文/正文误差的区别。
- **有限检查**：17 项新增、8 项复用的组合/标量计算。它们验证指定小实例，没有验证 DSG 安全假设、一般协议正确性或整个自适应安全证明。
- **来源完整性**：作者完整版、历史全文、勘误和官方实现未取得或未核准；失败和空查询按实际保存。
- **外部核查**：仅形成待审沟通草稿；实际作者沟通、外部同行和证明助手复核均未发生。

校验通过表明登记工件对应且未被意外改写；SOURCE_UNRESOLVED 和数学前提缺项仍保持可见。

本轮候选协议实现数为 0，原生 AS/RP 请求数为 0。两个离线工具仅处理组合对象与工件元数据。新增文档中的修订需求没有被实施为新协议。
