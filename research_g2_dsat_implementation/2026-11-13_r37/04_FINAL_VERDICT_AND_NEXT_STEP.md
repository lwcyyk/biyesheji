# R37最终裁决

**G3部分批准：28组规则获批或限定获批，9组仍需合同修改确认。** 16+12+0+0+9=37，原37组身份全部保留。R37_CONTRACT_APPROVED=false，R37_CONTRACT_PARTIALLY_APPROVED=true，R37_CONTRACT_APPROVAL_PENDING=true。

9组保留的直接依据是R37第七节列出的“原合同要求无损，候选方案采用有损表示”。R36为这些组保留了原完整责任；本轮已使用明确授权批准安全的28组，没有据此扩大原始保真豁免。

G3_BOUNDED_EVIDENCE_CONTRACT_APPROVED=false，G3_BOUNDED_EVIDENCE_CONTRACT_PARTIALLY_APPROVED=true，G3_FULL_APPROVAL_PENDING=true。G1_STORAGE_SAFETY_CONDITIONAL_PROVED、G2_REQUIRED_EVIDENCE_INCOMPLETE和G4_RUNTIME_ORIGIN_ADMISSION_PENDING维持原状态。四门整体仍未通过，D1-B1继续部分实现。

本轮SOURCE_MODIFICATIONS=0，DYNAMIC_TEST_RUNS=0，EXECUTION_AUTHORIZED=false。原42工程、测试/fixture、依赖、历史SOURCE_LOCK和R35禁用命令保持。原运行时身份差异继续待核，历史完整性匹配仅指入场字节/缺失状态与历史材料保持。

## Q1—Q12

| 问题 | 回答 |
|---|---|
| Q1 | 是。原合同有37个唯一ID：16核心组+21 R35组，身份与顺序均匹配，无数量/身份冲突。 |
| Q2 | 16核心L0组及其余原LOSSLESS_MANDATORY组保持完整；9组拟L2的原完整义务也保留，直至另行修改。任何安全/来源/消费/结果/费用事实在重叠容器内仍受L0保护。 |
| Q3 | 3个codec层及满足EQ_REF精确逆变换条件的原引用提案可限定使用。前提为原字节可取得、SHA/locator绑定、重建canonical值与实际原值完全相同，失败则缺证。 |
| Q4 | 当前可批准诚实的失败/不完整诊断显示及其标记规则；9组有损替代原完整责任仍为CONTRACT_CHANGE_REQUIRED。没有把原文降级为足够的完整证据。 |
| Q5 | 原37组没有已批准的L3可省略名单；冗余性未证或安全关键内容保持原完整义务。 |
| Q6 | 已明确原字节/保存字节/字符与转义长度、摘要真实处理范围、未渲染/截断区别及缺证分类。现有Runner是否实现这些语义仍由G2验证。 |
| Q7 | 批准合同中没有安全关键降级；L0优先，来源/结果/已知错误码/费用与消费事实全部保留。当前实现保全缺口仍在，政策批准不构成实现证明。 |
| Q8 | APPROVED16，APPROVED_WITH_RESTRICTIONS12，PENDING0，REJECTED0，CONTRACT_CHANGE_REQUIRED9，总37。未解决的9组属需合同修改类别，仍待另行确认；禁止解释另列不计字段组。 |
| Q9 | 完整G3=false；部分批准=true，FULL_APPROVAL_PENDING=true。缺9组原完整内容向有界L2替代的逐组责任确认。 |
| Q10 | 12条G2义务已建立：日志/格式化前登记原结果、保留多阶段原事实、逐用例详情转移、计数与检查点核对、L0保护头、溢出/UNKNOWN/来源Fail-Closed、有限收尾及owned读/hash截止门等。 |
| Q11 | 保持。G1为2000167B条件上界；G2未闭合/完整容量未证；G4仍为7内容变化+5路径缺失。2MiB/13路径/120秒及旧pin不变。 |
| Q12 | 唯一拟议最小工程任务是申请单Runner的G2原结果先登记、逐用例详情保留及收尾读取截止门修复。仅用已批准L0/无损规则，9个待确认L2不作豁免；本轮只形成规格，源码和测试实施须另行批准。 |

## 合同冻结

合同文件：R37_APPROVED_EVIDENCE_REPRESENTATION_CONTRACT.json。

完整文件SHA：`06230f8639ba3ee6624a766cd202f197221abbf0adb6c083e142ea02c052d235`。
正文规范化SHA：`49a6660d12d1595be34e9374a9dab337dc81f236582e0719d90ed9bf8ebac277`。

两种摘要作用域已经区分，来源均可追溯到当前研究者R37授权与R36原合同。外部独立核验待取得，当前为模型辅助静态逐字段审定。

## 唯一下一项工程申请

申请仅修改 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py` 的G2最小保全修复：先登记原结果再进行可失败日志/渲染；逐用例保留原DETAILS；为收尾owned读取/hash/元数据动作加一致截止门。完整责任见R37_G2_IMPLEMENTATION_OBLIGATIONS。

该申请仅采用已批准L0/无损规则，保留未批准L2的原完整责任，维持Fail-Closed和所有原边界。源码修改须新的明确授权，测试另行授权。9项保真责任差异在R37_REMAINING_APPROVAL_REQUEST中保留，不将其包装成G3全通过，也不启动第二工程动作。
