# Python导入与A17结果

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助真实离线调用及只读证据审查；工程源/Runner/测试/fixture修改0，自动重跑与额外测试0；独立外部核验待取得。

## 功能性恢复

此前R28在A1模块导入前停止；本轮所有原模块/CLI及D06实际依赖导入用例完成，功能性导入恢复已观察到。原A18、D10、D24也实际通过，涉及普通导入和SourceFileLoader辅助路径。

源码读取策略保持R29精确映射/源SHA/PermissionError回退，缓存内容授权0；没有全局.pyc白名单、删模块缓存或临时放宽394清单。

## 缓存逐探测证据缺口

expected_cache_probes和unexpected_read_denials位于内存meter，因收尾失败未进入RESOURCE_LEDGER/RESULTS；MODULE_ORIGINS也未生成。本轮无法从原文件恢复每个请求模块、source/cache绝对路径、mode/flags、判断和source SHA。

因此R30_PYC_IMPORT_FALLBACK_VERIFIED=false按完整动态审计要求登记，同时functional_import_recovery_observed=true。不能仅用最终68断言成功宣称所有缓存处理分支均已动态验证，也不能补造缺失counter。

未经批准读取/源码执行失败的拒绝代码保持；本轮未另做负向cache/权限注入。没有原始最终denial计数，保留“尚缺完整路径审计”的范围。

## A17动态验证

A17原方法在suite log第17行实际ok，源hash与原测试相同。原检查要求cryptography/services/storage/materials尚未进入相应模块状态；它实际执行通过。日志顺序A1→H1→D1A，D06晚于前44项。

R30_A17_IMPORT_ORDER_VERIFIED=true/A17_DYNAMIC_VERIFIED=true。冻结Runner没有删sys.modules或stubcrypto，原断言/fixture保持；这是当前实际检查点的证据。完整模块来源快照仍缺，不延伸为所有依赖来源已验证。

## 新错误的定位范围

错误谓词是某个所选依赖的__file__存在，但spec.origin为空或Path(file)不等于Path(origin)。具体名称未入原日志，不能猜定哪个模块。已锁cryptography源码有原生_rust派生模块导入线索，仅作为后续分类依据，不视为根因已识别或异常可忽略。
