# 运行时适配证据索引

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

|主题|工件|
|---|---|
|总裁决|[FINAL_DECISION](FINAL_DECISION.md)、[机器结果](evidence/STATIC_RESULT.json)|
|授权与门|[原文](evidence/TASK_REQUEST.txt)、[SCOPE_BOUNDARY](SCOPE_BOUNDARY.md)|
|版本/归属/完整性|[DISCOVERY](evidence/RUNTIME_DISCOVERY.json)、evidence/native_queries原始双流|
|来源/签名/索引|[审计](evidence/PROVENANCE_AUDIT.json)、[来源决定](evidence/PROVENANCE_DECISION.json)、evidence/provenance原InRelease/keyring/stanza/目录/日志|
|当前ELF/旧包/索引保存|[导出锁](evidence/PLATFORM_EXPORT.json)、evidence/platform_snapshot|
|ELF/ABI|[完整图](evidence/ELF_ABI_AUDIT.json)、[初图](evidence/ELF_ABI_AUDIT_INITIAL.json)、[旧新版本](evidence/OLD_NEW_SYMBOL_COMPARISON.json)、evidence/elf_raw与old_new_abi|
|配置与fresh条件|[最终平台](evidence/FINAL_PLATFORM_AUDIT.json)、[实际文件读取条件](evidence/MATCHER_FILE_ACCESS.json)|
|pin与源码差异|[3项pin](evidence/RUNTIME_PIN_DIFF.json)、[完整diff](evidence/FULL_DIFF.patch)、[前后SHA](evidence/FILE_DIFF_INDEX.json)|
|静态与保护|[20断言/3探针](evidence/SYNTAX_AND_IDENTITY_CONTROL_CHECK.json)、[13字节/70成员保持](evidence/PROTECTED_SEMANTICS_CHECK.json)、[导入图](evidence/IMPORT_GRAPH.json)|
|RA32/资源|[静态矩阵](evidence/RUNTIME_REGRESSION_STATIC_CHECK.json)、[预算重算](evidence/RESOURCE_BOUND_RECALCULATION.json)|
|新冻结与申请|[64项锁](evidence/STATIC_WORKSPACE_LOCK.json)、[绑定核验](evidence/FINAL_BINDING_REVIEW.json)、[未批准模板](evidence/TR_A2_AUTHORIZATION_TEMPLATE.json)|
|历史/交付|[旧包核验](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[8239基线](evidence/BASELINE_LOCK.json)、[历史保持](evidence/HISTORY_PROTECTION_CHECK.json)、[最终校验](evidence/DELIVERY_CHECK.json)|

所有业务套件和新RuntimeAdapt匹配器的原生服务调用尚未执行，Root只读进程映射不借作新batch14资格。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
