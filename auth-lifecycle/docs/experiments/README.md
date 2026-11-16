# A/B/AB 原生实验体系

本阶段新增了两个完整原生认证实现的受控部署、能力调查、统一日志、独立评分、故障触发、随机顺序配对运行及统计脚本。**当前可运行的是受限的原生校准预实验；完整的查询依赖 A/AB 原生效应实验和确认性实验尚未就绪。**

## 阅读和数据入口

- [实现分层审计与部署事实](AUDIT.md)
- [完整协议草案](PROTOCOL.md)
- [原生能力与故障矩阵](CAPABILITIES.md)
- [预实验结果、统计、功效和限制](RESULTS.md)
- [待冻结清单与未完成项](FREEZE_CHECKLIST.md)
- [假设登记](../../experiments/registry.json)
- [配对预实验计划](../../experiments/pilot-plan.json)
- [日志 JSON schema](../../experiments/log-schema.json)
- [版本/原生配置锁](../../experiments/l1/environment.lock.json)

H-S、H-A/H-B/H-AB、H-M、H-D 分开登记。阈值 0.80/0.80/0.85 与 −0.05 保持 v2.15 待确认建议；没有自动预注册或正式支持结论。

## 运行组件

| 文件 | 功能 |
|---|---|
| `scripts/l1_fetch.py` | 下载官方固定发行版并核对校验值，限定在私有运行目录 |
| `scripts/l1_environment.py` | 运行/停止本项目拥有的两个原生进程，不创建系统服务 |
| `scripts/l1_survey.py` | 13 类原生能力/故障调查；保存原始观测和源码快照 |
| `scripts/l1_freeze_environment.py` | 调查后固定原生版本、公开配置和调查证据，仅用于预实验 |
| `scripts/l1_pilot.py` | 同预算/批准/接口的随机顺序配对校准；正式入口硬阻断 |
| `experiment/providers.py` | 薄 HTTP 适配器，调用真正 Keycloak/Casdoor；只操作登记的自有 actor |
| `experiment/journal.py` | 脱敏事件链、批准/预算、响应隐藏和故障事件 |
| `experiment/resource.py` | 自写资源/broker/cache 夹具，明确不是第三个认证实现 |
| `experiment/witness.py` / `scoring.py` | 独立签名、作用域、原生单位、效果与费用核验 |
| `experiment/planning.py` | 调用固定 A/B 算法，范围为已知契约、单支持路径的原生绑定 |
| `experiment/statistics.py` / `scripts/analyze_pilot.py` | 保留全部配对臂、分层家族 bootstrap、相关/方差与条件功效分析 |
| `experiments/l1/run_reference_checks.py` | 同原生条件下 A1/R-J 的补充负控制，不混入主数据 |

## 复现

使用本次实际 Python（包含 cryptography 50.0.2），在项目根目录运行。L0 仍只依赖标准库；L1 额外依赖见 `experiments/requirements-l1.txt`。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/l1_environment.py serve
```

在另一个终端中运行新目录，不能覆盖历史数据：

```powershell
python scripts/l1_survey.py --out results/experiments/new_survey --repeats 2
python scripts/l1_pilot.py --out results/experiments/new_pilot
python scripts/analyze_pilot.py results/experiments/new_pilot --out results/experiments/new_analysis --bootstrap 10000
python experiments/l1/run_reference_checks.py --out results/experiments/new_reference
python scripts/validate.py --out results/experiments/new_regression
```

第一次安装新环境先运行 `l1_fetch.py`。现有 `environment.lock.json` 是当前环境的锁；换环境必须重新调查、审查配置差异并写入新的锁路径，不能静默覆盖旧证据。原生 UUID、令牌和墙钟时间不会逐字节重现；给定同一原始数据的统计结果应可确定重放。

新环境的锁可用 `l1_freeze_environment.py --survey results/experiments/new_survey --out experiments/l1/new-environment.lock.json` 创建，再用 `l1_pilot.py --environment-lock experiments/l1/new-environment.lock.json --out results/experiments/new_pilot` 指定。已有服务运行时不要重复启动 serve；它会拒绝占用中的端口。

停止本项目进程：

```powershell
python scripts/l1_environment.py stop
```

管理员口令、数据库和服务原始日志仅在 `.runtime/l1/`；不加入公开数据或源码归档。公开 JSONL 不含可复用 token/口令。当前项目无 Git 提交，源码哈希和归档支持复现，但不能替研究者确认正式代码提交。
