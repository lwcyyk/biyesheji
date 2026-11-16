# 68项原始断言结果

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助真实离线调用及只读证据审查；工程源/Runner/测试/fixture修改0，自动重跑与额外测试0；独立外部核验待取得。

| TOTAL | PASS | FAIL | ERROR | SKIP | BLOCKED | NOT_RUN |
|---:|---:|---:|---:|---:|---:|---:|
| 68 | 68 | 0 | 0 | 0 | 0 | 0 |

| 分组 | PASS | 原unittest时窗 |
|---|---:|---:|
| A1 | 20 | 1.809s |
| H1 | 24 | 2.668s |
| D1-A | 24 | 3.439s |

这是真实原用例断言结果，完整Runner退出码1。R30_68_TEST_ASSERTIONS_PASSED=true；R30_68_REGRESSION_PASSED=false按“含完整来源/资源/结果收尾”的合同口径登记。两项口径各自明确。

## 恢复来源

原始suite stdout有68个互异方法的“... ok”行，顺序与冻结清单完全相同，三个Ran/OK摘要为20/24/24。EARLY_FAILURE另保存相同68PASS计数。原run没有生成RESULTS，因此本报告与R30_68_TEST_RESULTS注明RECONSTRUCTED_FROM_ORIGINAL_UNITTEST_LOG，并逐项链接原行/文件SHA；逐项elapsed_ns保持null。

| ID | 组 | 实际结果 | 原日志行 |
|---|---|---|---:|
| A01 | A1 | PASS | 1 |
| A02 | A1 | PASS | 2 |
| A03 | A1 | PASS | 3 |
| A04 | A1 | PASS | 4 |
| A05 | A1 | PASS | 5 |
| A06 | A1 | PASS | 6 |
| A07 | A1 | PASS | 7 |
| A08 | A1 | PASS | 8 |
| A09 | A1 | PASS | 9 |
| A10 | A1 | PASS | 10 |
| A11 | A1 | PASS | 11 |
| A12 | A1 | PASS | 12 |
| A13 | A1 | PASS | 13 |
| A14 | A1 | PASS | 14 |
| A15 | A1 | PASS | 15 |
| A16 | A1 | PASS | 16 |
| A17 | A1 | PASS | 17 |
| A18 | A1 | PASS | 18 |
| A19 | A1 | PASS | 19 |
| A20 | A1 | PASS | 20 |
| H01 | H1 | PASS | 26 |
| H02 | H1 | PASS | 27 |
| H03 | H1 | PASS | 28 |
| H04 | H1 | PASS | 29 |
| H05 | H1 | PASS | 30 |
| H06 | H1 | PASS | 31 |
| H07 | H1 | PASS | 32 |
| H08 | H1 | PASS | 33 |
| H09 | H1 | PASS | 34 |
| H10 | H1 | PASS | 35 |
| H11 | H1 | PASS | 36 |
| H12 | H1 | PASS | 37 |
| H13 | H1 | PASS | 38 |
| H14 | H1 | PASS | 39 |
| H15 | H1 | PASS | 40 |
| H16 | H1 | PASS | 41 |
| H17 | H1 | PASS | 42 |
| H18 | H1 | PASS | 43 |
| H19 | H1 | PASS | 44 |
| H20 | H1 | PASS | 45 |
| H21 | H1 | PASS | 46 |
| H22 | H1 | PASS | 47 |
| H23 | H1 | PASS | 48 |
| H24 | H1 | PASS | 49 |
| D01 | D1A | PASS | 55 |
| D02 | D1A | PASS | 56 |
| D03 | D1A | PASS | 57 |
| D04 | D1A | PASS | 58 |
| D05 | D1A | PASS | 59 |
| D06 | D1A | PASS | 60 |
| D07 | D1A | PASS | 61 |
| D08 | D1A | PASS | 62 |
| D09 | D1A | PASS | 63 |
| D10 | D1A | PASS | 64 |
| D11 | D1A | PASS | 65 |
| D12 | D1A | PASS | 66 |
| D13 | D1A | PASS | 67 |
| D14 | D1A | PASS | 68 |
| D15 | D1A | PASS | 69 |
| D16 | D1A | PASS | 70 |
| D17 | D1A | PASS | 71 |
| D18 | D1A | PASS | 72 |
| D19 | D1A | PASS | 73 |
| D20 | D1A | PASS | 74 |
| D21 | D1A | PASS | 75 |
| D22 | D1A | PASS | 76 |
| D23 | D1A | PASS | 77 |
| D24 | D1A | PASS | 78 |

原callable/expected/source SHA也逐项保存。没有模拟PASS，没有用历史68补本轮结果，没有更改发现规则或断言。装配后的实际完整执行顺序可直接从日志核查。

## 框架错误

原用例完成后，Runner在main696→origins_snapshot366抛出DEPENDENCY_ORIGIN_MISMATCH。该错误单列为框架错误；原68中ERROR0与框架最终失败分别登记。实际依赖名/file/origin没有在抛错前持久化，无法按现有原文确定具体模块或将其判为正常原生别名。

冻结控制流显示：来源记录在全部验证后才append，收尾又在RESOURCE/RESULTS之前调用相同检查，第二次异常可能阻止最终输出。entry看到EARLY_FAILURE已存在便保留原文件；原始落盘直接保存了首条错误，具体后续异常值未单独保存。
