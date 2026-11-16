# 认证生命周期 L0 工程

新增的成熟在线状态运行层可从 `python scripts/online_state.py --help` 使用。
它实现 ONLINE_TRUSTED_STATE_V1 的本地事务、材料托管和恢复路径，使用可选依赖
`pip install -e ".[online-state]"`。本轮架构、复现和验收记录位于
[mainline_online_state_v1](../mainline_online_state_v1/ACCEPTANCE_REPORT.md)。
原生服务取证需要对应的后续授权和能力证据。

限定 Casdoor 适配器入口为 `python scripts/native_casdoor.py --help`，使用显式原生
profile、独立授权编号及持久 HTTP 预算。[M2 适配与验收](../mainline_native_casdoor_v1/ACCEPTANCE_REPORT.md)
记录材料束、迁移、四个新账户轨迹、评分修正和清理。

本阶段：**v2.16 有界正确性语义、独立参考与可检查证书**。代码版本 `0.16.0`。

这是从现有研究材料建立的有限状态开发基础。当前工作区没有找到此前文档所述的完整 A/B/AB、`handoff.py`、`CloseExecutor` 或认证后端源码，也没有既有 Git 仓库。这里不冒称接入或修复了缺失的系统；没有复制整套历史项目，没有改写 v2.15 的结果。

## 从这里开始

- [实现前审计](docs/AUDIT.md)：8 项检查、源码证据、缺失清单、Git 状态。
- [形式化语义与 H-S 条件性论证](docs/SEMANTICS.md)：有界递推、状态边界、独立性及证明限制。
- [证书协议](docs/CERTIFICATES.md)：多世界反证、检查器、不同结论作用域。
- [抽象保持条件](docs/ABSTRACTION.md)：有限关系检查、回译、反例及外部适配器限制。
- [变更与下一阶段](docs/CHANGES.md)：与现有材料的差异、已知限制、进入条件。
- [验证记录](docs/VALIDATION.md)：实际命令、失败开发记录、原始结果入口及穷尽范围。

## 运行

Python 3.11 或更高版本，运行与测试仅使用标准库，不需要安装依赖。`pyproject.toml` 只用于可选打包。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
python scripts/validate.py --out results/v2.16/my_run
```

输出目录必须是新的。重复运行时换一个目录名，不覆盖历史结果。本次宿主使用的完整命令：

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate.py --out results/v2.16/my_run
```

单独使用求解器和检查器：

```powershell
python scripts/cli.py solve examples/stay_finish.json --engine candidate
python scripts/cli.py solve examples/stay_finish.json --engine reference
python scripts/cli.py certificate examples/three_worlds.json --out three-world-certificate.json
python scripts/cli.py check examples/three_worlds.json three-world-certificate.json --kind impossibility
python scripts/cli.py certificate examples/adaptive_probe.json --scope no_common_immediate_completion --out immediate-only.json
python scripts/cli.py check examples/adaptive_probe.json immediate-only.json --kind impossibility
python scripts/cli.py solve examples/adaptive_probe.json
```

最后三个命令故意说明：**当前没有一步完成方案，不代表不存在两步观察策略**。CLI 的退出码只表示命令是否成功处理；语义结果在 JSON 的 `status` 或 `verdict` 字段中，不能只看 shell 返回 0。

## 代码边界

```text
src/auth_lifecycle/
  schema.py               数据契约、静态完整性检查、状态与结果类型
  semantics.py            候选侧 Pre、观察后继、目标及模型边界
  candidate.py            记忆化有界 AND/OR 搜索
  _reference_kernel.py    独立原始表解释器
  reference.py            R-I 可达图展开与自底向上判断
  certificates.py         不可信证书生成与世界子集缩减
  checker.py              独立策略/不可行性证书检查
  abstraction.py          有限抽象关系检查与策略回译
  adapters.py             可执行本地表适配器，仅 L0
  controller.py           有界实际派发入口及模型外结果保留
  fixtures.py             合成正负场景
tests/                    单元、篡改及有限穷尽检查
results/v2.16/            逐次运行的新目录，含原始输入和结果
```

候选和 R-I 不共用决策、前置条件或后继解释代码。R-I 与证书检查器共用 `_reference_kernel.py`，此共享明确披露；它们不是彼此完全独立的实现。所有模块共用数据结构验证，这是可信基础的一部分。

## 结果含义

`FEASIBLE`：存在完整、有界、以可见观察为分支的策略。

`IMPOSSIBLE`：指定模型、当前信息与给定决策步数内无策略；不表示任意时限或真实网站全局无解。

`INCONCLUSIVE`：搜索或检查限额耗尽；没有完整的所需证据。

`UNKNOWN`：空信息集、无效模型/状态或已观察到模型外冲突。不能按成功或无解处理。

本轮没有执行 H-A、H-B、H-AB 正式实验，也没有真实 OAuth、浏览器、AI 或新密码协议实验。有限检查通过不等于一般安全证明或创新性验证完成。

## 基于 v2.16 的研究 B 增量

新增 [研究 B 工程入口](docs/b/README.md)：统一凭据配置、B 完整有限搜索、B-B 四规则强组合、独立配置参考、G 原生效果域审计和冲突证书。旧 v2.16 模块与验收结果保持；B 子包版本 `0.1.0`。

```powershell
python scripts/validate_b.py --out results/b/my_run
python scripts/b_cli.py solve examples/b/mixed_alternatives.json --engine B
```

该增量只完成有限模型的算法正确性与开发预评估，不构成正式 H-B 判定。结果、负控制、等效范围、结构遗漏反例与限制见 [B 验证记录](docs/b/VALIDATION.md)。

## 固定 B 的 A1 / AB1 增量

[A/AB 工程入口](docs/a_ab/README.md)提供保守 K 更新、共享预算和义务、W_r 策略、配置冲突反馈、B-A/B-AB 对照、同动作 R-J、源语义独立审计和执行评分。B 源码保持固定。

```powershell
python scripts/a_cli.py solve examples/a_ab/simple_acquisition.json --method AB1
python scripts/validate_a_ab.py --out results/a_ab/my_run
```

本轮仅为开发预验证，不宣告 H-A 或 H-AB 正式支持；结果与反方分析见 [A/AB 验证记录](docs/a_ab/VALIDATION.md)及[审查](docs/a_ab/REVIEW.md)。

## 原生实验体系与校准预实验

[实验体系入口](docs/experiments/README.md)提供两个完整原生实现（Keycloak 26.8.1、Casdoor 4.25.0）的受控部署、能力调查、统一日志、独立评分、配对运行与统计脚本。资源/缓存/故障夹具明确与原生认证实现区分。

已完成的原生校准数据不等于正式验证：需要补证的 A/AB 原生绑定、独立家族数量、抽象保持、研究者阈值及留出确认仍未完成。原生环境使用额外依赖 `experiments/requirements-l1.txt`；L0 原模块保持。

```powershell
python scripts/l1_pilot.py --out results/experiments/new_pilot
python scripts/analyze_pilot.py results/experiments/new_pilot --out results/experiments/new_analysis
```

见[协议](docs/experiments/PROTOCOL.md)、[原生能力](docs/experiments/CAPABILITIES.md)、[预实验结果](docs/experiments/RESULTS.md)和[待冻结清单](docs/experiments/FREEZE_CHECKLIST.md)。正式确认性入口保持关闭。
