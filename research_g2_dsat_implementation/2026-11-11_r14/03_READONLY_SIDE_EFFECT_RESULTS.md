# 只读与副作用实际结果

来源：最终run_004/RESULTS.json、H1_SIDE_EFFECT_AUDIT.json。所有计数限定合成reader、codec和遥测；真实SQLite、key文件、fsync及网络费用保持NOT_MEASURED。

## 分开核验的四类状态

| 对象 | 最终结果 |
|---|---|
| 业务世界 | 73次常规调用和3组并发/排序场景的前后摘要相同；摘要覆盖整个合成state及authority version，包括grant/request/phase/预算/material/legacy window/历史event |
| 模拟操作额度 | 累计34次读取尝试，operations增加34；鉴权/scope/额度门前拒绝均无源费用 |
| 模拟源遥测 | 34次尝试、33条成功记录；一次遥测故障已扣额度，随后SELECT/key/解码均未执行 |
| 模拟key/codec | 33次key读取、32次解码尝试；key故障阻断解码，decode故障返回固定缺口；完整状态保持Authority域内 |

合成执行顺序与storage.py:93–120逐项对应：额度门 → operations+1 → 遥测尝试/完成 → SELECT → key读取 → 解码。源遥测对象仅包含kind/count/绑定字节数，host audit仅含固定码/来源类别/读数和额度增量。

额度上限7时，一次读留下6次旧writer预检余量；后续新读取安全拒绝，计费保持1。上限6时在读取前拒绝。主动事务状态触发HOST_CONNECTION_NOT_IDLE，COMMIT/ROLLBACK陷阱命中0。headroom保留的是有限余量，后续无限任务活性仍须另论。

## 失败费用

H13分别覆盖源遥测故障、key故障、decode故障、host audit故障，以及适配器完成源读后在返回边界抛异常。异常字符串包含合成秘密，公开结果均为固定码，秘密扫描CLEAN。

返回边界故障在run_002暴露计费缺陷；修复后finally记录实际operations变化。锁定的一读路径内，正的operation增量也支持本次读尝试已发生；即使常规cost envelope返回失败，也保留这项费用。该推断限定受锁且固定的R12/reader合同。

## 并发与撤回

- H10：4个实际线程在barrier会合，全部经同一policy锁和两层可重入reader锁进入源；4次读各计费1，世界保持。最终线程标识和source标识列表一致，批次耗时5.9835ms。
- H19：已授权读在源内受控暂停，撤回线程等待policy锁；释放读取后，撤回完成。后续请求在源读取前拒绝。前一份摘要维持授权点的历史观察语义。
- H20：2线程争用同一permit，一份STAGING_READY_WITH_GAPS、一份HOST_PERMIT_REPLAY，累计源读与费用均1。原始世界摘要一致。

上述3组均有原始结果，额外独立测试分母为0。它们分别属于原H10/H19/H20内部场景。

## 时间与测量范围

最终runner记录总耗时1.2636368秒，含预检、hash、测试和结果组织。73次常规调用的总计时41.7029ms；4线程批次计时单列。区间存在包含关系，不作互斥阶段相加。

该elapsed字段在主结果对象构造时取值，之后的RESULTS/Schema/索引文件写盘和最终退出成本未单独分段测量；其费用继续计入完整运行的文件I/O责任，不能将1.2636368秒视为精确端到端性能保证。工具记录该次命令墙钟约2.224秒，包含启动和调度，只作执行记录。

完整净化、摘要、Schema与序列化仍有CPU/内存成本；原R12主要工作在reader锁内，宿主还增加policy锁。真实解密、文件I/O、数据库竞争和部署耗时尚待H2。10秒为软期限，H24以极小期限验证结果丢弃，源读取费用继续保留；无强杀服务或自动重试。
