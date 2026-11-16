# DCL-R6-BudgetFix：BF-static-1已冻结

2026-11-11。[最终裁决](DCL-R6-BudgetFix/FINAL_DECISION.md)、[真实源码与输入锁](DCL-R6-BudgetFix/SOURCE_AND_INPUT_LOCK.md)、[独立batch03申请](DCL-R6-BudgetFix/BATCH03_EXECUTION_REQUEST.md)、[证据索引](DCL-R6-BudgetFix/EVIDENCE_INDEX.md)。

限定静态修复完成：guard.py与guard_probe.py变更，run_batch及五业务字节相同；最终语法编译通过。精确N范围预留与一次认领、局部前置扣减和计时修复已交付；BF-1/BF-4=CONDITIONAL_PASS，BF-2/BF-3=PASS_STATIC。动态故障、性能与资源资格保持未决。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；batch03=UNAUTHORIZED且未创建；IMPLEMENTATION_GATE=CLOSED；严格分离0。校准软300/100000、全批1000000/1800/1740及AS4合同保持。以下保留此前研究导航。

---

# 去中心化凭据生命周期：batch02-Perf 当前入口

2026-11-10。[静态裁决](DCL-R6-batch02-Perf/FINAL_DECISION.md)、[精确时间线](DCL-R6-batch02-Perf/PERF_EXECUTION_TIMELINE.md)、[预算成本](DCL-R6-batch02-Perf/PERF_PERSISTENCE_COST_ANALYSIS.md)、[最小修复](DCL-R6-batch02-Perf/PERF_REPAIR_OPTIONS.md)、[新申请](DCL-R6-batch02-Perf/BATCH03_AUTHORIZATION_REQUEST.md)。

直接核验batch02两个ZIP与原始hash。C00/C01到结果仅1.109秒；C02预付内部跨度298.626607199秒，占共同300秒软窗99.5422%，平均9.277864ms/混合周期。全部PREP/COMMIT复用同戳，单次fsync/锁/CPU份额仍UNKNOWN_INTERVAL，未把源码7同步计数当成实测时延。

32191=入口3＋未启动child预付32188；模型/内存子操作0。选择A0：冻结有界child精确N一次持久范围、一次委派，保持全部安全屏障和300秒软窗；C02事务数32896→1为静态计数，墙钟收益待测。普通模型visit暂不改。

PERF1/2 PASS_STATIC、PERF3 CONDITIONAL_PASS、PERF4 PARTIAL；当前只完成设计，未写修复/探针/配置，未新建lc03/batch03。副本47文件只读hash一致，未尝试任何被拒绝操作，未来输入仅用正确根。原C00/C01局部通过、C02失败、账/代码/历史/强G/零分离/协议1.1及主机制门CLOSED保持。以下保留历史。

---
# 去中心化凭据生命周期：DCL-R6-batch02 实际结果

2026-11-10。[本批裁决](DCL-R6-batch02/BATCH02_FINAL_DECISION.md)、[校准](DCL-R6-batch02/BATCH02_RESOURCE_CALIBRATION.md)、[资源账](DCL-R6-batch02/BATCH02_RESOURCE_ACCOUNTING.md)、[交付索引](DCL-R6-batch02/README.md)。

已按新专项许可执行冻结Launcher。C00/C01局部PASS，C02在300秒软截止到达时仍在持久预付，Controller信号9、原始FAIL，分析为INCONCLUSIVE_LIMIT_CAL_SOFT_TIME；allocator child未启动。C03–C12/五业务兼容/F1/F4未达，资源门未取得。

最终32191/1000000预留，PREPARED/COMMITTED各32191且连续完整，无模糊事务；T0+300.1698498秒关闭、外层exit65。父树/全部本批瞬态进程退出、无STOP_UNCONFIRMED；原ZIP及正确host快照核hash通过。batch02=CLOSED_RESOURCE_GATE_FAILED，无恢复/重试/新预算。

B02-1 PARTIAL、B02-2 FAIL、B02-3/4 UNRUN、B02-5 CONDITIONAL_PASS。正式模型访问0、无PASS_BOUNDED/协议反例；旧源码/账/各阶段/L-C保持，D1 1.1/D2/G覆盖/归档/严格分离0与主机制门CLOSED不变。行政误路径重复副本因自动审批拒绝迁移/删除而保留，正确封存已核验。以下为历史入口。

---
# 去中心化凭据生命周期：DCL-R6-LC 当前入口

2026-11-10。[LC裁决](DCL-R6-LC/LC_FINAL_DECISION.md)、[交付索引](DCL-R6-LC/README.md)、[资源代码差异](DCL-R6-LC/LC_LINUX_ADAPTER_DIFF.md)、[batch02独立申请](DCL-R6-LC/LC_BATCH02_AUTHORIZATION_REQUEST.md)。

CPY312-UBU24/1已批准用于静态部署。实际dcl-r6身份999/989、lc01工作区和两个inactive单位建立；八文件语法/单位verify通过，三资源程序完成Linux静态接入，五业务文件保持原hash。实际AS/Tasks/权限属性读回与配置一致，MainPID0，无动态enforcement实例。

LC1–3 PASS_STATIC，LC4 CONDITIONAL_PASS。静态manifest、1224代码树/31关键文件、源/缓存/单位/输入及14组payload argv已冻结；C09唯一计划恢复保持同boot/T0/账，未知退出关闭。后续特殊映射/TCB/停止假设、真实C00–C12与语义检查仍需新许可和证据。

RESOURCE_GATE_PASS=NOT_OBTAINED、F1/F4=UNRUN_RESOURCE_GATE、batch02=UNAUTHORIZED；两端batch02未创建，out为空。未启动/enable验证service、未运行目标模块正文/探针/校准/模型。原27次/118.7340827秒/关闭deadline、v1/v2/v3及全部历史保持。主机制门CLOSED、严格分离0与D1 1.1/D2/G覆盖维持。以下为历史入口；旧根导航在LC/evidence/navigation_before。

---
# 去中心化凭据生命周期：DCL-R6-LR 当前入口

2026-11-10。[LR裁决](DCL-R6-LR/LR_FINAL_DECISION.md)、[交付索引](DCL-R6-LR/README.md)、[运行时路线](DCL-R6-LR/LR_RUNTIME_ROUTE_DECISION.md)、[L-C申请](DCL-R6-LR/LR_NEXT_AUTHORIZATION.md)。

已发现原生/usr/bin/python3.12，版本3.12.3、Ubuntu包3.12.3-1ubuntu0.17，默认python3指向它；ELF/摘要/直接库/关键标准库有据。五业务文件静态未见必须3.14的依赖，推荐L2的CPY312-UBU24/1候选，等待明确批准和后续独立验收。没有自动改用3.12或安装3.14。

LR-1/2 CONDITIONAL_PASS，LR-3 PARTIAL，LR-4 PASS_STATIC。manager255.4-1ubuntu8.18为degraded，失败清单仅mnt-e.mount；根memory/pids已启用但当前无限，专用dcl-r6用户/组和Linux活账目录缺失。L-C范围已具体化：新身份/工作区、inactive单位、资源三文件静态接入与语法/配置校验；当前未执行。

本轮35条Linux查询，Python仅一次--version；无资源/业务执行、代码、配置、安装、模型。L-C/batch02仍UNAUTHORIZED、RESOURCE_GATE_PASS=NOT_OBTAINED、F1/F4仍UNRUN_RESOURCE_GATE；原WS4 E2未决、主机制门CLOSED/严格分离0。原账27次/118.7340827秒及所有历史原件保持；旧根导航快照见DCL-R6-LR/evidence/navigation_before。下方保留历史入口。

---
# 去中心化凭据生命周期：DCL-R6-P 当前入口

2026-11-10。[P裁决](DCL-R6-P/P_FINAL_DECISION.md)、[交付索引](DCL-R6-P/README.md)、[原始命令](DCL-R6-P/evidence/P_COMMAND_RESULTS.json)、[L阶段需求](DCL-R6-P/P_NEXT_STAGE_REQUIREMENTS.md)。

P专项授权已完整执行12条固定WSL argv：11条exit0，两个指定Python3.14路径缺失导致第12条exit2。实际kernel6.18.33.2-microsoft-standard-WSL2/x86_64，PID1为systemd，工具255.4-1ubuntu8.18；cgroup2根memory/pids可用且启用；查询身份root。P1 PASS_STATIC、P2 CONDITIONAL_PASS、P3 FAIL、P4/P5 PARTIAL。

AS4-PAYLOAD/1仅原则接受用于平台审查；目标AS/pids限制、权限封闭、特殊映射、runtime与停止校准均待后续授权/证据。batch02=UNAUTHORIZED、RESOURCE_GATE_PASS=NOT_OBTAINED、F1/F4仍UNRUN_RESOURCE_GATE。下一步先补L的native runtime/身份/管理接口等只读缺项，再形成实际配置和执行锁。

没有额外Linux命令、主动停止、单位/资源配置、安装、探针、模型或验证代码。Ubuntu-24.04在查询期间运行，客户端退出后的即时状态未追加检查。batch01原账/版本/失败及Envelope原件保持；D1 1.1、D2条件结论、强G覆盖、I1/I2/I3归档、严格分离0及主机制门CLOSED维持。旧根导航快照见DCL-R6-P/evidence/navigation_before。以下保留历史入口。

---
# 去中心化凭据生命周期：DCL-R6-Envelope 当前入口

2026-11-10。[本轮裁决](DCL-R6-Envelope/FINAL_DECISION.md)、[九文档索引](DCL-R6-Envelope/README.md)、[严格界](DCL-R6-Envelope/STRICT_MEMORY_BOUND_PROOF.md)、[合同与授权申请](DCL-R6-Envelope/BATCH02_AUTHORIZATION_REQUEST.md)。

三路线已比较，选定 C 的 AS4-PAYLOAD/1 条件方案：WSL2 Ubuntu-24.04＋systemd，AS 1 GiB/进程＋单批父 slice TasksMax=4。原 Windows WS4 的 E2=UNRESOLVED；cgroup memory.max 允许暂时超限，未登记为原指标通过。E1 CONDITIONAL_PASS，E3 静态设计完成附条件，E4 PARTIAL_UNAUTHORIZED；F1/F4 仍 UNRUN_RESOURCE_GATE。

本机只读清单显示三个 WSL2 发行版均 Stopped；Docker 固定本地端点查询失败；实际 kernel/cgroup/systemd/native Python 未认证。新增代码/校准/模型/平台启动/配置/安装均0。batch01 原62文件/ZIP和27次、118.7340827秒保持；v3 未改。下一步先审合同边界和有限平台 P 阶段申请，再据实际信息冻结最终批次锁。

原协议1.1、G覆盖、I1/I2/I3归档、严格分离0与 IMPLEMENTATION_GATE=CLOSED 保持。Repair 根导航快照在 revisions/DCL-R6-Repair；以下保留历史入口，当前状态以前置 Envelope 节为准。

---
# 去中心化凭据生命周期：R6-B-Repair当前入口

2026-11-10。[本轮裁决](DCL-R6-Repair/FINAL_DECISION.md)、[修复索引](DCL-R6-Repair/README.md)、[资源界证明责任](DCL-R6-Repair/RESOURCE_BOUND_PROOF.md)为当前交付。

完成原ZIP/版本/计数复核、Windows API与布局/时窗审查，v3独立静态修订只改资源三文件，业务五文件hash一致。87唯一根因及峰值内部计账仍待取证；启动前包络未证，v3未执行且正式准入有意关闭。

RG-1 CONDITIONAL_PASS、RG-2 PARTIAL、RG-3 UNRUN并保持RESOURCE_GATE_FAILED、RG-4 UNRUN_RESOURCE_GATE。F1/F4未恢复，新增校准/模型0，PASS_BOUNDED为空。batch01已到期；新批次草案含独立授权和严格技术前置。

原62文件/60项ZIP、v1/v2、27/118.7340827旧账及R1–R5保持。原生/外发/依赖安装0，主机制门CLOSED、零分离与强G覆盖维持。下方为历史入口。

---
# 去中心化凭据生命周期：DCL-R6阶段B当前入口

2026-11-10。[最终裁决](DCL-R6/R6_FINAL_DECISION.md)、[资源校准失败报告](DCL-R6/R6_RESOURCE_CALIBRATION_REPORT.md)和[机器结果](DCL-R6/evidence/stage_B/RUN_RESULTS.json)为最新交付。

专项授权已执行到资源校准：八程序创建，v1/v2及首次失败保留；normal/counter通过，memory峰值断言失败，RESOURCE_GATE_FAILED。F1/F4未启动，均UNRUN_RESOURCE_GATE；正式模型反例0、PASS_BOUNDED为空。

B1 FAIL、B2/B3 UNRUN、B4 CONDITIONAL_PASS。27次访问全部校准，118.7340827秒至v2退出，未重置总账。实际指标/采样下界/未测峰值分列，现有证据不足以认证全部授权硬界，未绕过失败运行模型。

原协议1.1及D2条件结论/强G覆盖保留，机制实现门CLOSED，严格分离0，原生/构建/依赖下载/外发0。R1–R5冻结，R6阶段A已锁存，独立batch01保留源码、日志、计数与结果。

以下为阶段A和更早历史。

---
# 去中心化凭据生命周期：DCL-R6阶段A当前入口

2026-11-10。[最终裁决](DCL-R6/R6_FINAL_DECISION.md)、[R6索引](DCL-R6/README.md)与[专项申请](DCL-R6/R6_TOOLCHAIN_AND_PERMISSION.md)为当前交付。

本轮已完成只读工具/规格预审：F1八个不变量、多配置/独立RHO监视、K1/U2与变异；F4阈值算法/独立具体轨迹参考、输入合法性、夹具和G64族；资源硬界/工具缺口及命令范围明确。

阶段B尚无单独许可，F1/F4结果UNRUN_PERMISSION；模型/参考/监督程序创建0、模型执行0、下载/原生请求/外发0。仅Java/Python版本查询2次，行政检查分列。当前没有PASS_BOUNDED/LEVEL-3结果。

R6-A CONDITIONAL_PASS，B UNRUN_PERMISSION，C CONDITIONAL_PASS，D PASS于决策。D1/D2纸面条件、强G覆盖/I1–I3归档、严格分离0、机制实现门CLOSED保持。R5原件/盲审包直接复用，根四份旧导航/历史单独锁存。

下方保留历史入口。

---
# 去中心化凭据生命周期：DCL-R5当前入口

2026-11-10。[最终裁决](DCL-R5/R5_FINAL_DECISION.md)、[R5索引](DCL-R5/README.md)和[证据索引](DCL-R5/R5_SOURCE_INDEX.json)汇总本轮增量。

重点结果：旧签名Stop与完整child激活/可信摘要锚分层；Ready与真实使用时点/在途责任限定；官方发行asset摘要匹配、固定版本stamp写入及SQLite静态配置证据；S2(T)备用当前资格与全部资源前缀复核。

F1–F4和T1–T4已形成准入申请材料，代码/工具/fixture/权限仍待绑定，当前未执行。原生计划完整展开最多92次、硬封顶114次，NC2清理均分已修正。第一阶段盲审只含定义/命题/实例/空白返回表，原R4完整审查ZIP复用，外部复核0。

R5-A CONDITIONAL_PASS、B PARTIAL、C CONDITIONAL_PASS、D PASS。强G覆盖/I1–I3归档保留，严格分离0，实现门CLOSED。D1/D2仍属纸面条件协议/有限配置成果，实际PBFT/跨域S2和独立原创性另待证。

历史内容与R4原件保留如下；R5对资格时点、冷备用和预算的澄清以当前文稿为准。

---
# 去中心化凭据生命周期：DCL-R4 当前入口

2026-11-10。当前交付为[最终裁决](DCL-R4/R4_FINAL_DECISION.md)与[完整R4索引](DCL-R4/README.md)。[本地独立审查包](DCL-R4/R4_EXTERNAL_REVIEW_PACKAGE.md)包含协议/证明、原生合同、强G、反例、未解责任及验证计划；外部独立审查仍为0。

本轮收敛：D1-PBFT-SEAL/1.1纸面条件完整；D2有限累计费用/共同策略规格条件闭合；A/B/C部署映射PARTIAL；B按S1与有限S2(T)分别裁决。单/双Gate共主Q在Seal时失去S2，独立持续路径的故障、网络、期限和费用条件已具体化。

当前原生二进制有dirty标记，源码到运行精确对应持续待证。强G覆盖和I1/I2/I3归档保留；严格分离0，实现门CLOSED。新增代码/原生实验/机器证明/外发0。原33输入和R1/R2/R3归档保持，哈希/链接检查只承担工件完整性。

规范优先级：R3固定业务/BFT/费用/组合文稿＋R4明确增量与具体合同。历史入口全文在下方按原内容保留，旧状态仅代表当时证据。

---
# 去中心化凭据生命周期：D1 / D2 研究交付 DCL-R3

定稿日期：2026-11-10，Asia/Shanghai。DCL-R3继续原研究；R1的46份工件、R2的94份活动工件分别固定在revisions/DCL-R1与revisions/DCL-R2，锁定清单在evidence/r2与evidence/r3。原33输入保留。

本阶段入口：[NC1/NC2重新推导](R3_INDEPENDENT_CONCURRENCY_AUDIT.md)、[入口与创建截止](R3_NATIVE_ENTRY_CUT_AUDIT.md)、[具体BFT重配置](D1/BFT_RECONFIGURATION_PROTOCOL.md)、[证明与部署义务](D1/PROOF_OBLIGATIONS_R3.md)、[费用语义](D2/COST_SEMANTICS_R3.md)、[组合合同](JOINT/R3_COMPOSITION_CONTRACT.md)、[两轮强G反证](R3_STRONG_G_REASSESSMENT.md)、[原创性/状态裁决](R3_NOVELTY_DECISION.md)。

R3规范优先级：上述R3合同/实例/证明限定R2的21业务转换；R2文稿和历史证据保持原版本，未将后来结论改写成过去已经验证。CONDITIONAL_PROTOCOL_COMPLETE限纸面实例；原强B前缀支持仍由D2检验，单路径暂停场景不能通过。

R2阶段入口（历史）：[Casdoor能力审计](CASDOOR_NATIVE_CONTRACT_AUDIT.md)、[全部转换与原生轨迹](NATIVE_SEMANTICS_REFINEMENT.md)、[直接先例对照](DIRECT_PRIOR_WORK_COMPARISON.md)、[强G与四项分离反驳](STRONG_G_COVERAGE_AUDIT.md)。R2当时为Gate A静态范围通过、Gate B来源缺口、Gate C协议精化待证，实现门关闭。

本目录给出条件协议、联合配置模型、反例、强通用组合覆盖构造及后续验证设计。当前具有可审查的技术规格；严格优势实例、机器证明和外部独立复核仍待取得。实现门保持关闭。

建议阅读顺序：

1. [当前裁决](CURRENT_VERDICT.md)与[现状审查](CURRENT_STATE_AUDIT.md)。
2. [分离声明与实现门](SEPARATION_GATE.md)、[最强适用组合 G](BASELINE_G.md)。
3. [D1 协议](D1/PROTOCOL_SPEC.md)、[安全性质与证明](D1/SECURITY_PROPERTIES.md)、[反例](D1/PROOFS_AND_COUNTEREXAMPLES.md)。
4. [D2 模型](D2/CONFIGURATION_MODEL.md)、[算法及证书](D2/ALGORITHM_AND_CERTIFICATES.md)、[正确性](D2/CORRECTNESS_AND_PROOFS.md)。
5. [集成架构](JOINT/INTEGRATED_ARCHITECTURE.md)、[组合证明责任](JOINT/COMPOSITION_PROOF_OBLIGATIONS.md)。
6. [先例核验](SOURCE_AND_PRIOR_WORK.md)、[验证计划](EVALUATION_PLAN.md)、[下一步](NEXT_ACTION.md)。

evidence/INPUT_MANIFEST.json 固定 33 份本地输入的 SHA-256；evidence/web/ 保存本轮 18 批公开检索及正文定位结果，public_sources/ 保存 Crossref 元数据。哈希承担版本识别；语义与证明由正文中的论证承担。检索资料按实际取得范围使用，全文未核验项保留缺口。

以上18批为R1；R2新增公开正文定位保存于evidence/r2/web，26份固定版本源码及13项18字段能力记录保存于evidence/r2/native。R2_SOURCE_INDEX.json与CLAIM_LEDGER_R2.json汇总新证据及状态；文档完整性检查不承担协议验证。

本轮活动：源码与既有证据只读检查、公开资料检索、手工状态轨迹、条件证明、研究文档整理。新增机制代码、求解器实验、历史测试重跑、原生账号操作和外部发送均为 0。所有研究推导由当前对话内知情模型辅助完成；外部独立评审尚待取得。
