# Case实际耗时及测量边界

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

|case|结果|服务启动秒|服务包络秒|child秒|已记录fsync数|fsync累计秒|
|---|---|---:|---:|---:|---:|---:|
|C00|PASS|0.022467|0.380646|UNRUN/UNMEASURED|11|0.028842|
|C01|PASS|0.024159|0.289374|UNRUN/UNMEASURED|11|0.031809|
|C02|PASS|0.023113|2.788151|2.362583|46|0.144014|
|C03|PASS|0.021786|1.097472|0.684494|30|0.092352|
|C04|PASS|0.024167|0.484814|0.147930|24|0.067997|
|C05|PASS|0.021175|0.908509|UNRUN/UNMEASURED|265|0.950257|
|C06|PASS|0.021052|2.160464|UNRUN/UNMEASURED|0|0.000000|
|C07|PASS|0.022866|0.196613|UNRUN/UNMEASURED|0|0.000000|
|C08|PASS|0.023650|0.233612|UNRUN/UNMEASURED|13|0.037015|
|C09|PASS|0.026009|0.610925|UNRUN/UNMEASURED|0|0.000000|
|C10|UNRUN_AFTER_RESUME_FAILURE|UNRUN/UNMEASURED|UNRUN/UNMEASURED|UNRUN/UNMEASURED|0|0.000000|
|C11|UNRUN_AFTER_RESUME_FAILURE|UNRUN/UNMEASURED|UNRUN/UNMEASURED|UNRUN/UNMEASURED|0|0.000000|
|C12|UNRUN_AFTER_RESUME_FAILURE|UNRUN/UNMEASURED|UNRUN/UNMEASURED|UNRUN/UNMEASURED|0|0.000000|
|C09H|PASS|0.023973|7.135260|UNRUN/UNMEASURED|2217|6.364018|
|RANGE|UNRUN_AFTER_RESUME_FAILURE|UNRUN/UNMEASURED|UNRUN/UNMEASURED|UNRUN/UNMEASURED|0|0.000000|

服务启动=journal Starting→Started；包络=Starting→terminal，均为journal MONOTONIC。child采用原BOOTTIME spawn_request→wait_return。C06/C07/C09的系统级失败退出为指定故障，其Root校准裁决是PASS。

fsync仅统计原程序已落盘的instrumented聚合；C06/C07/C09的0表示聚合文件缺失或未写出，实际持久化时间保持UNMEASURED。线程/阶段可能重叠，fsync累计值可超过对应服务墙钟，无法直接作为完整时间分区。纯程序、监督等待、清理和写证缺独立起止打点时保持PARTIAL/UNMEASURED。

|Root/合成阶段收据|访问增量|实际观测跨度秒|边界|
|---|---:|---:|---|
|C00_READY_QUALIFICATION.json|449|8.899268|First persisted charge to receipt sample; final receipt publication is outside this span|
|ROOT_IPC_QUALIFICATION.json|505|11.392948|First persisted charge to receipt sample; final receipt publication is outside this span|
|BOOT_CONTINUITY_QUALIFICATION.json|481|10.200091|First persisted charge to receipt sample; final receipt publication is outside this span|
|C09H_QUALIFICATION.json|273|7.649303|First PREP to last COMMITTED timestamp; final raw oracle/publication outside this observed span|

上述Root阶段从第一笔持久PREP采样起算；READY/IPC/BC到Root收据sample，H34到最后COMMITTED采样。函数前言与最终收据发布处于边界外，实际阶段总时间还包含这些开销。嵌套子case不与所属阶段重复相加。

已测Root跨度最长为IPC56 11.392948秒，其次BC40 10.200091、READY64 8.899268、H34至少7.649303。payload服务包络最长为C09H 7.135260，其次C02 2.788151和C06 2.160464。C09H落盘fsync累计6.364018秒提示已观测持久化开销突出，当前资料仍不足以推出剩余S34/门18的完整耗时。

[逐case机器结果](evidence/CASE_DURATIONS.json) · [测量覆盖](evidence/MEASUREMENT_COVERAGE.json) · [journal原件](evidence/FINAL_RUN_BOOT_JOURNAL.stdout.raw)。

194个已执行回归子case的真实收费起点/原始行结束书签、IPC fixture before/after及逐job费用另存[REGRESSION_JOB_TIME_BOOKENDS](evidence/REGRESSION_JOB_TIME_BOOKENDS.json)。这些是带边界说明的观测区间，最终oracle/发布耗时按对应阶段保留，时间项重叠时保持分列。
