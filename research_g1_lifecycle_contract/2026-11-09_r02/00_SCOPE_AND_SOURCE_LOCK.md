# G1-R02 范围与来源锁

主课题：《面向用户与 AI 智能体的全生命周期密码与凭据管理系统》。本轮任务：固定Casdoor Refresh的微步骤、失败后继、创建容量、费用与有限研究模型映射。过程为当前对话内知情模型辅助源码核读与纸面证明，外部核验待取得。

目录按2026-11-09启动日期保留，跨至2026-11-10（Asia/Shanghai）完成；各证据附UTC时间。R01及其他历史文件保持原字节。

## 1. 冻结来源

| ID | 来源 | 版本/读取范围 |
|---|---|---|
| R01 | `D:/毕业设计/research_g1_lifecycle_contract/2026-11-09_r01/` | 当前对话已完整编写/核读00—08，复用前先核对33项既有输出哈希，全部一致；索引与源码绑定沿用 |
| PY | `D:/毕业设计/auth-lifecycle/src/auth_lifecycle/` | 26份R01选定源码与closure锁；重新核读刷新相关Controller/Storage/Provider/HTTP/材料/恢复/有限语义；新增plant、独立参考与B kernel文本 |
| GO | `D:/毕业设计/research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0/` | 本地Git HEAD为`528a0213f01caf70b9f41009cbf7b2f67bdd67ec`；核读路由、controller、RefreshToken、生成/插入/过期/删除/内省及cookie-free UserInfo过滤路径 |
| ARCH | M3/M4/M6的model_sources与MODEL | 三份Go核心文件与归档哈希逐项绑定；不把不同批次Python适配器视为同版本 |
| HIST | M2—M6验收、M3 `CAPABILITY_AND_CLOSURE_CONDITIONS.md`、`PYTHON_TRANSPORT_SOURCE.json` | 复用历史结果；本轮新增核读固定源码责任及历史stdlib片段；未重跑 |
| MODEL | S11多尝试C1—C7、P1—P4、E1—E7；现有A/B/AB与检查器 | 沿用标准流/有限安全语义；本轮纸面合同未送入求解器 |

路径、SHA-256、符号/行范围和使用范围见 [SOURCE_INDEX.json](evidence/SOURCE_INDEX.json) 与 [SOURCE_LOCK.json](evidence/SOURCE_LOCK.json)。Go归档比对、Git对象和读取限制见evidence。源码身份只支持固定版本，源到运行二进制的语义忠实仍是显式部署前提；历史发行物摘要匹配不替代该证明。

## 2. 证明对象和分项范围

本轮区分四层：

1. 锁定代码的本地顺序/状态性质。
2. 对固定源处理与标准传输/数据库假设的条件性合同。
3. 该合同到已有L0语义的纸面嵌入及策略安全转移条件。
4. 当前A/B/AB source语法、运行投影与真实派发的实际接入。

第一层可逐函数证明；第二层明确假设；第三层仅为纸面映射；第四层仍有具体缺口。各自裁定，局部成功不会自动提升其余层。

## 3. 采用的最小profile族

P_local：当前可信权威/托管、单活持久状态、鉴别能力配置、固定账户/客户端/批准代次，原生调用仅由该Controller链产生；当前事务与密钥无回滚。

P_direct：在P_local上，增加每放行至多一次provider perform、固定无代理/无重定向/无应用级重发传输、一次完整HTTP请求至多一次AS handler执行、固定源/标准数据库语义。容量对象限该handler的一次新记录/材料束创建。

P_closed：在P_direct上，所有目标后续刷新、外部持有者和在途创建均封口或计入I；单位创建代次唯一，来源与失效证据可靠持续，范围读取获准完整，乙有明确独立支持。该层才支持声明材料范围关闭。

每项假设A01—A12详见04与05。原有单未知收据只承担其受限实例。任意网站会话、其他RP、离线JWT、ID token用途和已接纳业务效果均需额外接受路径合同。

## 4. 权限与成果类型

新增候选实现、参考实现、求解器、穷尽程序、测试重跑、原生/账号操作、外发和新代理均为0。辅助程序仅用于路径/文本、AST、哈希、Git对象和报告QA；项目模块导入执行0。没有读取/解封AT、RT、密码、cookie或评分秘密。

复用academic-research-suite的来源/论断纪律，在当前对话内完成。COL2026主动检索暂停、FS23延期；VPass废弃；G1独立创新继续ANALYSIS_ONLY。A/B/AB保留研究核心地位，G1为其提供可靠外包络，G2动态副作用研究另交接。

## 5. 核心裁决预览

一次源handler至多一次AddToken成立；一次持久放行的直接容量1依赖列出的完整调用/传输前提。无限制后代不能装入容量1。actual_sends是预记账机会计数。本文建立一个条件性、失败覆盖的纸面合同；当前A/B/AB的自动/原生接入和全部费用映射仍需具体桥接，详见09。

## 6. 交付导航

| 稿件 | 内容 |
|---|---|
| [01](01_CASDOOR_REFRESH_CALL_GRAPH.md) | 调用链、字段和事件蕴含 |
| [02](02_MICROSTEP_TRANSITION_MODEL.md) | 真实阶段、关系合同和不变量 |
| [03](03_FAILURE_SUCCESSORS.md) | 失败、迟到、重放与并发 |
| [04](04_CREATION_CAPACITY_PROOF.md) | 直接容量及假设/反例 |
| [05](05_REFINEMENT_PROOF.md) | α与P1—P8 |
| [06](06_COST_AND_RESOURCE_COVERAGE.md) | 多种G/Q、原生与完整费用 |
| [07](07_AB_MAPPING_AND_BASELINES.md) | 最小映射、表示边界与强基线 |
| [08](08_COUNTEREXAMPLES_AND_VALIDATION_PLAN.md) | 11项纸面反例与NOT_RUN计划 |
| [09](09_G1_R02_VERDICT.md) | 分项裁决、十问和唯一下一步 |
