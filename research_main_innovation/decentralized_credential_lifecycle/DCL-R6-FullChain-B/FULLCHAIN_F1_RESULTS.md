# F1有界模型检查

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


F1实际执行0，状态UNRUN_RESOURCE_GATE；状态空间访问量、覆盖率、变异检测与反例重放均为null/UNRUN。INV1 UniqueHistory、INV2 UniqueChild、INV3 SealSafety、INV4 RHOConservation、INV5 BudgetConservation、INV6 OriginPreservation、INV7 ReadySeparation、INV8 CurrentAuthority均未授予PASS_BOUNDED。

冻结run_batch按顺序列出6项基线：SMOKE_UNKNOWN、RELEASE_EMPTY、BRANCH_UNKNOWN、POST_TAKEOVER_B、CHAIN、RECOVERY_ABORT；9项mutant：double_child、drop_rho、drop_hist、drop_dedup、stale_cache、reset_budget、ready_confusion、rollback、relabel_origin。每个基线软访问12,000、mutant8,000；实际发现轨迹才使用同预算重放。KEY枚举3×2×2×3×2=72行认证谓词。

模型包含有限Cfg O/C、分支O→C/D、链O→C→E等；每Cfg4成员、f=1及受界应用状态。模型使用静态PBFT提交oracle假设，所获有限性质仍需精确有限域与穷尽证据。本轮仅解析该源码，语义模块导入和状态枚举均0。

五业务源f1_model.py/f1_check.py/compare.py/f4_dp.py/f4_reference.py摘要均与原最终锁相同。资源资格是唯一正式进入条件；当前静态拒绝阻止该链激活。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[冻结runner](evidence/FROZEN_RA_ORIGINALS/src/run_batch.py) · [源码摘要](evidence/SOURCE_LOCK_VERIFICATION.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
