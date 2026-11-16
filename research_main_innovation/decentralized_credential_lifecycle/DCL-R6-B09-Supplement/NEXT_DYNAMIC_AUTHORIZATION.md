# 新版本的两份独立动态执行申请

Material Passport：B09-AdmissionFix-static-1/r1；REQUEST_ONLY；本轮动态许可范围为0。

当前用户授权只涵盖静态修订。以下请求绑定新manifest `c7bed9528ea4a6ada08882d02be23dd37c62e8ee79fbb70a9445ddcc361ea127`、执行锁 `fcc70f0d78aefc1ccc1fcc96489a3984417c6b4b7f203c78162c910b64746b81` 和[42项源/输入锁](evidence/STATIC_WORKSPACE_LOCK.json)。旧batch09准备阶段锁、旧动态范围和batch08收据均保留历史归属。

## 方案B：有限完整校准诊断（当前推荐）

scope=CALIBRATE_S1S9_ONLY。请求将41份Linux源/输入部署到独立cr09并完成source-only原生语法、当前工具/权限/boot核验；用单次前台WSL、同进程exec、sealed与一次认领启动全新batch09-r1窗口。运行全部当前冻结校准与安全回归：C00/READY64、C01–C08、H34、IPC56、BC40、真实C09及一次同父恢复、C10–C12、S34、Root原件重算、门18、fresh健康账。正常完成即关闭封存，FORMAL分支保持关闭。

本方案请求保留：全批1,000,000访问/1,800秒/提前1,740，校准100,000访问/300秒，每进程AS1GiB，Payload父4tasks；原CPY312与AS4条件。Root父/scheduler/停止器及最多一个顺序凭据探针单列TCB，既有预检120秒/AS1GiB与初始sealed票据10秒保持。新增ledger不增加进程或service。

真实时间证据采用现有G.stamp、timing聚合、原始stdout/stderr、service journal、预算事务及Root文件采样。按stage开始/完成书签、各自时钟域及已有原件时间戳给出可核验包络；缺少精确函数返回点时报告区间/UNMEASURED。只读导出与行政解析不得调用目标语义重放或额外故障。每个阶段的Root结果/trace已有sample和原件顺序，足以形成当前关键路径的实际包络；细粒度未打点部分继续明确保留。

首个关键失败、证据缺失、预算状态不确定或300秒校准截止立即停止发新资格，使用原关闭/有限回收并封存；原T0/账保持，无重试、重置、现场修复或自动新批次。截止后的必要清理/封存单独计时，模型启动数保持0。若实际测量不足或超时，保留原始首次失败并另提最小修订意见。

当前B批准模板：[DYNAMIC_B_AUTHORIZATION_TEMPLATE](evidence/DYNAMIC_B_AUTHORIZATION_TEMPLATE.json)。它尚未批准，无法直接启动。

## 方案A：完整条件验证

scope=CALIBRATE_S1S9_THEN_F1_F4。前置条件为：身份及门18静态补缺完成；当前版本300秒时间可行性获得充分依据；当前工具/资源/boot及全部新摘要匹配；用户明确批准新版本A。校准顺序与B完全相同，当前资源资格全部真实通过后，同一剩余窗口自动F1→F4；首次关键失败停止并封存。

F1按冻结SMOKE/BRANCH/CHAIN/KEY及所有指定mutant与重放；F4按COST1/CE5/固定夹具/G64、DP/独立TRACE-REF、压缩比较、指定mutant与重放。全部共账，仅对实际穷尽指定范围授PASS_BOUNDED；动态覆盖和域/访问停止如实报告。F2/F3等其他范围继续另列。

当前A的时间前提为UNRESOLVED，故本轮优先请求B。A模板见[DYNAMIC_A_AUTHORIZATION_TEMPLATE](evidence/DYNAMIC_A_AUTHORIZATION_TEMPLATE.json)，批准位全部false。A/B是对同一个尚未建立运行窗的两个互斥方案；B若先执行并CLOSED，后续A须准备新的独立身份/执行锁与对应授权，旧窗保持关闭。

## 共用的精确入口和证据要求

命令和新控制路径见[B09_EXECUTION_LOCK_REFINEMENT](B09_EXECUTION_LOCK_REFINEMENT.md)。回执必须绑定batch09、r1、scope、全部新摘要、实际授权原文SHA，明确接受同会话、Root探针、同父一次C09恢复及原生特殊映射范围。入口依据scope选择被冻结A/B argv，运行时不改源码或任意替换批次字符串。

请求的只读部署/停止/证据导出范围限新cr09和batch09-r1的已冻结文件与单位。历史batch01–08、batch09旧准备锁、误路径副本与blocked by policy保持。全局WSL配置、安装下载、其他发行版/Docker、真实账户/凭据、主机制代码及外发保持原范围。
