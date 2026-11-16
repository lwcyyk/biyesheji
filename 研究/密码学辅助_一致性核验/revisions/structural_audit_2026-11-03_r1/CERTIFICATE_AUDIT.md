# 两类证书的独立审查

本文路径相对原研究根目录；新源码均在 `revisions/structural_audit_2026-11-03_r1/`。原文件只读，未修补原版后假称历史已经通过。

## 1. 原实现发现

| 位置/函数 | 可复核证据 | 影响与修订 |
|---|---|---|
| `construction/structural_checker.py:37`，`check_components` | 仅检查 kind=`INDEPENDENT_SUPPORT_MODEL_ONLY`、字典及代数资源；不接收外部支持策略 | 类别标签不是“实际策略等于全部独立集”的证明。新检查器接收独立提供的完整profile并穷尽核对实际公开族 |
| 同文件37–74行；`construction/structural_masks.py:59`，`compile_dictionary` | 生成器 `requires` 只是文字；删掉它并添加错误 world/amplitude 字段仍返回True，见 `results/dev01/legacy_findings.json` | 原证书只能当有外部前提的字典证书。新证书绑定完整profile；严格字段集合拒绝遗漏与多余伪装字段 |
| `construction/structural_checker.py:31`，`valid_dictionary` | q=3.0 可通过成员检查，随后 `range` 抛异常；None证书也可直接异常 | 新实现显式整数类型和状态，不把未检查/错误解释为数学不可行 |
| `construction/structural_checker.py:76`，`check_circuit` | 已核对幅值/掩码、字典、策略/世界/约束引用，且验证允许支持内的最小关系 | **不能把分量证书缺陷照搬给它。** 但其掩码标签把观察合在一句字符串里；没有完整profile摘要、批准预算来源引用、清晰的检查状态 |
| 同文件90行，`check_circuit` | 检查某关系包含于已列出的允许支持；不证明支持族完整，也不证明实际秘密支持是什么 | 一个肯定反例足以否定声明模型中的全输入可行性；无反例不等于可行。新实现保持这一逻辑不对称 |
| 原两个检查入口 | 主要输出布尔值 | 无法区分证书无效、超范围、模型不适用、预算未完成。新协议分别记录验证状态和数学结论 |
| 原 `checked_rank` | 不调用生成器，但 GF4乘法复用公共 `reference.mul` | 有算法分离，不等于完全独立实现。新版 checker 使用自己的GF4乘法表、消元与全回路枚举，不导入 compiler/algebra |

## 2. 新协议的信任边界

调用 `checker.check(certificate, expected_profile, max_rank_checks=...)`。expected_profile 必须由调用方从可信配置中取得；不能使用攻击者同证书一起替换的profile。SHA-256只做内容绑定，不是签名，也不会证明引用指向的服务事实。

规范JSON绑定全部字段：版本、profile标识、域及表示、维度、字典、支持族表示/完整性/列表、幅值模型、掩码模型、观察模型、活跃列保留范围、策略、世界、约束列表、批准、预算、来源引用。当前引用是标识字符串；引用内容的签名、有效期、撤回与实际预算执行，仍由外部来源机制负责，**检查器没有核实这些真实性**。

分量证书含 active_columns、basis、left_inverse、components、minimum_rows、entropy_orbit_size。检查器不信任 `premise` 标签：独立枚举活跃宇宙的所有子集，计算独立集并与完整声明族比较；不等则 `MODEL_NOT_APPLICABLE`。部分已知族则 `INCONCLUSIVE`。枚举所有最小回路重构分量，验证左逆和有效空间回译。

冲突证书含 support、非零coefficients、allowed_support_witness 及声明结论。独立验证系数关系、最小性、见证支持属于公开族且包含该回路。即使公开族只知一个子集，明确获准的依赖见证仍可核验；这不会证明未出现的支持。

`compiler.find_conflict` 返回 `SEARCH_RESULT/NO_WITNESS_FOUND` 时没有可行性证明权限；checker拒绝将它当作证书。任意允许族全部穷尽后的C2可以由数学命题解释，本版没有把“搜索无结果”封装成新的全局安全证书。

## 3. 返回状态

| verification_status | 含义 |
|---|---|
| VERIFIED | 证书与指定公开profile符合声明的有限代数检查 |
| INVALID_CERTIFICATE | 关系/资源/摘要/字段错误或授权越界 |
| INVALID_INPUT | 公开profile不合法、必要字段缺失或类型错误 |
| OUT_OF_SCOPE | 超过当前实现域/规模范围，未作判断 |
| MODEL_NOT_APPLICABLE | 幅值/掩码/观察模型不支持，或C3的完整独立族前提不成立 |
| INCONCLUSIVE | 支持族未完整给出或检查预算耗尽 |

mathematical_conclusion 独立取 `NONE`、`INFEASIBLE_IN_DECLARED_MASK_CLASS`、`CONDITIONAL_COMPONENT_OPTIMALITY`。数学不可行只否定“声明观察模型内完美隐私且无抹除的输入独立线性掩码”，不否定非线性MPC，也不等于B的全局配置无解。

所有输出固定 `scope=PUBLIC_MODEL_ONLY`、`runtime_support_verified=false`、`authorizes_execution=false`。UNKNOWN不是数学判定；它属于外部来源状态，应由接口另记。

## 4. 实现边界与验证

支持 GF(3) 与 GF(4)，后者固定多项式 x²+x+1；环境行数1–4、列数0–8。数学定理允许更广域与维数，当前证书实现不支持时明确拒绝。零活跃空间、未出现零列和空支持测试均保留。GF(2^128)的MPC gate参考**没有**被此小域证书检查器核验，不能拿小域证书冒充生产域证书。

测试涵盖两类证书的篡改、遗漏约束、世界/批准/预算改动、错误支持族、错误幅值和观察模型、空族、活跃零列、部分族、超范围、工作预算、不同基、可逆行变换。详细每项输入构造、预期与实际输出见源码和 `results/dev01/`、后续确定性重放目录。

证明与检查器是两个不同层次：checker确认一个有限公开实例符合已陈述的数学条件；不重新证明C3一般定理。生成器/检查器算法和算术实现分离降低同错风险，但本轮仍由同一助手开发，没有冒充第三方安全审计。
