# 其他必要生产者的终局处理

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

本报告只处理G04–G12/G15已有责任。**CONTRACT_REVISION_REQUIRED**：固定生产次数、读取接受cap与可用的生成字节/内存上界分别维护；域外输入不冒充冻结漏洞。

|生产者|次数/固定结构|来源与剩余最小合同|
|---|---|---|
|MR first/cleanup|abort≤16，attempt行≤16；错误notes有限；首错固定路径|R_MR已闭合；T/B由pinned错误profile实例化，随后使用既有逐字段式|
|payload timing|每key最多8 first_samples＋last，固定调用labels来自锁定程序|repr(error)文本、计数宽度与全部key集合需要量化wire profile；样本数不会限制每样本文本|
|stdout/stderr|固定服务/helper/host stream槽位；一次错误逐层展开，无自动无限重启|已收到raw保持；helper/解释器实际输出的字节/acquisition/总量必须由合同决定|
|TerminalRead|每原JSON接受4MiB，固定元数据；保存native review为exclusive一次|嵌入raw树与metadata组成的输出wire包络；读者接受cap不能自动当writer cap|
|readiness/RootIPC/MR/S1–S9|固定jobs/actor，现有单记录cap、旧4450集合|78905344/50331648等cap乘积仅为上界；聚合超限判据、全部异常/staging仍需统一|
|journals|visit≤1m、固定range任务；conditional字节模型已有|生成字节/行数应与所有validator接受条件统一；上界大于32MiB不证明实际达到该值|
|F1/F4输出|固定输入、visit slices和任务数，无本轮模型执行|邻居生成/trace/strategy/report编码和峰值对象常数未认证；精确输出profile字段留null|
|native/行政构建|once流程、现有archive/raw完整性检查|新总量、单成员、manifest、压缩膨胀、heap/FD/IO需审批前闭合|
|host最终错误|一次finalization-error，可嵌入preserved audit|它位于admin ZIP前像之外，仍需单独保留字节；不并入4452 runtime快照原件数|

JSON重编码有一项可终结的子结论：普通成功解析JSON树无自定义hook/环，compact ensure_ascii=True重编码≤25×原输入字节。字符串每code point≤12输出字节，float≤25，integer十进制不扩大，容器/键从不重叠的原token逐项求和。Terminal返回最多4个可能的raw根（closed、stop、waitpid、SEAL_ERROR），各4MiB，故这些嵌入根的保守贡献≤419430400 bytes，再加固定/已验证metadata的K。此为CONDITIONAL_BOUND，未证明全部极值同时可达，也不证明输出适配32MiB、heap足够或整个报告最终总值。见[TERMINAL_REENCODING_LEMMA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/TERMINAL_REENCODING_LEMMA.json)。

G12有一个冻结环境域内的具体反例，目标为“slice TasksMax4推出admin发现角色≤4”。令5个不同UID的普通进程在当前slice之外运行，实际执行无关程序，argv包含当前source/guard.py、--batch-root及ROOT；在合法preflight后、行政扫描前出现。[src/startup_lifecycle.py:392](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/startup_lifecycle.py:392)的role分支只匹配argv，不校验该分支的UID或InvocationID，因此roles≥5，同时当前slice可以为0。它们不写ROOT、不调用DCL函数、不修改TCB。返回会如实defer/UNKNOWN，未出现漏准入PASS。反例详情与环境前提见[AMBIENT_PROCESS_COUNTEREXAMPLE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/AMBIENT_PROCESS_COUNTEREXAMPLE.json)。

P_n说明全局/proc元数据需要自己的数量/argv/错误界，或正式批准等价的known-identity/current-cgroup发现合同；后者必须保留真实逃逸角色检查。当前旧writer域没有冻结整个主机的无关进程。若新合同另加全主机quiescence/no-lookalike假设，该更强域需要独立标明。

错误传播没有新增一个自动无限写循环：固定异常包装器按16/23/7/4包络展开；STOP可被覆盖，close_attempt可追加，native失败的SEAL_ERROR/处置走后续raw/admin层，行政失败收据在包前像外。一般API族E_n和stderr_m的pinned实际可达性继续与冻结调用图分开。源/输入不变时，这些责任不再重复审计，下一输入限定为合同决定或量化材料。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
