# 精确范围预留的安全条件与证明责任

Material Passport：纸面条件证明；代码实现/动态故障检验0。选A0，仅向冻结有界子任务提供一次精确N信用的能力，普通visit保持单信用接口。

## 状态与线性化

批次B、boot/epoch、源码/合同摘要、owner进程身份与task序号共同标识租约。R是已持久确认的全局占用高水位；pending描述一个尚未完整确认的范围。有效占用的保守恢复上界包括counter、有效COMMITTED及未知PREPARED的最大after；解析/一致性不明则整个批次HALT，拒绝初始化新账。

一次请求n必须为正整数、处于该case冻结上界内，且在global线程锁/文件锁同一临界区检查R+n≤1,000,000及适用cal软界100,000。分配信用区间[R,R+n)，沿用PREPARED意图→journal→counter→COMMITTED journal/intent及文件/目录同步。全部关键持久确认完成后，再检查停止/boot/deadline，最后交付唯一租约；过期则范围烧掉，不启动child。

租约绑定唯一owner incarnation（boot、PID/start_ticks与本次随机/单调实例标识），只能交付一次给固定child角色。父进程在spawn结果未知后不重试同一租约；fork不得复制可用授权，owner身份变化立即作废。进程重启从新的全局范围申请，旧范围全部占用。已运行/可能已运行的child保留旧范围，禁止将同一区间再次委派。

## BUD性质

|性质|保持理由/程序映射|未来必要验证|
|---|---|---|
|BUD-1 NoOverspend|reserve_counter扩展amount/范围；锁内检查global/phase cap，持久完成先于prepaid_child交付，child循环≤N|不足N的原子拒绝、n0/负/非整数/超cap、child试多一步；拒绝后无执行|
|BUD-2 CrashConservative|任意未明PREP、COMMIT/交付未知烧掉全范围；禁止退款/清零；沿用intent/journal毒化|PREP/各sync/counter/commit/交付前后故障；缺/短/损坏记录均停止|
|BUD-3 NoDoubleGrant|global范围分配串行、区间不重叠；一次性租约＋owner绑定＋不重试，不从磁盘恢复旧cursor|两线程/多caller竞争，9+9在cap17不能全过，9+8可各得不交叠范围；PID复用/fork/重放拒绝|
|BUD-4 MonotonicAccounting|R只能加n；boot/授权/root/hash错误拒绝；未知恢复只关闭或保守占用|counter回退/旧intent/重复初始化/错误Root/boot，不产生新信用|
|BUD-5 BatchIsolation|新B03单独授权/根/ledger，B02/原batch01只读；修复版移除B02写入资格|错误batch/path/旧票据，拒绝前后历史hash不变|
|BUD-6 FailClosed|任何已观察的锁/权限/解析/短写/fsync/校验失败永久停止该caller并联停批次；保留每次交付前状态/时间检查|存储/锁失败、poison广播失败、关闭/截止竞态；不交付缺持久确认的租约|

设X是已执行及可能已执行的访问**事件多重集**。要求存在从X到持久分配信用ID集合U的单射，不能只比较事件去重后的集合。初始R=0；分配n只将n个全新ID加入U；执行/可能执行事件只消费未消费的一个ID；崩溃不删ID、不允许重放租约；归纳得|X|≤|U|=R≤cap。并发在同一高水位临界区线性化，BOOTTIME/停止检查与持久确认分别保留责任。

这依赖可信内核/存储同步语义、冻结代码、进程身份和禁止恢复已用内存授权等假设；不声称对任意恶意payload/恶意root或存储回滚给出一般证明。当前没有机器证明或失效测试。

## 浪费与回收

A0精确N无舍入浪费，但子任务最多可能使用N；父进程在交付前崩溃或child提前失败时，未用占用可达N。H次委派的保守未执行占用上界为ΣN_i。已交付未知部分也算占用，当前不提供回收协议。

可选固定块k的普通pool中，正常owner最后一块未交付尾部≤k−1；崩溃可整块k未交付。H_normal/H_crash下未交付尾部≤H_normal(k−1)+H_crash k。另有提前委派child的N_i未执行信用，**不能**用k−1替代全部浪费。若未来采用pool，所有在途/已发未知事件仍需上述单射，当前A0不引入它。

安全证明、语法/接口检查、资源执行资格与性能收益各自验收。减少事务数量不减少grant前所需持久屏障；本轮不修改任何代码。
