# 跨进程授权与H2边界复核

执行与审查日期：2026-11-12（Asia/Shanghai）。证据类型：本对话内知情模型辅助实际离线运行、源码/日志核对；外部独立核验待取得。

F23、F26、T45及X01/X02本轮均实际PASS，登记 **R25_REEXECUTED_VERIFIED**。原R22证据仍以其历史版本单独保留。

## 当前独立进程轨迹

P1：PID106748，FILETIME134389255029067586；P2：PID42776，FILETIME134389255047865131。P1先用A产生一次离线启动效果并完成FINISHED，又消费K至CLAIMED后实际退出73。creator确认其退出后，P2才重新读取。

P2对A与K均返回REPLAY；issuer/source/client/display别名均REPLAY，A效果仍为1。缺slot、截断、broken chain及prepare/initialize读取损坏状态均进入RECOVERY_REQUIRED。两个actor、原始文件和检查见`R25_CROSS_PROCESS_AUDIT.json`。

| 核查 | 当前实际证据 |
|---|---|
| F23 | stale marker、wrong config、wrong origin、unowned、truncated均RECOVERY_REQUIRED；旧epoch STALE_EPOCH；missing授权APPROVAL_REQUIRED；已经运行SINGLE_ACTIVE_CONFLICT |
| F26 | P1退出后P2持久重读A/K，重放和显示别名均拒绝，A效果1 |
| T45 | 已消费与启动成功分开；K已消费但效果0且P1实际退出，P2仍拒绝；失败启动不能重开 |
| F24 | 两个真实竞争者仅一个接纳，当前链一次CLAIMED/STARTED |
| T39/T41 | 继承实际锁句柄及精确owner Event停止均执行PASS，所有worker正常按合同退出 |

| root | 当前持久链 | CLAIMED数 | 最终效果数 |
|---|---|---:|---:|
| cross_A | UNCLAIMED → CLAIMED → STARTED → FINISHED | 1 | 1 |
| cross_K | UNCLAIMED → CLAIMED | 1 | 0 |
| F24 | UNCLAIMED → CLAIMED → STARTED → FINISHED | 1 | 1 |

三条链均逐项核对seq、grant摘要、previous摘要、epoch与允许状态边。K保留CLAIMED，Recover只分类，不回写为未消费。ACK条件是在离线actor中刻意不发送启动成功ACK；本轮没有真实网络丢包实验。

## H2会话门的证据分层

原R16读取门与启动授权分别管理。读取门维持原进程域、指定connection/authorization/epoch/scope合同；其`claimed`、`_SESSION_NAMESPACES`和读取实现源文件摘要保持。LiveContext的P2默认关闭和MAX_SESSION_TOTAL_READS=1也保持。

本轮实际覆盖：T38 Dormant零read/permit并拒绝P2；T43 Recover零SQL/key/decrypt/自动start；F27/F28与T45/T46拒绝issuer重建、旧epoch、第二次Store和重开启动资格；X02拒绝来源别名消费绕过。新runner和pipe补丁没有修改这些协议，也未重新发放读取槽。

本轮真实H2读取次数 **0**。激活后完整读取流程中的一次总量、异常后再读以及完整A1/H1读取矩阵未重跑；其资格保持 **HISTORICAL_VERIFIED（旧运行）+源文件保持**，原68项总体仍为CROSS_VERSION_REGRESSION_EVIDENCE。启动批准的持久跨进程证据不会自动变成读取会话门的新持久性证明。
