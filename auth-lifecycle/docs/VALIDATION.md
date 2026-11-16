# v2.16 验证与复现

## 实际命令

工作目录：`D:\毕业设计\auth-lifecycle`。

本次使用 Python 路径 `C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`；没有安装第三方包。

```powershell
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate.py --out results/v2.16/final01
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/validate.py --out results/v2.16/final02
```

这两个目录是本次证据，复现请改用新的名称（如 `my_run`），不要覆盖它们。脚本会拒绝已存在的输出目录。准确命令、Python/平台及 UTC 时间保存在每次 `environment.json`，测试逐项 PASS/FAIL/ERROR/NOT_RUN 保存在 `tests.json`，完整日志为 `unittest.log`。

## 最终验证域与结果入口

代码版本：`0.16.0`。最终源码束 SHA-256：

`f12a2c630e176868c0969697a479bd8ed48181eb256e40860692f481d69d62b6`

该摘要覆盖运行所用 `.py`、打包/命令配置及示例 JSON 的逐文件哈希清单，不把不断增加的结果目录纳入源码摘要。原始清单见 `results/v2.16/final01/source_hashes.json`。

- 首次最终运行：41 个 unittest 测试方法，0 失败、0 错误、0 跳过；27 个命名回归场景全部符合预期，候选与 R-I 无分歧。
- 有限穷尽：1,296 个明确构造的小模型 × H=0,1,2,3，共 5,184 次查询；928 个 FEASIBLE、4,256 个 IMPOSSIBLE，全部候选/R-I 一致且对应正策略或不可行性证书通过独立检查。
- 单元场景另覆盖 H=8 和四任务边界；**不是**对全部四任务、深度八模型的穷尽。
- 运行期间源码未变化，407 个历史文件内容哈希保持不变。
- 同源码复跑的实际结果及逐文件比较见 `final02/summary.json` 和 `replay_comparison.json`；以原始文件为准。

穷尽域只有：两个候选世界、每世界 `s/done` 两状态、两个动作；每个源状态动作有无边或一条到 s/done 的边，观察为 0/1，成本为 0。枚举 `3^4 × 2^4 = 1296` 个参数实例（包含观察标签在无边时产生的行为等价重复），不是 1296 个互不等价自动机。没有借此穷尽任意概率、任意预算、任意网络并发或所有副作用模型。

## 原始工件

| 文件 | 内容 |
|---|---|
| `final01/inputs/*.json` | 27 个命名场景的完整输入 |
| `final01/regressions.json` | 每场景预期状态、候选/R-I 实际状态及检查器结果 |
| `final01/artifacts/*.json` | 完整策略、反证树、证书、探索节点计数与检查结果 |
| `final01/exhaustive_models.jsonl` | 全部枚举参数及模型，不仅记录一个汇总计数 |
| `final01/exhaustive.jsonl` | 5,184 个查询的 H、预期 R-I、候选实际及证书判定 |
| `final01/exhaustive_summary.json` | 有限域计数与最大展开节点，用于覆盖说明，不作性能优势结论 |
| `final01/progress_demo.json` | 无秩 stay 自环与有界菜单从 r=8 到 0 的对照 |
| `final01/runtime_progress_demo.json` | 实际本地适配器的七次 stay、拒绝最后一次 stay、finish 及效果记录 |
| `final01/boundary_demo.json` | 未注册外部观察、不可用 K、剩余步数及 UNKNOWN 结果 |
| `final01/environment.json` | 命令、版本、平台、Git 状态、源码束摘要 |
| `final01/summary.json` | 通过、失败、跳过、历史完整性及未运行项 |

## 关键测试定位

| 必须覆盖的情况 | 定位 |
|---|---|
| stay 永不完成 | `test_core.CoreTests.test_stay_requires_rank`；`test_controller.ControllerTests.test_real_local_dispatch_cannot_stay_forever` |
| P1/P2/P3 三世界冲突 | `test_exact_named_plan_sets`；`test_three_world_certificate_and_all_pairs` |
| 更大有限核心 | `test_arbitrary_core_not_hardcoded_to_three`，五世界 |
| 错账户 | `wrong-account` 回归；`test_wrong_account_has_no_effect` |
| 原生授权不独立 | `independent-grants` / `shared-native-root` 回归 |
| 受限 active:false | `test_active_false_does_not_assert_revocation` |
| 核验创建会话 | `session-cleanup` / `session-no-cleanup` / `session-no-cleanup-approval` |
| 响应丢失及未知句柄 | `test_lost_response_keeps_both_possible_effects`；`lost-response-unknown-handle` |
| 批准撤回 | `approval-stable` / `approval-withdrawn` |
| 预算不足及外部消耗 | `budget-insufficient`；`test_external_budget_debit_is_in_successor_state` |
| 空模型知识集、空后继 | `test_empty_no_vacuous_success`；`empty-successor` |
| 外部可观察冲突 | `test_observable_conflict_invalidates_knowledge`；控制器同名边界测试 |
| 未完成搜索 | `test_search_limits_are_inconclusive_not_impossible` |
| 抽象保持正负例 | `tests/test_abstraction.py`，覆盖每项条件及非平凡合并/回译 |
| 生成/检查分离 | `test_independent_import_boundary`，静态导入和运行时替换检查 |
| CLI 可用性与不覆盖结果 | `tests/test_cli.py` |

## 开发失败记录

`dev01` 是初始测试集通过记录，不冒称最终版本。新增篡改测试后，`dev02_snapshot_failure.log` 的 19 个测试中有 1 个失败：把证书快照整数 0 替换成 JSON false 仍被接受。对应 `.json` 保存当时输入、预期、实际与源码哈希。

修正为规范化 JSON 比较后，`dev03` 的 34 个测试和 26 个回归通过。之后新增真实本地有界派发、四任务/精确命名三世界等验证形成最终版本。所有早期输出原样保留；没有把失败计入最终通过，也没有删除失败证据。

## 未运行与解释限制

没有运行 H-A、H-B、H-AB 正式实验、真实网站、真实OAuth/浏览器、AI模型或密码学证明实验。没有执行机器证明和外部独立安全审计。没有性能优越性、创新性或统计总体安全结论。

所有 PASS 仅表示本次声明的有限 L0 检查域符合预期。原有 v2.15 假设登记表仍保留原状态；没有把本轮开发测试写回为其正式实验结果。
