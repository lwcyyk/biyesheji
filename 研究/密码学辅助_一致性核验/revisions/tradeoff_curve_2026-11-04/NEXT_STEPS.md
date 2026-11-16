# 剩余问题、复现与论文定位

2026-11-04。本轮完成来源位置核对、零误差资源审计、T2主分支上下界和有限LP、严格的类内秩分离区间、ramp/P04查杀、分离门及独立冲突引理。

## 1. 当前结果

| 内容 | 当前状态 | 贡献口径 |
|---|---|---|
| d、k、r与观察权限分开 | 已完成 | 修正研究对象 |
| d=k=4、r=2/3的精确Δ | OPEN | 显式上下界，匹配对偶待求 |
| d=k=4、q+1>400n的一段R_min(ε)=3 | 手工证明成立 | 非零误差区间的精确类内资源结果，推论型，优先权与独立价值未决 |
| 一般核—轨道LP | 手工双向归约 | 有限精确表述，闭式解未完成 |
| 秩1层与k=n全支持边界值 | 手工证明成立 | 群平均与码重量计数的自然组合 |
| 随机量、秘密乘法和通信账本 | 已完成理论计数 | 完整性能测量未运行 |
| k-wise独立强化基线 | 手工论证成立 | 经典方法，淘汰普适Θ(n)独立随机量主张 |
| 空支持冲突引理 | 手工证明成立 | 经典完美保密定义的直接推论 |
| 通用协议实现分离门 | NOT_PASSED | 仅类内秩分离通过，通用优势仍待证明 |

## 2. 下一轮的数学入口

优先固定d=k=4、r=3、n=5的最小超基字典，随后再处理r=2。先在纸面上列出核点相对于各四列基的零模式及其交叠约束，检查对称化后的每一种状态是否覆盖全部原始掩码分布。

下一轮需要的关键成果为以下任一项。

1. 给定明确字典族的匹配原始/对偶证书及自包含一般证明，得到真正的Δ闭式。
2. 在同域、同支持族、同观察契约下，证明两种表示的中间档误差严格不同，并明确是否超出已有r5推论。
3. 若完整曲线仍难求，扩大T2-GAP的精确最小行数区间，证明更紧常数并核对这些推论的先例。

新增候选机制实现继续受分离门约束。整数算术检查、文献工具及对照计数与候选实现分别登记。

## 3. 实现门还缺什么

SG6已经给出所有至多两行共享掩码与三行构造的严格误差分离。它使用不同的行数资源，证明一个受限类的必要代价。

面向主线的独立密码学贡献还需要解释共享MV关系为何由真实功能强制保留，并允许通用对照使用相同的服务接口、批准、随机源、底座和输出权限。若任务只要求给定S后的幅值隐藏，逐项非零掩码已是更强的简单对照。若要求E隐藏S，私密零判断和标准加性编码同样需要进入比较。

所有方法应统一计入采样、非零检查、秘密域转换、输入分享、私密结果交付、预处理、在线通信和重试。只有出现同契约的必要成本差距，才进入机制实现。

## 4. PI增量获取清单

### 出版者访问失败

| 目标 | 本轮结果 | 获取入口 |
|---|---|---|
| Yamamoto，1985日文原文/1986英文翻译的(k,L,n)方案 | TD01参考[14]核实题名、刊物和页码，出版者PDF请求403，候选DOI身份仍需出版者元数据复核 | https://onlinelibrary.wiley.com/doi/pdf/10.1002/ecja.4410690906 |
| Shannon，Communication Theory of Secrecy Systems，1949 | 出版者PDF请求403，原始全文未核读 | https://onlinelibrary.wiley.com/doi/pdf/10.1002/j.1538-7305.1949.tb00928.x |

### 后向原始文献

- *Nonperfect Secret Sharing Schemes and Matroids*，Kurosawa等，EUROCRYPT’93论文集，126–141。入口来自TD01[10]及TD02[16]，出版年存在会议年/论文集年差异，优先核对原版。
- *Lower Bound on the Size of Shares of Nonperfect Secret Sharing Schemes*，Okada–Kurosawa，ASIACRYPT’94论文集，LNCS917，34–41。入口来自TD01[12]。
- *Randomness in Distribution Protocols*，Blundo、De Santis、Vaccaro，Information and Computation 131(2)，111–139，1996。入口来自TD02[26]。
- *Improving the Linear Programming Technique in the Search for Lower Bounds in Secret Sharing*，Farràs、Kaced、Martín、Padró，IEEE Transactions on Information Theory 66(11)，7088–7100，2020。入口来自TD02[22]。
- MDS重量枚举的更早原始来源，TD08参考[3]的Theorem25.7。当前已经用TD08正文公式完成计数子项归属，更早源头仍可补齐。

三份旧被引页面原始存档继续保留缺失状态，已有API快照可用于后续版本比对。全体前向论文的正文核读仍未闭合。

## 5. 本轮验证与证据层

### 手工论证

TRADEOFF_CURVE包含条件采样上界、旧下界常数复核、核LP双向性、T2-GAP、秩1层和全支持精确边界族。RESOURCE_LEDGER包含k-wise独立采样与资源必要性。INCOMPATIBILITY_LEMMA提供完整短证明及最小域见证。以上均保留外部审稿与证明助手复核限制。

### 普通机器算术

check_arithmetic.py只检查整数和有理数。四个素数参数、两个严格间隙实例、两个满重量计数恒等式均通过。原始结果为ARITHMETIC_CHECKS.json。它没有生成掩码、求解LP或执行密码学协议。

### 原始文献和实测

本轮20次HTTP请求保留全部台账，其中9组arXiv查询成功，3次Semantic Scholar题名查询429，两个出版者PDF入口403。共取得并定向核读6篇新全文。继承16篇来源逐份哈希核对一致。

性能、MPC、有限掩码枚举和新的机器定理证书均为未运行。成本表中的数字为理论计数。

## 6. 复现命令

```powershell
$python = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$study = 'D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_curve_2026-11-04'
& $python -X utf8 -B "$study\check_arithmetic.py"
& $python -X utf8 -B "$study\evidence_tools.py" inspect "$study\inspect_new.json"
& $python -X utf8 -B "$study\evidence_tools.py" inspect "$study\inspect_mds.json"
```

可选的联网重新获取会产生新时间与版本，原始响应采用独立文件保存。

```powershell
& $python -X utf8 -B "$study\evidence_tools.py" fetch_serial "$study\research_requests.json"
```

本轮网络批次为research_requests、download_requests、followup_requests、mds_request。所有实际URL、时间、哈希和错误以HTTP_REQUESTS.jsonl为准。

HISTORY_HASHES_BEFORE.json及结束核验记录用于检查历史材料保持。ARTIFACT_SHA256.json保存交付快照哈希。

结束核验记录为VALIDATION.json，共16项证据管理检查通过、0项失败。133份被纳入核验的历史文件哈希一致，22份来源文件和20个HTTP响应哈希一致。该检查与8项普通算术核对分别登记，均不替代一般数学证明。

## 7. 论文定位

目前可主张研究一个明确受限观察类的统计隐私极值，保留r5精确点，并给出高维中间档的严格界及一段精确最小行数区间。该表述须附输入独立共享M、完整观察、支持已知和硬无抹除等条件。

强独立密码学原创尚待一般中间点、先例差异或必要成本分离的进一步证据。现阶段适合把这些结果作为密码学辅助线的理论候选与边界分析。通用协议优势、支持隐私新原理以及主线配置安全，各有独立验收条件。
