# 最小预算修复实现
Material Passport：BF-static-1 / STATIC_SYNTAX_PASS。真实源码位于 [guard.py](<D:/毕业设计/DCL-R6-isolated-verification/lc03/src/guard.py>) 与 [guard_probe.py](<D:/毕业设计/DCL-R6-isolated-verification/lc03/src/guard_probe.py>)。Windows路径以 SOURCE_AND_INPUT_LOCK 的实际绝对路径为准。

## 实际范围
修改两个获准文件；run_batch.py未改。五业务文件未改。源码起点为正确 batch02/FROZEN_LC/src；误路径副本读取仅用于完整性登记，参与实现输入次数0。完整八文件diff及新旧SHA见 evidence/SOURCE_DIFF_INDEX.json 和 evidence/diff/，相同文件diff为空。

guard.py新增：固定N合同校验、EXACT-RANGE/1格式、_counter_lock、_reserve、ExactReservation、claim_exact、LocalCredits、预算HALTED、阶段遥测；普通Budget.visit继续逐次持久计费，保留局部17上限镜像。计费路径复用原journal/intent/counter，新增每task一份registry事实及一次持久claim。batch身份、单位名、授权文本改为batch03，输入SOURCE只接受lc03。

guard_probe.py：原prepaid_child逐N次budget.visit替换为reserve_exact一次与dispatch_once；argv增加task-id及lease-id；child在降低C02 AS之前完成claim；各次分配/触碰/创建尝试先用LocalCredits.visit。probe的资源分配、固定循环、退出判据、软窗保持；新增结果只记录预算事实和阶段时间。父验收0≤operations≤credit_used≤N，允许扣减后中断造成的观察差额，租约须一致。

## 调用与复杂度
Controller run_case入口单信用 → prepaid_child → Budget.reserve_exact → 固定合同+持锁范围事务 → dispatch_once → 子进程exec → claim_exact → 局部前置扣减 → 原探针 → 输出与wait-return。普通F1/F4收费点及参数调度保持原源码。

以完整已知N子任务为单位，旧路径N个持久事务、7N同步机会；新范围事务原7加registry2=9，child claim2，合计11。每个同步机会对应源码一次os.fsync；日志、结果、心跳、初始化、停止与遥测另计。C02为230272→11；C03为28672→11；C04为7→11，后者选择统一安全接口且没有同步次数收益。全校准范围最大预算仍37034，额度口径无舍入增加。

T_old≈N·t_single+t_schedule；T_new≈t_range+t_claim+N·t_local+t_schedule。t_range包含新增序列化/校验/registry成本；t_local包含进程/文件/时钟检查与计数；调度、输出及监控另测。复杂度收益针对持久预付部分，局部处理仍O(N)。真实fsync、墙钟收益与C02成功启动尚无新测量。

## 版本边界
BF-static-1已冻结：后续代码变更需新版本、新diff、新SHA与适当静态检查。当前未安装batch03单位，未建立batch03目录、账或窗口。静态模板与未来命令在lc03准备目录，执行资格始终单列。
