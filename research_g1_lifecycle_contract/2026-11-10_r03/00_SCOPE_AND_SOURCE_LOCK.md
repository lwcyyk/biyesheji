# G1-R03 范围与来源锁

日期：2026-11-10，Asia/Shanghai。主课题：《面向用户与 AI 智能体的全生命周期密码与凭据管理系统》。本轮限“单次未知Refresh＋父p＋独立乙支持b”的纸面表示和保持检验，G1创新状态继续ANALYSIS_ONLY。

## 1. 继承与权限

R01/R02主报告在当前对话已完整编写/核读，本轮复用前将其53项既有输出与原QA逐项匹配，全部一致，两个QA回执另行固定；见evidence/PRIOR_VERSION_BINDING.json。继承R02：本地去重/预算/来源不变量、条件直接c_i=1、预记账含义、同父并发与父撤回后迟到创建反例、完整原生映射缺口。

定向重读当前L0/A定义、搜索、参考、策略/不可行证书检查、source compiler/audit、有限表关系及相关B语义。源路径/哈希/符号见 [SOURCE_LOCK.json](evidence/SOURCE_LOCK.json)，结构化论断索引见evidence。其他原生/论文材料按R02的实际阅读范围复用，不重启文献检索。

新候选/参考实现、求解器、生成器、穷尽程序、schema.validate/策略检查器调用、历史测试重跑、原生/账号/外发操作及新代理均0。附录JSON由手工逐项填写，为静态合同数据；仅做JSON文本解析与文档QA，未执行项目模块或数据所描述的动作。源码、R01/R02及历史结果原字节保留。

COL2026主动检索暂停，FS23延期，VPass废弃；外部数学/系统核验待取得。沿用academic-research-suite的来源与主张纪律，本轮为知情模型辅助纸面研究。

## 2. 本轮分开判定的三个层次

| 层次 | 对象 | 本轮初步裁决 |
|---|---|---|
| 通用L0数据语言 | 任意有限state、事实/批准/义务、观察边、多预算键 | 固定场景可保守编码；无需新增顶层schema字段 |
| 当前A source与A1/AB选择器 | B目录＋point/probe/session＋compiler生成的bundle | 能保留不透明责任；完整进度/来源/费用/迟到解除尚缺桥接 |
| 当前W_h执行门 | 每个动作全部观察后继须有界到达完整终态 | 允许持续UNKNOWN时，安全撤回/乙使用也可能被排除；具体路由见04/05 |

表达能力、实际派发资格和真实服务前提分别管理。静态JSON符合纸面语法不等于源审计通过、已有运行接入或原生保证。

## 3. 适用条件

沿用R02 A01—A12，尤其单调用/单dispatch、固定源/DB忠实、所有目标后代入I或封口、合法完整读取及持续失效。新增本例明确条件：

- B-independent：处置p或本次直接子代c的原生影响不会使b失效，b没有共享RT/撤销域；登记字符串不同仅是表示，原生独立性需可靠合同。
- B-window：分析窗口内b与乙批准保持适用；乙只要求一次声明的UserInfo能力及可观察执行。到期、用户另撤回、服务语义变化等需扩分支或退出当前profile，当前没有自动识别全部违约的证明。
- 固定一次放行、一次父处置、一次主动补证、至多一次迟到结果读取、一次子处置、一次乙调用的有限过程；失败后允许停止并保留UNKNOWN。它不覆盖任意重试策略全集。
- FOUND_C_BOUND/P_INACTIVE/C_INACTIVE等观察是可靠证据解释结果，须由具体接口证据支持其解释，原生适配和证明责任保持。

## 4. 交付导航

| 稿件 | 内容 |
|---|---|
| [01](01_MINIMAL_REFRESH_SCENARIO.md) | 事件、W0—W3与真实状态 |
| [02](02_L0_A_SYNTAX_AUDIT.md) | 现有字段/语义/源码定位 |
| [03](03_PAPER_EMBEDDING.md) | 完整手填L0/A样例、K与抽象 |
| [04](04_TRANSITION_AND_W_PROOF.md) | P1—P8、Post及W屏障 |
| [05](05_COUNTEREXAMPLES.md) | 两项要求反例与W路由障碍 |
| [06](06_MINIMAL_EXTENSION_ANALYSIS.md) | 现有复用与最小扩展责任 |
| [07](07_COST_AND_BASELINE.md) | 成本与强通用方法 |
| [08](08_G1_R03_VERDICT_AND_G2_HANDOFF.md) | 十问、分项裁决、唯一下一步 |

完整静态数据为evidence/PAPER_L0_INSTANCE.json、PAPER_PROGRESS_SLICE.json和PAPER_A_SOURCE.json，均按纸面样例管理；未生成机器ACCEPTED或实验结果。
