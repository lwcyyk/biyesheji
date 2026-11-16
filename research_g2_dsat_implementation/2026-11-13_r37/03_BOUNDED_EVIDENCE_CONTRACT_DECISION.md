# 冻结合同与G3裁决

合同标识：`G2-R37-EVIDENCE-REPRESENTATION-v1-PARTIAL`，版本1.0-partial。

- 合同正文SHA-256：`49a6660d12d1595be34e9374a9dab337dc81f236582e0719d90ed9bf8ebac277`。
- 完整合同文件SHA-256：`06230f8639ba3ee6624a766cd202f197221abbf0adb6c083e142ea02c052d235`。
- 完整文件为R37_APPROVED_EVIDENCE_REPRESENTATION_CONTRACT.json；正文hash作用于规范化contract对象。完整文件hash由R37_APPROVAL_RESULT及SOURCE_LOCK外部绑定，避免递归自哈希。

实际批准状态：PARTIALLY_APPROVED。G3_BOUNDED_EVIDENCE_CONTRACT_APPROVED=false，G3_BOUNDED_EVIDENCE_CONTRACT_PARTIALLY_APPROVED=true，G3_FULL_APPROVAL_PENDING=true。

## 表示类型

FULL_RECORD表示原必需语义完整，独立于耐久性和测试PASS。BOUNDED_EQUIVALENT须满足已批准可逆关系并通过绑定核验。TRUNCATED_DIAGNOSTIC可作为诚实失败记录，其原完整义务仍未满足。OPTIONAL_OMITTED对本37组没有可用L3名单。必需值/引用/来源/费用事实缺失归入REQUIRED_EVIDENCE_MISSING，完整合同接受false。

原始完整文本未实际处理时ORIGINAL_DIGEST_AVAILABLE=false，原长度UNKNOWN。截断后长度、字符数、JSON转义长度、原始字节数分别计量，不能互换。必须声明保存范围及原始编码；未渲染对象与已取得文本前缀使用不同原因。

来源字段缺失时ORIGIN_AUDIT_COMPLETE=false；费用或所有权事实缺失时账本不完整，实际未知量仍UNKNOWN。native_exit_required是验收要求，实际退出码由独立观察取得。完整性标记、持久化确认与业务结果分别核验。

## L1等价依据与限制

对原无损codec，严格base64/zlib逆变换必须返回完整canonical原字节，raw_bytes/raw_sha256和canonical数据均校验。部分压缩流/摘要不构成逆变换。

对R36已提出的冻结字段/重复记录引用，本轮限定批准以下等价规则：若实际原值为v，可取得的固定字节B与SHA绑定，确定定位器l提取X(B,l)，且已核对J(X(B,l))=J(v)，则解码返回同一原语义。任一依赖原语义的判断接收相同输入，故结果保持。对来源身份还必须先保留原实际观察和原身份判定，期望值不能替代未取得的观察。

引用对象1024B、定位器512B及0新增运行路径保持。具体定位器语法/解码器采用前仍需冻结与验证；不可用、歧义、循环、未绑定或内容不等的引用直接导致必需证据不完整。此为已证明条件下的表示规则批准，没有任何实际用例被宣称已满足这些条件，也没有新增读取权限。

## 审批边界

9组FULL_MANDATORY_UNTIL_EXPLICIT_CHANGE的拟L2替代，会改变原保真义务。本轮按R37第七节保留CONTRACT_CHANGE_REQUIRED；其必要L0成员继续无损。L3名单为空。诚实省略标志和完整摘要不能自行解除原文保存责任。

本轮审批只改变28组符合条件规则的授权状态。G1原条件证明及2000167B保持；G2语义/持久化/完整容量仍未闭合；G4的12项来源差异保持待核。2MiB、13路径、120秒和原测试定义/来源责任全部沿用。当前Runner、任何解码器、时限门及输出schema的实际符合性均未借此登记通过。
