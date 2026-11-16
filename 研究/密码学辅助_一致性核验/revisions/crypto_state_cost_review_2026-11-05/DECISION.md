# 一次性裁决：条件覆盖，冻结主动机制合成

2026-11-05，Asia/Shanghai。

**主裁决：`REQUIREMENT_OR_EVIDENCE_MISSING`。条件结果：F1–F3 已有成熟方法覆盖映射；严格密码学分离实例为 0。**

研究者明确确认：“这些约束尚未确定，本轮给出条件覆盖与冻结裁决。”实际故障模型、可信写入预算、在线访问许可、撤回 ACK 时限和合法 B 中断上界尚未确定，主度量因此保持未选定。该事实足以决定当前投入：冻结本辅助线的主动机制合成，保留成熟密码机制支撑主线及现有归档成果。

## 本轮改变判断的结果

1. **找到直接的优化强对照。** CRISP §III.B–C 已同时提供批处理与阻塞 Checker；让应用撤回 ACK 等待 Checker 后，可以在同一强承诺下合并持久更新。Nimble §3.1–3.2 已提供签名状态/位置、expected-index 更新、新鲜 nonce 读最新回执，并允许大状态留普通存储、摘要进入账本。这些具体协议足以排除把简单批量或远端摘要当前性包装成独立创新。
2. **区分恢复安全与恢复可用性。** Memoir-Opt 节省 NVRAM 依赖可靠关机 checkpoint、PCR 和 UPS 等条件；异常破坏性断电后的拒绝旧状态并不保证恢复 B。Nimble 多数 endorsers 永久丢失也保留相同活性边界。成本比较需要完整计入这些资源。
3. **完成可手工复核的最小覆盖实例。** 严格顺序撤回的受限离线模型需要每个恢复可区分承诺留下持久区别，标准状态连续性可匹配其次数阶数。四项撤回、到达 `[0,1,2,6]`、ACK 窗口 3、提交耗时 1 的实例恰需两次组提交，优化通用基线同样达到两次。迟到请求加新批准由来源/pending 事务与当前状态后端条件覆盖。

以上为标准近邻映射、手工边界与条件组合。它们支持停止无差距构造，尚未构成新的密码协议、安全归约或独立原创资源权衡。

## 最终问题逐项回答

| 问题 | 裁决 |
|---|---|
| 既有授权/撤销安全目标是否存在 | 存在；本地状态连续性与来源绑定直接服务主线 |
| 是否成立新的独立密码学功能需求 | 本轮未建立。受限披露分支继续 NOT_ESTABLISHED；现有状态功能可由成熟方法条件实现 |
| 相对成熟组合还剩何种精确增量 | 当前为 0 项已证明增量。实际剩余是恢复/ACK/B/在线合同、生产持久接纳及原生截止前提 |
| 是否已有严格分离实例 | 0。F2 的两次写对四次朴素写只比较到弱实现，优化 G 同样两次 |
| 缺失的是哪类证据 | 首要为资源与故障需求；其次为部署实现、来源闭包和原生能力证据。尚无确定的新增密码证明对象 |
| 本轮能否给全部部署判定成熟覆盖 | 条件模型的覆盖已给出；生产符合性继续未决，因此总裁决选 REQUIREMENT_OR_EVIDENCE_MISSING |
| 是否存在已证系统增量 | 尚无新的实测或严格系统差距。组提交/状态分解可支撑工程，但本轮不据此选 SYSTEMS_ONLY_INCREMENT |
| 是否进入下一阶段机制实现 | 实现门 NOT_PASSED；最小实施规格未激活；候选代码 0 |

G0 的本地检查仍需当前批准、来源、任务绑定与原子接纳；G9 的枚举/逐材料处置仍需查询授权、完整分页、派生归属、并发截止和 B 保留。恢复当前性分析没有取消这些前提。R 本地状态安全没有自动改变 AS/RP 的接受策略。

## 覆盖成立与失效条件

- **可信当前数据库分支**：G1 的事务、来源账本与持久 pending 足以实现本地功能；数据库自身当前性和合法恢复是前提。
- **离线任意断电分支**：G2-Basic/受保护当前锚点配合认证普通存储，给出 O(b) 逻辑可信更新上界。本文 H-O 在明确排除外部当前信息的协议类中给出 W_local≥b；物理写字节、故障修复与通用协议最优性保持开放。
- **可靠关机分支**：G2-Opt 的慢持久写可按启动/检查点计，PCR 操作、可信关机、UPS 和活性成本保留。
- **在线当前权威分支**：G3 支持认证更新与恢复新鲜读，写入/通信转移到权威；同条件可使用缓存、增量和合理批量。多接纳者还需一致当前性与撤回协调。
- **仅历史一致分支**：SUNDR/LCM 的单独保证按原文限制使用；加入在线权威或可信 checkpoint 后再比较强合同。

如果攻击者可以回滚全部可信当前信息，同时要求离线恢复、强撤回 ACK 和合法状态恢复，先按 H-O 的不可区分性边界审查合同。若只有部分数据损坏或缺失，可返回 UNKNOWN/ABORT；合法 B 的有界恢复需要可用数据和公平调度前提。

## 冻结与精确重开条件

当前研究工作流转为维护状态。后续使用成熟签名/MAC、认证信道、可信事务、受保护锚点或在线当前性机制支撑主线，选择取决于确认后的合同。既有 B、七种机制淘汰结论、PSCD 与数学证书归档及历史成本函数全部保留。

**最有信息价值的下一项外部输入**是一份研究者确认的资源合同，包含一个具体恢复故障、撤回承诺点、B 可用性目标、在线访问许可及可量化的写入/通信预算。实际部署事实与设计选择分栏记录。无需再次询问尚未成立的私密验证参与方来阻塞该合同。

满足以下证据链才重开资源增量方向：

1. 上述合同明确且与主线一个安全决定对应；
2. 给出优化 G1–G5 在同条件下仍超出该预算的具体证据，或有效反例推翻本轮覆盖条件；
3. 给出输入族、主度量、最强具体 G、候选结构、完整成本和至少一个严格差距实例。

若强基线满足同一合同和预算，即停止该候选投入。若优势依赖降低 ACK 强度、无限拒绝 B、隐藏可信状态/外部通信成本，也停止投入。私密证明分支只有在真实受限披露职责被确认后单独重开；机制 B 的终止状态保持原裁决。

## 交付、证据层及复核

| 交付 | 内容与证据等级 |
|---|---|
| [PROBLEM_AND_MODEL.md](PROBLEM_AND_MODEL.md) | 需求状态、F_AUTH_CURRENT、攻击查询/失败事件、条件模型、成本向量、源码定位 |
| [GENERIC_BASELINES.md](GENERIC_BASELINES.md) | 7 篇状态/存储近邻的定向正文定位、2 份原生近邻、G1–G5 完整资源与假设 |
| [INPUT_FAMILIES.md](INPUT_FAMILIES.md) | F1–F3 手工合法/攻击轨迹、受限下界、最小组提交计数、条件组合及反方审查 |
| [SEPARATION_CLAIMS.json](SEPARATION_CLAIMS.json) | 空候选列表、条件结果、严格实例为 0、判废/重开条件及机器可读状态 |
| 本文件 | 一次性方向裁决与冻结条件 |

原始输入哈希见 [INPUT_MANIFEST.json](evidence/INPUT_MANIFEST.json)；新论文版本和哈希见 [NEW_SOURCES.json](evidence/NEW_SOURCES.json)；HTTP 台账保留响应文件。新 PDF 结构预检 5/5 PASS。SUNDR 页结构继续 UNAVAILABLE，采用章节正文锚点。Ariadne 必要性原文未补取，仅将 REBOUND 中的引用作为二手线索；本轮没有依赖它给新的下界。

只读核对 [SOURCE_AND_RAW_AUDIT.json](evidence/SOURCE_AND_RAW_AUDIT.json) 重新计算了 511 个历史事件哈希、25 个冻结源码条目，全部匹配。21 项本轮起始输入哈希保持一致。当前与历史的 MODEL_AND_CONTRACT.md 字节不同，历史批次继续绑定冻结版本；原始材料保持原位。当前源码额外登记 SHA-256，Git 查询结果为该路径不属于 Git 仓库。哈希一致性支持材料完整性，独立于语义正确性与防回滚部署保证。

复核范围包括所需文件存在、JSON 可解析、计数与 F2 算术一致、文本没有使用被禁止句式。最终结果见 evidence/VALIDATION.json，文件清单见 evidence/DELIVERY_MANIFEST.json。新增候选机制测试、原生服务请求和实现代码均为 0。本文手工证明没有机助定理证书，文献协议没有在本项目重跑，无外部独立审稿。

可重复的只读材料检查命令（PowerShell；检查本轮文件与历史冻结事件，不运行原生服务）：

```powershell
$taskReview = @'
from pathlib import Path
import hashlib, json
p=Path(r"D:\毕业设计\研究\密码学辅助_一致性核验\revisions\crypto_state_cost_review_2026-11-05")
manifest=json.loads((p/"evidence/DELIVERY_MANIFEST.json").read_text(encoding="utf-8"))
for row in manifest["files"]:
    f=p/row["path"]
    assert hashlib.sha256(f.read_bytes()).hexdigest()==row["sha256"], row["path"]
v=json.loads((p/"SEPARATION_CLAIMS.json").read_text(encoding="utf-8"))
assert v["primary_verdict"]=="REQUIREMENT_OR_EVIDENCE_MISSING"
assert v["candidates"]==[] and v["strict_separation_instances"]==[]
audit=json.loads((p/"evidence/SOURCE_AND_RAW_AUDIT.json").read_text(encoding="utf-8"))
for row in audit["frozen_entries"]:
    assert hashlib.sha256(Path(row["snapshot"]).read_bytes()).hexdigest()==row["expected_sha256"]
for run in ("run01","run02_secretless","run03_listing"):
    f=Path(r"D:\毕业设计\research_main_innovation\ci01_contract_audit\raw")/run/"http_and_events.jsonl"
    prev="0"*64
    for i,line in enumerate(f.read_text(encoding="utf-8").splitlines(),1):
        r=json.loads(line); h=r.pop("sha256")
        assert r["seq"]==i and r["previous"]==prev
        assert hashlib.sha256(json.dumps(r,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()==h
        prev=h
print("PASS: artifacts, frozen sources and historical event chains")
'@
$taskReview | & 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -X utf8 -
```

后续主线程继续开发时，当前工作树哈希可能改变；该变化应形成新版本记录，已有事件仍绑定历史快照。上述命令核对交付文件和冻结字节，不把当前工作树的未来变化判作历史证据损坏。
