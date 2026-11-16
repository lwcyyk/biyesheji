# R6工具链、资源门与最小专项授权

2026-11-10。当前UNRUN_PERMISSION。许可缺口来自用户R6任务§3阶段B：“需要独立的明确授权，才允许”创建模型/参考、执行枚举/变异及写机器执行记录；§14要求缺许可时完成准备并提出最小申请。当前任务本身仅启动阶段A。[原任务副本](evidence/TASK_REQUEST.txt)、[许可核对](evidence/PERMISSION_AUDIT.json)可复查。

## 1. 实际本地核验

|对象|真实观察|范围|
|---|---|---|
|OS/PowerShell|Windows NT10.0.26200；PowerShell7.6.5|元数据读取|
|Java|Amazon Corretto1.8.0_502，64位；绝对路径见TOOL_INVENTORY|实际执行`java -version`一次，非模型运行|
|Python|`C:/Program Files/Python314/python.exe`，3.14.0|实际执行`--version`一次；WindowsApps python3别名未使用|
|TLC/PlusCal/Apalache|PATH及已检查的Program Files、VS Code扩展、Downloads、research_main_innovation目录未找到对应工具|已查范围未发现，不声称整个磁盘均无文件；不存在的常用目录单列|
|资源监督|已读主工程源未找到可直接复用且已验收的Job/硬限监督器；本轮未创建/校准|RESOURCE_GUARD_UNQUALIFIED|

两个实际runtime exe的SHA-256分别锁于[TOOL_INVENTORY.json](evidence/TOOL_INVENTORY.json)；没有通过文件版本猜测Python运行版本。

[官方TLA+当前说明](https://github.com/tlaplus/tlaplus)要求Java11+，并给出TLC CLI；现有确认的Java8不满足该当前工具链前提。已读旧tag v1.7.4的README未认证其二进制兼容性，不将它当作已安装可运行工具。若未来选择TLC，需单独批准取得固定JAR和兼容JDK、核官方来源/版本/哈希、审状态计数接口；本轮依赖下载0。

## 2. 最小离线方案

主申请采用现有Python3.14.0与标准库，创建明确的F1显式状态检查和两条独立F4语义路径。该方案不安装TLC/JDK、包管理依赖、浏览器或服务。结果如获执行仅为自编检查器的PASS_BOUNDED，工具自审/独立monitors、变异命中及F4交叉参考是必需证据；TLC交叉实现仍可作为以后独立范围。

未来隔离根：`D:/毕业设计/DCL-R6-isolated-verification/batch01`。创建前解析路径及父目录，若已有不符锁的工件则保留并换新批次需重新明确，禁止覆盖历史。冻结研究目录/主系统只读；研究目录仅追加审查/结果索引和经授权的证据投影。

未来拟创建八个程序：`src/guard.py`（含独立watchdog模式）、`src/guard_probe.py`、`src/run_batch.py`、`src/f1_model.py`、`src/f1_check.py`、`src/f4_dp.py`、`src/f4_reference.py`、`src/compare.py`。模型与checker分别承载业务转换/独立监视器；F4两实现不互相导入业务语义。行政预算/日志接口可共用。此列表是请求写入范围，当前文件均不存在。

## 3. 硬资源资格门

单批全体上限为1,000,000累计访问、1800秒墙钟、4GiB进程树峰值内存，校准/失败/重跑也计入。进程和访问规则必须在进入正式模型前验收。

|维度|拟采用机制与资格要求|
|---|---|
|进程树封闭|Windows Job先配置，再创建暂停子进程、分配Job与限制、最后Resume；禁breakaway及WMI启动；限制同时进程数，所有校准子孙也在Job内。嵌套Job/句柄权限不满足即停止，不绕开宿主限制|
|提交内存|Job-wide committed memory≤4GiB，超限失败/终止；记录OS Job统计和每进程统计|
|峰值工作集|另需能强制的每进程硬working-set限额与进程数/角色预算，其和≤4GiB，含controller/watchdog/worker/校准子孙及预留；所有子进程执行前设置。普通RSS轮询和Java/Python堆上限不足以充任该保证|
|墙钟|单一monotonic起点/绝对deadline，独立watchdog/OS定时等待终止本Job；正常程序也检查deadline，终止/落盘保留余量；不把CPU时间限额当墙钟。失败导致整个Job停止|
|访问|集中预算服务在处理/展开状态前授不可回收额度；DP缓存调用、参考具体前缀、证据重放及mutant均申请。可批量预留但按保守上界收费，实际数与收费上界分开；崩溃丢失的额度保留占用。未获得额度不能处理下一状态|
|代码/依赖|仅冻结runtime和审查过的本批源码；纯标准库、无worker自行启动未登记进程；行政数据不得改业务语义|

[Windows官方结构说明](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)将JobMemoryLimit定义为job可提交虚拟内存的界；它与总working-set峰值有不同口径。[Job官方说明](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)给出子进程归属、breakaway与终止机制。当前尚无实际校准，不能据文档就登记硬界已生效。

资源资格测试须用小规模、确定上界的探针：额度用尽前阻止下一次处理；短deadline终止等待/子孙；有限小分配触发测试Job限制；拒绝breakaway、父进程故障/句柄关闭与子孙清理；测试和报告不得超过主批总界。任何口径/硬界无法验收，输出UNRUN_RESOURCE_GUARD，仅封存校准记录，F1/F4仍不启动。此时不会自行把4GiB解释成仅堆或仅commit以继续运行。

## 4. 授权后的固定命令计划

工作目录统一为上述隔离根，调用固定绝对路径Python。下列文件尚未创建，命令未执行。

|顺序|未来命令|含义|
|---|---|---|
|0|审核程序/输入/计划并计算SHA-256，写AUTHORIZATION_RECEIPT与BATCH_LOCK|收据绑定本次用户许可、范围、资源和源码/输入版本；预存在许可不能自动复用到不匹配版本|
|1|`"C:/Program Files/Python314/python.exe" -I -B src/guard.py --plan inputs/batch01.json --qualify-first`|单次监督入口，资源门合格后调用批控制；-I隔离环境，-B禁止pycache噪声|
|2|监督器内启动`src/guard_probe.py`的额度/时间/内存/子孙小探针|所有校准共享预算；不合格则批次停在资格报告|
|3|监督器内`src/run_batch.py --phase F1 --plan inputs/batch01.json`|SMOKE→BRANCH基线与mutants→CHAIN/KEY，顺序和子范围在锁定计划固定|
|4|同一监督器/预算下`src/run_batch.py --phase F4 --plan inputs/batch01.json`|夹具→独立参考/DP/压缩→G64及mutants；不重置时间/访问数|
|5|同一批内`src/compare.py --batch reports --replay-witnesses`|对照与重放计入资源；结束后写退出/总预算和工件锁|

可提前结束某扩展子域，将它标INCONCLUSIVE_LIMIT并给剩余额度做下一锁定子任务；不能把未完成范围写PASS。失败后修订代码用新版本保留首个失败，不自动开启第二批。若需要下载TLC、执行F2/F3、Casdoor构建/T1–T4、访问真实账户或外发，另有权限范围，当前申请不包含。

## 5. 最小专项申请

请求批准：仅在上述隔离目录创建八个验证/监督程序及有限输入，使用已有Python、无下载，先进行硬资源校准，合格后按F1→F4执行baseline/已知变异/独立穷举交叉检查，保存输入/源码/命令/反例/资源/退出记录；单批总限额保持100万访问、30分钟和4GiB进程树峰值，超限INCONCLUSIVE_LIMIT，资源门不合格即止于校准。主系统机制实现门继续CLOSED，原生请求/构建/外部发送不在申请内。

当前需要用户单独明确回复后才能创建上述程序。完整阶段A材料已先完成，许可对象为此具体申请范围。
