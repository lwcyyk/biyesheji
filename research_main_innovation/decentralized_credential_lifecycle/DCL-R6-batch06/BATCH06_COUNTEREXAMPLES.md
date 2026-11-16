# batch06 首次失败与预检连续性缺口

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

## CE-B06-PF01：同一准入证据链跨越不同boot

具体输入轨迹：命令1完成1326项hash核对 → 命令2在boot `3f63d905-84a9-47c0-b212-fdda02584774`取得运行时/身份/无残留与旧账证据 → 管理命令及宿主间隔 → 命令6–13执行冻结准备/安装授权 → 命令15在boot `c92b8cbc-fada-48bd-8b61-eaaf134a06ee`检查最终状态 → `same_boot=false` → PREFLIGHT_FAILED → Launcher调用0。

命令15观测UTC区间 `2026-11-11T08:58:08.088657+00:00` 至 `2026-11-11T08:58:08.298670+00:00`。最终其他检查（限额、metadata/ACL、同设备、fresh窗口、授权摘要、slice hash）全部true；唯一失败谓词为same_boot。证据来源是[PREPARE_AND_RUN.py](evidence/PREPARE_AND_RUN.py)最终核验，依据本次授权对当前boot/完整环境及失败停止的要求建立准入连续性检查。

事后命令16再次观测boot `b69460ad-afd5-4185-871d-43277baacf85`。这支持“独立WSL调用之间存在实例生命周期变化”的行政缺口。命令6和16的较长冷启动样式耗时只提供线索；本轮没有WSL宿主关停/重启事件记录，具体触发源仍UNRESOLVED。当前boot变化前后目标Root/Receiver均未启动，不能归因为RootIPC业务执行缺陷。

## 实际停止及证据边界

首次关键预检失败后，只执行只读状态核对和host字节导出。原准备目录、授权与slice保留；没有重跑预检或case、临时改权限、修改代码/锁、重置窗口或创建batch07。未生成运行CLOSED，因为运行窗口尚未建立。行政状态PREFLIGHT_STOPPED，后续测试发放0。

RootIPC权限、取消、waitpid、ACK和模型算法都未执行，当前无对应协议反例。原batch05 EACCES和300秒停止延迟证据全部保留；本轮无法认证这些修复的动态效果。

## 后续审查目标（当前实现/执行0）

后续先收敛WSL预检编排：在稳定Linux会话或同一受控连续进程中完成fresh runtime/单位/UID/hash核验、准备与最终冻结入口交接，明确该会话生命周期和boot锚；所有最终启动断言以当前boot为准。保留本轮失败样本，核对WSL生命周期触发源，独立冻结可审阅的行政流程，再处理匹配的后续执行授权。当前batch06不自动重启，也不增设新运行窗。

这些是基础设施建议，候选协议实现门继续CLOSED；严格分离实例0。[首次失败JSON](evidence/FIRST_FAILURE.json)、[原命令2](evidence/commands/02.result.json)、[原命令15](evidence/commands/15.result.json)、[原命令16](evidence/commands/16.result.json)。
