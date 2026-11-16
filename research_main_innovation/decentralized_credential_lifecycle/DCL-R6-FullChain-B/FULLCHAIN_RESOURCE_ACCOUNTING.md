# 资源预算独立核算

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


冻结可达完整校准访问硬界独立重算为68,498≤100,000，余量31,502；总1,000,000内余量931,502。这个数值覆盖现有路径；FC-S03缺失的原生异常清单尚无额外预算证明。

|阶段|保守访问硬界|
|---|---:|
|C00_C12|37,034|
|READY64|512|
|C09H_IPC_BC_joint|5,000|
|RANGE34_gate18_ledger_raw|20,000|
|MR64_native_prepaid|1,536|
|PT64|1,536|
|PF48|1,152|
|TR40|960|
|RA32|768|
|合计|68,498|

C00–C12：13次入口访问＋C02预留128×(1＋1MiB/4096)=32,896＋C03预留16MiB/4096=4,096＋C04预留1＋C05尝试18＋C11循环4＋C12拒绝6=37,034。page4096为该算式前提，本批实际page查询尚未执行。

C09H成功路径精确273，冻结max_events64推得上界2,245；IPC完成收费505/硬512，BC完成481/硬512。联合保守上界3,269低于保留的5,000封套，避免再次叠加共同费用。真实C09入口访问计入C00–C12；原生恢复审查在C00后预付256，MR回归完成833，合计1,089；保守专项硬界1,536。

RANGE成功上界：1＋68×281＋2×34＋34＋1＋18＋631=19,861。分别覆盖driver入口、两actor上界、job设置/即时checker、Root原件checker、健康控制、门18循环和ledger聚合。聚合595=1＋18×(32＋1)，两次Root重审36，合计631；以硬640替换后为19,870≤20,000。独立生产oracle只在未来受控计费路径调用，本轮调用0。

PT/PF/TR/RA的固定成功收费分别1,089/817/681/545，由1＋jobs×(driver_prepay＋1)推得；上表采用各自更保守硬界。FORMAL控制器与run_batch重复准入另收费2，发生在校准结束后的同一全局剩余预算中。模型本体访问预算服从全局剩余额度和原deadline。

旧boot/root_ipc/readiness合同内仍保留65,618描述字段；本轮根据实际新增套件重算为68,498，与当前manifest/execution_lock的完整硬界一致。旧描述与现路径数值差2,880记入机器证据；相关字段的运行时引用扫描没有发现其作为动态上限被使用。本轮保持原字节。

资源合同：AS1GiB/进程、Payload父TasksMax4、墙钟1800/提前1740、校准300、TCB120。实际T0/deadline/R、内存峰值、进程峰值、I/O耗时均null；新增已消费访问为0。访问上界合格与封存容量准入分别裁决。

[完整算式与逐case收费](evidence/RESOURCE_BOUND_INDEPENDENT.json) · [容量冲突](evidence/SEAL_CAPACITY_STATIC_WITNESS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
