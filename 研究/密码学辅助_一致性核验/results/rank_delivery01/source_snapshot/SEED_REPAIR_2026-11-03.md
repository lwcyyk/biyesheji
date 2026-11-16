# 两故障诊断的确定性单遗漏修复

## Material Passport

origin_skill: academic-research-suite；origin_mode: construct-and-validate；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: seed-repair-01；repro_lock: null。

这是非零种子方案的进一步改造。中间的重采样版本仍保留在 NONZERO_SEED_2026-11-03.md 和原始结果中，本文件不改写那些历史结果。

## 1. 修复，而不是重新诊断

依旧采样均匀非零系数向量(r0,r1)，公开四个R(X)=r0+r1X的掩码矩，得到候选支持S'。在真实支持S大小≤2的前提下，S\S'最多包含一个位置。

计算秘密剩余矩 E0=Σ_(i∉S')d_i、E1=Σ_(i∉S')d_i a_i。取新鲜秘密σ∈F*，先公开z0=σE0：

- z0=0：没有遗漏，接受S'。
- z0≠0：恰好遗漏一个位置j，此时E0=d_j，E1=a_jd_j。再用同一个σ公开z1=σE1，得到a_j=z1/z0。核对它是尚未包含的合法标签，并核对最终支持大小≤2，再接受S'∪{j}。

这消除了诊断阶段重采样。合法种子下，所有稀疏输入都精确完成；剩余INCONCLUSIVE只来自输入无关的种子生成预算、不可达于诚实稀疏执行的解码拒绝，或底座/执行故障。稠密gate仍可能误放行，整体不具有无条件零错误。

## 2. 为什么这里可以复用σ

跨批次复用盲因子通常会泄漏幅值比值。但此处结构已保证剩余向量只有一个非零项，公开二元组恰为(z,a_j z)，其中z在F*均匀。其分布只依赖允许泄漏的遗漏位置j，与d_j无关。

给定S及第一阶段公开矩，模拟器知道S'。无遗漏时输出0；有遗漏时选均匀z≠0，输出(z,a_jz)。与非零种子阶段的幅值隐私结合，得到理想稀疏执行中整个公开转录的完美幅值隐藏。

这个结论只能用于同一次、已经证明一稀疏的剩余向量。不能把它用于任意两个残差、跨批次查询或未经检查的稠密输入。如果省略非零种子条件，两个相等遗漏会令E0=0，仍可错误接受。

## 3. 终止与成本

种子生成仍最多T=2次，失败概率为q^−4；成功后没有随机诊断耗尽。因此在诚实理想稀疏执行中，本层正确完成概率为1−q^−4，错误接受概率为零。这个概率不涵盖恶意中止或底座失败。

一般情况下，包含相同稀疏gate、种子生成和真实随机量三元组，消耗32个triples、9个inverse tuples。触发修复时再增加1个秘密乘积，复用已经生成的σ，不增加inverse tuple。

强化后的旧moments同样消耗32个triples而非原实现的33；本方案不能声称三元组数严格优于所有旧实现。其区别是稀疏层精确性及取消诊断重试，代价和时延仍须实际比较。与此前GL2方案相比，种子生成失败从约q^−2（两次GL2尝试）降至q^−4，但不能据此宣称整个协议安全参数提升，因为gate与底座仍是限制。

## 4. 验证

results/seed_repair_algebra01/02 对全部1,411个GF(16)稀疏向量及255个非零种子，即359,805对输入执行精确检查，其中发生41,400次实际修复，全部恢复真实支持。21,165对另外调用候选实现与独立矩表比较。15,300组完整公开随机转录检查确认所测同支持不同幅值分布精确一致。

results/seed_repair_secure01 是正常随机采样的真实两方MPC，九个合成批次均通过独立检查。GF(2^128)中修复极罕见，该运行没有假装覆盖到随机修复事件。

为覆盖真实执行器里的修复分支，results/seed_repair_lab01 使用显式固定种子的专用程序，把根放到最后一个标签，正确执行了单故障和双故障的修复分支。程序和日志均标记 LAB_FIXED_SEED_NOT_PRIVATE。**这只是合成数据下的功能分支测试，不是私密协议运行或隐私证据；该程序禁止用于真实秘密。** 小域完整分布检查与正常随机程序是另外的证据。

## 5. 与维数定理的关系

r≥k下界针对输入独立的掩码表示同时要求完美幅值隐藏和中间绝不抹除。本方案使用r=1，允许中间抹除，再通过经过结构约束的自适应补证恢复位置，因而没有违反该下界。

更一般地，秩r使剩余错误数上界降到k−r，可在这个更小的承诺域里调用精确私密诊断。只有k=2的单遗漏修复完成了本轮实现；一般递归版本、最优总成本和统一最优参数选择均未证明或实现。

## 6. 代码与复现

- construction/nonzero_seed_repair.py：明文候选，仅用于验证。
- construction/validate_seed_repair.py：精确有限检查。
- mpc/seed_repair2.mpc：正常随机采样程序。
- mpc/seed_repair2_lab_last.mpc：非私密、固定种子的分支测试程序。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\研究\密码学辅助_一致性核验'
wsl -d Ubuntu-24.04 -- python3 construction/validate_seed_repair.py --out results/my_repair_algebra
wsl -d Ubuntu-24.04 -- python3 mpc/run_backend.py --out results/my_repair_mpc --source mpc/seed_repair2.mpc --compiler-arg 8 --compiler-arg 9 --fixture results/rowspace_paired01/n8.json
wsl -d Ubuntu-24.04 -- python3 mpc/fixtures.py --verify results/my_repair_mpc --fixture results/rowspace_paired01/n8.json
```

输出目录必须是新的。当前底座统计参数仍为40、同机两方；没有完成全面恶意行为审计、机器形式化证明或新变体的AES-GCM前端重跑。
