# 逐文件容量证书

源码给出13个证据文件对象，其中12个由Runner创建，approval由受信准备步骤创建并供Runner只读。State.write、State.checkpoint及Sink的创建/写入/flush/close构成6处底层写入生命周期；D24生产者通过ProjectionFile进入State.write。完整字段见 `R34_EVIDENCE_FILE_MANIFEST.json`。

证书中U(file)指完整必需内容的序列化上界；allocated_cap指写入时拒绝超额的份额。两者各有来源。UNBOUNDED表示生产接口缺少可核验的预算相关界，未断言所有构造字符串均由冻结68实际产生。完整冻结执行的最大值未建立时另列UNKNOWN。

| 对象 | 分配额度 | 完整序列化上界 | 证书状态 |
|---|---:|---|---|
| F01 RUN_APPROVAL_RECEIPT.json | 8192 | 8192 | CONDITIONAL |
| F02 SUITE_INVOCATION_01.json | 8192 | 681 | PROVED |
| F03 TEST_RUNS.json | 65536 | UNBOUNDED | UNBOUNDED |
| F04 COMMAND_stdout.log | 65536 | UNBOUNDED | UNBOUNDED |
| F05 COMMAND_stderr.log | 65536 | UNBOUNDED | UNBOUNDED |
| F06 RUN_START.json | 16384 | UNKNOWN | CONDITIONAL |
| F07 stdout.log | 65536 | UNBOUNDED | UNBOUNDED |
| F08 EARLY_FAILURE.json | 1048576 | UNBOUNDED | UNBOUNDED |
| F09 RESULTS.json | 262144 | UNBOUNDED | UNBOUNDED |
| F10 MODULE_ORIGINS.json | 262144 | UNBOUNDED | UNBOUNDED |
| F11 RESOURCE_LEDGER.json | 131072 | UNBOUNDED | UNBOUNDED |
| F12 test_metadata.json | 1032 | 1032 | CONDITIONAL |
| F13 test_request.json | 287 | 287 | CONDITIONAL |

调用槽文件取得681字节上界：固定12项argv、最长32字符UTC、64位十六进制SHA、固定suite与max_runs，按真实canonical参数加LF计算。D24原始数据为1032/287字节，依赖冻结生产者/fixture与golden内容身份合同；错误数据走拒绝分支。approval的8192字节依赖明确准备合同并由controls再次检查。RUN_START仍包含没有独立长度校验的运行时文本，故其完整证书为条件性。

三份最终JSON分别审查如下，Source Schema已从AST提取到 `sources/STRING_FLOW_AND_SCHEMA_MAP.json`。

| 文件 | 内层字段与数组 | 动态内容责任 | 完整字节界 |
|---|---|---|---|
| RESULTS | 27字段；cases68、details正常至多68、工程42、fixture10、control_pins12 | case.detail、details内部、错误链、嵌入资源与来源信息 | UNBOUNDED接口／实际冻结上界UNKNOWN |
| MODULE_ORIGINS | 9字段；snapshot至多8、fixture10、记录数≤ΣM_s | inventory计数、模块名、file/spec/loader字段及拒绝详情 | UNBOUNDED接口／实际冻结上界UNKNOWN |
| RESOURCE_LEDGER | 13字段；cache不同源至多422，phase5、test ID68 | cache尝试计数宽度、denials、错误全文和traceback | UNBOUNDED接口／实际冻结上界UNKNOWN |

框架错误数组的条件数量界可拆为29个failure字典和160条close错误repr；每条文本长度仍缺界。该数量推导依赖标准非重入诊断，记录在 `sources/COUNT_BOUND_DERIVATION.json`。cache422来自442个已锁源中422份.py的可逆单一缓存映射，文件目录数量也无法直接界定sys.modules库存。

控制流给出snapshot≤8、固定两个包装模块的额外观测≤16，以及journal尝试次数≤128+2ΣM_s。M_s没有源级界，记录总数及单条value尺寸继续受限。历史609条逐条验链并无损重编码，实际817454字节，只覆盖这些确定输入。

JSON参数为sort_keys、ensure_ascii=True、紧凑分隔、allow_nan=False。n个Python字符的JSON字符串保守界为12n+2字节；日志先按UTF8编码计数。若raw长度n、zlib长度z，则encoded_payload精确长度为147+digits(n)-1+4ceil(z/3)；普通压缩产物再加48字节外框/LF，receipt按FAILED或FINALIZED分别加97/99字节。未使用历史压缩率作为最坏保证。

明确的局部限制也已保留：deny_read.cause_repr在redact后截取1024字符，ASCII转义界12290字节；它不约束其他路径/错误字段。源码中 `State.failure:298` 的完整traceback、origins_snapshot:708/723的repr、close_connections的repr以及Results格式化详情均无相应长度界。完整流转与最小约束位置逐字段列于JSON。
