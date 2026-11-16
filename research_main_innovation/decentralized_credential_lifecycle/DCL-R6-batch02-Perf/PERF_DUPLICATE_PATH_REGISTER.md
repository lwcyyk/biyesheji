# 误路径副本登记（只读）

Material Passport：READ_ONLY_REGISTER。误路径为`D:\毕业设计\System.Management.Automation.Internal.Host.InternalHost`，仅包含native_snapshot与FROZEN_LC两棵副本。

本轮枚举/hash共47文件，逐项与正确batch02目录对应文件一致：native_snapshot32项、FROZEN_LC15项。完整相对路径、字节数及双方SHA在[evidence/DUPLICATE_REGISTER.json](evidence/DUPLICATE_REGISTER.json)。正确目录为`D:\毕业设计\DCL-R6-isolated-verification\batch02`，其外层证据ZIP与原生ZIP直接核验通过。

来源为batch02封存时误用PowerShell Host只读变量；随后正确根已建立安全复制并核hash。原审批记录位于DCL-R6-batch02/evidence/BATCH02_COPY_CORRECTION.json，实际返回仅`blocked by policy`，缺少更具体理由。当前不补造拒绝原因。

本轮没有再次尝试迁移/删除、改名、覆盖、提权或使用其他接口。副本及metadata保持原样。它不影响正确封存的分析，也不属于未来正式输入。

batch03唯一可信历史输入为正确batch02/FROZEN_LC及对应已核原始输入计划；新版本只从这些摘要匹配的字节创建。执行锁要求绝对source_directory、canonical路径与root-owned来源链，拒绝误路径前缀、目录联接/符号链接跳转或按文件名/当前目录自动发现。修复工作区也不得从该误路径导入。

冻结源码的Source由__file__.resolve定位，不会自己搜索误目录；但若操作者直接从误目录启动脚本，SOURCE仍会落在那里。因此新启动器必须额外固定/校验唯一批准SOURCE，不将“resolve了”当作可信来源证明。

目录整理若有需要，单独提交该已知路径/47文件清单的处置申请，仍服从系统审批结果。本轮不执行、不要求通过其他途径绕开策略。
