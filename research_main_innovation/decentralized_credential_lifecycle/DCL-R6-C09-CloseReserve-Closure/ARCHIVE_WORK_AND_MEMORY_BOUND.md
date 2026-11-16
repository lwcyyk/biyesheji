# native、行政及独立校验的工作量与内存

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

**CRB-5=PARTIAL；完整WORK_BOUND_PROVED尚未取得；WALL_TIME_BOUND_UNRESOLVED。** 已接受且受完整输入cap约束的流式校验具有条件工作量界，整个生成/回收/构建链仍缺总输入和峰值证明。

|步骤|可明确的工作量|剩余边界|
|---|---|---|
|关闭核心生产|160＋H次记录尝试；字节W_core使用精确schema公式|160计量核心尝试，完整关闭另含其他文件；E/V/T等及staging/原始流仍缺数字|
|MR预算快照|每abort前后至多2次，A≤16时最多32次三文件扫描|每次读取counter＋intent＋journal；需J的生成字节界与扫描时静止性|
|待批v2局部日志|旧971216写字节、1316 durability尝试、retained350166保持原声明子集|调用界/失败不重试/跨角色责任尚未接线；不可加成全关闭证明|
|native构建|排序O(N log N)，raw hash一次＋ZIP读取一次，加manifest|[src/guard.py:96](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:96)digest整文件read_bytes；未知最大raw会影响峰值；压缩库参数/输出未闭合|
|runtime TR独立读|已接受compressed/uncompressed各32MiB；manifest4MiB；成员当前257；64KiB块CRC/hash|ZipFile构造与中央目录分配先于成员count检查；对象常数和TCB内存尚需证明|
|maintenance双oracle|原审查组件各受32MiB/4MiB/名字/EOCD/成员集合约束，O(N+B)流式校验|未部署；不能把组件read限制自动当成现行生成/资格合同|
|post-exit原生核查|按manifest逐成员hash；导出64KiB读取/hash/copy|[src/startup_lifecycle.py:461](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/startup_lifecycle.py:461)使用z.read整成员；/proc环境扫描不受当前slice TasksMax4约束|
|host finalizer|逐份copy hash、归档、z.read复核；nativeZIP作为成员再读取|raw host流、审计数组和最终收据可能多次物化；未有全量峰值界|

对一份已接受总未压缩B、成员N、路径最大F的归档，读取/CRC/hash可写O(B＋NF)，排序比较需O(N log N×F)。两个oracle各自完整扫描，不共享单个hash结论；行政层nested nativeZIP本身的压缩文件字节亦需处理。单份输入有限的结论只对已接纳集合成立，不能替代全部必需生成对象均会通过检查的证明。

数据I/O调用次数也单独计量：BC私有put通常file＋同目录fsync；RootIPC跨目录put为file＋destination＋private fsync；mr_close_attempt append只有file fsync。payload和host write_text/ZIP close并未形成与RootIPC相同的磁盘durability合同。上轮1316已经含其声明的两标记，不能再次当作全链fsync总数。

FD方面，TR固定目录链8、boot1、counter1、phase1、ZIP open/dup2构成13个已列增量FD；还需进程既有FD、短时文件、pidfd、socket和helper PIPE。stop_other_roots至多2个目标pidfd，异常分支和并行角色另计。当前未批准新NOFILE值，完整峰值FD为UNRESOLVED。

工作内存包含raw read_bytes、JSON对象、路径/manifest列表、ZipInfo索引、hash/压缩缓冲、异常文本、subprocess捕获和行政审计的多份视图。AS1GiB可强制失败，但它不提供所需工作能在该内存内完成的结论。32MiB压缩输入也会在ZipFile内部先展开目录对象，提前成员cap与对象常数应独立审查。

保持旧visit68498和潜在新预付256→68754（仅旧项＋该预付，未含新增测试/核验Δ）。global1m、calibration100k、300s、preT0120、stop1740、全窗1800及terminal5s/admin30s原合同保持。有限循环次数/fsync次数不足以推出最坏墙钟；调度、存储、阻塞syscall、manager和外部Windows wait均需另证。当前无新动态时间或资源资格证据。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
