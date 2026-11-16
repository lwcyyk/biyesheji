# 私密一致性核验：两处失败定位的研究原型

本目录是独立研究草稿，不修改 `auth-lifecycle` 的 A/B/AB 主线。

**状态：已有代数构造、条件性证明与有限验证；没有真实恶意安全 MPC、密码学输入绑定或完整 TLS 密文到份额协议；独立原创性未确认。** Python 中的秘密全部是测试驱动者可见的普通数值，不能部署为秘密保护实现。

本轮将上一阶段“最多一处失败”的构造扩展为“最多两处失败”，重点处理：低维随机掩码可能遗漏错误、重复检查的公开结果会泄漏额外信息，以及输出定位结果与真实剩余残差的一致性。

- [协议与威胁边界](PROTOCOL.md)
- [条件性论证和受限最优性](PROOFS.md)
- [验证、反例和复现](VALIDATION.md)
- [先例与反方审查](REVIEW.md)

## 文件

| 文件 | 内容 |
|---|---|
| `field.py` | GF(2⁴)、GF(2⁸)、GF(2¹²⁸) 算术；非恒定时间实验代码 |
| `kernel.py` | 理想算术模型、秩检查、秘密域范数组合、五乘法中间积、定位与复核状态机 |
| `reference.py` | 独立域乘法、Leibniz 行列式、小域精确解码表和显式 Prony 重放 |
| `tests.py` | 单元、反例和独立实现比较 |
| `native_demo.py` | 标准 AES-GCM 的合成链接测试；实际密钥由测试驱动者掌握，不是 MPC |
| `validate.py` | 完整原始记录与确定性重放 |

核心验证仅用 Python 标准库；合成 AES-GCM 测试另用 `cryptography`，本机为 50.0.2。

`results/` 为合成模型重放而保存输入与模拟随机性，**不是生产日志格式**。本目录没有真实用户凭据，也没有把普通 Python 变量当作受保护秘密。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\研究\密码学辅助_一致性核验'
python validate.py --out results/my_run
python validate.py --out results/my_replay --replay-of results/my_run
```

输出目录必须是新的。没有初始化 Git、修改历史结果或更新主线版本。新构造的实际 MPC 通信量、TLS 总开销和新颖性仍需独立验证。
