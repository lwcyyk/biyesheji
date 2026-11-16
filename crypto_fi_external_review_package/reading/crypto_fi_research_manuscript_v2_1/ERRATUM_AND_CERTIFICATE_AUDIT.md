> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_research_manuscript_v2_1/ERRATUM_AND_CERTIFICATE_AUDIT.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# INC976勘误、影响范围与确定性证书审计

2026-11-10，Asia/Shanghai。研究稿版本：**v2.1**。身份：**AUTHOR_ERRATUM_IMPACT_AUDIT_AND_DETERMINISTIC_CERTIFICATE_REPLAY**。状态：**INC976_CLOSED；976_CERTIFICATE_REPLAY_CONFIRMED；THREE_DISPLAY_TABLES_BOUND_TO_CDF_AND_INPUT**。

本轮成果为文稿勘误、影响范围审计和确定性有限分布证书重放。用户提供了已有“系数匹配、界成立”结论；本版另执行可追溯程序，并以实际输入、完整输出和整数比较记录作为当前交付依据。新增独立、人工、跨模型、盲审、子代理和证明助手认证均为0，精确后端ID按可见运行信息为null。历史稿和审阅材料保持只读。

## 1. 勘误的准确范围与来源

v2正文附录B（冻结件L708）的χ976质量显示行，把±5、±6、±7、±8、±9各点分子分别写成1131、426、138、38、8，正确值为1101、396、118、29、6。分母65536，其余点保持。旧显示行也出现于v1；本轮只认证实际读取到的这条沿用链，最早产生该转录差异的编辑过程未另行推断。

发现来源为发表影响审计INC976（ORIGINAL_CLAIM_AND_PARAMETER_MAPPING §7、VERDICT.incidental_finding）。旧显示总质量为65718/65536，正确总质量为1；更正十个有符号原子、五个绝对值列，总分子减少182。原显示的支持和对称形状保持，但其分母下总质量和声明的均匀奇偶质量无法成立。正确质量的逐点差异如下。

| 绝对值j | 旧的每点分子 | 正确每点分子 | 每个符号点变化（新−旧） | 两符号点合计变化 |
|---:|---:|---:|---:|---:|
| 0 | 11278 | 11278 | 0 | 0 |
| 1 | 10277 | 10277 | 0 | 0 |
| 2 | 7774 | 7774 | 0 | 0 |
| 3 | 4882 | 4882 | 0 | 0 |
| 4 | 2545 | 2545 | 0 | 0 |
| 5 | 1131 | 1101 | -30 | -60 |
| 6 | 426 | 396 | -30 | -60 |
| 7 | 138 | 118 | -20 | -40 |
| 8 | 38 | 29 | -9 | -18 |
| 9 | 8 | 6 | -2 | -4 |
| 10 | 1 | 1 | 0 | 0 |

完整21点有符号差异也保存在DISTRIBUTION_TABLES.json。勘误落点包括附录B显示表、从表重放说明、976电子复算入口、机器主张的分布选择器，以及新版人工审阅入口。§7.1中的ε₉₇₆≤2^-1118保持原值，已有电子证书无需数值修订。

## 2. 官方采样规则、CDF与质量推导

| 原始来源 | 固定版本/位置 | 本轮使用 |
|---|---|---|
| 官方2021规范 | 2021-06-04，59页；PDF15–16 §2.2.4/Algorithm5，25 Table3 | 严格阈值反CDF、976质量及CDF—质量公式；该版未列CDF数值表 |
| 官方2023提案 | 2023-03-14，21物理页；物理PDF8/印刷4 §7.4，15–16/印刷11–12 TablesA.3/A.4 | 独立版本的规则、976质量和CDF对应 |
| 官方1344勘误 | issue35，Patrick Longa回复2024-11-27，comment2504969837 | 1344完整CDF的T(5)=32765、T(6)=32767；2023旧CDF印表缺项按旧版记录 |

两份冻结PDF的SHA256分别为`5c3440b311c7ee4fba8b9a12e0ff567eb75c29fef66843f3eecc16f137164f7d`和`4688192bf5f5ac29e622ef359860890d2e97c224216baea2216dc42ef8d1547f`。采样/表的本轮提取与图像在evidence/official_2021_*、official_2023_*；对应已有结构预检PASS的字节再次核验。1344官方回复本轮只读重新取得并保存原始工具回执。

把16位均匀字r写成符号位r₀与t=r>>1∈{0,…,32767}。绝对值e=Σ_(i=0)^(s−1)1[t>T(i)]，输出(−1)^r₀e。由于比较严格，t∈[0,T(0)]给0，t∈[T(j−1)+1,T(j)]给绝对值j；最后一段止于32767。因而分母65536下w₀=2(T(0)+1)，w_(+j)=w_(−j)=T(j)−T(j−1)。T(s)在循环中不访问，其值32767固定最后区间的完整15位输入合同。

976的官方CDF为

`[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767]`。

推得0及每个正负点的质量分子为

`[11278,10277,7774,4882,2545,1101,396,118,29,6,1]`。

零点只计一次；976支持为[−10,10]共21点，每点正质量，对称。总质量65536，偶/奇分子各32768，最大原子唯一在0，a=11278/65536=5639/32768。每个内部阈值T(i)与T(i)+1逐一核对；对全部65536个输入字的确定性穷举得到完全相同频数。这些是有限域内枚举，随机采样次数为0。

## 3. 976的64重整数卷积与概率界

递推采用p₀(0)=1、p_(t+1)(k)=Σ_(z=−10)^10w_zp_t(k−z)，t=0,…,63。每阶段均检查总质量65536^t和完整支持宽度。最终结果：

| 项目 | 本轮结果 |
|---|---|
| 偏移及支持 | offset=−640；[−640,640] |
| 系数数量与逐项比较 | 全部1281个系数匹配；首次差异null |
| 分母、总质量 | 65536^64=2^1024；总质量等于该分母 |
| 对称性与峰值 | 完全对称；唯一峰值在0 |
| 峰值另一核对 | M=Σ_k p₃₂(k)²，精确相同 |
| 模群无合并 | q=65536>1280；1281个支持点的模像互异 |
| 文件字节 | 重建文件与v1冻结系数文件逐字节相同 |

完整峰值整数M为：

`3867742326778460011505695120010034781390274545577465781630059485327756844458410412224819576568141761707058469407320847309904413987741471919430419694124682422249747918267697550441983303134630087858796326969946459806636087193400711643940706661309666062380715683797783316484275155322980327315388516870855818374`

μ₆₄=M/2^1024，γ=21μ₆₄≈0.45181564799471987180061448706472，仅展示小数。a、μ和γ的约分后精确分数与PARAMETER_CERTIFICATES.json的976 profile逐项相同。旧γ显示0.4518156480是舍入近似；认证继续采用精确分数。

对

\[
\epsilon_{976}=\binom{976}{63}(11278/65536)^{913}+(21M/2^{1024})^{976},
\]

取公共分母2^999424，整数分子

\[
N=\binom{976}{63}\,11278^{913}\,2^{984816}+(21M)^{976}.
\]

本轮直接比较N≤2^998306，得到ε₉₇₆≤2^-1118。第一项还≤2^-1985；高重量项及总式的最大整数二进制上界指数均为1118，与旧证书ceil_log2_raw=−1118一致。总式不满足下一个2^-1119界，只描述这个上包络的松紧，实际误接受概率或解码错误率的下界各有不同责任。

REPLAY_976.json保留全部M/μ/γ、64个阶段记录、每项匹配结论、整数分子的因子化定义、位长、无符号大端字节SHA256以及正比较余量的身份。完整大整数由所列因子和指数唯一重建，无需依赖十进制近似。chi_976_64fold_coefficients.json保留全部1281个重建系数；replay_976_and_check_tables.py给可重放计算。来源位置校准后完成最终执行，243项确定性检查通过；本阶段完整976重放执行2次，最终证据绑定当前脚本与输出。

## 4. 三个显示表的针对性一致性

| χ | 显示质量=CDF导出=旧证书输入 | 支持 | 总分子 | 偶/奇分子 | 本轮完整卷积/ε |
|---|---|---|---:|---|---|
| 640 | 逐点相同 | [−12,12]，对称25点 | 65536 | 32768 / 32768 | 沿用历史证据 |
| 976 | 逐点相同（本版已更正） | [−10,10]，对称21点 | 65536 | 32768 / 32768 | 64步、1281系数与ε完整重算 |
| 1344 | 逐点相同（CDF含官方勘误） | [−6,6]，对称13点 | 65536 | 32770 / 32766 | 沿用历史证据 |

本轮三种采样器各穷举65536个输入字，并核对端点、归一化、支持、对称性、奇偶和最大原子。640/1344的64重卷积和ε界保持既有审阅身份；本轮未作这两项完整重算。旧official_cdf_input.json的三组显式质量、PARAMETER_CERTIFICATES.json的source_cdf与最大原子/奇偶字段均匹配。DISPLAY_TABLE_BINDING.json直接解析本版附录B三行，把实际文本行、行哈希、CDF、官方质量、证书输入与采样频数绑定。

## 5. 输入来源链与逐主张影响

| 材料 | 实际输入类别 | 本次影响 |
|---|---|---|
| official_cdf_input.json及旧生成脚本 | 正确官方CDF导出的质量 | pmf_from_cdf/conv64使用CDF文件，未读取文稿错误表 |
| PARAMETER_CERTIFICATES.json | 正确CDF、a、μ₆₄、γ与精确比较结果 | 976的值全部复现，原数值保持 |
| 旧chi_976_64fold_coefficients.json | 正确质量的已封存卷积系数 | 新计算逐项匹配，并且文件字节相同 |
| ROUND-005 phase1/math_verify.py | 硬编码的正确三组质量 | 旧976复核使用正确输入；本轮只读代码和记录，未重新执行整套旧检查 |
| v1/v2附录B | 错误的显示表及从表重放说明 | 当前文稿显示及其复核入口修正 |
| v2 §7.1概率表与C10 | 已封存正确证书输出 | 976界保持；当前证据增强为可追溯完整重放 |
| A与B的原证明/概率包 | χ640及其各自参数合同 | 声明、模型、量词和精确640概率数据保持 |

机器矩阵把原C10总项展开为C10_640、C10_976、C10_1344。C09（A）的依赖由C10总项细化为C10_640；C08、C14–C20的χ640语义输入，以及C25a/C25d（B）的χ640精确概率输入另作选择器登记。共享的PARAMETER_CERTIFICATES文件含多个profile，语义依赖通过profile640选择，不把同文件的976字段并入A/B。

对每条现有主张及新增子项，CLAIM_EVIDENCE_MATRIX.erratum_impact_by_claim记录传递依赖、影响与当前证据状态；完整来源材料分类和依赖闭包见MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json。976的来源事件ε界与976更新解码可靠性分开，C25b保持原未决状态。

## 6. 本版修正闭合表

| ID | 旧版/来源位置 | v2.1落点 | 状态 |
|---|---|---|---|
| INC976-R01 | v2附录B L708错误显示行；影响审计INC976 | 版本说明、附录B.1与逐点差异表 | CLOSED |
| INC976-R02 | 官方2021 Algorithm5/2023 §7.4及CDF | 附录B.1(B1)、本报告§2、DISTRIBUTION_TABLES | CLOSED |
| INC976-R03 | 旧976系数与μ证书 | 附录B.2、本报告§3、重建全部系数 | CLOSED |
| INC976-R04 | 旧976两项概率上界 | 附录B.2(B2)、REPLAY_976整数比较 | CLOSED |
| INC976-R05 | 三个显示表/官方输入/证书输入 | 附录B.1、DISPLAY_TABLE_BINDING、三次有限采样域穷举 | CLOSED |
| INC976-R06 | C10总项与A/B依赖 | C10三子项、语义profile选择与逐主张影响表 | CLOSED |
| INC976-R07 | 影响审计人工入口指向v2及INC976待修说明 | 本版HUMAN_REVIEW_ENTRY指向v2.1并附闭合结果 | CLOSED |
| INC976-R08 | 版本、来源、计算记录及历史字节 | 本版五份核心文件、MANIFEST与最终QA | CLOSED |

## 7. 保持的证据边界与人工审阅就绪

本版保留A的CF-1逐样本正确性、≤3n+1调用和Δ→1；保留B在均匀Setup、iid χ640、既定Ord、一次诚实未筛选TG/Upd及官方舍入合同下的初始完整正确率≥1−2^-132、更新完整错误率≥99.9969655%及初始正确条件下显示下界。原游戏、LWE与概率证明的人工/模型审阅身份按原记录引用。

本轮没有新增应用优先权搜索，采用发表影响审计截至2026-11-10的有界检索状态；同对象应用候选、全球优先权未决及Nishimaki/CJL来源版本责任保持。作者实际程序、config、A与秘密噪声联合律、Ord/取模/舍入对应以及FI完整LWE归约继续需要外部证据。最高价值的外部输入仍是作者准确UE commit/config、随机带与算术说明，以及一条含消息相等断言的Enc→TG→Upd→Dec轨迹。

本版具备交给人工密码学审阅的完整入口、全文证明、主张依赖、来源与有限证书材料。该就绪状态描述送审材料的完整性，人工同行裁决和正式发表状态分别待取得。数据与材料路径、字节哈希、当前有限执行范围及历史起止一致性由MANIFEST固定。

## 8. 直接复核入口

- [CRYPTOANALYSIS_DRAFT.md](CRYPTOANALYSIS_DRAFT.md)
- [CLAIM_EVIDENCE_MATRIX.json](../../frozen/crypto_fi_research_manuscript_v2_1/CLAIM_EVIDENCE_MATRIX.json)
- [HUMAN_REVIEW_ENTRY.md](HUMAN_REVIEW_ENTRY.md)
- [replay_976_and_check_tables.py](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/replay_976_and_check_tables.py)
- [REPLAY_976.json](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/REPLAY_976.json)
- [chi_976_64fold_coefficients.json](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/chi_976_64fold_coefficients.json)
- [DISTRIBUTION_TABLES.json](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json)
- [DISPLAY_TABLE_BINDING.json](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/DISPLAY_TABLE_BINDING.json)
- [MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json)
- [976_MENTION_INVENTORY.json](../../frozen/crypto_fi_research_manuscript_v2_1/evidence/976_MENTION_INVENTORY.json)
- [PARAMETER_CERTIFICATES.json](../../frozen/crypto_fi_research_manuscript_v1/sources/PARAMETER_CERTIFICATES.json)
- [official_frodo_2023.pdf](../../frozen/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf)
- [official_frodo_2021.pdf](../../frozen/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf)
