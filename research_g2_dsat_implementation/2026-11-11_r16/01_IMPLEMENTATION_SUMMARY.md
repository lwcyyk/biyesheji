# R16：A1实际实现

2026-11-11，Asia/Shanghai。知情模型辅助成熟工程实施，外部独立安全审查待取得。

**七目标已经实现。最终run_005：新A01–A20全部PASS；原H01–H24回归全部PASS；FAIL/ERROR/SKIP均0。** 内部检查分别558与1361，共1919条满足。44项按20新增、24回归分别管理。

## 工程交付

工程根`D:/毕业设计/auth-lifecycle`。

| 获准目标 | 实际变化 |
|---|---|
| src/auth_lifecycle/online_state/services.py | Store构造后、Handler建立前的可选挂载；默认ticket=None；专用读取分支传递认证上下文，保留旧分派；读取日志故障无数据回应。 |
| src/auth_lifecycle/online_state/dsat_authority_read_host.py | 注册来源对象接口、会话claim、指定rid核验和有出处的SQL/Schema/audit计量；默认合成路径保留。 |
| src/auth_lifecycle/online_state/dsat_authority_host_activation.py | 新增393行；受信注册、来源绑定、进程级会话命名空间、全permit单读门、有界reader、HMAC认证上下文和受限分派。 |
| scripts/read_dsat_authority_once.py | 新增72行；严格argv、单次离线transport接口、默认真实执行关闭。 |
| tests/test_dsat_authority_host_activation.py | 新增560行；20项冻结身份，内存SQLite/codec/身份/并发及CLI替身。 |
| scripts/run_dsat_authority_activation_tests.py | 新增297行；限定20＋24发现、1320项版本保护、内存连接/文件/网络隔离和失败保留。 |
| tests/fixtures/dsat_authority_host_activation/ | 新增3份JSON：合成STATE_SEED、CANARIES和CLIENT_MANIFEST。 |

实际行数、SHA和差异固定于CODE_DIFF/SOURCE_LOCK。两份修改前源码完整字节保存在sources/original；原H1测试、runner和R14锁保持原字节。

## 运行

R15冻结命令已实际执行：

```powershell
& 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\Scripts\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_activation_tests.py'
```

使用CPython3.12.14、标准库SQLite3.53.1，无新依赖。五轮数据位于`research_g2_dsat_implementation/2026-11-11_r15_activation_offline/`，最终run_005。A1_ACTUAL_RESULTS为该轮RESULTS原字节副本。

首轮44项通过后，A09新增原责任范围内的issuer/来源别名重置挑战，run_002实际得到同一授权累计SELECT2次，形成19新PASS/1 FAIL、24回归PASS。修复为进程级来源命名空间后，run_003/004均44项PASS。末轮补齐完整a/W等价、CLI重新连接和注册/遥测费用证据，原失败记录保留。

## 实际执行范围

18个自有`:memory:`连接，全部按runner生命周期关闭。SQLite文件库、ATTACH/扩展、网络、子进程、私密文件和越界写入尝试均0；services/storage/materials/cryptography运行导入均0，services仅作AST检查。真实DB/key/RPC/服务、P1/P2/B2/S5均0；原115/46/33及原生批次执行0。

A1完成的是获准离线接线与验收。实际部署、服务导入、WAL/ACL、真实AES-GCM/身份/实例和真实一次读取仍待独立准入。
