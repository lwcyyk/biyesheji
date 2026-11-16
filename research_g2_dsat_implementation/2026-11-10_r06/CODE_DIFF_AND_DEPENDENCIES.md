# 新代码与依赖

工程无Git元数据。以实施前BASELINE.json比对116份既有源码/脚本/测试数据及pyproject，全部哈希一致；345项历史研究输入也保持。源差异采用evidence/NEW_CODE.patch的新文件补丁和CODE_AND_COMPATIBILITY.json记录，未覆盖用户已有源码。

## 新增8份Python文件

| 路径（主工程内） | 功能 |
|---|---|
| src/auth_lifecycle/online_state/dsat_types.py | 12类数据及独立manifest、严格类型/规范化/资源和域分离摘要 |
| src/auth_lifecycle/online_state/dsat_projection.py | 纯合成冻结证据投影、birth/来源/历史/前沿、只增保留O提案 |
| src/auth_lifecycle/online_state/dsat_flow.py | m/d网络、±h需求、证明绑定；缺库返回明确未求解 |
| scripts/check_dsat_certificate.py | 标准库独立网络/整数流/残量势/割/摘要/范围检查及CLI |
| scripts/run_dsat_offline_tests.py | 只加载两个指定模块，保存每轮代码/输入哈希及结果 |
| tests/dsat_test_support.py | 合成fixture/独立脚本加载和篡改测试辅助 |
| tests/test_dsat_projection.py | 24例及S1/网络/缺库边界测试 |
| tests/test_dsat_certificate.py | 核心/变体/篡改/独立性测试及缺库跳过项 |

另新增tests/fixtures/dsat下A01—A24和MANIFEST，共25份JSON。所有标记SYNTHETIC_CONTRACT；独立manifest固定快照/合同/证据/O/费用，投影不从不可信payload读取source_confirmed=true获得信任。

## 依赖与执行隔离

新模块只用Python标准库；没有新增第三方依赖、修改pyproject或安装包。现有cryptography可选依赖未由新投影/数学检查器调用。NetworkX和pytest在已查本地环境中未找到，研究者确认未安装流库。pytest以unittest替代；最小费用流依赖保持待批准。

`solve()`只构造两个网络并返回BACKEND_UNAVAILABLE，m/d/R/H为None，避免零流伪解。证明装配函数只序列化给定向量和绑定，独立检查器负责验证。当前没有临时编写替代优化器。

新检查器独立重建图，不导入dsat_flow、dsat_types或任何优化器。外部expected digest pin可以核验固定目标/版本字节；摘要不提供真实AS来源认证。原请求摘要仍按旧规范，旧源码和CLOSED/1未修改。

S3真实typed导出/提交、旧window退出、Provider路由和原生状态均未接线。Python授权导入可能产生__pycache__，其不作为源码变更，不删除旧缓存。
