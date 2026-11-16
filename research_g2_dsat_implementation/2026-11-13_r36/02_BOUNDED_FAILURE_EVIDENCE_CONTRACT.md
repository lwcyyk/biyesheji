# 有界失败证据合同审定

**合同已明确，批准仍待取得。** R36静态授权没有批准新的有损诊断语义。R34申请原文要求：`any truncation/digest/reference substitution must state recoverability and obtain approval`；并规定受限/未渲染文本须标记不完整，完整合同false。R35同样保留待审批状态。

R36_BOUNDED_FAILURE_EVIDENCE_CONTRACT逐项覆盖16组核心事实和R35全部21类字段，共37组。每组同时登记原有效义务、候选等级、等价条件与审批状态。

| 等级 | 本轮审定 |
|---|---|
| L0 无损必需 | 测试ID/原结果/已执行事实/计数与顺序、原必需checks、来源判断与身份、代码/依赖/fixture摘要、拒绝码、已知errno/winerror、费用与不确定性、资源所有权、journal链、结束状态和已可靠观测的native退出。 |
| L1 等价表示 | 原已采用的canonical JSON及可逆zlib/base64继续按原合同核验。新的固定字典引用/内容引用需要精确定位、摘要、可取得原字节与逆变换，并单独批准。 |
| L2 有损诊断 | 仅建议涵盖不参与安全/结果/来源判断的异常原文、参数、traceback/源摘录、因果链渲染和冗余日志外观。候选方案待批准。字段内部的决策信息仍属L0。 |
| L3 可选 | 本轮没有将任何原必需字段降为可选；可选纯外观副本仍须明确列出并获批准。 |

L1路径引用须在原始完整身份校验后进行。保存期望路径不能代替观察真实路径；同名/同后缀/同版本也不能代替原文件身份。引用须能取得SHA绑定的确切字段；只有长度或摘要无法恢复全文。

L2审批稿要求保留内容类型、有界内容、逐字段省略/未渲染原因、完整原文保留标志、原完整长度是否可知、原完整摘要是否可知。只有真正完整处理原始内容才允许ORIGINAL_DIGEST_AVAILABLE=true。部分内容/规范化内容的摘要另作类型标记；未知原始长度仍为UNKNOWN。源/摘要/结果等L0缺失必须使CORE_EVIDENCE_COMPLETE=false及完整接受false。

R35当前全部exception_record均先置evidence_complete=false，FULL_EXCEPTION_TEXT_PRESERVED=false。它保持了保真声明的保守方向，但描述对象仍可能在record-overflow/recorder-failed分支丢失其他已知信息。审批L2无法把这些L0缺口升级为完整。

建议采用独立指标：CORE_EVIDENCE_COMPLETE、DIAGNOSTICS_COMPLETE、REQUIRED_EVIDENCE_COMPLETE、FULL_EXCEPTION_PRESERVED、ORIGIN_AUDIT_COMPLETE和FINALIZATION_INCOMPLETE，并绑定具体EVIDENCE_CONTRACT_ID。上述完整新schema尚未全部在当前代码实现，本轮仅形成审批稿。

必须分清原合同完整性与拟修订合同完整性。将原完整异常改为L2属于明示合同变化；不能同时声称原全文无损等价。失败路径可以保留有用的受限取证，完整任务接受继续false。存储完全不可用时，实际可确认前缀与native非零退出应保留其已观测范围，完整耐久证据责任无法由有限预算保证。

唯一主动审批提案见BOUNDED_EVIDENCE_CONTRACT_APPROVAL_REQUEST.md和R36_NEXT_AUTHORIZATION_REQUEST.json。当前approved=false；源码修改、依赖变更、回归运行和真实部署权限保持关闭。

具体候选边界：L1引用对象最多1024B、locator最多512B；L2描述对象16384B、消息4096B、参数2048B、traceback8帧/路径1024B/函数与模块256B、链3链接、源摘录0。每日志原64KiB份额保持。引用与诊断对象以最终转义JSON计量，日志以实际UTF8文件字节计量，L0头独立于L2溢出；引用解析/必需内容缺失继续完整接受false。逆变换、原文摘要与长度真实性、L0保留及联合容量均列为独立验证责任。
