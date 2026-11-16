# batch07 C00–C12校准结果

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

当前C00服务准入失败，校准probe执行0、root机器PASS0；C01–C12均未运行。batch05的C00–C08旧PASS继续保留旧批次范围。

|case|实际结果|阶段|
|---|---|---|
|C00|FAIL_STARTUP_GATE|服务启动请求1；票据/探针0；BC_SERVICE_IDENTITY_OR_LIMITS|
|C01|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C02|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C03|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C04|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C05|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C06|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C07|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C08|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C09|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C10|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C11|UNRUN_RESOURCE_GATE|首次失败后保持未运行|
|C12|UNRUN_RESOURCE_GATE|首次失败后保持未运行|

first C00MainPID由非阻塞systemd-run后的PID轮询取得；新service_confirmed在票据放行前检查8项/执行身份与限额，当前复核拒绝。C00未运行入口kernel/AS映射探针，C02内存/预留、C04第五task、C07/08异常退出、真实C09、C10封闭、C11故障和C12关闭/恢复均UNRUN。

slice配置与停止前kernel快照支持parent4tasks/4GiB这一窄范围；当前没有完整AS4资源资格或300秒整套可完成性结果。时间/预算上限未扩张，T0后0.309秒已关闭。[失败分析](BATCH07_COUNTEREXAMPLES.md)、[实际资源](BATCH07_RUNTIME_AND_RESOURCE.md)。
