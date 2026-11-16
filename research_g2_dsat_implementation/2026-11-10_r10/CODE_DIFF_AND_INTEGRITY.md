# 新增差异与旧文件完整性

工程采用逐文件哈希验收，当前无Git元数据。

## 新增

- src/auth_lifecycle/online_state/dsat_commit_types.py
- src/auth_lifecycle/online_state/dsat_commit.py
- src/auth_lifecycle/online_state/dsat_synthetic_store.py
- tests/test_dsat_commit_contract.py
- tests/test_dsat_commit_store.py
- tests/test_dsat_commit_recovery.py
- scripts/run_dsat_s3a_tests.py
- tests/fixtures/dsat_commit/：49件合成输入/来源资料。

其余工程文件保持。没有更改__init__、migrations、storage/services/native_provider/reconciliation、dsat_types/projection/flow、原checker或旧测试。Python使用-B并禁写bytecode；新模块导入闭包仅标准库和本轮模块。原有S1/S2算法沿用固定输出，无新数学算法或依赖安装。

## 核对

修改前核779项，修改后及最终运行再次核779项，全部匹配；R09十一件资料逐件匹配。`SOURCE_LOCK.json`记录各项expected/actual、7份最终源码哈希、49新夹具哈希和5次尝试的原始定位。最终源码哈希与run_005记录一致。

所有修复均在新增七文件内。初始版本保存在sources/INITIAL_CODE_SNAPSHOT，run_002至run_005各存执行前代码快照。失败日志、EARLY_FAILURE、部分运行以及数据库都保留；TEST_RUNS收录全部尝试，最终分母只引用run_005。

## 隔离与留存

数据库及伴随/ticket文件只在R09固定子树，报告在R10。源文件/夹具创建前核验目标为空；未知DB、越界文件名、junction、实例/header/schema冲突均实际安全拒绝。junction测试只删除本次创建的链接条目，目标库保留。

数据库/回执清单包括所有尝试的477件数据库相关文件；归档时整个执行树约20.30MB，低于256MiB监测阈值。独立SHA固定操作只读文件字节，未连接真实AuthorityStore。所有正常/故意损坏测试库继续留存。

当前没有真实路由、生产迁移、Native写回、用户凭据或密钥接触；最终受控程序的审计记录无越界调用。源包含、权限、加密、进程fence及消费者兼容的生产工作继续归属S3-B。COL2026检索暂停、FS23延期、VPass废弃均沿用。
