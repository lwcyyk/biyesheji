# 离线复核、证据口径与复现

所有本轮材料位于 `D:\毕业设计\crypto_unidirectional_ue_adaptive_r2\`；9 个起点文件由 `INPUT_LOCK.json` 冻结，旧算法/游戏/候选结论保持只读。本轮未发外部消息，未访问原生 AS/RP，未实现候选协议。

## 复现

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$pythonExe = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe 'D:\毕业设计\crypto_unidirectional_ue_adaptive_r2\mathematical_checks.py'
& $pythonExe 'D:\毕业设计\crypto_unidirectional_ue_adaptive_r2\verify_artifacts.py'
```

第一个命令只处理有限集合、域运算和有理评分恒等式；原始输入、预期与结果保存在 `MATHEMATICAL_CHECKS.json`。13 项检查包括 2048 个 L=4 闭包状态的联合/分阶段一致性及单调性、合法未来钥匙的三个负控制、边界双射及桥接等式、带符号求和和三角计数。它没有生成密钥/密文、执行群加密或进行 Frodo 参数实验。

第二个命令只读校验工件哈希、冻结范围、裁决与数学结果字段，输出见 `VALIDATION_RESULT.json`。`ARTIFACT_MANIFEST.json` 排除自身及验证结果以避免循环哈希。

## 各层证据

- 原文：GP23 的已取得正式版，及 p407/Fig.2、p423/Fig.6 本轮原图。历史 PDF 结构预检已经 PASS；其哈希与本轮输入锁对应。
- 手工一般证明：联合最小闭包与历史合法性、ALL 的事件分解、NORMAL-BRIDGE、UNI-FRESH-CHAIN、SELECT 的带权规范边界归约。
- 有限复核：上列 13 项算术与集合检查。一般安全性不由小例或检查数推出。
- 独立审查：当前为同一代理的内部反方核查；外部同行、作者、跨模型及证明助手复核均未发生。
- 原创性/优先权：保留为理论候选，未清除既有方法覆盖及先例问题。Frodo 候选仅复核表述和依赖，无新实验。

G-ALL 与 G-SELECT 使用最终有效性；归约提前停止的评分对应及猜错路径损失写入证明。没有把模拟器不能响应的查询统一改为真实游戏非法。
