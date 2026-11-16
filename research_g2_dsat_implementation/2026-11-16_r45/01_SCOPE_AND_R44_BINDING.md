# R45范围与来源绑定

已按R45授权新增一个Windows父进程监督器，完成声明架构下的源码、ABI、句柄和路径静态审查。当前执行门为BLOCKED，八类approved_maximum仍为null。

唯一新增工程文件为 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_poison28_supervisor.py`，实施前ABSENT，当前SHA-256为

`953d15d7b000b02014062924f80a40d537cba214e17e3459070000f70b8f16d1`

授权附件为 `C:\Users\a1887\.codex\attachments\fe77c29c-502b-4ca1-b48d-39b630025493\Pasted text.txt`，其SHA为 `676f7bf3014d913695f900b4e287f688bf8a33174759907a3b1a2b38fc2fe2ae`。R44申请指向相同文件，现有文件编辑许可为0。R45授权覆盖该单文件创建。

## 输入核验

R44全部28份材料完整读入，包含六份主稿、资源/T20/内存/时限/产物/来源合同及来源定位。R44锁为 `d56f1f7b2b70160c29fc99d3dcbd4a7e9f8872557d3b76fca5c1ad135fa749ec`。

R41 Runner为 `245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f`。R43 Driver为 `28e9ccf96f20a634b274f5350e8044da87b33f0c73905448664a68a3c41c67fd`。原五函数/helper和28项身份以旧锁逐项核验。

## 实施和验证范围

本轮实际NEW_FILES=1、R41_RUNNER_MODIFIED=0、R43_DRIVER_MODIFIED=0。Job创建、Child创建、采样、ETW及动态测试均为0，EXECUTION_AUTHORIZED=false。

独立静态工具只处理文本、AST、哈希和整数布局。ctypes结构大小按Windows AMD64 LLP64纸面规则计算，当前结构和函数均未导入或执行。运行时sizeof校验已写进惰性入口，实际验证仍待授权。

采用了两个只读辅助审查任务。策略审查完成，ABI审查覆盖布局和部分源码后结束，主审继续完成最终源审查。外部独立OS验证待取得。

## 历史保护

继承R44的2533项保护状态，并纳入R44全部28份交付，共2561项旧文件/缺失状态。旧45份SOURCE_LOCK纳入哈希比对。唯一项目新增例外为本监督器，证据目录中的文本快照/diff按取证材料记录。

G2完整L0、G3部分批准、G4七变化/五缺失及D1-B1部分实现继续由独立合同管理。
