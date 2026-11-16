# 独立输出与历史只读修订

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助源码修订、纸面分支复核与静态取证；动态验证与外部独立复核待取得。

**OUTPUT_ISOLATION_STATIC_PASSED / R24_OUTPUT_ISOLATION_STATIC_VERIFIED。** 证据为源码/AST/路径推导，运行行为待后续一次验证。

## 根与批准分层

- 新运行输出根：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs`。
- 唯一run：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs\r24_new54_001`。
- 新的动态执行批准：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\RUN_APPROVAL_RECEIPT.json`，runner与子进程只读。
- 原合成bootstrap批准：`D:\毕业设计\research_g2_dsat_implementation\2026-11-11_r22\APPROVAL_RECEIPT.json`，继续只读，用于保持原启动动作合同和T52接口。

runner与Windows模块固定到同一个R24输出根。新CLI参数`--output-root`为required，并必须等于冻结根；省略或不同路径均拒绝。没有R22输出根fallback。Windows的`RECORD`有意保持指向R22：`dsat_authority_live`与六操作接口继续读取原APPROVAL_RECEIPT，批准ID、摘要字段和journal序列语义不变。新R24批准属于外层测试作业准入，不能发行真实部署或P2资格。

## 执行门及唯一性

主入口只接纳new54。R24独立receipt需匹配准入稿摘要、真实批准回复摘要、解释器路径/摘要、根、run ID、最多一次、自动重跑0和资源预算，所有真实权限位为false。源锁与原测试计划SHA另行核验。缺少批准或版本失配会关闭准入。

授权后唯一`SUITE_INVOCATION_01.json`采用x模式创建；固定新run目录采用独占mkdir。没有第二槽位或自动测试循环。新JSON输出统一x模式；`TEST_RUNS.json`位于新验证根并独占创建。运行中故障和部分结果保留，已有槽位或run阻断后续复用。

## 写入点追踪

`R24_OUTPUT_ROUTE_AUDIT.json`列出直接工作流五份文件中的 **113处潜在写入/持久化调用点**，逐项包含文件、行号、表达式和路径保护。此数为语法级调用点，包含故障注入和重复封装调用，不等于实际写次数。

| 输出类别 | 路径来源与保护 |
|---|---|
| 调用槽、TEST_RUNS索引 | 新OUTPUT，target检查后x创建 |
| RUN_START/RESULTS/FAULT_COVERAGE/EARLY_FAILURE | 独占新RUN内，write统一x创建 |
| 代码快照、suite stdout | 新RUN/code_snapshot及stdout.log；RUN先独占创建，audit复查写范围 |
| 外层完整stdout/stderr | 冻结PowerShell命令先独占新验证根，然后重定向到该根 |
| 独立进程见证、worker manifest | TestScope.root即新RUN；保留真实独立进程要求 |
| grant、marker、消费journal、effect | 原scope.path/lease保护，创建于新RUN；R22格式名保留 |
| 合成SQLite及测试key/TLS文件 | 原scope.path和runner DB/file audit限定新RUN |
| 子进程stdout/stderr及cleanup JSON | `child_NN_*`全部由scope.write_new创建于新RUN |
| 临时替换、损坏注入、已有marker更新 | 仅作用于本次新RUN生成的测试状态，原测试必要行为保持 |
| ACL、instance.lock与Stop Event | 原拥有型scope/句柄机制，文件限新RUN；Event名称中的r22前缀仅为协议命名 |

runner target检查绝对路径、ADS/UNC/越界、重解析点和硬链接；原TestScope再检查本run边界与文件身份。audit继续关闭所有新根外的写入、socket和正式部署访问。原保护历史仍只读核验。

## 子进程与失败

父进程创建命令及audit白名单同步加入明确的`--output-root`；worker要求固定run根，再复核新receipt、RUN_START摘要、原bootstrap批准与源闭包。手工创建的外来进程仍需通过原creator登记，命令参数不能替代拥有性。

RUN建立后的异常写入RUN/EARLY_FAILURE；此前的异常只落到明确重定向的新根stderr，不回退旧目录。外层命令若发现验证根已存在便停止，避免覆盖之前stdout/stderr。静态阶段只保存命令文本，没有创建验证根。

保证适用于原可信本机Windows/NTFS、正常OS、完整ACL模型。恶意同SID/管理员在检查后并发替换路径、卷回滚和断电持久性沿用未验证边界。静态路径检查不升级为该攻击模型下的原子路径证明。
