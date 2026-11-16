# 当前权威、事务与恢复审计

以下为实际源码事实S，设计建议另标P。未实例化AuthorityStore。

## 1. 持久结构和读写

| 源码位置 | 实际支持 |
|---|---|
| C07 migration.sql | authority_state单行id=1、version、ciphertext；authority_events以version为主键，operation/projection；user_version=1 |
| C08 migration_2.sql | 仅把user_version置2，接受typed material；物理加密行与schema-1 AAD不变 |
| C01:47—91 | SQLite isolation_level=None；WAL、synchronous=FULL、busy_timeout=5000、wal_autocheckpoint=1000；RLock；支持SQL schema0/1/2 |
| C01:103—120 | 外部32字节key，随机nonce、AES-GCM整份canonical(state)，AAD固定；一次SELECT取得version/ciphertext再解密 |
| C01:122—159 | recover仅读；其余允许操作BEGIN IMMEDIATE→读/解密→handler→整状态加密UPDATE→INSERT事件→COMMIT |
| C03:91—98/C01:93—101 | 每条SQL执行前另写EventLog并flush/fsync；该遥测在数据库事务之外 |

成功的state和authority_events属于同一SQLite事务。InvalidInput或异常走回滚/UNKNOWN；预算耗尽还使用原生connection.rollback清锁。SQLite/文件系统正确持久化、key可用、无外部回滚/篡改仍为前提，FULL/WAL本身不证明恶意主机下的历史单调性。

构造时migration/初始INSERT/initialized marker/storage_configuration.json不处于一个统一显式事务；当前代码不能据此宣称升级/初始化跨全部文件原子。marker主要检测“已初始化但DB缺失”，不检测恢复旧DB。AAD未绑定外部version列或单调世代，事件也不是防回滚签名链。

## 2. 版本语义

`version`在所有正常返回的非recover调用后+1，包含DUPLICATE/CONFLICT/REJECTED以及作为operation调用的reconciliation_context。拒绝不等于版本不动；只有抛异常回滚或事务前拒绝入口等不走成功包装提交。

没有base_revision入参、带版本WHERE的CAS、独立O revision、authority_instance、S3提案表/回执表或typed O。SQLite写锁提供串行化，尚不检查离线计算是否基于当前状态。

grant_ops/revoke_ops、rid/digest及disposal_op具备各自已有去重绑定，但不会因此支持S3同体重放、跨cost/O原子提交。旧去重调用仍可触发外层全局版本递增。grant窗口检查甚至先于旧grant_op lookup，不能把旧API说成所有当前状态下都返回同一历史回执。

## 3. 请求、责任和单未知窗口

C01:197—259先admit保reserved，再当前release生成唯一attempt/version并spent+1；结果绑定五元，撤回后迟到进QUARANTINED（261—308）。撤回取消队列但保留已放行未知/来源。处置前后是独立操作；成功命名观察才标DISPOSED（310—344）。

O当前为state_projection派生的rid列表：DISPATCHED_UNKNOWN/QUARANTINED，加未CLOSED窗口的target。它不包含完整typed来源/后代/审计。save_reconciliation（397—415）重核单未知、A撤回/材料处置/B检查和attempt/digest，保存旧收据；只有旧CLOSED才关闭其窗口。

C02.reconcile通过多次权威RPC与Provider查询/处置构建该收据，不构成跨SQLite/AS原子事务。旧单目标逻辑继续保留其原合同。

## 4. Controller与恢复

C02:70—79 recover读取当前权威，cache/view.json仅display_only；不以缓存授新权。Controller的SingleActive为控制器文件锁，不能概括成所有AuthorityStore实例都有进程级单活锁；AuthorityStore的RLock是实例内锁，跨连接写依赖SQLite/部署前提。

原生结果Inbox与权威record分开持久，二者之间崩溃可能让结果仍UNKNOWN；Provider日志也位于响应后。恢复不能凭空得知AS是否创建或handler是否结束。

C02:94—102给代理过滤请求并重新按phase生成自身O；这些旧消费者看不到新增typed O。旧评分/测试还检查固定字段及rid义务。新增一个顶层字段就期望旧客户端理解全局责任，会有兼容风险。

## 5. S3所需最小变化

既有test_online_state源码含撤回ACK丢失、释放/结果崩溃、缓存/密钥不可用和事件前失败回滚案例。其setUp会启动本地服务，本轮只读；这些旧用例未覆盖新的O revision/提案簿合同，不能当作本轮S3验证。

P：分离新的提交dispatcher/事务结果类别，增加typed O/revision、原请求受控快照、幂等提案簿和依赖验证。S3-A用独立合成DB验证，不改真实storage/services；S3-B再处理版本3迁移、全部writer/O更新钩子和旧客户端门。不能只新增一个getattr handler就宣称CAS/失败无版本变化已成立。
