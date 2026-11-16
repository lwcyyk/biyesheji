# 持久化成本：可测部分与未知部分

Material Passport：既有时间戳计算与源码成本模型，没有运行新基准。

## 混合周期实测

PREP4至PREP32191覆盖298.626607199秒，32187个相邻PREP间隔。均值9.277863957ms，吞吐107.783429956周期/秒；min6.775579ms、P50 8.708005ms、P90 10.085053ms、P95 10.738904ms、P99 15.226956ms、max410.970416ms。分位数使用nearest-rank；原始样本CSV保留。

**全部32191对PREPARED/COMMITTED时标完全相同。** 源码只在PREP创建record时stamp，COMMITTED只改status。因此所谓“commit−prepare=0”仅说明复用时标，无法测量同步耗时。

相邻PREP跨度包含当前事务的持久化、解锁/返回、下一调用的状态/截止/额度检查、打开与读counter/intent、锁等待及stamp；它是循环混合周期。单次reserve纯耗时、fsync各阶段、CPU/序列化、锁等待与调度时间均UNKNOWN_INTERVAL。

## 每次预留的静态路径

|动作|常规数量|数据/复杂度|
|---|---:|---|
|读batch_state/停止/boot/clock|每visit重复|常量大小；当前状态约346B|
|读globalcounter|软阈值预检＋锁内pread|24B固定，非全journal|
|读/解析intent|1|约196–197B常量|
|PREPARED atomic intent|1次文件+1次目录fsync|完整重写小JSON/rename|
|journal PREPARED|1次append+fsync|不扫描旧记录|
|counter pwrite8B|1次fsync|高水位递增|
|journal COMMITTED|1次append+fsync|复用PREP时标|
|COMMITTED atomic intent|1次文件+1次目录fsync|完整重写小JSON/rename|

合计每个完整返回事务7个同步调用。7×32191=225337是**源码路径调用机会估算**，没有syscall追踪或逐次返回时标，不能登记为225337次实测成功fsync。实际成功次数、耗时份额、设备flush行为留待获准测量。

每visit大致有两次indent intent序列化、两次journal行序列化，均为小对象；逐次文件重写存在，按增长journal全量序列化/重扫不存在。执行时只有append，离线本轮扫描11,634,011B journal与原运行开销分别登记。Counter和intent的读量O(1)，N次预付的应用层路径O(N)，没有代码依据把它归因为O(N²) journal扫描。

哈希/manifest复核在入口/构造等阶段，未出现在每次reserve路径；C02预付循环的开头已在T0+1.373秒，入口哈希无法解释余下298秒。文件fcntl与线程RLock都存在，唯一预算writer为C02主线程；其他角色不写counter。没有lock重试/等待计数，不能断言存在竞争或将其时间置0。心跳也同步写文件，可能影响I/O，份额未知。

## 随序号的观测

4096周期分组均值依次9.846、8.430、10.027、8.607、9.227、9.345、9.136ms，末3515样本9.658ms；见[CYCLE_SEQUENCE_BINS.csv](evidence/CYCLE_SEQUENCE_BINS.csv)。没有明显随文件长度单调增大的序列，符合常量操作重复，但该观察不替代复杂度证明或存储性能归因。

最小新增测点是预算lock/check、intent文件/目录sync、journal sync、counter sync的开始/返回、grant_emit、child_spawn/execute_count。用有界内存汇总和一次结果写出记录遥测，保持权威ledger原有持久屏障；对遥测丢失明确标UNKNOWN，避免测量日志再逐事件fsync扰动结果。当前未增加这些代码/探针。
