# 最小成熟工程方案与后续执行申请

本稿是具体可审查方案，未修改以下任何源码，也未编写新检查器。成熟工程与候选算法创新分开；新机制严格分离门继续未通过。

## 1. 文件级最小清单

根：`D:\毕业设计\auth-lifecycle`。现有文件：

- `src/auth_lifecycle/online_state/storage.py`：受控typed snapshot及后续独立dsat_commit；保留旧recover/state_projection/单未知关闭合同。
- `src/auth_lifecycle/online_state/services.py`：新增管理scope的导出/提案路由及权限表接线，不授代理通用原生或管理secret访问。
- `src/auth_lifecycle/online_state/native_provider.py`：增加相关Inbox/journal全条目无秘密导出；旧results操作视图保留，证据视图另建，冲突显式返回。
- `src/auth_lifecycle/online_state/lab.py`及相应隔离profile：仅在集成授权后增加精确管理权限；旧角色能力与默认行为回归。
- `pyproject.toml`：若采用成熟流库，仅增可选dsat依赖并冻结版本/许可证；当前项目dependencies为空，未有NetworkX依赖。

拟新增路径（均未创建）：

- `src/auth_lifecycle/online_state/dsat_projection.py`：strict typed输入、证据去重/来源/问题与O提案，复用C11/C13而保留旧兼容语义。
- `src/auth_lifecycle/online_state/dsat_flow.py`：成熟整数流后端薄适配、输入/费用与数学证明导出。
- `scripts/check_dsat_certificate.py`：独立标准库检查，重建完整弧/残量/势/割，不导入求解器或其建图函数。
- `tests/test_dsat_projection.py`、`tests/test_dsat_certificate.py`与`tests/fixtures/dsat/`：离线合成合同/篡改反例和显式预期。

独立库候选为NetworkX整数min-cost-flow/network-simplex；具体版本/分发哈希/许可证和资源界待S2冻结，本轮未安装/导入。现有cryptography可选依赖只在可信材料验证/加密边界复用；秘密不进入数学检查器。旧C15检查脚本保持原义。

## 2. S1：可信导出与纯投影

依赖C01—C03/C10—C13。输入为允许的权威/原请求/证据条目；输出无秘密typed snapshot、全部冲突/缺口、U/E/c/D候选与scope/O提案。源容量、来源与持续D不能自动填true。

回归风险：新增字段泄露handle/material；snapshot版本不一致；旧inbox行为被更改；legacy HTTP缺项被升级。验证：单独合成夹具、原摘要重算、跨origin拒绝、冲突/尾行/别名保留、旧API输出相容。退出：字段与权限边界具备离线可验收样本；失败则拒绝片段或UNKNOWN，不写关闭。

## 3. S2：标准流与独立检查

依赖完整D_fin数学输入及04。输出可行流/势或不足割、m/d/R/H和分层状态。求解器、规范化/证据连接与检查费用分别记账。

后端要求源需求−h、汇需求+h、其余0，不能采用默认零需求得到零流。NetworkX候选公开接口的流/费用输出不预设包含势；若未给势，需在完整残量网络加到全部节点的零费用超源，用成熟Bellman–Ford求距离作为势，费用另加O(VM)。失败/负环时拒绝这份最优性包。不可行时另用成熟max-flow/min-cut输出不足流与割，或由选定算法提供同等证据。

O(hVM)是M01所述逐次最短增广算法的可实现求解包络；连同一次全残量势提取可写O((h+1)VM)加位费用。不能把该理论界直接贴给尚未冻结的NetworkX network-simplex后端。库版本、实际算法/资源界必须在实施前核读冻结；超过工程资源限额返回UNKNOWN_RESOURCE_LIMIT，不牺牲正确性求通过。

回归风险：漏残量弧、错用反向费用、float/bool、改网络、同birth多计、错误容量截断。验证：A01/A06手工流/势、A19割与输入/流/势/目标/摘要单字段篡改；检查器不得回调求解器“验证自己”。退出：授权离线测试达到明确预期，仍标合成合同/条件结果；失败停用本包，不删除旧O。

## 4. S3：版本化提交与恢复

依赖S1/S2和真实部署前提准入。新dsat_commit在当前Authority事务中比较base authority/O revision及已审证据/profile/scope/frame，保存历史、证书和O转换。新增JSON状态命名空间需版本标记/默认行为，是否需要DB migration在实施时按实际最小改动判断，不预先升级整个数据库。

旧CLOSED/1记录原字节不变；新证明不写旧单未知window CLOSED。DSAT启用profile必须禁止旧消费者把legacy obligations视图误认完整新typed O；对重叠全局关闭/自动化先关使用入口，直到兼容测试证明scope。旧窗口退出要经过对应真实接口与授权。

风险：跨库TOCTOU、原生前沿变化未进authority、部分提交、恢复丢typed O、旧客户端忽略新字段。独立验证：事务前后快照、失败点/重启保持、证书依赖变化及并行A/B守卫。失败：不提交强声明，保留旧O与提案/缺项，持久化费用和UNKNOWN。

## 5. S4：离线验收

将24例补成显式合成证据/contract/数学包，锁expected state/cert/O/费用。只运行经批准的新增离线文件；旧test_evidence_semantics/test_reconciliation仅在单独选定且源码范围确认后回归，不启动整套tests或native CLI。现有test_reconciliation在导入时会装载独立脚本，这也属于执行，需要资格。

退出：离线数学、scope/拒绝、冲突/O守恒和兼容性的真实结果报告。源到原生事实不因离线测试通过而自动成立。当前所有步骤NOT_RUN。

## 6. S5：受控故障与原生

依赖独立环境/账号/组织、固定运行实现、批准读取/处置/故障接口、额度和清理责任。沿07收缩试验；Issue响应丢失、Go检查后插入前位置没有现成通用注入证明，不能把refresh hook免费迁用。

退出：有限声明范围的真实证据与失败/未知分母、B保留和清理结果；任何越界、泄露、额外writer/创建、来源冲突或预算不足停止，保O并隔离环境。没有统一有限完全清理承诺。

## 7. 已完成的后续执行申请正文

**申请范围：S1—S2的离线成熟工程最小闭环。** 仅限新增typed数据/证据导出设计的离线部分、纯投影、成熟流适配和独立证书检查，及为其准备明确的合成夹具。现有运行权威/Provider/API路由修改和真实状态读取/写回先不启用，原生配置/账号/秘密均不触及。模块/测试执行另以批准清单明确；依赖安装也需列范围。

交付为上述最小文件差异、合成输入/证书、离线结果与费用/兼容说明。S3真实提交及S5原生仍须补真实来源/持续D/部署/清理准入并单独授权。当前申请状态PENDING，未获得本轮执行资格。

这份申请用于把已审成熟规格推进到工程阶段；没有发明新算法或调用T3/旧机制来规避创新实施门。
