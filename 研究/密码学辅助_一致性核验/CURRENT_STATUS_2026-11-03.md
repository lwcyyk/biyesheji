# 本轮交付：保留行空间的私密稀疏诊断

## Material Passport

origin_skill: academic-research-suite；origin_mode: construct-and-validate；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: rowspace-delivery-01；repro_lock: null。

本轮产生了一个实际结构变化：用秘密均匀可逆矩阵混合短 Hankel 矩阵，公开其结果并从行空间恢复支持。在至多 k 处失败、算术正确且成功采样合法掩码时，非零幅值完美隐藏，支持精确恢复，取消旧诊断层的遗漏复核。它没有取消前置稀疏 gate，也没有消除端到端概率错误或中止。

**当前状态：候选构造、条件性证明、独立有限核验及 k=2 真实 MPC 已完成；强独立密码学原创性仍未确认。**

## 交付入口

| 交付 | 文件 |
|---|---|
| 构造、证明、错误界、受限最小性及反例 | [ROWSPACE_2026-11-03.md](ROWSPACE_2026-11-03.md) |
| 有限验证、同功能三方比较、旧方案更紧界及复现 | [ROWSPACE_VALIDATION_2026-11-03.md](ROWSPACE_VALIDATION_2026-11-03.md) |
| 新增一手文献及原创性反方审查 | [LITERATURE_2026-11-03.md](LITERATURE_2026-11-03.md) |
| 候选与独立参考 | [construction/rowspace.py](construction/rowspace.py)、[construction/rowspace_reference.py](construction/rowspace_reference.py) |
| 真实 MPC | [mpc/rowspace2.mpc](mpc/rowspace2.mpc) |
| 完整测试入口 | [construction/validate_rowspace.py](construction/validate_rowspace.py)、[mpc/rowspace_sweep.py](mpc/rowspace_sweep.py) |
| 原始实验记录 | [results/rowspace_paired01/summary.json](results/rowspace_paired01/summary.json) |
| 交付哈希、源文件快照与历史保持 | [results/rowspace_delivery01/manifest.json](results/rowspace_delivery01/manifest.json) |

## 已得到的证据

- 1,411 个稀疏向量、8,466 次比较、192 个一般参数例及4,096个公开解码输入均一致。
- 对完整 GL2(GF16) 的244,800次分布枚举确认所测同支持不同幅值公开分布完全相同；一般结论仍依赖数学证明。
- 12次两方 MPC、108个逻辑批次全部通过独立输出核对，包含专门构造的稠密伪装输入。
- 保留四种不安全变体及受限列数/矩数量碰撞；进一步收紧旧方案误差界，以保持比较公平。

## 实测限制和未完成项

新方案与旧方案耗时接近，没有稳定加速结论。新方案成功采样后的诊断是精确的，但采样可能耗尽；全有效和单故障场景不具有统一可用性优势。数据域 GF(2^128)，底座统计参数40；真实 MPC仅实现k=2。没有进行正式 H-A/H-B/H-AB 统计判定。

本轮发现的2026年共享 Reed–Solomon 解码是优先级很高的直接比较对象，仍需阅读全文排除自然扩展等价性。完整残差来源绑定、恶意实现审计、并发/重启和端到端组合证明也尚未完成。

此前文档和实验保持原状；本文件是新增阶段入口，不替换原 CURRENT_STATUS.md，不修改主线 auth-lifecycle 或原毕业设计 DOCX。
