# G2-R03：范围、继承结论与来源锁

日期：2026-11-10。对象：固定 Casdoor v4.25.0 源码、现有 Controller/Provider 和历史 M2—M6 证据。研究方式：当前对话内知情模型辅助源码核读、纸面轨迹和条件证明；外部数学及安全复核待取得。

## 1. 本轮结论

关闭候选：**在已知轮换开启的固定 profile 中，通过独立发行 z0 再刷新为 z1，识别旧甲任务 i1/i2 的来源、撤销关系或创建终态，并据此取得独立算法增量。** 已读代码未提供该观察联系；旧 handler 可以在整个验证流程结束后继续创建。合法只读证据充分时，可删除这条主动路线并减少新增材料与请求机会。

支配结论具有范围：04—06 定义的 F0 和完成子域 D1。权限不等、账户策略变化、资源耗尽、目标要求新凭据等情形另列。全部 Casdoor 状态上的无条件支配没有建立。

## 2. 冻结问题与证据类别

甲 gA 已撤回；p 为旧父 RT；i1/i2 已放行且结果未知。乙 gB 有独立合法 b。管理批准 gV 若成立，须新建自己的发行/刷新请求与来源。目标：停止甲的新受控放行，可靠处理甲的旧创建机会及声明接受路径，保留乙的一次合法 UserInfo 和仍获准支持，并结清验证路线自己的责任。

`C_local`、命名材料失活、创建前沿关闭、任意 RP 会话关闭、业务效果停止分别管理。UNKNOWN、安全退出与完整成功分别记账。

| 标记 | 含义 |
|---|---|
| H | 历史已记录事实；仅继承原批次、分母和测量范围 |
| S | 当前锁定源码的静态事实；源到运行二进制符合性仍待证明 |
| D | 由 S 与列明前提得到的纸面推导 |
| C | 条件命题、反事实轨迹或配置拓展；本轮未运行 |
| P | 拟议工程规格；当前程序尚未具备完整接线 |

全文数值例均为 C 类条件费用，真实新 API 调用和测量数为 0。

## 3. 继承与不变边界

完整继承同对话已经核读的 G2-R02 十稿、静态模型、费用、策略编译和准入卡。`evidence/PRIOR_G2_R02_BINDING.json` 记录其 35 项旧输出与旧 QA 的逐件匹配，并额外锚定旧 QA。原输入锁 218 项逐件复核，结果见本轮 SOURCE_LOCK。

有限、完整形式模型到通用信念 AND/OR 的编译保持观察、策略、安全、目标及轨迹费用。同能力精确 G 达到同策略空间最优 Q。合成 I_INFO 的 8/10、λ=6 的 12/10 限于 SYN_BOUNDED；本轮重新计算原生成本。

真实 DIAGθ、EnsureQ、EnsureRoot、RootCut、完整 Fence 仍缺可靠映射。T3、旧淘汰结论和原 A/B/AB 范围保持。COL2026 主动检索暂停，FS23 延期，VPass 废弃。

## 4. 来源导航

Go 根 `research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0`；引用提交 `528a0213f01caf70b9f41009cbf7b2f67bdd67ec`。逐文件字节哈希及与该 Git blob 的比较放在 SOURCE_LOCK；换行规范化相符与原字节相符分别记录。源码到已运行二进制的可复现构建仍为 UNPROVED。

实际结果：锁定264个输入文件；继承218项输入全部与原锁一致。重点10份Go源码原字节均受CRLF/LF差异影响，LF规范化后10/10与指定提交内容相符；本轮未改源码。35项前轮输出与前轮QA清单匹配，前轮QA文件另行固定。

Python 根 `auth-lifecycle/src/auth_lifecycle/online_state`。

| ID | 文件与核心定位 |
|---|---|
| C01 | storage.py：24—40 公开投影，161—259 批准/放行/同 origin，264—395 迟到/撤回/处置/窗口 |
| C02 | services.py：103—151 处置/lookup/调用，153—217 对账，297—309 RPC 权限 |
| C03 | native_provider.py：41—149 原生调用/收件/标识，151—224 点读与单未知枚举 |
| C04 | native_http.py：101—113 reserve，117—189 范围与先记账，194—232 单次发送/结果 |
| C05 | enumeration.py：全文，单 Find 的完整性与单来源充分条件 |
| C06—C09 | lab.py 79—92；isolation_acceptance.py 111—150；native_isolation.py 64—84；native_isolation_service.py 全文 |
| C10 | materials.py：14—101 类型、验签、账户/client 绑定及内部摘要 |
| G01 | controllers/token.go：37—100 列表/点读，230—428 发行入口，500—554 撤销，634—757 内省 |
| G02 | object/token_oauth.go：27—165 分派与后写，290—388 password 发行，494—539 策略检查 |
| G03 | object/token_oauth_util.go：351—393 撤销，562—769 刷新 |
| G04 | object/token.go：28—54 Token 字段，56—100 列表/主键，106—218 hash/用户/后写 |
| G05 | object/token_jwt.go：630 起发行束/claims；复用 G1 已读范围 |
| G06—G08 | object/check.go 232—319、646—742；object/check_util.go 41—125；object/user.go 936—1040、1315—1378 |
| G09—G10 | routers/authz_filter.go 36—58；object/ormer_session.go 32—53 |
| G11—G12 | controllers/account.go 774—803 UserInfo入口；routers/auto_signin_filter.go 28—142 cookie-free Bearer记录/有效期/用户检查，复用并补读G1来源 |
| H01—H04 | M6 NATIVE_ISOLATION_PROFILE；M4 COMPLETENESS_AND_ATTRIBUTION；M3 CAPABILITY_AND_CLOSURE_CONDITIONS；EVIDENCE_SEMANTICS |

SOURCE_INDEX 给出绝对路径、实际核读范围、主张与来源对应。已继承论文保持原阅读限制，本轮无需扩目录或重述未读证明。所选源码摘录在 evidence/SOURCE_EXCERPTS.md。

## 5. 执行与版本

本目录是当前连续任务首次创建的未交付目录，本轮接续完成；旧文件与历史目录保持原字节。现有 PRIOR_G2_R02_BINDING 作为最初绑定原样保存。

实际工具工作仅限文本/AST/哈希/JSON/文档取证和只读 Git 身份比较。项目模块导入执行、求解器、穷举、测试重跑、真实 API、账户变更、凭据读取导出、外发和新代理均为 0。辅助文档处理与候选机制实现分开登记；本轮未编写机制实现代码。

当前状态：`ANALYSIS_ONLY / NOVELTY_NOT_ESTABLISHED / COVERED_BY_MATURE_COMPOSITION`。本轮可进入后续纸面工程规格阶段，机制实现门继续关闭。
