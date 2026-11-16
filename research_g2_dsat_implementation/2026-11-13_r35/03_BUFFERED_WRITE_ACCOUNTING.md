# 写前扣费与无缓冲持久化

R34的失败缓冲缺口已在源代码层修复。全部持久化输出通过 `open_owned` 的 xb / buffering=0 FileIO，以及 `io_write`。audit要求实际打开路径等于本次受控opening_output；D24也通过此通道。配额按固定路径预留，计费在open/write之前完成。

## 不变量与状态

对每个owned路径f，记c_f为charged_bytes，v_f为实际st_size，q_f为原配额。在受信独占写入、底层FileIO每次最多写请求长度的接口合同下：

`0 <= v_f <= c_f <= q_f`。

初始owned文件均不存在。序列化先经过字段/结构计量；完整待写长度先加入c_f，之后才调用I/O。短写、write/flush/fsync失败继续保留全长c_f，不退费并poison。成功fsync后推进已确认持久化的返回字节前缀。关闭使用无缓冲句柄，产生新payload的Python待刷字节为0；关闭失败保留句柄与不完整状态，每个文件只作一次明确关闭尝试。

| 状态 | 费用/持久化 |
|---|---|
| RESERVED | 固定q_f已隔离，实际待写扣费可为0 |
| SERIALIZED | c_f已加入完整待写长度，尚可未open |
| WRITE_STARTED | 在真实write syscall之前累加attempted，返回数量逐次检查 |
| FLUSHED | write完整返回且flush成功，fsync仍待确认 |
| PUBLISHED | fsync成功，更新confirmed prefix |
| PERSISTENCE_UNCERTAIN | 全费保留、poison、stop；真实不确定持久化量UNKNOWN |
| FINALIZED | 单次close已返回且.closed确认；费用继续保留 |

RESERVED/SERIALIZED/ATTEMPTED/RETURNED/CONFIRMED/UNCERTAIN分别保存。BUFFERED_BYTES=0指Python用户态待刷payload；内核缓存和真实物理持久化与此分开。CONFIRMED=0只表示尚无成功fsync证据，未把实际未知持久化量记作0。uncertain字段是charged-confirmed的保守字节上界，实际量仍可为UNKNOWN。

已计费、已见文件和不确定字节是同一分配的不同观察，容量求和只加c_f一次。SERIALIZED_BYTES记录成功取得配额的序列化字节，超额拒绝前在RAM中的序列化尝试单列为未写入；该值没有被称作所有内存构造量。

## R34反例回查

从可见60000、已扣60000开始，首个4000在I/O前把c_f推进64000。若flush失败，c_f仍64000且流poison。第二个4000在poison门拒绝；它不能进入write或在close时形成新增未扣费payload。此为源码/接口推导，未作故障注入。

每个普通文件序列化/发布尝试最多1；日志每份最多8192次、journal最多8320次。失败普通文件保留部分前缀，不重新创建。没有退款、truncate、删除证据、rename或replace。输出open还受固定13路径和独占创建约束。ACK丢失也不会得到第二次发布额度。

原子性沿用逻辑提交：三JSON与日志/journal本身通过fsync和hash绑定，最后TEST_RUNS绑定成套证据，完整接受还需native exit0。磁盘临时副本峰值0；正式目标部分文件始终计入。物理簇、内核缓存、RAM对象、OS掉电持久性均未被虚报为已测0。

失败存储下完整receipt的可用性仍有条件。receipt失败时journal保持到最后，可尝试记录失败；journal也失败时保留已有可确认前缀，native非零，FINALIZATION_INCOMPLETE。该边界与2MiB存储安全分开。
