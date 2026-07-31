# ADR-003：确定性 CBOR 作为协议编码

- 状态：Accepted
- 追踪：FR-004、FR-012、FR-023、FR-031～032、FR-043；AC-010、AC-012～013、AC-018

## 背景

签名、哈希、KDF 和 Merkle 输入必须跨 Go/TypeScript 重现；直接签 JSON 会受键顺序、数字和 Unicode 表示差异影响。

## 决策

协议对象使用 RFC 8949 Core Deterministic CBOR；禁用浮点、tag、不定长、重复 key、未知字段和非最短编码。API JSON 只做传输，验证前重建强类型对象。

## 替代方案

- JSON/JCS：调试友好，但二进制 ID、数字边界和双实现约束更多。
- Protobuf deterministic：未知字段、map 与 schema 演进仍需额外协议约束。

## 后果

需要严格 wrapper、固定字节向量和双语言 manifest；协议字段或枚举变化必须显式升级版本。
