# 全证据字节与工作量最终裁决

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

**FULL_BYTE_BOUND_UNRESOLVED；CONTRACT_REVISION_REQUIRED。** 保留旧scope条件性数量4450 raw、4451 native成员、4452行政导出；完整参数须加未来精确diff的Δ。G13属于未来域，当前无法通过旧代码实例化Δ。

令R_raw为唯一路径raw和、M_N为native manifest、Z_N为nativeZIP、H_host为host原始流/审计输入、S_lock为源锁、M_A为行政manifest：

\[U_N=R_{raw}+M_N,\quad Z_N=ZIP(U_N),\quad E_A=R_{raw}+M_N+Z_N.\]
\[U_A=E_A+H_{host}+S_{lock}+M_A,\quad Z_A=ZIP(U_A).\]

Root原件与snapshot均保留时还应计量两份E_A及host、行政归档、最终收据的实际磁盘路径。nativeZIP在行政层重读和包内包的真实复制成本保留；相同字节内容不会使独立原件/输出消失。

|要求项|当前实际参数/计算|终局状态|
|---|---|---|
|总未压缩量|U_N/U_A上述式；R_raw、host/输出profile和Δ未填|UNRESOLVED_EXACT|
|单成员最大|各reader接受4MiB/32MiB或局部source cap；没有完整生成max|UNRESOLVED_EXACT|
|native manifest|ASCII名字F≤1535、off_t19、N4450时粗界7436121|CONDITIONAL_BOUND；大于4MiB接受cap不作实际超限证明|
|native ZIP|U_N=32MiB且ZIP32 profile时stored≤47628516；额外pinned zlib条件下deflate≤47696620|条件上界；实际完整生成U_N尚未闭合|
|行政ZIP|对R_raw＋M_N＋Z_N＋host＋source＋M_A按独立codec再次计算|UNRESOLVED_EXACT|
|hash/独立读取量|已接受输入每遍O(N+B)；MR预算snapshot最多32次三文件扫描；native hash＋ZIP read；admin copy/hash/ZIP/verify分别计遍|局部CONDITIONAL_BOUND，全链未闭合|
|工作内存|整文件read_bytes、JSON/ZipInfo/trace对象、pipe capture、host多个审计视图|UNRESOLVED_EXACT；AS1GiB为失败界|
|FD|TR列明增量13；helper/socket/pidfd/继承基线另计|完整max为null|
|syscall/存储I/O|212 core尝试已有有限结构；每项字节、glob/scan、短读/重试/环境前提另计|完整max为null|

冻结SOURCE的读取接受cap、固定记录数和表示空间分别保留。4450×(2^63−1)之类物理表示粗界不会成为精确应用层容量，任意上界超过cap也不会自动产生可达违例。阻断完整闭包的最小量化参数已列入方案B，未补入默认长度。

有限归档输入的流式独立checker可以维持O(N+B)；native builder在全raw界定前整文件哈希，postexit/host有z.read整成员，/proc扫描也有独立环境域。文件描述符与TasksMax分别计量；前置ZipFile目录分配与后置count检查的内存责任保持。

失败/处置/最后收据按时间前像分层：成功native构建取静止raw，后续失败raw不回填已经消费的native前像；admin输出在ROOT之外，receipt在自己ZIP前像之外。没有自动递归归档直到成功。部分包、后层UNKNOWN和完整性缺失持续保留。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
