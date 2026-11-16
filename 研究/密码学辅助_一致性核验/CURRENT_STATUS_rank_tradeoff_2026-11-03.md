# 本轮交付：掩码秩与确定性补证的理论及实例

## Material Passport

origin_skill: academic-research-suite；origin_mode: research-construct-validate；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: rank-delivery-01；repro_lock: null。

本轮把创新主张集中到一个明确问题：完美隐藏稀疏残差幅值时，掩码维数、随机遗漏和所需补证之间有什么必要关系。

已给出限定模型下的分布刻画、无中间抹除时r≥k的必要性、随机性下界、精确遗漏概率，以及k−r个固定剩余矩的充分必要性。再由此实现两故障的非零系数向量与单遗漏修复：成功生成种子后，稀疏输入精确完成，不重跑诊断。

这构成了更明确的理论与构造贡献候选；**一般证明尚未获独立/机器核验，文献优先权仍未确认，不能宣布较强独立原创性已最终达标。**

## 入口

| 内容 | 文件 |
|---|---|
| 定义、定理、证明、边界 | [RANK_PRIVACY_TRADEOFF_2026-11-03.md](RANK_PRIVACY_TRADEOFF_2026-11-03.md) |
| 最终两故障修复构造 | [SEED_REPAIR_2026-11-03.md](SEED_REPAIR_2026-11-03.md) |
| 中间的非零种子重试版本与四方法比较 | [NONZERO_SEED_2026-11-03.md](NONZERO_SEED_2026-11-03.md) |
| 创新主张、先例和反方审查 | [NOVELTY_RANK_PACKAGE_2026-11-03.md](NOVELTY_RANK_PACKAGE_2026-11-03.md) |
| 正常随机采样的实际MPC | [mpc/seed_repair2.mpc](mpc/seed_repair2.mpc) |
| 理论有限检查 | [construction/rank_tradeoff_checks.py](construction/rank_tradeoff_checks.py) |
| 完整修复检查 | [construction/validate_seed_repair.py](construction/validate_seed_repair.py) |
| 原始结果、重放、历史保持与快照 | [results/rank_delivery01/manifest.json](results/rank_delivery01/manifest.json) |

有限检查覆盖359,805组稀疏向量与非零种子，其中41,400次遗漏修复全部正确；完整小域公开转录分布与独立参考一致。理论群轨道检查覆盖GF(3)/GF(4)六个档，包含条件失效的反例。

四方法同输入开发比较全部通过，并提供加强旧基线的随机量复用变体。实际成本没有支持新方案整体加速：三元组消耗相同不等于通信和时延相同。固定种子MPC程序仅用于触发修复分支，明确标为非私密实验，不并入协议隐私证据。

所有工作位于独立研究目录，原始源码、DOCX、主线auth-lifecycle及既有结果保持不变。此前AES-GCM前端未改动；本轮没有把其旧实验重标为新修复变体的结果。
