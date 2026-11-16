# 行政证据合同审计

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


256来自startup_contract.json的admin_max_files，同时由startup_lifecycle.post_exit_export:496–503的逐文件导出计数和host/startup_finalize.finalize再次强制检查。它限制运行原件导出工作量/元数据内存与行政格式容量；独立的32MiB总字节界及30秒alarm保护仍生效。它具有安全与资源边界意义。

256约束作用于导出的运行文件。最终host ZIP另加入10份固定host侧件、4份源锁和1份manifest，因此原配置下行政ZIP总成员上界为271，而非256。TR-A2实际235＋14＋1=250已由两份真实manifest核对。

原代码逐件复制、记录相对路径/字节/摘要，再逐件打包。未发现允许删除必需原件或将完整审计对象视为等价汇总的现行承认规则。相同摘要仅说明内容相同，路径/批次/来源身份仍具有独立证明责任。

本次授权覆盖维护性版本化合同修订；既有合同未附加“256必须另行批准”的独立条款。当前停止上限实装的依据是精确最大必要数量与资源证明缺失，保持本轮明确限制。当前生产源与256硬界原字节保留。

[容量修订提案](proposals/CAPACITY_CONTRACT_REVISION.json) · [真实行政manifest](evidence/ACTUAL_ADMIN_MANIFEST.json) · [实际旧guard AST边界结果](evidence/HOST_ATTEMPT_R2/ACTUAL_FROZEN_CHECKER_RESULTS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
