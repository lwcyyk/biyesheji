# 15项剩余责任的终局分类

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

本轮结束同一冻结范围的静态审计。**当前合同CURRENT_CONTRACT_UNSAT；后续采用CONTRACT_REVISION_REQUIRED。** 不再以相同源/输入重复打开15项清单。新用户决定、量化TCB材料、批准后的具体diff或新证据可以定义新的审查输入。

|缺口|实际变量/范围|最终分类|最小处置|
|---|---|---|---|
|G01|O_native_pending；current no record quota; draft256/263 only|COUNTEREXAMPLE_IN_FROZEN_SCOPE|approve native observation quota and encoded schema; stop after full256th PENDING|
|G02|H;R_budget；H<=52, core<=212; STOP one path|REQUIRES_NEW_CONTRACT|TCB diagnostic wire profile or separately approved bounded control/raw-acquisition policy|
|G03|E;sumV；stop_tree<=23; stop_result path<=23|REQUIRES_NEW_CONTRACT|pinned kernel/file-error wire profiles; producer size/read limits and exact failure/UNKNOWN semantics|
|G04|R_MR;T;B；abort<=16; first path1; cleanup rows<=16|CONDITIONAL_ON_EXISTING_TCB|bind complete reachable exception catalogue/T_max or approve typed finite error profile|
|G05|SEAL_ERROR_repr;helper_output；<=4 SEAL_ERROR writes; one path|REQUIRES_NEW_CONTRACT|bound helper response acquisition and persisted diagnostic bytes; overflow cannot claim complete evidence|
|G06|terminal_report；exclusive saved review<=1; reader capped roots4MiB|REQUIRES_NEW_CONTRACT|typed terminal output composition/byte envelope preserving required raw provenance|
|G07|timing_error;stdout/stderr;traceback；finite file slots;timing first_samples<=8 per key|REQUIRES_NEW_CONTRACT|raw stream/acquisition/per-error/aggregate bounds plus explicit incomplete/UNKNOWN policy|
|G08|per-record-to-total aggregation；fixed jobs and source caps; old4450 envelope|REQUIRES_NEW_CONTRACT|versioned aggregate reservation/acceptance contract and producer/exception-staging union|
|G09|journal_total_bytes；global visits<=1m; candidate conditional471876988|REQUIRES_NEW_CONTRACT|align generated journal byte/row limits with mandatory validators and preserve unspent/ambiguous semantics|
|G10|model_state/trace/strategy_wire；fixed jobs and budget; neighbour generation/serialization constants not certified|UNRESOLVED_WITH_EXACT_REASON|frozen model wire profile with per-output/trace/serialization limits and incomplete-on-limit semantics; keep numeric fields null|
|G11|raw/native/admin bytes;memory;FD；old4450/4451/4452 conditional; current257/256 unsatisfiable for full target|REQUIRES_NEW_CONTRACT|versioned counts only after delta; derived raw/manifest/ZIP/working-set/FD limits before effective capacity|
|G12|ambient_roles/args;admin views；samples<=128; P5 gives roles>=5 despite slice<=4|COUNTEREXAMPLE_IN_FROZEN_SCOPE|choose global environment/input envelope or equivalent scoped discovery, preserving all genuine exit checks|
|G13|new implementation/test/oracle deltas；current新增运行producer0; future delta unknown|OUTSIDE_FROZEN_SCOPE|explicit maintenance scope + concrete diff/set/byte/visit delta review; no same-scope repeat audit|
|G14|syscall/scheduler/IO_latency；existing deadlines are attempts/refusal guards, not success WCET|UNRESOLVED_WITH_EXACT_REASON|approve environment latency envelope/measurement objective or preserve timeout/UNKNOWN; strict guarantee remains unproved|
|G15|host finalization error/embedded audit；one extra error path, outside admin ZIP preimage|REQUIRES_NEW_CONTRACT|post-seal control/raw/error envelope, explicit preimage scope and aggregate limit|


[RESIDUAL_15_GAP_MATRIX.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/RESIDUAL_15_GAP_MATRIX.json)为每项保留全部要求属性：gap_id、producer、source、unresolved_variable、input_domain、occurrence_bound、byte_bound、trusted_assumption、existing_evidence、counterexample、minimum_constraint和唯一verdict。原编号G01–G15一一保持。

具体收敛：H已由角色图给出52，关闭核心最多212次生产尝试；MR固定调用reason的JSON token≤38。T/B/E/V仍依赖量化TCB/kernel profile，其中source-owned异常类名和健康预算映射已有子界。G12得到P5环境输入反例，目标是slice TasksMax4无法约束全局发现角色数；G13归入尚未存在的新实施/测试域，不再通过重读旧代码填造Δ。

stderr_m及一般API重复族E_n继续属于域外/未证明pinned可达性的接口风险。上界乘积超过32MiB没有被登记为实际超限实例；内存/物理文件表示空间也未被用来填应用层cap。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
