# PT/PF及RA32兼容回归

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**TR-D4=PASS_DYNAMIC（本批冻结合成范围）。** PT64=55 PASS＋9变异检出，PF48=40 PASS＋8变异检出。当前源码/运行时/身份重新取证，未借用旧112项资格。

PT预算1→1090，消费1089；PF1090→1907，消费817。新增RA32在TR之后执行，24 PASS＋8变异检出，预算2588→3133消费545。新RA32范围RA-SIMULATION/1，包/路径/Build-ID/预加载/新旧混用/跨batch/漂移决策为合成输入，实际系统库没有被破坏。

四套总184job＝151safe＋33mutant，均由原生独立oracle接受。Root资格绑定源/contract/checker/raw/input哈希，完整集合和计数匹配。数据审查没有修改allowed_violations或将预期填充为结果。

此前PT/PF历史通过原样保留；本批兼容通过只覆盖当前四个版本化模型/清单，无法替代未来版本fresh资格和完整资源链。

[全部实际原件定位](evidence/TEST_CASE_RESULTS.json) · [计费一致性](evidence/BUDGET_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
