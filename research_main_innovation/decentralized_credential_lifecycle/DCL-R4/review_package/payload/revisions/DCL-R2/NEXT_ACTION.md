# DCL-R2下次可直接恢复的任务

恢复顺序：CURRENT_VERDICT最新R2节 → CASDOOR_NATIVE_CONTRACT_AUDIT → NATIVE_SEMANTICS_REFINEMENT → STRONG_G_COVERAGE_AUDIT。R1已存revisions/DCL-R1，原33输入继续只读锁定。当前实施门关闭。

## 当前最高优先级：独立静态核对精确反例与部署前提

核对NC1/NC2/NC7与COST1，确认所审源码之外是否有whole-handler锁、同一DB事务或实际入口限制能排除这些轨迹。固定源码副本在evidence/r2/native/source，commit与哈希在SOURCE_LOCK.json；NC轨迹及局部行号在NATIVE_SEMANTICS_REFINEMENT。只读审查即可推进，受权新原生实验另行决定。

对NC1重点核对F3有效父副本→V3/V4→F5的可执行性和真实DB提交模型；对NC7核对password RT省略secret及两个入口的所有前置filter。若出现排除该顺序的新证据，修正当前源码允许历史；实际复现之前保留SOURCE_ADMISSIBLE而非EXPERIMENT_OBSERVED。

## 后续可直接执行的三项纸面工作

1. **Gate B来源补齐**：SC-A2A官方发表日2026-10-13、卷页与作者已核，正文/实现仍缺。已有直取/stamp/出版方PDF/Crossref staging失败记录在evidence/r2/web。只跟进真正的新官方/作者全文入口，不重复宽泛搜索，也不联系作者或发送私有项目。
2. **Gate C具体化**：选择一个成熟BFT状态服务/成员变更的明确版本，仅核对其接口如何保存RHO与当前资格/数据可用性；原生动作仍分域。加入选择需要的证据/信任与费用同等交给G。实际部署与代码继续受实施门控制。
3. **费用与保持证明**：按D2累计费用阈值模型、非空Post和真实handler相位，对一个CD25-BOUND的最小RHO迁移作完整手工走查；同时确认CD25-LEAK的S_bypass不能由Q预算截断。预期产物为更严密的条件证明或反例，不预设严格优势。

## 路线裁决

S1–S4已完成本轮最小分离/反证尝试；没有存活的严格实例。可行的条件迁移/配置继续作为成熟组件工程底座，原生并发/入口/审计语义作为待独立确认的系统发现。只有新实例展示候选可达性质及G的必要额外代价，才重新登记机制实施资格。

以下为R1恢复任务的历史记录，已执行项以本节和最新裁决为准。

---

# R1下次任务记录（历史）

恢复入口：CURRENT_VERDICT → SEPARATION_GATE → 本文件。先读取 evidence/INPUT_MANIFEST.json 与最新用户指示；历史状态变化时重新锁定相应输入。当前实现门关闭，纸面与公开来源工作可继续。

## 优先任务 A：有限原生 profile 的纸面精化

读取：D1/PROTOCOL_SPEC T03/09/12/13/19、JOINT/COMPOSITION_PROOF_OBLIGATIONS CP2–5，以及当前 native_provider.py:151/192、reconciliation.py、M6 NATIVE_ISOLATION_PROFILE。

构造一张“实际原生接口→请求/材料身份→原子竞争→派生覆盖→迟到拒绝→异步效果”对应表。只读公开 Casdoor 4.25.0 源码与已有 M3/M4/M6 证据，检验 E1 已看到密码时能否继续登录、枚举范围如何覆盖新派生、原生端是否存在对稳定 k 的终态化。

预期产物：一个可复查的实际不可行输入，或一个精确的条件 profile；对每条映射标 S/T/N/P/U。若接口缺失，给最小新增原生能力及对 G 同等开放后的结论。此任务无需实账号操作或新代码，能直接检验目前最关键的模型前提。

## 任务 B：直接近邻的窄范围补读

1. SC-A2A：evidence/public_sources/SC_A2A_CROSSREF.json 已核作者/DOI；补出版方正文的协议、安全模型与撤销/迁移段，418 障碍保持记录。
2. DISC2026 Fair Binding：官方题录/摘要已核，全文解析读取受限；补 witness validity、reserve/use 与重配置覆盖，判断隐藏状态联审是否产生直接覆盖。
3. ALP §5、AH §§8–10 与 D1 T08–19 逐字段对照；公开草案实际证据已经足以支持概念重叠，具体 Provider 条件仍逐条核。
4. Seal 当前设计/最佳实践与 Lit v3 当前 TEE/onchain 权限：冻结不可变版本，补秘密/子材料输出与回滚模型。保留 legacy Datil 检索片段与 v3 正文差异。
5. 国内 CNKI/万方及 ESORICS/ACSAC/FC/TDSC/TIFS/ICDCS 的系统数据库查重仍未完成。先建立可复查题录与原文读取范围，再作优先权判断。

## 任务 C：新的分离资格

只有 A/B 补读产生了一个具体、标准 G 无法在相同能力/观察下匹配的性质，才登记新输入族和固定成本。先手工证明候选可行与 G 必要费用；若 G 通过相同闭包/博弈/工作流即可完成，新增 COVERED_BY_G 记录并停止该变体。当前不存在已经具备必要下界的待实现机制。

可保留的硕士论文定位为：凭据生命周期威胁建模、原生接口可实现边界、条件跨域协议、联合配置规格与工程精化。其学术创新强度仍依赖实际 profile 发现、完整证明和先例补核。
