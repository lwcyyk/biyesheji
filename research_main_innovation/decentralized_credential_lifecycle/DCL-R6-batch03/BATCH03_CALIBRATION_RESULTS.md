# batch03逐项校准结果
Material Passport：PRELAUNCH_BLOCKED；RESOURCE_EVIDENCE_INCOMPLETE；新校准实际执行0次。

|case|冻结目标|本轮实际结果|
|---|---|---|
|C00|入口资源限制|NOT_EXERCISED|
|C01|正常执行|NOT_EXERCISED|
|C02|AS/内存与精确预留|NOT_EXERCISED|
|C03|共享映射与继承|NOT_EXERCISED|
|C04|父层任务数|NOT_EXERCISED|
|C05|普通访问预算/并发|NOT_EXERCISED|
|C06|绝对时间及超时停止|NOT_EXERCISED|
|C07|Controller崩溃|NOT_EXERCISED|
|C08|Watchdog崩溃|NOT_EXERCISED|
|C09|启动器预定退出与恢复|NOT_EXERCISED|
|C10|权限/逃逸限制|NOT_EXERCISED|
|C11|局部单信用日志故障|NOT_EXERCISED|
|C12|批次/身份/状态拒绝|NOT_EXERCISED|

首次阻断发生在启动前：冻结的精确范围故障/重试/并发/N+1夹具缺失，自动转换门无法检查本次全部必要条件。用户§5/§6要求该情形关闭资源门；§9保持BF-static-1源码冻结。执行锁限定完整launcher时序，无法通过当前冻结开关分离校准和FORMAL。因此资源单位、票据、账及窗口初始化均保留未执行状态。

本次授权已接受；条件执行资格由本表的RESOURCE_EVIDENCE_INCOMPLETE阻断。没有新的运行中FAIL或超时退出码，也没有把未执行case标为FAIL。batch02中C00/C01原PASS及C02原失败仅作历史证据，保持原文件和口径。

校准退出原因：PRELAUNCH_REQUIRED_CAPABILITY_MISSING。本批没有新进程需要清理，后台stop/watchdog创建次数0；原单位及其他系统工作负载保持。
