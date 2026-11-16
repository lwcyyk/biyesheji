# SQL、秘密与费用边界

## 固定读取

新reader使用R15固定模板和绑定`:ceiling`，语句标识在A11逐字比较。该语句仅选择authority_state.id=1的版本、有界ciphertext及同语句Schema元数据。代理执行一次旧Store.execute，检查缺行、Schema2、长度/密文结构后，调用一次旧Store.cipher接口及原AAD/nonce切分，再JSON解码。

A11在同一次受保护read_state内捕获完整(a,W)，与声明的完整夹具状态比较，未为该比较额外读取源。A12实际内存SQL覆盖超界、Schema错误、缺行，均在key前拒绝。connection身份/事务状态、固定SQL及total_changes验证分别见A02/A13/A15。extra grant/rid/body字段和scope引用不符不能转移目标。

测试的fixture建表、填充、Schema设置与前后摘要查询属于自有内存测试准备/验证，单列于受保护源路径之外；它们没有被宣传为整个测试只执行一条SQL。未加载migration文件、文件数据库或外部扩展。

## 秘密与输出

codec为合成spy，检查nonce/body/AAD接口，不提供真实加密安全证据；实际AES-GCM模块未导入。完整fixture状态和敏感原请求留在模拟Authority域内，由原R12核digest/handle/origin/operation/source_rid，再经H1摘要出域。

摘要保持≤4096字节和原闭合字段集合，Native/math/global资格为false、o/instance为null。缺来源、typed O/o、前沿、持续失活等保持固定gap；公开结果不含原请求/handle/Token/key/全状态。Registration/ticket/peer/mount禁止序列化，repr固定redacted。

CLI默认真实执行关闭。只有注入的离线transport才会处理严格的offline manifest，单个Invocation一次调用，无URL/token/key或debug开关；没有实际凭据加载器。未知argv和错误只输出固定拒绝，A18对CLI错误和合法离线重连输出均扫描canary。

Python进程内对象、旧Store/connection引用和其密钥路径的可信使用仍是前提；没有对恶意同进程代码的防护或安全内存擦除保证。

## 额度与故障

计量分开记录：注册尝试/成功、permit发行/消费、会话槽、read_state/SELECT API尝试、成功SQL、key/decode、metadata检查和日志。源execute先operations+1，再遥测，随后实际SQL。最终18次源尝试/计费，17次物理内存SELECT成功；日志故障仍占槽并扣额度，key/decode失败不重试，返回故障延续H1 finally计费。

会话总量针对一次授权机会，预算不足也不会自动恢复。权限、scope、来源、默认关闭和活动事务等前置拒绝保持源SELECT/key为0。所有实际源行/event前后hash一致，连接total_changes在读取范围内保持；没有据此推断其他进程或真实AS不变。

结束阶段若total_changes观察失败，观测值保持unknown，丢弃数据、保留已发生费用并清理inflight，claimed槽保持。A14以受控观察故障视图验证；这项旧行为未在修复前执行，来源为静态核读发现后的保护修订及最终实测，不与run_002的实际两读反例混淆。

## 成本记录

SESSION_GATE_AUDIT提供C_registration、C_authorization、C_permit、C_session_gate、C_select、C_key、C_decode、C_telemetry、C_output。注册计时覆盖33次入口（27成功、1关闭、5拒绝）；其余相位按计量出处记录。telemetry spy约19.8微秒，包含于select阶段，时段有重叠，不能当互斥阶段相加。

部分被拒绝的dispatch/HMAC和夹具准备费用只在case/runner总体中体现，不伪装为独立精确阶段值。最终runner在结果对象构造时累计2.3097757秒；结果/索引最终写盘另有成本，不能当作精确端到端性能界。

界内源处理按完整state字节S、记录扫描和原请求校验长度计费；输出虽有界，完整JSON与临时密文/明文对象仍有内存展开。进程级命名空间上限4096，保留已消费命名空间以避免重置。真实文件SQLite/WAL、ACL、AES-GCM/key、部署、网络/RPC和fsync成本均NOT_MEASURED。
