# 实际测试与费用

日期：2026-11-11。范围：研究者本轮明确批准的成熟工程接线与离线验收。证据为本对话内模型辅助实现、实际执行与知情源码复核；外部独立验证待取得。


## 最终冻结结果

| suite | 项数 | PASS | FAIL | ERROR | SKIP | 满足的检查 |
|---|---:|---:|---:|---:|---:|---:|
| d1a_002 | 24 | 24 | 0 | 0 | 0 | 137 |
| regressions_002（A1 20 + H1 24） | 44 | 44 | 0 | 0 | 0 | 1919 |
| 最终总计 | 68 | 68 | 0 | 0 | 0 | 2056 |

检查数为测试内部布尔检查数量，存在重复断言。最终验收分母为 68；历史重复运行保存在记录中。

新增 ID 来自本轮 R19 清单，原计划的 NOT_RUN 是执行前冻结快照。实际结果在 `D1A_ACTUAL_RESULTS.json` 及两个最终 `RESULTS.json`。预期拒绝属于 PASS 条件；UNKNOWN、STAGING_READY_WITH_GAPS 等业务状态保持实际含义，未升级为完整数学/原生可用性。

## 准确复现命令

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_runtime_tests.py' --suite d1a
```

```powershell
& 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\Scripts\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_runtime_tests.py' --suite regressions
```

这是原实际两种调用模板，单次执行对应一个独立进程。Windows venv launcher 使回归结果的 `sys.orig_argv` 首项显示 base Python；runner 的 preflight 同时以 `sys.executable` 校验获批 venv 路径。原始 argv 记录保留；这里区分工具请求的入口和解释器看到的启动向量。两次最终结果的六个源码 SHA 列表完全一致，并与当前源码一致。

## 所有轮次与修复

1. `preflight_001`：AST 源读取使用 Windows GBK 默认编码，产生 UnicodeDecodeError（byte 0xae，position 519），测试执行数 0。记录保存实际异常、归一化栈位置和六文件快照，原始完整控制台输出未另存。
2. 新 runner/test 的源码读取显式设为 UTF-8；`d1a_001` 24 PASS，`regressions_001` 44 PASS。
3. 知情代码复核后补强真实内存 Schema2/history 准备、策略拒绝 listener 的拥有资源关闭、严格 bool 类型及直接配置构造校验。此阶段属于审查补强，未发生测试 FAIL。
4. `d1a_002` 与 `regressions_002` 按最终源码重跑，取得上述 68 项结果。

完整 suite 调用 4 次，共重复执行 136 次测试用例；另有 1 次预检失败。两种模板共 5 次测试进程调用，测试自行派生进程 0。失败记录和前序结果均保留。

## 新增24项

| ID | 目标 | 结果 | 检查数 | case inclusive ns |
|---|---|---|---:|---:|
| D01 | confirmed-config | PASS | 2 | 340600 |
| D02 | missing/unknown-field | PASS | 14 | 2129200 |
| D03 | root-path-isolation | PASS | 10 | 1487100 |
| D04 | derived-path-and-source | PASS | 6 | 1031700 |
| D05 | reparse-existing-root-facts | PASS | 8 | 1095900 |
| D06 | dependency-import-and-gap | PASS | 8 | 36010000 |
| D07 | canonical-synthetic-seed | PASS | 5 | 392400 |
| D08 | public-AES-memory-SQLite | PASS | 3 | 1669200 |
| D09 | crypto-invalid-vector | PASS | 4 | 298100 |
| D10 | strict-offline-launcher | PASS | 2 | 5264900 |
| D11 | bootstrap-order-single-store | PASS | 5 | 294600 |
| D12 | dormant-zero-read | PASS | 5 | 255300 |
| D13 | opaque-source-binding | PASS | 8 | 251300 |
| D14 | epoch-config-source-binding | PASS | 4 | 657100 |
| D15 | closed-stale-context | PASS | 5 | 245800 |
| D16 | closed-detached-metadata | PASS | 7 | 441300 |
| D17 | one-target-metadata-provider | PASS | 3 | 424400 |
| D18 | P1-privilege-boundary | PASS | 5 | 251300 |
| D19 | loopback-TLS-port-policy | PASS | 8 | 1211000 |
| D20 | port-conflict-no-fallback | PASS | 6 | 872100 |
| D21 | owned-cleanup-failure | PASS | 3 | 433400 |
| D22 | phase-authorization-gates | PASS | 5 | 745200 |
| D23 | services-AST-compatibility | PASS | 5 | 4119900 |
| D24 | CLI-and-secret-sinks | PASS | 6 | 15242700 |

## 依赖层级

实际新域：CPython 3.12.14 AMD64、cryptography 50.0.2、SQLite 3.53.1。D06 真实最小导入，D08/D09 执行公开向量 AES-GCM 加密/解密及错误向量拒绝。`METADATA_PRESENT` 和 `PACKAGE_IMPORTABLE` 已验证；完整真实 Authority 的 `RUNTIME_COMPATIBLE` 仍待验证。本轮依赖安装次数 0。

## 费用

最终新域总时段 1,170,382,800 ns；回归域 1,278,059,000 ns；合计 2,448,441,800 ns。计时包含 preflight、哈希和测试至结果构造；结果文件/运行索引尾部写入未单独计时。这些数值是本次离线运行成本。

以下分类用对应测试 detail 的时长求和，包含配置、断言及序列化等辅助工作；它们是覆盖用例的 inclusive 代理值，组件级独立计时保留 NOT_MEASURED。分类可能重叠，总计使用独立 suite 时段。

| 类别 | 用例 | case-duration sum ns |
|---|---|---:|
| C_config | D01, D02, D03, D04, D05 | 6084500 |
| C_dependency_check | D06 | 36010000 |
| C_bootstrap_preflight | D10, D11 | 5559500 |
| C_dormant_registration | D12, D13 | 506600 |
| C_epoch_binding | D14, D15 | 902900 |
| C_session_gate | A09, A10, A13, A14, A19 | 15055600 |
| C_metadata_check | D16, D17, D18 | 1117000 |
| C_cli_validation | D24 | 15242700 |

`C_secret_scan` 已完成 CLEAN 检查，独立计时 NOT_MEASURED。真实启动、TLS 握手、WAL、真实 AES-GCM key 文件访问和实际 P1 全部 NOT_MEASURED。D08 是公开向量密码学功能检查。更细费用和数据来源见 `D1A_COSTS.json`；注册数、槽位、模拟读取与预期业务拒绝保存在结果 details。
