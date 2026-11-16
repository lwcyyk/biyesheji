# 源码与输入审查锁

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


静态版本FullChainAdmission-static-1/review-1冻结4个新维护组件和4个合同/执行提案，逐件摘要见[STATIC_REVIEW_LOCK](evidence/STATIC_REVIEW_LOCK.json)。这是一份主机审查锁，runtime_enabled=false；当前没有可激活的新执行锁。

原ra01最终64文件保持，manifest SHA `738eb2982953971f94019b913f6b302808f9b7a8d29e784038e8e6babb50de89`；原execution_lock SHA `691f2503f2db6906552241692db0b27ec6a982a7c738839d99f3cd93f3729da6`。全部旧程序/输入副本保存，旧命令只作为不可复用的历史引用。

新组件：archive_check、archive_oracle、mr_native_entry、mr_native_oracle。实际新增patch与未应用MR guard patch分别保存。原TerminalRead活动/终态policy、预算核心/RootIPC权限/C09/Boot/PreT0/PT/PF/MR分类均通过整文件摘要保持验证。

新admin/native生产N、原生A的batch/source/boot/argv、runtime receipt和nonce均未签发。A的entry属于可审查代码组件；实际集成需源/合同hash绑定、门检查、完整argv和资源证明闭合。B的生命周期规则尚待明确批准，release=false。

[实际新增diff](evidence/ACTUAL_ADDITIONS.patch) · [MR hook提案](evidence/PROPOSED_MR_HOOK.patch) · [原源锁](evidence/SOURCE_BASELINE_LOCK.json) · [执行锁提案](proposals/EXECUTION_LOCK_PROPOSAL.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
