# ADR-008：RFC 9381 Provider 与显式模拟器

- 状态：Accepted with Gate
- 追踪：FR-033～035；AC-006～007、AC-012、AC-018

## 背景

未来随机性必须可验证且在集合承诺后产生。现有部分 Ed25519 VRF 库实现旧 draft，若直接采用会造成算法名称与实际字节不一致。

## 决策

生产 profile 只接受 RFC 9381 `ECVRF-EDWARDS25519-SHA512-TAI` 且必须通过 Appendix B.3。测试 Beacon 使用独立 adapter，类型和 UI 强制标记 `SIMULATED`，不得称为 VRF。

## 替代方案

- 使用旧 draft 库：接入快但协议不兼容。
- 把 HMAC/签名哈希称作 VRF：可确定复现但没有标准 VRF 证明语义。

## 后果

真实 Provider 未通过门禁时生产 profile 必须拒绝启动；答辩仍可用显式模拟 profile 演示状态闭环，但不能据此宣称 VRF 安全完成。
