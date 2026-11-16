# 当前项目状态审查

2026-11-09。复原依据为用户指定文件、2026-11-09 汇总源索引、当前源码与历史裁决。证据标签：S=已有源码支持；T=历史测试支持；N=原生实验支持；F=形式化证明支持；P=纸面假设；U=尚未验证。F 在本目录另注明纸面或机器证明。本轮新机制的机器证明数为 0。

## 1. 核查事实

以下代码路径均相对 D:/毕业设计/auth-lifecycle/src/auth_lifecycle/，行号以本轮 INPUT_MANIFEST 锁定字节为准。

|事实|标签及证据位置|范围与结论|
|---|---|---|
|AuthorityStore 为 SQLite 单一持久权威|S：online_state/storage.py:46、63、122–159；online_state/migration.sql 由架构文档定位|BEGIN IMMEDIATE、WAL、整份应用状态 AES-GCM；跨域复制待设计|
|批准、caller、task/account/audience/generation 绑定|S：storage.py:161–225；services.py:81 起|caller 来自服务身份；请求正文与 caller 一并摘要|
|接纳预留、持久放行计费|S：storage.py:197、227–259|QUEUED 预留，DISPATCHED_UNKNOWN 增 spent；来源材料需同 origin|
|同 rid 幂等及正文冲突|S：storage.py:202–207、261–282|当前合同以 rid 为键；跨 rid 的业务意图等价性仍需另建规范|
|撤回及迟到结果隔离|S：storage.py:261–308|撤回取消 QUEUED；迟到结果保留原 origin，进入 QUARANTINED|
|恢复与单活|S：services.py:22、42–79|OS 文件锁、当前权威读取；已有恢复范围为同机退出/重启及展示缓存回滚|
|原生适配为限定 Casdoor|S：native_provider.py:19、41、151、192；materials.py:60、83|JWT 发行者/受众/时效检查、材料束、标识点读与限定组织枚举；历史密码可在可信组件使用|
|对账关闭为条件收据|S：reconciliation.py:4–44；storage.py:346–430|依赖单未知创建、单效果、停止创建、未来重试排除、已知 A 失效及 B 保留|
|证据类型已细分|S：evidence_semantics.py:16、58、65|RT 内省与真实刷新分别表示；count 与 Find 快照分别表示|
|B 已配置 AND/OR 路径、环境及撤销域|S：b/model.py:23–76、b/engine.py、b/search.py:7|原生效果域要求 partition；重叠/相关撤销效果及动态历史暴露超出现有模式|
|A/AB 有限补证选择及反馈存在|S：a/candidate.py:15–107、a/compiler.py:17、a/bridge.py|W_r 屏障、全观察后继、配置反馈；作用域为有限源模型|
|证书与抽象检查器存在|S：certificates.py:17；checker.py:37、64；abstraction.py:6、71|有限表关系，external_adapter_proof=NOT_PROVED；求解器与检查器共享部分语法/参考内核|
|A/B/AB 接入 M1–M6 尚待补齐|S＋U：mainline_research_closure_v1/ALGORITHM_RUNTIME_MAP.md；online_state 导入定向检查无研究选择器匹配|验收程序固定高层动作，Controller 完成成熟准入与对账|
|历史 157/157 回归|T：mainline_research_closure_v1/VALIDATION_SUMMARY.md、FULL_REGRESSION_V2.log（后者本轮仅由汇总定位）|历史 2026-11-06 版本证据；本轮重跑 0|
|原生校准成本比 1.00|N：auth-lifecycle/docs/experiments/RESULTS.md §§1–4|576 次已知契约运行；A/AB 查询激活 0，H-A/H-B/H-AB 保持 NOT_TESTED|
|M6 原生隔离两轨迹|N：mainline_native_isolation_v1/NATIVE_ISOLATION_PROFILE.md；2026-11-09 总说明|单机、专用组织、可信 OS、限定 UserInfo；跨主机及任意业务效果待验|
|独立区块链创新与部署|U：历史 E36–E39 裁决；本轮 D1/D2 为 P|已有覆盖、判废继续有效；新增链模块部署证据为 0|
|D1 分布式安全、D2 精化与独立贡献|P＋U：本目录规格与证明义务|纸面条件命题可复查，生产实现与通用优势待证|

## 2. 信任边界及遗留风险

现有 profile 信任 OS/管理员、Controller、权威、适配器及冻结配置。M5/M6 使用 Windows 限制 SID、低完整性代理和 DACL，loopback RPC TLS。原生 Casdoor 端点为同机 HTTP。实际任意出口封锁、恶意管理员及多主机 BFT 验证分别保留缺口。秘密加密存储与可信进程中可见明文属于两个能力阶段。

三种停止保证分别保留：C_local 为权威撤回后的新放行截止；C_native 为指定接受路径/材料失效；C_effect 为指定时点后受禁止业务效果的未来路径关闭。UserInfo 拒绝只承担该材料在该端点的观察。任务撤回、链上记录和本地密钥轮换各自需要额外原生依据才能扩大保证。

## 3. 历史裁决恢复

- ae_strict_separation_gate/DECISION.md：X-EL / X-CUBE 的必要额外费用主张被强组合关闭，实现门沿用。
- ae_blockchain_architecture_prior_art_2026_11_09/DECISION.json 与 PRIOR_ART_AND_OVERLAP.json：退出预案、责任接管、分阶段迁移已有 ALP/AH/ICWS 等近邻。
- ae_blockchain_architecture_fullflow_check_2026_11_09/FULL_FLOW_COVERAGE.json：历史潜在披露＋原生有效性＋同版本预留＋有限闭包由标准组合覆盖。
- research_v12/README.md、AUDIT.md：A4/B4/AB3 优化同等开放给 G；单世界 B 建议的权限与跨世界统一策略分别审查。

本轮逐行阅读集中在关键守卫和返回；清单中的 b/engine.py、a/compiler.py 部分范围为结构定位。33 份锁定输入的存在和字节可在 evidence/INPUT_MANIFEST.json 复核，整个工程全部文件检查属于范围外。用户粘贴 AGENTS 指令作为本轮最高项目约束；目录定向检索未发现额外 AGENTS.md。
