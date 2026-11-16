# batch09 F1有界机器检查状态

Material Passport：DCL-R6-batch09；2026-11-12；F1=UNRUN_RESOURCE_GATE。

RESOURCE_GATE_PASS尚未取得，F1入口、枚举、变异及重放启动数均0。INV1 UniqueHistory、INV2 UniqueChild、INV3 SealSafety、INV4 RHOConservation、INV5 BudgetConservation、INV6 OriginPreservation、INV7 ReadySeparation、INV8 CurrentAuthority的本轮正式机器结论均为UNRUN，PASS_BOUNDED=[]。

冻结f1_model.py/f1_check.py及runner字节核验通过。runner实际清单为SMOKE_UNKNOWN、RELEASE_EMPTY、BRANCH_UNKNOWN、POST_TAKEOVER_B、CHAIN、RECOVERY_ABORT六个正模型子任务，九个指定mutant，以及KEY_AUTH_TABLE的72个认证谓词组合；各子任务精确输入由冻结runner生成。它们属于原规格的显式有限子族，范围按实际输入和覆盖报告授予。KEY谓词表本身只覆盖有限认证判断。

六个baseline各12,000 BFS访问软片、九个mutant各8,000软片，配置容量合计144,000；KEY收费72，反例重放另行共账。该配置与访问、覆盖、域溢出、耗时等真实运行统计分别登记，当前真实统计均null。INCONCLUSIVE_LIMIT/INCONCLUSIVE_DOMAIN/未命中变异保持相应边界，只有完整穷尽的实际指定范围可取得PASS_BOUNDED。

模型源码保持冻结，首个协议反例为0条。D1-PBFT-SEAL/1.1条件结论、强G覆盖、严格分离实例0及机制实施门CLOSED保持。

[源核验](evidence/FROZEN_HASH_CHECK.json)；[原始规格索引](evidence/CONTEXT_SOURCE_INDEX.json)；[最终裁决](BATCH09_FINAL_DECISION.md)。
