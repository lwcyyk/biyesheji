# 复核执行与复现

本轮指定无历史语言模型子任务未执行，原因是当前侧会话禁止子代理交互。实际执行为同会话知情重建、原材料阅读和新的独立 Python 进程做确定性算术。进程隔离只用于复现有限检查，不形成独立数学判断。

`REVIEW_INPUT_MANIFEST.json` 明确保存实际执行方式、13个冻结对象、4份第一阶段允许输入、未执行阶段的null结果字段，以及当前重建结果的时间与哈希。`input\` 不含项目待审证明或裁决结论；官方GP23全文是允许的先例材料。

## 命令

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$pythonExe = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe 'D:\毕业设计\crypto_unidirectional_ue_review_r3\review_checks.py'
& $pythonExe 'D:\毕业设计\crypto_unidirectional_ue_review_r3\verify_review.py'
```

第一个仅用标准库精确算术，运行时将完整有限输入/结果表写入本目录的 `FINITE_RAW_RESULTS.json`，stdout摘要保存为 `REVIEW_CHECKS.json`。其输出角色与一般密码学证明分开。

20项检查含1项旧工具结果复用汇总；旧工具自己的13项结果在原始记录中单列。小L静态历史计9360条，抽象自适应特征树计2048行。形式指数分布只是小群映射计数；没有实际UE、群密码库、Frodo参数或AS/RP实验。

第二个命令只读验证文件哈希、源版本、阶段执行状态和裁决字段，结果见 `VALIDATION_RESULT.json`。`ARTIFACT_MANIFEST.json` 排除自身和验证结果避免循环哈希。

新补全证明为 `REVISED_SELECT_PROOF.md`。它补充原R2的论证而不修改历史文件。优先复核项目是两世界的受限子概率质量，不由有限检查数或角色分离代替独立证明复核。
