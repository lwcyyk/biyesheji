# R6阶段B实际执行清单

2026-11-10。许可EXPLICITLY_AUTHORIZED；运行结果RESOURCE_GATE_FAILED；F1/F4均UNRUN_RESOURCE_GATE。

实际命令两次均为：在D:/毕业设计/DCL-R6-isolated-verification/batch01运行固定Python3.14.0的 `-I -B src/guard.py --plan inputs/batch01.json --qualify-first`，输出分别保存raw/launch.s1.txt、launch.s2.txt。v1源版本先锁定，失败后保留并生成v2；BATCH_STATE起点/deadline及visits.bin持续沿用。

|对象|实际执行/状态|
|---|---|
|guard.py|2次；首轮初始化错误87、退出2；v2完成3项校准后以资源失败退出2|
|guard_probe.py|normal/counter/memory共3次；分别退出0；memory的资格判据失败|
|guard.py watchdog|v2启动1次，收到正常停止事件后退出0；尚未校准强制墙钟/父失效分支|
|run_batch.py、F1、F4、compare模型对照|未启动/未执行|
|计数/时间|27次校准收费；118.7340827秒至v2退出|
|峰值|连续OS Job提交峰值145354752字节；树WS采样下界97099776字节，精确聚合峰值null|

八程序源码hash、v1/v2锁、每probe命令/退出/内存、统一账和失败清单均在隔离目录。初版API设置失败早于结构化资源采集，首轮峰值/PID缺测明确记录。BATCH.2.json中配置推导的enforced_tree_ws_upper_bound不是已校准保证。

[机器结果](evidence/stage_B/RUN_RESULTS.json)、[资源报告](R6_RESOURCE_CALIBRATION_REPORT.md)、[当前F1](R6_F1_RESULTS.md)、[当前F4](R6_F4_RESULTS.md)为正式阶段B入口。以下为阶段A计划历史。

---
# R6执行清单与真实状态

2026-11-10。`status=UNRUN_PERMISSION`。此文件是执行准入清单，当前无模型/参考执行日志和模型源码。

## 1. 已执行的阶段A操作

|类型|命令/对象|实际结果|证据|
|---|---|---|---|
|TOOL_VERSION_ONLY|已存在Corretto java.exe `-version`|1.8.0_502，64位|TOOL_INVENTORY.json，非TLC运行|
|TOOL_VERSION_ONLY|已存在Python314 python.exe `--version`|3.14.0|TOOL_INVENTORY.json，非枚举运行|
|ADMIN_CHECK|R5输出锁/历史、文件/JSON/链接/包与runtime摘要|仅工件完整性/路径检查|evidence/各锁与DELIVERY_CHECK.json|
|SOURCE_READ|官方TLA+/Job文档、既有研究与源码|当前工具/资源口径与模型对应审查|evidence/web/web01.json、R6_SOURCE_INDEX.json|

## 2. 待授权批次

批次ID：拟议R6-batch01；写入根：`D:/毕业设计/DCL-R6-isolated-verification/batch01`；来源版本：R6本组非可执行规格及其SHA-256锁，未来模型程序另锁代码版本。当前源码commit/model digest/模型命令实际退出码/实际访问/耗时/峰值均null。不能把行政脚本的退出码当作模型退出码。

F1顺序为SMOKE、BRANCH、必要变异、CHAIN/KEY；F4顺序为固定夹具、独立参考/阈值比较/压缩校准、G64及变异。每个子任务保存：工具/可执行摘要、模型及输入摘要、参数、确定性排序/随机种子null、初态、声明域、访问/不同/生成状态数、批内累计收费上界、执行时间、Job与working-set峰值、结果、首个完整反例及所有分支指纹、退出状态、完整命令、代码版本。每个未完成子任务明确首个未完成输入。

## 3. 未来目录与文件（当前未创建）

|目录|范围|
|---|---|
|src/|八个申请中的程序，未来版本v1/v2变更用版本目录/哈希保留|
|inputs/|batch01资源/顺序计划，F1各族参数/初态，F4夹具与G64固定数据、mutant注册|
|raw/|各进程stdout/stderr、预算事件、Job/峰值/时钟与退出记录|
|reports/|baseline/变异/参考对照、失败分类、完整轨迹和证据重放|
|versions/|每次首次失败/修订的源码及输入锁；不覆盖失败|
|AUTHORIZATION_RECEIPT.json / BATCH_LOCK.json|实际授权范围、父指令、工具/代码/输入/资源摘要|

当前研究目录只含本轮Markdown/行政JSON/任务副本；没有在报告内嵌可执行模型代码，也没有把预期数值伪装为CSV运行结果。

## 4. 结果状态约束

许可缺失：UNRUN_PERMISSION。资源资格失败：UNRUN_RESOURCE_GUARD（已获许的校准可有真实记录，模型仍未启动）。达到单批任一界：INCONCLUSIVE_LIMIT。输入/域不完整：INVALID_MODEL或ABSTRACTION_GAP/INCONCLUSIVE_DOMAIN。完整有界检查：PASS_BOUNDED。变异可达反例：COUNTEREXAMPLE_FOUND，按其预期/非预期分类。

检查门不把“mutant有反例”改写成“正协议有缺陷”；正模型反例先核是否满足全部假设及模型对应。F4两实现不一致时没有默认真值，先封存两边输入/版本/见证，逐步骤定位。LEVEL-3仅在实际独立逻辑实现检查后授予；LEVEL-4一般证明与LEVEL-5外审仍需各自证据。
