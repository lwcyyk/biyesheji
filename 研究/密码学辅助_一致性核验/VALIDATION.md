# 验证记录与复现

## Material Passport

范围：理想算术协议、有限域、公开转录分布、独立代数参考及合成 AES-GCM 例子。非真实 MPC、非在线 TLS、非安全认证产品。所有原始输入都是合成数据。论证为人工可复核数学文本，未进行机器证明或独立同行审定。

最终状态：**PASS_STATED_ALGEBRA_CHECKS**。这一状态不表示“协议零错误”“原创新颖性成立”或“完整 TLS 协议完成”。

## 工件

- [最终汇总](results/final04/summary.json)
- [环境与实际命令](results/final04/environment.json)、[源码哈希](results/final04/source_hashes.json)
- [16 个自动测试日志](results/final04/unittest.log)、[逐测试状态](results/final04/tests.json)
- [有限检查范围与计数](results/final04/finite_summary.json)
- [全部公开矩的解码检查](results/final04/decoder_exhaustive.jsonl)
- [掩码分布精确比较](results/final04/mask_privacy.jsonl)
- [稀疏性门的原始枚举](results/final04/gate_exhaustive.jsonl)
- [反例与分布距离](results/final04/counterexamples.json)
- [360 次理想运行及独立重放](results/final04/trials.jsonl)
- [合成 AES-GCM 与错误明文链接反例](results/final04/native_binding.json)
- [额外保留的误接纳随机带](results/final04/error_witness.json)
- [重放比较](results/final04/replay.json)

最终源码包 SHA-256：`bd1e0e4a86d25c05197b8deddb8aaabea578876fc77a533875e4084da7f3a5ef`。哈希清单只包含目录顶层 Python 源码；说明文档另列交付清单。

## 实际执行范围

| 检查 | 范围 | 结果 |
|---|---|---|
| 自动测试 | 16 个测试方法 | 0 失败、0 错误、0 跳过 |
| 公开解码 | GF(16)、6 个位置、最多两处错误，穷尽全部 16⁴=65,536 个四元矩 | Berlekamp–Massey、显式 Prony、3,466 个稀疏向量精确表一致 |
| 数值隐私 | GF(16)、4 个位置的全部 1,411 个零/一/二稀疏向量；每个遍历 256 个掩码 | 361,216 次掩码求值；分布与仅知道支持集的模拟器一致 |
| 门可靠性 | GF(16)、4 个残差，残差取 {0,1,2,3}；k=1/2 的 432 个超阈值输入 | 穷尽 692,550 个单轮挑战元组，全部满足解析上界 |
| 放大可靠性 | 对上一行的精确失败集合取两次独立笛卡尔积计数 | 是精确计数推导，不冒称又逐项枚举了全部平方数量 |
| 理想端到端 | 固定种子 20261102；GF(16) 200 次、GF(256) 120 次、GF(2¹²⁸) 40 次 | 360 次候选与独立参考一致；5 次 INCONCLUSIVE 保留；该随机样本未观察到错误分类 |
| 五乘法中间积 | 三个域的双线性基向量与随机输入 | 与直接表达式一致，实际应用层计数为 5 |
| 范数零点 | GF(16) 全部 256 个输入对 | 仅 (0,0) 映射为零 |
| 重放 | final03 与 final04 | 8 个确定性结果文件逐字节相同；时间不比较 |

这些行存在重叠执行，不能相加为独立统计样本。κ=128 的 40 次运行只是代数检查，不表示验证了 128 位计算安全。GF(16) 和 GF(256) 都是故意选取的小域，不可作实际安全参数。

## 三个明确结果

**全局非零掩码筛选会泄漏。** 两个相同支持集、不同非零数值的输入，在过滤“任何公开位置有零值”的掩码后，总变差距离为 **2/13**。这否定了该受限类中“通过全局过滤即可同时消除重试且保持原隐私”的优化。

**分别公开重复结果不能同步放大隐私。** 在所列 GF(16) 验证子例中，两次独立检查分别公开零标志的分布距离为 **56/225**；先在秘密域内作范数组合、只公开联合零标志后为 **2/225**。这不是完整协议总体泄漏率，而是特定条件下公开验证视图的精确比较。

**五乘法只属于一个子层。** 四个掩码矩从朴素的 8 次秘密乘法降到 5 次；放大后的整个 k=2 一次尝试仍为 **31 次**，每次重试增加 9 次。预处理、输入认证、真实网络与 TLS 成本没有计入，不报告端到端加速比。

## 错误概率不是零

单轮门枚举中，k=1 的最大失败挑战数为 55/225，k=2 为 855/3375，均低于对应的解析界。放大后错误概率按独立乘积下降，但不会消失。

另外保存了一个明确随机带：GF(16)，输入 `[1,1,1,0]` 有三处错误；两套门挑战都为 `[1,1,1]`，掩码为 `[0,0]`，两个遗漏检查挑战都选为输入多项式的根，最后错误输出 ALL_VALID。它确实可能由均匀随机币产生，概率很小但非零；若攻击者能够选择这些币，则可以直接利用。

该例与 360 次固定种子样本分开保存，未删除、未混入通过计数。不能把“随机样本没观察到误分类”写成完美可靠性。

重现这一随机带：

```powershell
@'
import json
from pathlib import Path
from field import Field
from kernel import run
x = json.loads(Path('results/final04/error_witness.json').read_text(encoding='utf-8'))
print(run(Field(x['field_bits']), x['input'], **x['randomness']))
'@ | python -
```

## 开发审查发现与修复

首轮 13 测试和独立参考增强后的 15 测试结果分别保留在 dev01、final01/final02。

随后发现 `lru_cache` 默认键会使 `True` 与 `1` 混同：缓存命中可跳过低层域元素类型检查。原始输入和错误返回保存在 [review_bool_cache.json](results/review_bool_cache.json)。Session 入口原本另有类型检查，所以此问题不改变所测整数输入的代数结论，但低层 API 仍需修复。

修复为 `typed=True` 并增加回归测试。final03/final04 使用同一修复后源码。修复前后的 7 个整数语义结果文件也逐字节一致，见 [比较记录](results/semantic_comparison_after_type_fix.json)。没有覆盖旧结果。

## 复现命令

```powershell
Set-Location -LiteralPath 'D:\毕业设计\研究\密码学辅助_一致性核验'
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' validate.py --out results/reproduce01
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' validate.py --out results/reproduce02 --replay-of results/reproduce01
```

主测试脚本生成常规原始结果；上述误接纳随机带是单独补充的定向反例。所有输出目录必须新建。

## 尚未运行或建立

真实恶意安全 MPC、真实 TLS、凭据非导出、输出份额来源绑定、底座预处理与通信成本、完整计算安全归约、一般实现的机器证明、正式新颖性验证。这些状态均不能由本轮代数验证升级为完成。
