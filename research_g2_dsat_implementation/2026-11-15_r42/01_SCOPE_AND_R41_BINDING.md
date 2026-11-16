# R42范围与R41绑定

本轮完成28项Poison分类测试的静态准入审查及专用驱动规格，裁决为 **R42_STATIC_PREFLIGHT_BLOCKED**。所有28项仍为NOT_RUN，动态测试0，执行授权false。

## 条件授权的实际适用

本轮附件为 `C:\Users\a1887\.codex\attachments\7f7fee2c-197c-48ab-a599-03acce50b7ff\已粘贴的文本.txt`。第一节规定：“只有当 R41_NEXT_AUTHORIZATION_REQUEST.json 明确包含该驱动的创建权限，并且给出可核验的文件路径、修改范围和资源边界时，才允许新增对应驱动文件及进行静态检查。”同节为权限缺失预设了“只形成驱动规格及最小代码实施申请”的分支。

实际R41申请包含拟新增文件和phase_A_requested请求范围；其 `/phase_A_requested/test_harness_creation_authorized_now=false`、`/approved=false`，并保留最终资源账本及整进程内存缺口。本轮将这些字段按待批准申请处理，采用上述规格分支。具体条款、JSON路径和判断存入sources/INPUT_BINDING_AND_PERMISSION_AUDIT。该判断没有覆盖研究者后续明确授予的创建权限。

因此当前：DRIVER_SCOPE_APPROVED=false、DRIVER_IMPLEMENTED=false、DRIVER_SOURCE_HASH=null。单文件实施请求已具体化，当前源码创建0、目标Runner修改0。

## 完整读取与版本核验

R41目录全部26份文件完整读入；JSON完整解析并逐字段核对，六份报告核读。当前Runner全文及AST读取，复核五函数和helper。R41原SOURCE_LOCK SHA：

`c36dc66873a1c99c5bf5d2aca14ca045b10b27c112e23595b3d8fb6fbf915791`

当前Runner：`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`，125930字节，SHA：

`245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f`

五函数及helper的原字节摘要均与R41_CODE_DIFF的new pin相符。解释器现有字节与R41提议的50f885…指纹一致，完整值见R42_SOURCE_LOCK。该核对绑定拟用单元验证环境，G4旧/新运行时等价与准入仍待完成。

## 原有结论

R41局部Poison静态修复继续沿用。已扣费用、确认前缀、短写/flush/fsync/提交未知和身份冲突各保留原语义；R42没有将其升级为动态PASS。G2完整L0容量UNKNOWN/UNPROVEN、G3部分批准、G4待核及D1-B1部分实现保持。

R40/R41原测试计划按28个ID逐项核对，剥离R41新增定位字段后，全部原字段一致。原55项工程/测试/fixture pin仍匹配。

## 历史保护和实际操作

继承R41当前2457项保护状态，R41本轮已经授权的Runner变化作为当前基线；另保护R41全部26交付文件，总计2483项。入口与结尾核对见HISTORY_BEFORE/HISTORY_AFTER。先前41份历史锁及R41锁均保留，共42份旧SOURCE_LOCK。

本轮只新增R42静态报告和JSON。Runner、生产源码、测试/fixture、依赖、旧锁修改0；目标或抽取函数执行0，动态导入0，测试SQLite/密钥/子进程/线程/网络/服务0。verification_runs没有创建，运行额度没有消费。

证据属于当前对话内知情模型辅助静态装配审查，独立外部核验待取得。
