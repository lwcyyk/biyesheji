# B 开发验证与复现记录

## Material Passport

对象：基于已验收 v2.16 的 B 子包 0.1.0。证据类型：本地合成有限模型、自动测试、确定性重放、单机计算成本预评估。无真实参与者数据、无外部服务派发、无正式 H-B 统计。执行和解释由同一工程代理完成；独立性指代码实现隔离，不是独立研究团队。

验证状态：**VERIFIED / PASS_FINITE_B_ONLY**，仅对下列已运行范围。一般证明、新颖性确认和真实服务保持性质未完成。

## 结果入口

- [final02 汇总](../../results/b/final02/summary.json)
- [源码与工件哈希](../../results/b/final02/source_hashes.json)、[环境和实际命令](../../results/b/final02/environment.json)
- [单元测试原始日志](../../results/b/final02/unittest.log)、[逐测试状态](../../results/b/final02/tests.json)
- [21 个具名用例预期/实际结果](../../results/b/final02/regressions.json)，对应输入与交付/冲突证书在同目录 `inputs/`、`artifacts/`
- [384 个有限输入](../../results/b/final02/finite_inputs.jsonl)、[全部原始输出与冲突检查](../../results/b/final02/finite_results.jsonl)、[范围和计数](../../results/b/final02/finite_summary.json)
- [96 个结构输入及全部输出](../../results/b/final02/structural.jsonl)、[简表](../../results/b/final02/structural_summary.json)
- [固定规模性能原始数据](../../results/b/final02/performance.json)、[具名测试计时](../../results/b/final02/timings.json)
- [确定性重放比较](../../results/b/final02/replay.json)
- [原 v2.16 验收脚本重跑](../../results/b/v216_regression/summary.json)、[原有限穷尽查询计数](../../results/b/v216_regression/exhaustive_summary.json)

最终 B 源码工件包 SHA-256：

`b760698dc03dd62c368563868a5e39781ed51fa35ab4ee13f927880a43ab8147`

清单包含全部 src/scripts/tests Python、B 示例、pyproject 和比较前的 OBJECTIVE_LOCK。文档解释不计入该源码包；交付清单另外记录文档哈希。旧验收脚本的哈希集合不同，见其 source_hashes.json，不把不同哈希集合产生的摘要当作源码变化。

## 已完成检查

| 检查 | 实际范围和结果 |
|---|---|
| B 自动测试 | 15 个测试方法；0 失败、0 错误、0 跳过；包括具名、参数矩阵、结构生成、CLI 和依赖隔离子检查 |
| B 具名回归 | 21 个用例；预期状态/最优 G、候选/参考配置、交付与不可行证书检查均一致 |
| 参数矩阵 | 384 个输入；84 FEASIBLE、300 IMPOSSIBLE；B 与参考一致；84 可行输入与 B-B 的最优 G 相同 |
| 结构生成 | 固定种子 20261102，96 个输入；60 不可行、34 B/B-B 同 G、2 B 有解而 B-B 规则无解；B 与参考全部一致 |
| 8 任务边界 | 单元测试强制 8 个门控动作，H=8 可行、H=7 不可行；另有 16 路径规模预评估及补充完整核验 |
| 重放 | final01/final02 使用同一源码；28 个确定性输出文件字节一致；时间和运行日期不要求相同 |
| v2.16 回归 | 原脚本执行 56 个测试方法（原 41+新增 15），0 失败/错误/跳过；原 27 具名回归无差异 |
| v2.16 有限穷尽 | 保留 1,296 个参数模型×4 个 H=5,184 次查询；928 可行、4,256 不可行；候选/参考一致 |
| 历史保护 | 修改前 294 文件中仅 README 追加导航；旧源码/结果无变化。旧脚本跟踪的 407 历史文件亦无变化 |

不同表行有重叠执行，不相加成统计样本数。384 范围只穷尽所定义参数积：2 任务、4 路径、3 原生域；local/remote×preserve/不preserve×all_material/refresh_only×4 批准包×请求预算 {1,3,8}×H {0,1,2,3}。96 结构输入为固定种子生成，不是穷尽；它们含 3 任务、6 路径、AND/OR、混合环境及合并效果域。

已测反例包括共享根误判独立、scope 不足、错账户、仅刷新失效、未经批准、请求/批准/隔离预算不足、门控无控制权、零停止步数、空路径目录、未核实原生契约、重叠撤销域、替代路径残留及证书/交付篡改。完整 8 任务的工作限额用例不能混入“已穷尽参考”的分母。

## 计算成本预评估

环境：Python 3.12.14，Windows 11，AMD64 Family 25 Model 97，32 逻辑处理器。采用 final02 的单次墙钟秒数；final01 曾与旧回归脚本并发，故不用于下表。每个方法的预设限额均为 50,000 工作单元。预算单位类别见原始 stats，不能跨算法当成等价指令数。

| 任务 / 路径 | B 秒 / 状态 | B-B 秒 / 状态 | 精确参考秒 / 状态 |
|---|---|---|---|
| 2 / 4 | 0.0019 / FEASIBLE | 0.0045 / FEASIBLE | 0.0011 / FEASIBLE |
| 4 / 8 | 0.0069 / FEASIBLE | 0.0585 / FEASIBLE | 0.0213 / FEASIBLE |
| 6 / 12 | 0.0191 / FEASIBLE | 0.7304 / FEASIBLE | 0.3491 / FEASIBLE |
| 8 / 16 | 0.0378 / FEASIBLE | 4.1576 / INCONCLUSIVE | 2.9765 / INCONCLUSIVE |

这是一组本地停止负控制，全部已完成求解的最优 G=1。8 任务超限方法也保留了检查器接纳的 incumbent，但未以其宣告该次枚举已经完成。候选的 G 剪枝与基线“枚举全部适用项”的实现成本不同；基线尚未做直接生成优化。**这些时间不证明新算法优势，也不是 H-B 资源效果。** 未测真实请求延迟、CPU 峰值内存、存储或延迟分位数；计时只有一遍，不能给置信区间。

为消除“8 任务只有限额结果”的正确性不确定性，另外用默认 1,000,000 工作单元对同一 16 路径目录执行完整参考与 B-B，原 50,000 限额结果保留。补充结果及准确命令见 `results/b/boundary_full/`，不替换或重算上表。

补充完整运行已通过：[边界核验汇总](../../results/b/boundary_full/summary.json)。参考枚举 65,536 个路径子集及 13,122 个规划状态；B-B 生成、规划并检查全部 6,561 个适用配置。两者配置相同、G=1；全部 B-B 合法交付经检查器复核。此为一个明确有限目录的完整运行，不是所有 8 任务模型的穷尽。

## 精确复现命令

```powershell
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate_b.py --out results/b/reproduce01
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate_b.py --out results/b/reproduce02 --replay-of results/b/reproduce01
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate.py --out results/b/reproduce_v216
```

应在新目录复现，不能覆盖 final01/final02。CLI 的 `--out` 同样只允许新文件。具体输入、预期/实际、交付计划、每个 B-B 候选和证书均可从原始 JSON 重建，不依赖本文摘要。

`results/b/dev01` 保留初次 12 测试的日志和当时哈希；`dev02` 保留扩展到 14 测试时的完整原始输出。最终新增 CLI 测试并收紧复现记录后为 15 测试。均不冒充历史正式实验。

## 解释限制

本轮没有计算 p 值、bootstrap、完成率总体推断或 C_G 均值比。没有把“未检出差异”解释成统计等效。只对单 broker 配置全集与 B-B 集合相同的受限域作结构等效说明；其他域详见反方审查中的两个规则遗漏例。

未运行 H-A、H-B、H-AB 正式判定、真实认证接口、真实 AI 代理、机器核验一般证明。有限测试通过不能验证新颖性，也不能证实真实系统满足输入契约。下一阶段进入条件见 ADVERSARIAL_REVIEW.md；原 v2.15 假设登记和历史结果没有被改写为成功。
