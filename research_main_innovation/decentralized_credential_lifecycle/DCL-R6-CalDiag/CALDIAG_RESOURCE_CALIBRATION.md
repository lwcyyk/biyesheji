# C00–C12实际校准结果

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

|case|本轮结果|实际访问|
|---|---|---:|
|C00|PASS|1|
|C01|PASS|1|
|C02|PASS|32897|
|C03|PASS|4097|
|C04|PASS|2|
|C05|PASS|19|
|C06|PASS|1|
|C07|PASS|1|
|C08|PASS|1|
|C09|PASS|1|
|C10|UNRUN_AFTER_RESUME_FAILURE|0（未启动）|
|C11|UNRUN_AFTER_RESUME_FAILURE|0（未启动）|
|C12|UNRUN_AFTER_RESUME_FAILURE|0（未启动）|

C02按N=32,896一次持久范围后由child扣减，实际内存探针PASS；C03共享页和C04第5任务拒绝PASS；C05并发局部17成功/1拒绝；C06时间停止、C07控制器exit23、C08 watchdog故障均按预期PASS。真实C09取得PASS。恢复前言失败使C10–C12保持UNRUN。

C00最终八项双侧实际值：

|字段ID|期望|实际双侧|结果|
|---|---|---|---|
|CR-01|[999]|[[999], [999]]|MATCH|
|CR-02|[989]|[[989], [989]]|MATCH|
|CR-03|[989]|[[989], [989]]|MATCH|
|CR-04|0|[0, 0]|MATCH|
|CR-05|1|[1, 1]|MATCH|
|CR-06|1073741824|['1073741824', '1073741824']|MATCH|
|CR-07|1073741824|['1073741824', '1073741824']|MATCH|
|CR-08|/dclr6batch09.slice/dclr6batch09-c00.service|['/dclr6batch09.slice/dclr6batch09-c00.service', '/dclr6batch09.slice/dclr6batch09-c00.service']|MATCH|

当前C00先观察到STARTING/STARTING，随后两轮READY/READY；前五凭据在STARTING按合同defer为NOT_READY，最终全部MATCH。屏障返回区间为0.132469145–0.137505897秒，重复验证结束为请求后0.164874062秒。独立pidfd时刻/后侧原始stat/精确返回点继续缺打点，诊断完整性FIELD_EVIDENCE_PARTIAL保留。

BC40已完成：30 PASS＋10 MUTATION_DETECTED；它是冻结模拟启动回归。真实前缀另有单会话、同PID、sealed认领及服务内复核证据，真实交接后的C10连续性资格仍未取得。

[八字段与原始来源](evidence/C00_ACTUAL_FIELDS_AND_TIMING.json) · [原生检查摘要](evidence/COMPLETED_NATIVE_AUDITS.json) · [实际环境绑定](evidence/RUNTIME_EXPECTED_AND_OBSERVED_BINDING.json)。
