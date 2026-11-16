# 跨实例承认的信任与攻击边界

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


唯一候选承认类别为：相同受审实现及声明故障模型下，独立A实际观察到的一次原生服务异常处理能力。其事实强度为特定轨迹接受；有限测试不推出所有后续实例都能成功关闭。

TCB继续包含受信kernel/systemd/Root、源码与授权存储、现有包数据库/密钥环及无并发特权更新前提；GNU libc2.39/Ubuntu8.12来源条件与缺独立.deb payload再现原样保留。候选规则限定A/B同boot，关键binary/loader/maps/配置必须由B重新核验。Root恶意伪造与未声明的TCB失效超出原信任模型。

跨namespace的whole-source hash必然可能不同，不能只比较版本名。草案要求精确A/B artifact pair和按AST坐标逐项审阅的namespace字面量映射；所有安全分支、数字界、UID/GID/权限、运行时pin、故障/测试要求必须保持。禁止忽略全部字符串或盲目替换路径。当前approved_pairs=[]，实际等价证明未完成，证书当前不可用。

独立oracle重读原字节，来源靠Root绑定、原始单位实例事件、前后预算及真实退出相关联；生产者自报PASS不构成原生来源。现有archive主体与参考均依赖zipfile，存在共同parser TCB；现有15变异只证明已运行主机夹具，当前规则的攻击测试仍为设计状态。

|攻击|条件|明确拒绝|
|---|---|---|
|old_version_replay|R03/R10/R12|Reject different exact artifact pair, projected security core, rule digest or target lock|
|fake_abnormal_close|R02/R06/R07|Reject claimed FAIL/PASS without current native event and automatic STOP/CLOSED/exits|
|simulation_as_native|R02/R05|Reject MR-SIMULATION/1 or host-shaped data without raw OS provenance|
|wrong_source|R03|Reject uncontrolled normalization, changed guard/operator/constant/call graph or missing pair review|
|wrong_boot_batch|R02/R04/R10|Reject mismatched A identity, different current boot or wrong B target|
|fault_not_triggered|R02/R05|Reject normal exit, wrong status/code/InvocationID/PID or missing matching journal event|
|exit_unconfirmed|R06/R07|Reject missing waitpid/role/current cgroup emptiness facts or caller_exit_pending unclosed|
|fallback_only|R06|Keep FALLBACK_CLEANUP_ONLY/UNKNOWN; reject primary automatic capability class|
|partial_seal|R08/R14|Reject absent member/manifest, byte/hash/type/path mismatch or unresolved archive status|
|shared_checker_error|R07|Disclose same-parser common-mode TCB; require rule independence plus independent raw review. Avoid universal independence claims|
|missing_replaced_file|R14|Reject absent original, wrong digest/path, member set mismatch or forged content-to-identity relation|
|budget_window_transfer|R11|Reject A counter/T0/deadline/receipt used as B current resource facts|
|stale_B_current_state|R04/R11|Reject stale C00/real C09/current supervisor/state regardless of valid A certificate|
|use_nonce_replay|R10/R13|Reject duplicate B activation or a use record outside exact freshly authorized target; no new free window|
|certificate_self_hash_cycle|R09/R10|Reject contract requiring certificate inside its own earlier archive or receipt/use-record mutual hashes|

撤销/新鲜性采用窄范围策略：同boot、单个预声明B、当前直接用户授权固定CA/rule/use_spec摘要和nonce；新版本/新boot/新TCB/新目标需重新审阅。草案没有声称已经部署防回滚注册表或无限期证书缓存。

[逐条攻击矩阵](proposals/ATTACK_REJECTION_MATRIX.json) · [源码对关系约束](proposals/SOURCE_PAIR_REVIEW_REQUIREMENTS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
