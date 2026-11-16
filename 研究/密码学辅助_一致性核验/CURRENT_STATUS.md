# 当前交付：一般阈值掩码、紧泄漏界与真实 MPC 开发验证

## Material Passport

origin_skill: academic-research-suite；origin_mode: construct-and-validate；origin_date: 2026-11-02；verification_status: UNVERIFIED；version_label: crypto-aux-delivery-02；repro_lock: null。

**已有可核对的构造、条件性证明和真实 MPC 开发证据；“较强独立密码学原创性”目标尚未确认达到。** 主线 A/B/AB 仓库及原毕业设计 DOCX 未被本轮改动。旧 README、PROOFS、delivery_manifest 和 final04 仍表示前一阶段，均保留原文和原始结果。

本轮最有价值的理论进展是：先得到三点非零 affine 掩码的幅值区分距离紧界 1/(q−2)，再推广到一般次数<k 的掩码，得到全局 n 点非零约束下的最优模拟误差 **1−N/(q−1)^k**，其中 N 是合法多项式数量。k=2 时精确化为 **(n−2)/(q−1)**，并给出达到它的分布。这解释了低维掩码为何不能同时简单消除遗漏并保持原隐私界。它是限定模型下的完整数学推导，尚未完成文献优先权与独立证明审查。

另将掩码矩层推广到一般 k，以 3k−1 次双线性乘法完成，去掉原五次单位根限制。此方法明确基于经典转置中间积，不另立“新乘法理论”主张。

真实 MP-SPDZ/MASCOT 两方实验通过同功能逐项独立掩码基线比较；八次运行的 64 个逻辑批次均经独立期望值检查。64 项批次中候选减少通信及含预处理耗时；8 项批次中简单基线更快，两种规模下基线在线耗时均更低。完整数据保留，未执行正式统计支持判定。

## 交付入口

| 内容 | 文件 |
|---|---|
| 一般阈值构造、条件性归约、紧泄漏界证明 | [CONSTRUCTION_EXTENSION.md](CONSTRUCTION_EXTENSION.md) |
| 更一般的最优模拟隐私界及匹配分布 | [TIGHT_LEAKAGE_BOUND.md](TIGHT_LEAKAGE_BOUND.md) |
| 原创性重新核验、关键先例、反方审查 | [NOVELTY_REASSESSMENT.md](NOVELTY_REASSESSMENT.md) |
| 实际 MPC、成本、负结果、复现命令 | [MPC_VALIDATION.md](MPC_VALIDATION.md) |
| 候选与同功能强基线 | [mpc/locate2.mpc](mpc/locate2.mpc) |
| 独立输出检查与实验驱动 | [mpc/fixtures.py](mpc/fixtures.py)、[mpc/sweep.py](mpc/sweep.py) |
| 一般掩码层及有限验证 | [construction/general_mask.py](construction/general_mask.py)、[construction/validate_general.py](construction/validate_general.py) |
| 紧泄漏界的穷尽实例 | [construction/leakage_barrier.py](construction/leakage_barrier.py) |
| 源码哈希、历史保持与重放核对 | [results/construction_mpc_delivery03/manifest.json](results/construction_mpc_delivery03/manifest.json) |

## 与主线的准确关系

这个模块最多证明某些认证残差的一致性及定位完整性，不能自行证明服务的撤销语义，也不改变 B 的原生独立撤销单元 G。完整来源绑定缺失时，它不是端到端认证契约证据。

如后续接入 A，接口必须包括上下文/密钥代次、证据范围、公开位置泄漏批准、随机误差预算、故障及中止、清理义务和失效条件。MANY、INCONCLUSIVE 和密码学认证失败都不能直接等同 B 的配置不可行。原 W_r 的逐轨迹保证也不能直接吸收密码学小概率误接纳而不修改定理前提。

## 尚未达到的目标及明确进入条件

1. 先排除 Arithmetic Sketching 与既有私密稀疏恢复的自然组合等价性，并核验紧泄漏界的优先权，才能确定可主张的独立原创贡献。
2. 完成被认证响应到残差份额的真实来源绑定，且证明其不会被恶意执行器替换，才能声称解决主线信任问题。
3. 独立核验底座与端到端参数。当前开发运行统计安全参数为 40，不能因使用 GF(2^128) 宣称完整 128 位或 256 位安全。
4. 加入恶意行为、重启、并发及跨机器检查，补足实现证据；一般 k 的完整协议移植仍待完成。

若文献比较证明本方案只是已有组件的自然实例，应将其如实归为专用优化和安全工程，不通过更名、改成本函数或降低泄漏要求维持原创主张。
