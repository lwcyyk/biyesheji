# 复现、原始结果与成本口径

版本：`structural-audit-r1`，2026-11-03。该研究目录不是Git仓库，本轮不创建或改动Git；源码身份由快照和SHA-256确定。原主线auth-lifecycle无写入。

## 1. 环境与运行命令

PowerShell，WSL Ubuntu-24.04，Python3；命令从 `D:\毕业设计\研究\密码学辅助_一致性核验` 执行。所有输出限制在本轮revision。现有结果目录不覆盖；再次复现时换成未存在的输出名。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\研究\密码学辅助_一致性核验'
wsl -d Ubuntu-24.04 -- python3 -B revisions/structural_audit_2026-11-03_r1/test_all.py --out results/dev03
wsl -d Ubuntu-24.04 -- python3 -B revisions/structural_audit_2026-11-03_r1/verify_group_steps.py --out results/algebra03
wsl -d Ubuntu-24.04 -- python3 -B revisions/structural_audit_2026-11-03_r1/verify_certificate_attacks.py --out results/certificate_attacks03
wsl -d Ubuntu-24.04 -- python3 -B revisions/structural_audit_2026-11-03_r1/public_costs.py --out results/public_costs02.json
```

本轮已运行dev01/dev02、algebra01/algebra02、certificate_attacks01/02。各自的确定性结果逐文件比较在交付manifest中；时间数据不要求字节重现。

MPC使用已有固定MP-SPDZ 0.4.4发布包，归档SHA256为 `73d6473526101b4433999fc4f7521fdfdc53ddf018e5f64480518d6293f62760`。读取原 `mpc/run_backend.py`，不修改它。使用两本地进程、GF(2^128)、`-S 40`、live preprocessing，无fake预处理。`PYTHONDONTWRITEBYTECODE=1` 防止往历史vendor写pycache。

```powershell
wsl -d Ubuntu-24.04 -- env PYTHONDONTWRITEBYTECODE=1 python3 -B mpc/run_backend.py --out revisions/structural_audit_2026-11-03_r1/results/gate_original_replay --source revisions/structural_audit_2026-11-03_r1/gate_mpc/support_gate.mpc --compiler-arg original --fixture revisions/structural_audit_2026-11-03_r1/gate_mpc/fixture.json --timeout 180
wsl -d Ubuntu-24.04 -- env PYTHONDONTWRITEBYTECODE=1 python3 -B mpc/run_backend.py --out revisions/structural_audit_2026-11-03_r1/results/gate_restricted_replay --source revisions/structural_audit_2026-11-03_r1/gate_mpc/support_gate.mpc --compiler-arg restricted --fixture revisions/structural_audit_2026-11-03_r1/gate_mpc/fixture.json --timeout 180
wsl -d Ubuntu-24.04 -- env PYTHONDONTWRITEBYTECODE=1 python3 -B mpc/run_backend.py --out revisions/structural_audit_2026-11-03_r1/results/release_original_replay --source revisions/structural_audit_2026-11-03_r1/gate_mpc/gate_release.mpc --compiler-arg original --fixture revisions/structural_audit_2026-11-03_r1/gate_mpc/fixture.json --timeout 180
wsl -d Ubuntu-24.04 -- env PYTHONDONTWRITEBYTECODE=1 python3 -B mpc/run_backend.py --out revisions/structural_audit_2026-11-03_r1/results/release_restricted_replay --source revisions/structural_audit_2026-11-03_r1/gate_mpc/gate_release.mpc --compiler-arg restricted --fixture revisions/structural_audit_2026-11-03_r1/gate_mpc/fixture.json --timeout 180
```

独立日志核对：`verify_gate_logs.py --out results/gate_log_verification02.json` 默认复核本轮四个原始目录；若复核上面的_replay目录，加 `--suffix _replay`。它从残差值自行推导支持和两种语义谓词，不使用gate生成器计算预期。每方进程返回值、party0输出及拒绝时无支持输出都核对。未把runner的success直接当成功能验证。

## 2. 本轮测试结果

| 项目 | 实际范围 | 结果 |
|---|---|---|
| 主有限审计 | GF3/GF4，8种字典×2域，66种基、228个二维可逆行变换、538个gate输入 | 898条断言通过，dev02重放一致 |
| 额外两类证书攻击 | 逐字段遗漏、上下文替换、重绑定错误模型、移除允许支持见证 | 70条断言通过，重放一致 |
| 群生成及边界 | GF3/GF4，维2/3的1016个显式恒等式实例；GL2的48/180个矩阵上完整三角独立支持分布 | 21条汇总断言通过，重放一致 |
| 正常随机MPC参考 | 两profile×两参考，各8个合成残差场景 | 32例输出符合预期，进程成功；不是恶意安全测试 |
| 文献PDF检查 | Oxley版次及页结构 | preflight stdout PASS，722页；Windows直接--output失败后用stdout保存，记录于来源附注 |

原旧实现可复现问题保留在 `results/dev01/legacy_findings.json`；它们不是新checker测试失败。没有删掉不合规反例，亦没有将部分未运行项目计入通过。

关键反例原始值：(1,1,0,0)在原契约可定位，在每记录至多一个失败的契约必须拒绝；三角字典仅单点族的一行掩码；相关支持加余单元素；省略左逆回译使第二列抹除；两个块共用frame系数泄漏比例。输入构造和实际/预期记录可在三个测试脚本及checks结果核对。

## 3. MPC开发测量（每行是8例一批，仅一次）

| 参考/profile | 接受/拒绝 | 秘密乘法triples | 全局通信MB（含预处理） | 底座耗时秒（含预处理） | party0总轮次 |
|---|---:|---:|---:|---:|---:|
| gate / 原最多两失败 | 7/1 | 8480 | 331.380 | 1.72982 | 4435 |
| gate / 限制族 | 5/3 | 8416 | 328.923 | 1.75343 | 4435 |
| gate后直接支持 / 原最多两失败 | 7/1 | 8480 | 331.383 | 1.58758 | 4484 |
| gate后直接支持 / 限制族 | 5/3 | 8416 | 328.924 | 1.53023 | 4470 |

来源：`results/gate_log_verification.json`；保留party日志、编译日志和各阶段命令/退出码。耗时波动不能用于声称支持输出更快；可确定的是新增秘密乘法为0，新增开值仍有开销。两个profile成功范围不同，不能直接比较接受率或通信后宣称结构收益。

统计口径：底座Time包含预处理但不含编译及SSL脚本；runner墙钟另列；在线/离线通信、轮次与CPU日志保留。四批编译约1.83–2.38秒，SSL建立约1.83–3.63秒，均不能从总成本中抹去。正常随机MPC不是固定种子掩码隐私实验；合成输入本来就被测试器知道。

本版指数链每坐标254次秘密乘法，4坐标每例1016次。通用gate用秘密常数开始累乘，原族11个minterm×4、限制族9×4，故每例1060/1052次，8例恰为8480/8416。与L0解释器GF4的41/35次秘密乘法不矛盾，域、指数链和常数实现不同，禁止直接横比。

公开编译/检查在n=4两profile各5次，启用Python tracemalloc：编译0.191–0.420ms、检查0.289–1.850ms；对应traced peak 2912–3395 / 4224–5680 bytes。原始每次记录见 `results/public_costs01.json`；不是内核RSS或生产性能。编译器基选择及基坐标/图处理为多项式；独立checker枚举所有活跃子集和回路，最坏为指数，因此显式n≤8且预算耗尽INCONCLUSIVE。

## 4. 未运行/未测量，不补造数字

- 结构优化掩码MPC、五方法完整公平端到端比较：决策门未过，NOT_RUN。
- MPC峰值内存、真实WAN条件、并发负载、恢复/取消/恶意偏离与侧信道：NOT_MEASURED/NOT_RUN。
- 结构采样和预处理成本：只有解析表达式；本轮无结构采样MPC计时。
- 服务来源绑定的新一轮执行、生产域代数证书、主线真实撤销：NOT_RUN。
- 正式H-A/H-B/H-AB统计判定、一般安全或原创性验证：未执行。

因此尚无完整成本优势结论。一般证明、独立优先权、部署安全均不能由上述有限测试替代。

## 5. 快照与保护证据

`input_receipt.json` 固定十份指定输入；`inputs/`存逐字节副本。`delivery_manifest.json`列当前输入与已知旧hash核验、确定性重放、全部本轮文件哈希和状态。`source_snapshot.zip`仅打包本轮源码/报告/fixture/必要运行依赖记录，不复制或重命名整套项目；原始MPC结果保留在results。

旧manifest的523条historical_files中部分只有unchanged布尔声明，没有可用于本轮比对的起始hash；这些只核对存在，不据此声称全部523项已重新证明未变。十输入及旧manifest明确列出的source/raw hash另作实际比对。未取得主线全树的起始哈希，所以报告的是本轮无写入主线，而不是伪造全树差异证明。
