# A1 与 AB1：有限契约获取和配置冲突反馈

本增量使用已验证的 B 0.1.0 作为固定依赖，新增 `auth_lifecycle.a` 0.1.0。原 v2.16 与 B 的源码、测试、报告和结果保持。目标是为 v2.15 H-A/H-AB 建立可运行、可反驳的开发基础；没有执行正式统计判定。

## 交付入口

- [模型、K 更新、预算、义务与条件正确性](MODEL.md)
- [A1、B-A、AB 配对、R-J 和复杂度](ALGORITHMS.md)
- [验证、原始结果、成本与复现](VALIDATION.md)
- [反方审查、限制和下一阶段条件](REVIEW.md)
- [开发前固定的目标和对照规则](DEVELOPMENT_LOCK.json)
- [原 v2.16/B 工件保护清单](baseline_manifest.json)
- [基线一手来源核对](SOURCES.md)

## 实现

| 文件 | 功能 |
|---|---|
| `src/auth_lifecycle/a/model.py` | 有限服务候选契约、操作/批准/价格表、故障日程、任务性质投影 |
| `plant.py` / `_plant_reference.py` | 分开的具体状态转换实现；后者不调用候选转换器 |
| `compiler.py` / `audit.py` | 编译到 v2.16 L0；逐状态、逐动作、逐结果独立核对源语义 |
| `candidate.py` | 共用 W_r 屏障、控制选择、缓存的 A1 与 B-A；AB 只改变 feedback 开关 |
| `bridge.py` | B 的逐配置冲突证书、语义分歧及配置后下一停止动作的阻塞引用 |
| `evidence.py` | 非空支持更新、模型外围栏、范围受限的契约证据与失效 |
| `joint_reference.py` | R-J：完整观察信念图和最坏总请求数动态规划 |
| `runtime.py` | 不向选择器传入真实分支的独立 L0 执行评分器 |
| `ablations.py` | 无获取耦合消融、义务遗漏×反馈开关的明确不安全诊断 |
| `fixtures.py` / `tests/test_a_ab.py` | 合成正负场景、篡改检查、故障、CLI 和独立性测试 |

`A1` 与 `B-AB` 调用同一选择器、同一关闭反馈设置；保留两个标签用于研究对照。`AB1` 仅将 feedback 改为 True。`B-A` 使用成熟广义二分测试选择的任务性质版本，并附加完全相同的安全、批准、预算和处置规则。不是随机探测、全量学习或不安全学习器。

## 使用

在 `D:\毕业设计\auth-lifecycle`，Python 3.11+，仅标准库：

```powershell
python scripts/a_cli.py solve examples/a_ab/simple_acquisition.json --method AB1 --out ab-result.json
python scripts/a_cli.py check examples/a_ab/simple_acquisition.json ab-result.json
python scripts/a_cli.py solve examples/a_ab/simple_acquisition.json --method B-A
python scripts/a_cli.py solve examples/a_ab/simple_acquisition.json --method B-AB
python scripts/a_cli.py solve examples/a_ab/simple_acquisition.json --method R-J
python scripts/a_cli.py compile examples/a_ab/lost_probe_unknown_handle.json --out compiled-source.json
python scripts/validate_a_ab.py --out results/a_ab/my_run
python scripts/validate_a_ab.py --out results/a_ab/my_replay --replay-of results/a_ab/my_run
```

所有输出必须使用新路径，不能覆盖历史结果。CLI 返回 0 表示命令已处理，语义结果看 `status` / `verdict`。CLI 只操作合成 L0 状态，不会联系真实服务。

R-J 允许 probe、configure、stop、cleanup 的同一动作集，且能在配置后继续核验。首版 configure 是可靠原子宏：计入固定 B setup 的全部请求和批准，但只占一个决策步；这不是任意异步认证工作流的联合规划。范围与待证明部分详见 MODEL.md。
