# D24实际投影与输出边界

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助真实离线调用及只读证据审查；工程源/Runner/测试/fixture修改0，自动重跑与额外测试0；独立外部核验待取得。

**R30_D24_PROJECTION_VERIFIED=true / D24_DYNAMIC_VERIFIED=true**，范围为本轮原D24正例、双文件内容与上下文控制流；失败恢复和额外JSON负例本轮未另行注入。

D24原方法实际ok，完整D1A组返回后才触发phase_finished来源异常。由固定OrderedSuite的with退出可核对：原runtime.Path/CONFIG.output恢复语句在进入后续来源核验前已执行，两个written名完整。直接projection runtime记录留在内存未落盘，该来源范围明确保留。

| 文件 | 冻结SHA-256 | 后处理 |
|---|---|---|
| test_metadata.json | `1c6283d77d75d9617adff2b06cea39bc1658aa4b9c0d9ee2e823fcc2c8d50037` | 原文/目标均匹配 |
| test_request.json | `90cf2149c79ccd43caa82aa8da51d6542b5776ac8bd9ec5ecc01cb163f9f0c69` | 原文/目标均匹配 |

原JSON只读、生产reader和白名单源hash保持。目标副本只在新run，均单链接，未借cache策略开放其他JSON。

## 实际输出

当前仅9个文件、2个目录、11,530B，均在原13名字和R29新根。两个COMMAND日志为0B，suite log5745B，EARLY_FAILURE776B；有RUN_START、批准和唯一槽位，两D24副本。

未生成：MODULE_ORIGINS.json、RESOURCE_LEDGER.json、RESULTS.json、TEST_RUNS.json。缺件本身是本次收尾失败证据，后处理不会在原run填造这些文件。

现有9文件SHA/路径/nlink/对象身份已固定于sources/RUN_ARTIFACT_MANIFEST。没有与四份旧T33硬链接共享对象；旧历史原文无改写。日志和stdout/stderr只使用冻结路径，未fallback到R26/R28旧树。

## 收尾义务

本轮positive D24可验证，框架来源与资源缺件仍阻止完整合同验收。未来修复应把部分origin、meter、cache和projection证据置于可保留的失败快照，并在来源判断失败时仍输出真实非零状态，避免丢失已完成原断言。
