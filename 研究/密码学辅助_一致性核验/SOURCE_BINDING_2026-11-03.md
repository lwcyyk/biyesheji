# 从原生 AES-GCM 记录到私密诊断残差

## Material Passport

origin_skill: academic-research-suite；origin_mode: construct-and-validate；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: source-binding-01；repro_lock: null。

本轮把“直接给诊断器输入残差”的实验推进为“在真实认证 MPC 内根据共享密钥、公开密文和声明明文份额计算残差”。这是来源绑定的一个有界记录层实现，不是完整 TLS 实现，不是新的 AES/GCM 算法，也不是对代码正确性的机器形式化证明。

## 1. 明确的输入关系

限定 AES-128-GCM、96 位 nonce、完整128位 tag，每条密文恰好16字节。主实验包含两条记录和八种验证场景，使用同一个事先建立的共享密钥。公开输入为记录的 nonce N、AAD A、密文 C、收到的标签 T；秘密输入为两方各自的密钥份额，以及声明明文 P_hat 的份额。

在 MPC 内计算：

- H=AES_K(0^128)，J0=N||0^31||1。
- T_expected=AES_K(J0) XOR GHASH_H(A,C)。
- P_expected=C XOR AES_K(inc32(J0))。
- d_tag=T_expected XOR T。
- d_plain=P_expected XOR P_hat。

两个残差均为完整128位差值，没有通过摘要再压缩。一条记录两项检查，两条记录形成四项残差，交给固定 k=2 的诊断方法。主运行不会公开密钥、期望标签或明文，只公开允许的诊断结果；日志不可见秘密本身不构成隐私证明，隐私仍依赖完整协议及底座假设。

这里的输出是双方参与的 MPC 计算结果，不是可供任意第三方离线验证的零知识证明或签名证书。结果日志也不能自行被当成可信服务证明。

## 2. 字节表示和输入域验证

AES 字节域的模多项式为 x^8+x^4+x^3+x+1。诊断器和 GHASH 使用 GF(2^128)。实现选择 GF(2^128) 中该字节多项式的一个根 θ，用 θ 的幂构造嵌入 E:GF(2^8)→GF(2^128)。

对每个输入密钥份额字节，先秘密计算 x^256−x，再用独立均匀非零因子盲化打开。合法输入均得到零；非法字节域输入在任何 AES 或诊断输出之前触发 INPUT_DOMAIN_INVALID。不能把任意128位域元素默认为合法 AES 字节。

AES S-box 用字节域逆元 x^254 与标准仿射变换实现，零的逆元约定仍给出标准 S-box(0)=0x63。仿射变换、字节转换采用线性化多项式；其系数由公开基向量求解，没有新增密码假设。

GHASH 的位串约定与普通大端整数的多项式系数方向不同。实现明确反转每个128位串的位序，并把秘密嵌入字节转换为相同约定。测试包括65,536个字节乘法嵌入关系、全部256个S-box及字节映射、标准 AES-128 测试向量和独立库 AES-GCM 比较。

## 3. 条件性正确性与组合

假设共享密钥确实属于目标会话，双方已同意不可变的记录上下文与程序，认证算术正确且输入域检查通过。则标准 AES/GHASH 算术关系成立：d_tag=0 当且仅当收到的标签等于该密钥、nonce、AAD、密文计算出的标签；d_plain=0 当且仅当声明明文等于该密钥下的 CTR 解密结果。

因此，合法标签不能替代明文份额绑定。测试 wrong_claim0 中，标签差为零，但声明明文差非零，真实 MPC 返回失败位置1，准确对应第一条记录的声明明文检查。

将这些残差在同一 MPC 程序中直接送入诊断器，消除了“执行器在 AES 检查后另外提交一组任意残差”的接口。条件于算术与诊断前提，零/非零关系保持到最终定位输出；端到端误差仍需计入诊断 gate、MPC 底座及密钥/上下文来源假设。AES-GCM 的标签匹配也不能被表述为没有密码学伪造概率的来源真实性证明。

**尚未包含：** TLS握手与证书、会话密钥派生及其身份绑定、记录序号/nonce唯一性管理、跨会话重放控制、输出到AI代理的可信传输、HTTP解析与字段语义。本轮仅完成给定密钥与上下文后的记录关系验证。旧记录原样重放仍可能通过这些加密关系；“此时服务是否仍 active”需要主线的时效及外部状态语义。

此诊断功能允许公开四项残差的受限支持信息，包括在标签异常时某个声明是否一致；它不是标准 AEAD 解密 API 的完整隐私接口。生产接入应审批该诊断泄漏、限制自适应查询，并按主线要求决定是否先完成认证再开放明文相关诊断。

## 4. 代码与独立检查

- source_binding/aes_field.py：标准 AES、字节域嵌入、GHASH表示及运算。
- source_binding/validate_aes.py：独立 cryptography 库与已知向量比较。
- source_binding/build_experiment.py：生成自包含 MPC 程序和合成测试输入，引用原诊断器源码哈希。
- source_binding/build_comparators.py：给原 moments 和 coordinate 基线接入完全相同的记录验证前端。
- source_binding/generated01/bind_gcm.mpc：实际执行的新方案；生成的公开程序不含合成密钥或声明明文的明文值。

密钥和合成明文在测试驱动者掌握的 fixture.json 中保存，用于复现与独立期望值核对；这不是生产秘密存储示例。两个同机进程也不构成独立管理域。

## 5. 验证范围与结果

明文算术检查：全部256个 S-box、65,536个字节域乘法关系、9个 AES 块例、4个不同 AAD 长度的 GCM 例通过。AES 已知向量 000102…0f / 001122…ff 得到 69c4e0d86a7b0430d8cdb78070b4c55a。GCM 的独立基准来自 cryptography 库，而不是诊断器输出。

真实 MPC 八类输入：全有效、仅标签错、仅声明明文错、同记录两项错、交换两条声明、改密文、改AAD、三项同时失败。三种诊断方法使用同一个密钥份额、声明份额和公开记录，独立输出检查均通过；新方案另外作一次语义重放。域外密钥份额的故意负例必须在双方日志中出现 INPUT_DOMAIN_INVALID、无 RESULT/PROTOCOL_DONE，且双方异常退出，才记为预期拒绝通过。

实际运行：MP-SPDZ v0.4.4 / MASCOT，真实预处理，数据域 GF(2^128)，统计安全参数40。没有将128位域大小等同于完整128位安全，也没有使用假预处理。

### 成本核对

每次运行共享五次AES块计算及一次密钥扩展，为八个篡改场景复用两个基础记录的H、标签掩码和计数器输出；这是功能验证批次，不是八个独立 TLS 会话的吞吐测试。

| 方法 | 实际 triples | 实际 inverse tuples |
|---|---:|---:|
| 新 rowspace | 16,297 | 95 |
| 原 moments | 16,269 | 109 |
| coordinate | 16,220 | 116 |

共享前端消耗16,016个triples：字节域验证288、AES及输出转换15,680、GHASH 48。新诊断部分为281。这个口径说明总开销主要在记录关系计算，而不是诊断器；不能用核心少一次乘法宣称端到端显著提速。上述是本机单次/重放开发数据，不作正式统计判断。

## 6. 复现

以下目录名应换成尚不存在的新目录，历史输出不会被自动覆盖。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\研究\密码学辅助_一致性核验'
wsl -d Ubuntu-24.04 -- python3 source_binding/validate_aes.py --out results/my_aes_clear
wsl -d Ubuntu-24.04 -- python3 mpc/run_backend.py --out results/my_binding --source source_binding/generated01/bind_gcm.mpc --compiler-arg 4 --compiler-arg 8 --fixture source_binding/generated01/fixture.json --timeout 240
wsl -d Ubuntu-24.04 -- python3 mpc/fixtures.py --verify results/my_binding --fixture source_binding/generated01/fixture.json
wsl -d Ubuntu-24.04 -- python3 mpc/run_backend.py --out results/my_domain_reject --source source_binding/generated01/bind_gcm.mpc --compiler-arg 4 --compiler-arg 8 --fixture source_binding/generated01/invalid_fixture.json --timeout 240
```

最后一条预期非零退出，必须核对具体原因，不能把任意崩溃当成安全拒绝。原始结果目录为 source_binding_mpc01/02、source_binding_moments01、source_binding_coordinate01 和 source_binding_invalid01，均位于 results/ 下。

标准来源：[NIST FIPS 197，2001/2023更新](https://doi.org/10.6028/NIST.FIPS.197-upd1)；[NIST SP 800-38D，2007](https://doi.org/10.6028/NIST.SP.800-38D)。本轮没有声称通过 NIST 实现认证。
