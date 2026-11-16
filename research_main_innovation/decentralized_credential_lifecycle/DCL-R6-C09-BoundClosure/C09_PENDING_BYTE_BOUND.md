# 单条编码、总量与配额合同

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


现行event没有显式单行字节检查。对固定原生调用点，字段为封闭schema，pid/ticks/clock/boot取受信ABI值；原生PENDING行不含task_id、自由错误文本、traceback、raw systemd返回或resources大对象。

|参数|宽度假设|来源/证明边界|
|---|---:|---|
|batch_id、mode|7、27字节|固定ASCII身份及C09可达scope；新身份超长须重算|
|boot UUID、各hash|36、64字节|kernel UUID与SHA-256 hex|
|revision|1字符|冻结进度最多6；PENDING保持4|
|PID、start_ticks、utc_ns|10、20、20字符|pid_t32、proc计数u64、CPython时钟i64的明确ABI假设|
|JSON binary64数值|25字符|17位有效数值与符号/小数/指数的保守编码界|
|witness退出值|11字符|保守带符号整数退出值；PENDING固定null|

compact sorted JSON默认ensure_ascii=True，当前字符串均白名单ASCII，不产生额外转义；每行计入1 LF。通用Unicode扩展若获准，应另计BMP/非BMP转义（每code point最多12个ASCII字节），当前1322界不自动覆盖。

序列化骨架加上述数值宽度得到：PENDING≤1298、任意分类行≤1322、stage≤948、ACK≤1028字节。该结果为**CONDITIONAL_PROVED**，条件为固定调用者/schema/命名及ABI宽度；源码没有逐字段range/digit/byte validator，任意外加Root调用或未知ABI不属于该证明。

现行总量B_pending=ΣL_i，N_pending缺上界，故总量仍UNRESOLVED。27144字节/最大实测行1211只属于历史，未用平均值或历史峰值推最坏界。

独立待批配额草案：256次分类尝试，成功路径最多255条PENDING加1条终态分类；失败路径允许256条完整PENDING后立即关闭。所有已计算分类均保留raw facts，再计6个stage＋1ACK，主日志最多263行。256来自已使用的native-review块尺度，作为新的独立政策额度；它既非状态机隐含上界，也不挪用旧MR的256额度。

记录实际类型上界：max(256×1298,255×1298＋1322)＋6×948＋1028=339028字节。为分类前预扣最坏槽位，合同按256×1322＋6×948＋1028=345148字节预留，不退还未用字节；sidecar≤956、固定失败摘要≤334，稳定对象合计≤346438；两份cursor失败staging和一份emergency失败staging再计≤2246，全部配额相关保留对象≤348684。cursor中的reserved/debited字段不冒充实际写入数量。

额度共享单一batch/boot/handoff绑定；Receiver独占分类额度，Sender/恢复stage与ACK类别各有固定次数；全部原生生产者共用总字节界。预付应在C09控制器/ready marker/counter冻结之前完成，之后只更新独立Root保护cursor，全球R/ACK counter保持。

追加前先校验字段类型/长度与身份/截止/终态，持久预扣一次完整槽位，再写原始行/fsync；模糊持久化立即停止并保留原件，余额不退、缺/错配cursor不重建。第256次仍PENDING时，先完整保存该条facts/PENDING，再写固定错误码摘要并请求关闭；禁止第257次分类。摘要不会替换已计算的原始观察。耗尽表示资源/观察限额，不构成协议反例或交接PASS。

任何有限次数可能在父协调者获CPU前被合法快速轮询耗尽，故该政策有明确活性代价，历史17条只提供一个可行观测。cursor/锁序/首错/崩溃恢复和新字段校验的最小实施仍需新授权与静态接线审查。

[单行代数与骨架](evidence/NATIVE_RECORD_BYTE_ALGEBRA.json) · [具体待批配额](proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json)。

表示上界与工程上界分别登记：附加off_t64假设给单原生日志B≤2^63−1、完整原件集粗界4450×(2^63−1)=41044005564003752341150字节。这些巨大表示界没有满足32MiB/1GiB/期限的证明作用；当前缺的是可用于准入的数值化生成与处理合同。

[表示边界与量词范围](evidence/REPRESENTATION_LIMIT_CAVEAT.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
