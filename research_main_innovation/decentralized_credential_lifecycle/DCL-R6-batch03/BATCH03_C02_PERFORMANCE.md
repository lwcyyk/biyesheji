# batch03 C02性能与实际执行
Material Passport：C02=NOT_EXERCISED；RESOURCE_EVIDENCE_INCOMPLETE；预检阻断。

|验收项|本轮实际结果|
|---|---|
|C02.memory.v1合同及N|冻结hash匹配；N=32896，4KiB页合同匹配；静态事实|
|一次N持久预留|NOT_EXERCISED|
|PREPARED写入/结束|N/A，无新账|
|fsync实际耗时|N/A，目标路径未调用|
|COMMITTED完成时刻|N/A|
|局部扣减耗时|N/A|
|内存分配child启动|0次|
|child退出/内存失败行为|NOT_EXERCISED|
|300秒内完成|NOT_EXERCISED|
|性能改善倍数|UNMEASURED|
|C02资源资格|NOT_EXERCISED|

batch02原事实保持：C00/C01结果到T0+1.109256092秒；C02预付区间298.626607199秒；共32191预留，其中32188为尚未启动child预付；旧COMMITTED复用PREP时标，旧fsync细分未知。当前11次只读查询的耗时与C02预付/处理毫无对应关系。

BF-static-1源码对每个精确范围为9个预留同步机会加2个claim同步机会，C02旧完整预付为7×32896；这是保留的静态成本模型，本轮没有速度实测。资源身份、N+1拒绝及范围崩溃/重放能力缺口先于执行构成阻断，尚无可用于C02 PASS的实际证据。首次阻断详见evidence/FIRST_BLOCKING_EVENT.json。
