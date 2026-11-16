# batch09资源校准清单与真实状态

Material Passport：DCL-R6-batch09；STATIC_INVENTORY_ONLY；2026-11-12。

|校准|冻结测试责任|本轮结果|
|---|---|---|
|C00|真实身份/资源/就绪|UNRUN_STATIC_ADMISSION|
|C01|正常执行与watchdog|UNRUN_STATIC_ADMISSION|
|C02|内存AS故障与32,896信用预留|UNRUN_STATIC_ADMISSION|
|C03|共享16MiB映射与4,096信用预留|UNRUN_STATIC_ADMISSION|
|C04|第5任务EAGAIN/父TasksMax=4|UNRUN_STATIC_ADMISSION|
|C05|18次并发请求/局部上限17|UNRUN_STATIC_ADMISSION|
|C06|同窗口时间停止|UNRUN_STATIC_ADMISSION|
|C07|控制器故障退出|UNRUN_STATIC_ADMISSION|
|C08|watchdog故障后拒发资格|UNRUN_STATIC_ADMISSION|
|C09|真实交接和Launcher退出|UNRUN_STATIC_ADMISSION|
|C10|实际权限/AS/网络/进程限制，原生READY|UNRUN_STATIC_ADMISSION|
|C11|四个镜像账持久故障|UNRUN_STATIC_ADMISSION|
|C12|boot/期限/关闭/根目录/重初始化/独立正式入口拒绝|UNRUN_STATIC_ADMISSION|

另有READY64（47 safe、17 mutant）、BC40（30 safe、10 mutant）、RootIPC56（48 safe、8 mutant）、C09H34（28 safe、6 mutant）、S34（17 safe、17 mutant）及17项门负向检查。case_id唯一性及数目已从当前冻结输入直接核对。所有本轮运行数为0。

既有程序、输入及独立oracle均存在；全链固定顺序见[静态准入](BATCH09_STATIC_ADMISSION.md)。预算账异常的独立资格负向项仍为REQUIRED_TEST_MISSING，现有17项的实际检出数保持null。

当前Python3.12.3、systemd255.4、UID999/GID989、cgroup2和运行单位资格尚待未来单会话fresh核验；旧包记录仅作为源锁中的期望值。实际平台门及RESOURCE_GATE_PASS保持关闭。

[完整库存与只读argv](evidence/FROZEN_TEST_INVENTORY.json)；[访问边界](BATCH09_RESOURCE_ACCOUNTING.md)。
