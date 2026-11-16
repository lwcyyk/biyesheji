# GATE-LEDGER-ANOMALY用例

Material Passport：B09-AdmissionFix-static-1/r1；STATIC_IMPLEMENTED；全部测试UNRUN。

新增第18项门是一个聚合用例，包含18个内部specimen：1个健康正控制、13个异常原件、4个故意错误行为mutant。所有字节在未来Root RANGE审核期间从冻结合同构造，写入新建Root私有目录；正式活账和历史账均排除在写入目标之外。用例正文没有独立CLI执行入口。

|类别|实际可表达的冻结输入|原始检查责任|
|---|---|---|
|A1–A4|缺COMMITTED、重复COMMITTED、PREP/COM配对字段冲突、提交先于准备|native记录配对与顺序|
|B1|counter.used超过cap|累计容量|
|C1–C4|range请求batch错误、记录boot错误、Root快照执行锁错误、journal描述符指向外部路径|当前身份及文件集合|
|D1–D4|journal末行截断、实际字节与已持有摘要不符、范围序列空洞、intent缺失|完整性与持久原件|

原生格式包含before/after/amount/cap/request/protocol/boot，transaction_id和逐行checksum字段在现有格式中缺席。A3使用这些真实字段定义配对身份；D2使用Root快照持有的文件SHA，记录摘要责任在原件封套层落实。当前全局单信用记录的batch/执行锁由当前路径和Root快照绑定，精确range请求还直接核其batch、boot、T0及来源。

局部发放超过持久预留由既有S1/S3/S4覆盖；实际访问超过局部信用由S9覆盖；关闭后继续使用由S8与C12状态拒绝覆盖。覆盖层次和原有局部合成账语义保持，新增用例聚焦全局格式及资格读路径。

实际资源门使用ledger_gate.evaluate，调用独立range_evidence.check_global_ledger，并前后核文件集合、字节摘要和当前绑定。该生产路径接收实际文件与当前绑定，输入中没有expected=false授权字段。健康账结果为ACCEPT_LEDGER_HEALTHY，异常账结果为REJECT_LEDGER_ANOMALY并保存真实原因。

ledger_gate_oracle另行解析counter/journal/intent及封套，独立计算容量、配对、身份、连续性与摘要问题；其导入仅含标准库。它读取实际字节和subject实际decision，检查故障真正存在、拒绝真正发生以及mutant是否真实错误接纳。

四个mutant分别吞掉缺COMMIT、累计超额、batch错误、摘要错误的拒绝结果，改变隔离subject的实际接纳行为；生产门始终调用完整evaluate，mutant参数只存在冻结测试驱动。原始参考必须发现错误接纳才能记录MUTATION_DETECTED。当前这些实际结果统一UNRUN。

计费为1＋18×32＋18初次总审＋2×18 Root资格重算=631，专项硬限640。既有17项循环新增一项再收费1；全部共用原RANGE与全批账。case数、输入摘要、原件摘要、当批身份、实际decision/reason、fault_exercised和独立结果进入Root保护资格摘要，缺件或结果不符立即失败。

[完整输入](evidence/SOURCE_AFTER/inputs/ledger_gate_contract.json) · [subject与真实门](evidence/SOURCE_AFTER/src/ledger_gate.py) · [独立原始oracle](evidence/SOURCE_AFTER/src/ledger_gate_oracle.py) · [隔离驱动](evidence/SOURCE_AFTER/src/ledger_gate_regression.py)。
