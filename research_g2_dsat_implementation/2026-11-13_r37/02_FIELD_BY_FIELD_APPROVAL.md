# 37组逐项决定

| 序号 | 原字段组ID | 当前保真责任 | 原候选上限 | 本轮决定 |
|---|---|---|---|---|
| 1 | `test_identity` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 2 | `test_outcomes` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 3 | `test_counts_order` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 4 | `assertion_checks` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 5 | `origin_decisions` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 6 | `origin_identity` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 7 | `version_pins` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 8 | `refusal_header` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 9 | `error_numbers` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 10 | `fee_state` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 11 | `owned_resource_state` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 12 | `journal_integrity` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 13 | `native_exit_observation` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 14 | `terminal_status` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 15 | `D24_exact_bytes` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 16 | `cache_policy` | L0 | 分成员沿用原边界；无新组总界 | APPROVED |
| 17 | `r35.generic_json_string` | L0 | 8192 | APPROVED_WITH_RESTRICTIONS |
| 18 | `r35.module_name` | L0 | 256 | APPROVED_WITH_RESTRICTIONS |
| 19 | `r35.module_metadata_path` | L0 | 2048 | APPROVED_WITH_RESTRICTIONS |
| 20 | `r35.module_type` | L0 | 256 | APPROVED_WITH_RESTRICTIONS |
| 21 | `r35.loader_label` | L0 | 512 | APPROVED_WITH_RESTRICTIONS |
| 22 | `r35.exception_text` | L0；拟L2待确认 | 4096 | CONTRACT_CHANGE_REQUIRED |
| 23 | `r35.exception_args` | L0；拟L2待确认 | 2048 | CONTRACT_CHANGE_REQUIRED |
| 24 | `r35.exception_filename_strerror` | L0；拟L2待确认 | 1024 | CONTRACT_CHANGE_REQUIRED |
| 25 | `r35.traceback_file` | L0；拟L2待确认 | 1024 | CONTRACT_CHANGE_REQUIRED |
| 26 | `r35.traceback_module_function` | L0；拟L2待确认 | 256 | CONTRACT_CHANGE_REQUIRED |
| 27 | `r35.traceback_source_excerpt` | L0；拟L2待确认 | 0 | CONTRACT_CHANGE_REQUIRED |
| 28 | `r35.exception_descriptor_total` | L0；拟L2待确认 | 16384 | CONTRACT_CHANGE_REQUIRED |
| 29 | `r35.failure_stage_code` | L0 | 256 | APPROVED_WITH_RESTRICTIONS |
| 30 | `r35.case_error_text` | L0；拟L2待确认 | 8192 | CONTRACT_CHANGE_REQUIRED |
| 31 | `r35.case_detail` | L0 | 65536 | APPROVED_WITH_RESTRICTIONS |
| 32 | `r35.raw_json_payload` | L1 | 1048576 | APPROVED_WITH_RESTRICTIONS |
| 33 | `r35.compressed_payload` | L1 | 1114112 | APPROVED_WITH_RESTRICTIONS |
| 34 | `r35.base64_data` | L1 | 1485484 | APPROVED_WITH_RESTRICTIONS |
| 35 | `r35.log_input_utf8` | L0；拟L2待确认 | 262144 | CONTRACT_CHANGE_REQUIRED |
| 36 | `r35.read_denial_path` | L0 | 2048 | APPROVED_WITH_RESTRICTIONS |
| 37 | `r35.SQL_kind` | L0 | 128 | APPROVED_WITH_RESTRICTIONS |

总计：APPROVED16+APPROVED_WITH_RESTRICTIONS12+PENDING0+REJECTED0+CONTRACT_CHANGE_REQUIRED9=37。未解决9组归入“需合同修改”类别，均仍待另行确认；它们没有被算入已批准28组。禁止解释作为独立拒绝规则列示，不虚构新的字段组计数。

16组核心字段批准其原L0完整义务，包括原测试身份/结果/计数、原必需checks、来源、拒绝码、errno/winerror、费用/所有权、完整性链、退出观察和截止状态。授权消费状态映射到assertion_checks及case_detail中原有票据/消费观测成员，不新增第38组，也不从PASS推断不存在的消费数据。

12组限定批准包括9组L0文本/成员边界和3组L1序列化层。限定含义为：完整接受值保持全部原信息，超限则必需证据不完整；没有截断L0以适配预算的许可。L0与L1是语义内容/表示层关系，L1编码必须精确还原原L0值。

## 字节单位与重叠规则

通用字符串8192B仅约束原语义JSON树。外层base64使用其既有独立边界；压缩缓冲1114112B为二进制中间值。base64内容1485484个ASCII字节来自4*ceil(1114112/3)，JSON字符串另加两引号为1485486B，键/结构/LF另计。此项单位澄清没有增加任何文件份额。

日志262144B是最多65536字符在UTF8编码前后得到的单次输入源级松包络；实际每个日志累计额度仍65536B。它没有赋予丢弃原必需日志内容的权限。

核心字段组的独立总字节界未建立时填写null并列明原成员/容器/文件约束，语义批准保留完整义务。完整负载联合容量仍由G2负责，未以null表示0或无限配额。

不同组重叠时，原安全事实的L0义务优先。例如exception_descriptor_total内部的类型/errno、exception_args中的拒绝码、filename中的来源身份，以及case_error_text中的原结果依据，均不能因外层拟L2标签被降级。

## 八类决策依赖

R37_SECURITY_DECISION_DEPENDENCY_AUDIT对37组逐项记录授权、来源、一次性消费、PASS/FAIL、预算、异常分类、历史完整性与最终验收八类依赖。根据内容决定的字段保持CONTEXT_DEPENDENT，未经证明不得作“纯诊断”断言。原37组审计义务均参与相应完整验收；本轮没有将任何原必需内容登记为L3可省略。

9组拟L2均保留原完整义务。当前可限定批准诚实的失败/不完整显示：明确未渲染或截断、保存范围、未知长度/摘要和完整保留=false；这条规则不解除原完整内容责任。具体合同差异逐组列于R37_REMAINING_APPROVAL_REQUEST。
