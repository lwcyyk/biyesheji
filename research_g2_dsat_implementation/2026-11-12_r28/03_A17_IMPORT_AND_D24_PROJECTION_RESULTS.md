# A17与D24实际覆盖范围

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助实际离线调用与只读证据审查；独立外部核验待取得。本轮源码、Runner、测试及fixture修改均为0。

## A17

A17状态：**NOT_RUN_NOT_REACHED**。A17_IMPORT_BARRIER_PASSED=false，R28_A17_IMPORT_ORDER_VERIFIED=false。实际执行在A1模块顶层导入就中止，A1/H1/D1-A均未完成装配。

load_group进入A1后曾通过其初始“禁用模块尚未导入”判断，才到固定源compile/exec；最终MODULE_ORIGINS及runtime_versions中cryptography仍缺席。这些是入口的辅助观察，不替代原A17断言执行。

未删除sys.modules、未stubcrypto、未改A17或fixture，没有第二次启动以重置导入状态。R27的正确阶段顺序代码仍原字节保持，实际完整分阶段执行尚待后续验证。

## D24

D24状态：**NOT_RUN_NOT_REACHED**。D24_PROJECTION_PASSED=false、R28_D24_PROJECTION_VERIFIED=false。实际projection记录为空，两个目标JSON均未创建；临时provider没有激活，恢复责任为NOT_APPLICABLE。

两个原始JSON前后摘要均与冻结SHA一致，D24_SOURCE_JSON_UNCHANGED=true。生产runtime.read_offline_json及白名单源hash保持，D24_PRODUCTION_WHITELIST_UNCHANGED=true。

原/目标绝对路径、SHA和不存在目标的证据在R28_A17_D24_WITNESSES。静态R27双文件代入证明继续作为历史纸面依据，不能改名为R28动态投影通过。

## H2与持久授权

本轮会话总量、来源绑定、秘密隔离、并发和Dormant的68项回归均未执行。原工程源和相关依赖保持，R25真实54PASS（F24/F23/F26/T45）原文及hash继续有效，本轮未重跑54项。

H2真实读取0、持久启动协议修改0。当前无法依据R28补全H2/A1/H1/D1-A的同构建动态兼容性责任，也不产生真实部署安全结论。
