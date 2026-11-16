# R24最终裁决与唯一专项运行申请

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助源码修订、纸面分支复核与静态取证；动态验证与外部独立复核待取得。

**两项最小补丁已实现，静态准入通过；当前保持D1B1_PARTIAL_IMPLEMENTATION。** 已有剩余1次额度保留，本次授权仅用于修订和静态检查；新源码的实际运行需要研究者再次独立批准。

| 状态 | 登记 |
|---|---|
| R24_PATCH_IMPLEMENTED | TRUE |
| R24_OUTPUT_ISOLATION_STATIC_VERIFIED | TRUE |
| R24_PIPE_POLICY_STATIC_VERIFIED | TRUE |
| R24_HISTORY_INTEGRITY_VERIFIED | TRUE |
| R24_STATIC_PREFLIGHT_PASSED | TRUE |
| R24_RUN_AUTHORIZATION_PENDING | TRUE |
| F24_FIX_NOT_YET_EXECUTED | TRUE |
| D1B1_PARTIAL_IMPLEMENTATION | TRUE |
| D1B2_NOT_AUTHORIZED / P1_NOT_AUTHORIZED / P2_NOT_AUTHORIZED | TRUE |
| S3B2_NOT_AUTHORIZED / S5_NOT_AUTHORIZED | TRUE |

| 问题 | 回答 |
|---|---|
| Q1 两项阻塞是否修复？ | 静态范围内均已修复；运行验证待批准。 |
| Q2 文件和函数？ | 仅runner与dsat_windows_runtime两个文件；详细定义/行号见R24_CODE_DIFF.json及01。 |
| Q3 旧R22只读？ | 所有新输出固定R24验证根，audit关闭根外写入；R22仅来源/原bootstrap批准的只读引用。原可信本机模型边界沿用。 |
| Q4 F24错误码是否明确？ | 仅原stdin的EINVAL22或BrokenPipeError/EPIPE32且无native winerror，另须确认精确拥有子进程已退出。 |
| Q5 write/flush非预期错误？ | 保留并传播；同时尽可能完成拥有型清理和日志收集。 |
| Q6 退出码/主清理异常/输出？ | 静态实现已逐项保留，受秘密脱敏和有界文件规则约束；实际运行证据尚缺。 |
| Q7 协议/会话总量门变化？ | 未修改原持久消费、journal、Store、H2总量门或P2权限。R24作业批准独立新增且仅控制专项运行。 |
| Q8 54 ID与预期？ | 原测试文件、计划和fixture保持原字节；runner额外结果完整性门单列。 |
| Q9 历史哈希？ | R22/R23共51份交付、391份公开旧测试证据及1194份保护文件一致；13份私有合成材料仅元数据核对。 |
| Q10 是否具备申请条件？ | 是，23项静态检查通过，冻结真实命令/源码/预算；AUTHORIZED_FOR_DYNAMIC_RUN仍为false。 |
| Q11 54项运行次数？ | 本轮0次，原剩余1次保持；F24单项和子进程测试也未运行。 |
| Q12 唯一下一轮动作？ | 按R24_VERIFICATION_ADMISSION.json新源码哈希独立批准并执行一次new54；自动重跑0，失败后停止。 |

## 一次性申请的具体范围

申请仅使用原剩余的 **一次54项专项额度**，自动重跑0。采用`R24_VERIFICATION_ADMISSION.json`固定的2份新修改源码、全部源闭包和5份fixture、原54 ID及预期、解释器、工作目录和资源预算。24/44回归本次不申请、不执行；真实服务/DB/key/RPC/P1/P2/S3-B2/S5保持关闭。

准确argv（真实源码支持，本轮未执行）：

```text
["C:\\Users\\a1887\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "-B", "D:\\毕业设计\\auth-lifecycle\\scripts\\run_dsat_authority_live_lifecycle_tests.py", "--suite", "new54", "--output-root", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r24\\verification_runs"]
```

工作目录：`D:\毕业设计\auth-lifecycle`。外层命令与日志路径完整保存于`sources/VERIFICATION_COMMAND.ps1`；文件当前只作为冻结文本与静态解析对象。该命令独占创建新输出根，再执行一次Python；任何失败均无第二命令或自动重试。

未来研究者明确批准后，保存实际回复及摘要，按`sources/RUN_APPROVAL_RECEIPT.template.json`在新R24记录根建立实际receipt，绑定**准入稿SHA `3635abfb2d6c02e26fb76da547ba947bb45865dc7cf7afca416a5c9e93bb3698`**。原R22批准与SOURCE_LOCK保持。当前模板approved=false，实际receipt不存在。

新输出根：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs`；唯一run：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs\r24_new54_001`。实际启动后，无论成功、失败、异常或部分完成均消耗唯一额度。原始日志、退出码、每个子进程cleanup、资源账和完整54结果必须保留。

成功条件为54 PASS且worker额外完整性门、F24实际退出/日志/资源回收、F23/F26/T45、资源上限与历史保护均满足。失败时保留证据并停止，后续修改及额外运行另行批准。

未来54项成功会改变F24修复和专项验收状态；完整合同仍有当前版本68项兼容性责任，详见04。学术创新资格和严格分离门继续分别管理。COL2026主动检索暂停、FS23延期沿用。

## 授权依据

本次用户请求第一节明确写明“本轮不批准执行任何动态测试”，第八节要求“未来执行需依据本轮新源码哈希再次独立批准”。因此本轮交付可复核的静态结果和具体运行范围，等待新版本的一次专项运行批准。
