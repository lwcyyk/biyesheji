# batch04资源与预算账

Material Passport：停止后原始文件独立行政解析；PASS_RAW_ACCOUNTING；资源资格仍失败。

## 唯一运行窗口
T0=199.727213695，boot99fbdfbd-f0b9-4cf2-8914-0d71867b6138。
总deadline1999.727213695，提前停1939.727213695，校准共同截止499.727213695。
关闭时刻209.077071432，elapsed9.349857737秒；组空确认elapsed9.362411078秒。未调用C09恢复，resume_count=0；窗口初始化1次，计数重置0、退款0。

## 原始账
counter37021/1000000。journal62行，PREPARED31、COMMITTED31，连续配对且counter/intent一致；最终intent为COMMITTED/after37021。没有模糊未决主账或退款。本次独立PowerShell解析没有导入目标模块，也没有执行后续oracle job。

|来源|持久事务数|预留额度|
|---|---:|---:|
|普通单信用：10个case入口＋C05的18次尝试|28|28|
|C02.memory.v1|1|32896|
|C03.shared.v1|1|4096|
|C04.fifth-task.v1|1|1|
|合计|31|37021|

三份范围事实均为CLAIMED；实际child报告操作分别17991、4096、1。C02未用14905持续占用；C05局部额度拒绝分支的全局预付同样保留。实际处理、尝试与预留额度分别报告，未用残额没有回收；不从部分观察捏造完整语义访问总量。

模型状态访问0、RANGE job计费0；已完成C诊断计入同一主账。原batch02的32191保持原历史账，与本次独立账并列；没有以新账抵销旧消耗。

## 内存与任务
父组charged peak观测125067264字节，C04 pids.current=4且第五task被拒绝。C02 AS=100663296字节、VmSize快照100515840、RSS快照93478912；树RSS精确峰值UNMEASURED。全部处于所声明AS4条件范围，未授予完整资格。

## 关闭与封存
停止器写CLOSED后停止父slice并确认empty=true，组已移除；专用UID后查无进程。controller/stopper运行日志按冻结16-unit清单导出40条。因launcher在C09预定os._exit后停止器误判，程序自动seal路径未运行，native EVIDENCE.zip不存在。已做停止后94文件逐字节行政快照，另保存30个冻结源/输入/缓存；完整快照与双流以行政包封存，来源和缺失自动封存事实均保留。

后续查询观察到另一boot，运行时统计仍只取原99fb…窗口；没有重新初始化或激活本批。
