# batch02：F1结果

2026-11-10。Material Passport：MODEL_CHECK_UNRUN。关键资源校准C02失败，正式入口未开放，没有F1进程/模型摘要/反例轨迹。

|性质/输入族|实际状态|
|---|---|
|INV1 UniqueHistory|UNRUN_RESOURCE_GATE|
|INV2 UniqueChild|UNRUN_RESOURCE_GATE|
|INV3 SealSafety|UNRUN_RESOURCE_GATE|
|INV4 RHOConservation|UNRUN_RESOURCE_GATE|
|INV5 BudgetConservation|UNRUN_RESOURCE_GATE|
|INV6 OriginPreservation|UNRUN_RESOURCE_GATE|
|INV7 ReadySeparation|UNRUN_RESOURCE_GATE|
|INV8 CurrentAuthority|UNRUN_RESOURCE_GATE|
|SMOKE/UNKNOWN/BRANCH/POST_TAKEOVER_B/CHAIN/RECOVERY_ABORT/KEY|UNRUN_RESOURCE_GATE|
|九个原mutant及反例重放|UNRUN_RESOURCE_GATE|

Gate B02-3=UNRUN，正式访问0、PASS_BOUNDED为空、协议反例0、变异检测无实际值。未修改五业务文件/域/不变量，D1-PBFT-SEAL/1.1继续冻结。

既有同attempt已发权利的迟到IO/U2、oracle抽象及真实PBFT/nativehandler等边界原样保留，当前资源失败不对这些协议主张给出支持或反证。不存在“未见反例所以通过”的机器结论。
