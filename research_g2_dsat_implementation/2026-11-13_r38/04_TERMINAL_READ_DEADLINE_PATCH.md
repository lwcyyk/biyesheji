# 收尾读取截止门

原时间分区保持：工作90秒、terminal读/写准入115秒、安全关闭准入120秒，起点仍为main进入。terminal_read_deadline显式等于原terminal截止，无新增宽限。

read_gate/terminal_read_gate:404按纯词法范围审定目标与时间。内容仅限原13项owned路径；listdir仅OUTPUT/RUN；metadata另允许原checked所需祖先重解析检查，未新增祖先内容读取权限。原来源/fixture/历史/测试模块内容在terminal仍拒绝。

## 实际调用图

- sha在terminal分派hash_owned_file；每次open、open返回、每个64KiB read前后和返回hash前检查。open阻塞晚返回也无法进入下一次read。
- checked内部stat/lstat/exists/is_file/is_symlink等由metadata代理前后检查。
- journal的fstat/tell由descriptor_metadata前后检查；write/flush/fsync保留原时间门。
- sizes及最终artifact构造改为固定两目录listdir遍历；目录打开/返回和后续metadata逐项检查，根/子目录及13文件身份均验证。
- entry的RUN目录判断同样经过metadata，收尾read/close错误保持已有primary与独立secondary事实。

23处显式读调用及动态metadata代理逐项映射于R38_TERMINAL_READ_AUDIT。controls/init是准入阶段；来源扫描/preflight/load_group由check_work父调用控制；ProjectionRead属于原D24测试栈，在进入terminal前展开退出，terminal路径没有测试/投影调用。异常采集与JSON处理仅使用已缓存内存，源摘录读保持0。

## R36 W05回查

若旧日志close在120前启动、121才返回，后续output_files/read_gate立即拒绝，新的owned读取/hash不会开始。若一次读取本身晚返回，返回后门拒绝新操作和未完成引用；原已可靠取得的数据保留，后续缺失保持UNKNOWN/不完整。

32个read-handle槽、稳定owned文件每次ceil(cap/65536)+1读取及一次关闭尝试构成有限界。正常单main调用图read-handle总上界17、同时最多1；原13对象及读取白名单不变。read_audit统计准入检查次数，包含helper和audit重复检查；它没有被称作OS syscall实际进入次数。

读取句柄只关闭本次取得的对象。120后停止新显式关闭、保留未确认状态；关闭晚返回可确认物理关闭同时标记时间不完整。进程/OS最终回收与原生阻塞活性未被虚报为已确认。

本轮证明前置/返回后准入检查和固定预算控制。Python检查与OS进入之间可被调度暂停，底层I/O也可迟返；硬实时120秒结束、任意存储故障下完整收尾均未证明，仍需后继独立动态验证。
