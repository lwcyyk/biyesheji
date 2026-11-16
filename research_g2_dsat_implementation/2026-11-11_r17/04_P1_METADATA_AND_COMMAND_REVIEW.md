# P1元数据、命令与权限

## P1a最小范围

仅在D1已获批准、指定实例存在后，核验一个明确PID及批准的非秘密metadata文件：PID/OS创建时点/服务主体、exe路径、部署版本/加载来源、指定回环endpoint归属、运行epoch、DB/key的非秘密引用、来源挂载/关闭状态。

禁止全系统/其它用户/其它进程枚举，完整command_line、环境变量（包括批量hash）、secure配置、认证header/token、state key或ciphertext/state读取。现有isolation_service会记录完整argv和环境项hash，m6_environment_acl硬编码旧.runtime并可能改ACL，故不作为P1a入口。旧评分器也会读取/解密真值，范围过宽。

PID、ready文件或磁盘源码hash本身都不足以证明加载版本。需要D1受信清单/加载顺序/代码冻结、OS创建信息和runtime描述互相绑定；不符则停。P1a的key引用是逻辑标识/已批位置关联，不能读取其内容或对key做hash。

拟议metadata出口≤16KiB，闭合字段：schema、environment_id、service_role、pid、process_creation_time、exe_ref、loaded_build_ref、epoch、approved_listener、db_ref、key_reference_type、storage_configuration_ref、mount_state、P2_read_enabled=false、missing_fields、observation_time。实际脚本/出口尚未实现，字段仍需实施前冻结；不得直接dump对象或config。

## P1b条件与准确操作

当前P1b必要性UNRESOLVED。若P1a通过受信的当前启动记录足以固定Schema/WAL且无其它配置变更，可暂不执行；若仅有旧文件、静态声明或缺现场一致性，再单独申请P1b。

P1b只对一个已批绝对DB路径建立一条SQLite URI只读连接（mode=ro、uri=True、正确转义），最多执行各一次：

```sql
PRAGMA user_version;
PRAGMA journal_mode;
```

禁止world SELECT、Token读取、key、解密、ATTACH、扩展、checkpoint、PRAGMA赋值、migration或修复。实际DB/library版本和WAL/SHM条件未确认；mode=ro不代表文件系统零变化。必须预审WAL/SHM可读性、共享内存/锁/atime及可能文件效果；不满足时停止，不使用immutable，也不降级rw或创建缺失文件。

连接1次、语句最多2、应用重试0；建议10秒软期限，实际命令/退出码和输出上限需由已实现受审脚本确定。目标和脚本未定，预算是提案，当前全部NOT_RUN。

## 三份命令锁

| 锁 | 实际入口情况 | 当前可执行性 |
|---|---|---|
| D1 | old online_state.py的init/serve存在；CLI不传ticket，也不提供dormant注册/epoch描述及专用准备/安全停止 | false；新环境/root/Python未定，真实bootstrap尚缺 |
| P1a | OS内置的单PID能力可作组成部分；项目无符合上述白名单的完整检查入口 | false；PID和实际检查脚本均缺 |
| P1b | SQLite库API可用性有历史线索；项目无严格两PRAGMA的指定DB检查脚本 | false；DB路径、可选必要性、脚本和权限未定 |

argv、可执行程序绝对路径、实际输入/输出、目标和authorization_id均为null/UNRESOLVED；command_executable=false、environment_locked=false、authorization_status=PENDING。只有实际存在、审核过且无占位符的命令才能升级就绪，不能将新脚本名或示例参数当成命令。

## 权限与费用分离

D1允许的未来写入只能在指定新root及批准部署文件内，明确包含新key/TLS/private配置、DB初始化、marker/config、metadata/log、端口和一个拥有进程；无其它组件或外站。D1不附带任何B1/read_state或旧grant/RPC调用。

P1a只读批准的非秘密运行元数据，不改ACL、配置或服务；P1b单独metadata DB连接；P2再独立批准管理主体/精确scope/key与整行解码/单会话读1次。P1a不包含P1b，D1/P1均不把少量输出当作解密权限。

未来D1/密钥准备如需真实文件型AES-GCM加密新合成state，必须显式批准新key生成及逻辑读取次数；已有用户密钥、备份/生产库仍禁用。P2每次cipher重读key的费用独立，状态明文只能留Authority域内，原R12净化后仅输出已批摘要。

所有新增D1/P1验收用例状态NOT_RUN，不用A1的1919条检查填为现场PASS。单条失败固定记录成本/不确定性，不自动增加尝试、扩大scope或删改原始证据。
