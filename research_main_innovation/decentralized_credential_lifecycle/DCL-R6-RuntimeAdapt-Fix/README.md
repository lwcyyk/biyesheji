# DCL-R6-RuntimeAdapt-Fix

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

RuntimeAdapt-static-1/r1已静态冻结。GNU libc上游2.39未变，Ubuntu修订8.9→8.12；3项文件身份/包/签名索引与静态ABI必要条件核验完成，基线依赖受信Root/dpkg/keyring条件。

64文件/44程序，原严格摘要守卫保留，新增路径/包/Build-ID/自身映射重查及RA32/8变异。当前业务动态测试0，A2模板未批准，剩余执行身份原子性和完整性能未决。

[最终裁决](FINAL_DECISION.md) · [时间线](RUNTIME_CHANGE_TIMELINE.md) · [包审查](GLIBC_VERSION_AND_PACKAGE_AUDIT.md) · [3 ELF](ELF_THREE_COMPONENT_AUDIT.md) · [来源](RUNTIME_PROVENANCE_ASSESSMENT.md) · [Python ABI](PYTHON_NATIVE_ABI_COMPATIBILITY.md) · [安全矩阵](RUNTIME_SECURITY_IMPACT_MATRIX.md) · [锁精化](RUNTIME_LOCK_REFINEMENT.md) · [负向计划](RUNTIME_NEGATIVE_REGRESSION_PLAN.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [下一申请](NEXT_DYNAMIC_AUTHORIZATION.md) · [证据索引](EVIDENCE_INDEX.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
