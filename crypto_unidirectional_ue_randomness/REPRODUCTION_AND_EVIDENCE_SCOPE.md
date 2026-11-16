# 离线复核与证据范围

本轮输出全部位于 `D:\毕业设计\crypto_unidirectional_ue_randomness\`。历史输入保持原始版本，通过 `INPUT_LOCK.json` 冻结。没有修改 auth-lifecycle，也没有创建、发送外部通信或调用 AS/RP。

## 复现命令

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$pythonExe = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe 'D:\毕业设计\crypto_unidirectional_ue_randomness\mathematical_checks.py'
& $pythonExe 'D:\毕业设计\crypto_unidirectional_ue_randomness\verify_artifacts.py'
```

两个命令只向 stdout 输出 JSON，均无网络调用。前者仅用 Python 标准库，计算 16 项有限算术、矩阵计数与闭包检查；原始输入、预期、结果见 `MATHEMATICAL_CHECKS.json`。其中未核准的 Frodo 数值输入明确标为示例，未用作实际实验参数。

后者核对历史和新工件哈希、来源实际类型、profile 范围与实现门字段。原始结果见 `VALIDATION_RESULT.json`。`ARTIFACT_MANIFEST.json` 排除自身与校验结果以避免循环哈希。

## 各种依据分别登记

- **原文**：RC26 14 页与 FI 23 页为历史输入；GP23 30 页及 MPW23 31 页正式全文本轮新取得。对应版本、哈希和实际读取章节见 `SOURCE_REGISTER.json`。
- **手工证明**：Frodo 真实分布下成功率恒等式、方阵可逆支撑攻击界、GP23 明确 profile 的正确性归纳、挑战新鲜化及完整 DDH* 归约。
- **有限数学检查**：GL 计数、支撑双射、Ord/Tensor、均匀平移及闭包负控制，支持指定输入的算术复核。没有实现实际 Frodo、群加密、UE 原型或进行原生采样。
- **类型/接口补全**：Frodo 的 Ord 列数重载；主 profile 的非零密钥域、目标公钥上下文、消息群和指数域。每项在正文显式列出，未冒充已核准作者代码。
- **缺项**：两篇 PKC 扩展 PDF 返回 HTML；官方 Frodo 参数参考获取失败。MPW 具体 DDH 实例的带保持性质及 FI 实际性能配置的正确性符合性保留未核实。
- **审查方式**：同一研究代理在纸面上构造归约并作内部反方核查；无作者联系、外部同行、跨模型或证明助手复核。优先权尚未清除。

正式交付的增强结论只针对 UNI-R-CPA-1 固定切点/历史 K1 暴露/全公开 token。固定 profile 的较小损失不与不同量词的原文定理作性能或理论优越性比较。
