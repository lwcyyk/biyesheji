# 研究 B：生命周期约束下的凭据配置与委托规划

本增量基于已经验收的 v2.16；原 L0 代码版本仍为 `0.16.0`，新增 `auth_lifecycle.b` 版本为 `0.1.0`。没有复制项目，没有把此前拟议的 B 算法记作历史实现。当前实现是**有限、已知、确定性原生契约内的完整配置搜索**，不是开放网站的通用规划器。

## 阅读入口

- [模型、形式化语义与条件论证](MODEL.md)
- [算法、B-B 规则、精确参考与复杂度](ALGORITHMS.md)
- [证书与独立检查](CERTIFICATES.md)
- [反方审查与尚未完成项](ADVERSARIAL_REVIEW.md)
- [测试、原始结果与复现](VALIDATION.md)
- [比较前固定的成本目标和规则](OBJECTIVE_LOCK.json)
- [直接从 v2.15 DOCX 读取的指定章节及原件哈希](v215_requested_sections.json)
- [修改前的 v2.16 文件清单与哈希](v216_baseline_manifest.json)

v2.15 §2.3 要求接受静态签名最优和本地代理负控制；§5.3 要求组合四种简单配置、同检查器和同成本目标；§6.1 区分 L0、真实认证、真实 AI；§6.3 要求同批准和接口，禁止真值泄漏。这四项约束均落实到本增量的模型、基线、结果记录和边界说明中。

## 与基线的差异

| 项目 | 已验收 v2.16 | 本次新增 |
|---|---|---|
| 输入 | 有限认证状态转移表 | 任务、原生授权目录、撤销效果分区、环境、AND/OR 支持路径、批准和预算、停止/保留场景 |
| 配置综合 | 尚无 B 配置优化器 | B 完整子集搜索与 G 下界剪枝 |
| 简单强基线 | 尚无四方法配置组合 | B-B 四规则，保留所有适用候选、全部合法交付及来源标签 |
| 精确参考 | 观察分支 R-I | 新增全局位掩码配置枚举和独立状态 BFS；不替换原 R-I |
| 检查 | L0 策略/多世界反证 | 配置、setup、每条停止计划、G 效果域核算、完整配置冲突覆盖证书 |
| 证据 | 已验收的 L0 有界正确性检查 | 配置层开发测试、有限枚举、结构生成模型、计算限额预评估 |

旧 `src/auth_lifecycle/*.py`、旧测试、报告和结果均保留。根 README 只追加导航；新增文件位于 `src/auth_lifecycle/b/`、`tests/test_b.py`、`scripts/b_cli.py`、`scripts/validate_b.py`、`docs/b/`、`examples/b/` 和 `results/b/`。无 Git 仓库，使用源码哈希标识版本；不伪造提交号。

## 使用

在 `D:\毕业设计\auth-lifecycle` 目录运行，Python 3.11+，仅标准库：

```powershell
python scripts/b_cli.py solve examples/b/mixed_alternatives.json --engine B --out b-delivery.json
python scripts/b_cli.py check examples/b/mixed_alternatives.json b-delivery.json
python scripts/b_cli.py audit-g examples/b/mixed_alternatives.json b-delivery.json
python scripts/b_cli.py solve examples/b/mixed_alternatives.json --engine B-B
python scripts/b_cli.py solve examples/b/mixed_alternatives.json --engine reference
python scripts/b_cli.py conflict examples/b/shared_root_conflict.json --out b-conflict.json
python scripts/b_cli.py check examples/b/shared_root_conflict.json b-conflict.json --kind conflict
python scripts/validate_b.py --out results/b/my_run
python scripts/validate_b.py --out results/b/my_replay --replay-of results/b/my_run
```

`--out` 必须指向新文件/目录。CLI 返回 0 仅表示命令已处理；读取 JSON 的 `status` 或 `verdict` 判断语义结果。限额耗尽为 `INCONCLUSIVE`，不得将可能附带的合法 incumbent 当成最优性证明。

本轮未执行正式 H-B、真实认证适配或真实 AI 运行。有限检查和原型成本不能证明创新性、一般安全或独立算法优势。
