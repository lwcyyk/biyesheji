# 开发验证、成本和复现

## Material Passport

范围：固定 B 0.1.0 上的 A/AB 0.1.0；合成 L0、独立源检查、有限观察策略、开发成本。执行者：同一工程代理；没有独立团队或真实服务复现。状态：**VERIFIED / PASS_FINITE_A_AB_ONLY**，仅限记录的有限域。H-A/H-AB 正式实验：**NOT_RUN**。

## 原始证据

- [final04 汇总](../../results/a_ab/final04/summary.json)、[环境与实际命令](../../results/a_ab/final04/environment.json)、[源码哈希](../../results/a_ab/final04/source_hashes.json)
- [自动测试日志](../../results/a_ab/final04/unittest.log)、[逐测试结果](../../results/a_ab/final04/tests.json)
- [具名输入预期/实际](../../results/a_ab/final04/regressions.json)、[指标汇总](../../results/a_ab/final04/metrics.json)
- [48 个有限输入、策略和实际分支](../../results/a_ab/final04/finite.jsonl)、[有限简表](../../results/a_ab/final04/finite_summary.json)
- [开发规模成本](../../results/a_ab/final04/performance.json)、[编译/审计/求解/重放分别计时](../../results/a_ab/final04/timings.json)
- [规模模型的完整源转换审计](../../results/a_ab/final04/scale_audits.json)、[限额返回](../../results/a_ab/final04/limits.json)
- [重放比较](../../results/a_ab/final04/replay.json)
- [v2.16 全项目回归](../../results/a_ab/v216_regression02/summary.json)、[B 固定依赖回归](../../results/a_ab/b_regression/summary.json)

`inputs/` 保存逐场景源 JSON，`compiled/` 保存全部编译表与具体映射，`artifacts/` 保存每种方法的策略、诊断、B 冲突证书、独立执行轨迹、证据和消融。输出不保存真实密码或 token，所有材料为合成标识。

最终源码工件包 SHA-256：

`a2bc5a9058578c190c3d6da3ec660cf3e07c04392ecf48b67a7b2528afee4726`

源码包包括 src/scripts/tests Python、A/AB 示例和 DEVELOPMENT_LOCK；文档在交付清单另记哈希。旧脚本因清单集合不同，其摘要不同，不等于固定 B 文件被修改。当前项目没有 Git 仓库，未伪造 commit。

## 测试范围

| 检查 | 结果 |
|---|---|
| 新增自动测试 | 21 个方法，0 失败/错误/跳过 |
| 具名场景 | 19 个；A1/B-A/AB1/B-AB/R-J 与原 R-I 可行性一致；所有接纳策略通过独立执行 |
| 有限参数积 | 48 个输入，16 可行、32 不可行，0 差异 |
| 重放 | 修正反馈边界后的 final03→final04 比较 25 个确定性文件；此前 dev03→final01→final02 的记录保留；时间不比较 |
| v2.16 全项目套件 | 77 个测试方法（原 41+B 的 15+A/AB 的 21），全部通过；原 27 回归无差异 |
| 原 L0 穷尽回归 | 1,296 参数模型、5,184 查询；928 可行、4,256 不可行，无候选/参考差异 |
| 固定 B 回归 | 原 15 测试、21 场景、384 参数模型、96 结构模型全部通过 |
| 历史保护 | 本轮清单中的 294 个原源码/测试/脚本/B 文档与结果无变化；原历史证据保护亦通过 |

48 个输入只穷尽以下生成参数：任务 2、路径 3、语义世界 2/4、请求预算 {3,4,6}、H {2,3,4,5}、核验创建会话与否。不是整个认证模型类的穷尽。各表行有重叠运行，不相加为独立样本数。

具名反例覆盖：未知结果不能当成功、调用方受限 active:false、调用方错误、共享预算不足、核验创建会话、未知句柄与账户根清理、有害批准撤回探针被过滤、probe/stop/cleanup 响应丢失、配置后核验、可观察 epoch 变化、空 K、无须学习的本地目标、昂贵通用配置、源转换缺失分支及策略证书篡改。

限额测试分别使编译、候选 W、R-J、执行轨迹检查耗尽，均返回 INCONCLUSIVE，不作为不可行证明。`UNKNOWN` 既可用于空 K/模型无效/模型外边界；一个已登记观察字符串恰为“UNKNOWN”则是普通不确定观察，其有限任务可能被证明 IMPOSSIBLE。这两个层次没有混用。

## 完成与拒绝

以下是全部 19 个具名开发输入的**描述性、最坏分支**结果，不是总体完成率估计。5 个拒绝输入均由独立参考确认为该有限目标不可行；1 个 UNKNOWN 是空初始 K。

| 方法 | 完成 | 完成率 | 拒绝 | 拒绝率 | UNKNOWN | INCONCLUSIVE | 接纳运行安全反例 | 终态未决义务 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A1 | 13/19 | 68.42% | 5/19 | 26.32% | 1 | 0 | 0 | 0 |
| B-A | 13/19 | 68.42% | 5/19 | 26.32% | 1 | 0 | 0 | 0 |
| AB1 | 13/19 | 68.42% | 5/19 | 26.32% | 1 | 0 | 0 | 0 |
| B-AB | 13/19 | 68.42% | 5/19 | 26.32% | 1 | 0 | 0 | 0 |
| R-J | 13/19 | 68.42% | 5/19 | 26.32% | 1 | 0 | 0 | 0 |

所有接纳输入的所有登记轨迹均完成；这依赖共用精确 W 和有限模型前提，不是新颖性证据。拒绝时实际请求数 0 仍计失败惩罚 `C_Q=Q_cap+1`，不能用提前拒绝取得“请求更少”的收益。完整逐输入 Q/C_Q 向量保留在 metrics.json。

## 请求、副作用与消融

| 场景 | A1 / B-A / AB1 / B-AB 最坏 Q | R-J 最坏 Q |
|---|---:|---:|
| 必要原生语义核验 | 4 | 4 |
| 额外 scope 无关信息负控制 | 4 | 4 |
| 核验会话与正确清理 | 5 | 5 |
| 丢 probe 结果并可能有未知句柄 | 6 | 6 |
| stop 生效不明后重试 | 5 | 5 |
| cleanup 生效不明后重试 | 6 | 6 |
| 配置后核验再停止 | 5 | 5 |
| 仅本地停止、无须核验 | 2 | 2 |
| 昂贵通用配置与联合规划 | 5 | 4 |

各正常方法的“每输入最坏新会话数之和”为 4，全部被清理；这不是 4 个独立真实用户事件。原始轨迹逐动作记录新会话、当前义务、实际费用、观察、证据失效和故障日程是否触发。被安全屏障避免的有害探针没有被算成故障恢复成功。

当前输入族中 A1 与 B-A 请求结果等效，AB1 与 B-AB 也等效。反馈接口产生并检查了冲突信息，但没有减少 Q。R-J 在昂贵配置例中以相同 G=2 少用一个请求，保留这一反方结果。

`no_acquisition_ablation` 在同一接口目录下限制策略不查询；它的拒绝只说明该策略子类不够，不能宣布联合任务无解。`obligation_ablation_2x2` 在两个场景中故意遗漏会话抽象，分别开启/关闭反馈：4 个诊断运行都被独立源审计拒绝；绕过审计作离线诊断重放时，均出现未结清 1 个义务和错误完成声明。每个运行有两个初始世界的反例轨迹，不能当成 8 个独立漏洞或混入正常方法安全统计。

## 求解成本预评估

final04 单独运行，Python 3.12.14，Windows 11，AMD64 Family 25 Model 97。任务数固定 2，路径数固定 3，H=4，统一节点限额 50,000。下表是单次求解墙钟秒数，**不含预编译/审计和输出写盘**；这些费用另列 timings.json。

| 可能世界 / 具体节点 | A1 | B-A | AB1 | B-AB | R-J |
|---|---:|---:|---:|---:|---:|
| 2 / 174 | 0.00941 | 0.00967 | 0.01569 | 0.01037 | 0.00962 |
| 4 / 536 | 0.03044 | 0.03366 | 0.07002 | 0.03284 | 0.02885 |
| 8 / 1,072 | 0.07297 | 0.06377 | 0.08389 | 0.06414 | 0.06115 |

所有规模方法都完成，Q=4。候选 W 实际节点为 89/161/233，R-J 为 89/193/297；AB1 额外 B 工作单元为 76/152/304。完整源审计另核对了 174/536/1,072 个具体节点及 188/576/1,152 条边。

A1 与 B-AB 是同一算法，时间仍有差异，说明单次计时存在调度/缓存噪声；不能据此算加速比或尾延迟。没有执行统计显著性检验、功效分析、真实平台吞吐测试或峰值内存测量。这里 R-J 的计算量没有形成明显工程障碍，结果亦等效或更好，因此不主张新的信息获取与控制原理。

## 复现

```powershell
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate_a_ab.py --out results/a_ab/reproduce01
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate_a_ab.py --out results/a_ab/reproduce02 --replay-of results/a_ab/reproduce01
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate.py --out results/a_ab/reproduce_v216
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate_b.py --out results/a_ab/reproduce_b
```

输出路径必须新建。补充的规模源审计可用 `a_cli.py compile results/a_ab/final04/inputs/scale_8.json --out new-compiled.json` 重现；CLI 在返回 COMPILED 前会执行独立源审计。该补充文件未计入 25 文件重放列表，但交付清单记录其哈希。

`dev01`、`dev02`、`dev03` 均保留。dev01 通过首轮 14 个测试后发现基线投影问题，记录了审查修正；dev02 为 18 测试/17 场景；dev03 扩展到 20 测试/19 场景；之后直接反馈 API 的空 K 分类反例被记录并修复，final03/final04 为 21 测试/19 场景。没有把开发过程改写成历史正式实验。

未运行真实认证/浏览器/AI 部署、一般抽象保持的机器证明、H-A/H-AB 正式统计。原文档与假设登记仍保留原状态。
