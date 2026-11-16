# CalDiag实际执行时间线

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

时间主线采用本批CLOCK_BOOTTIME，T0=1357.752228527。journal服务跨度单列MONOTONIC，各自同boot内作差。Windows UTC/perf_counter只作host调用证据。

|事件|BOOTTIME或相对T0|实际证据|
|---|---|---|
|预检开始/通过|1356.587195913 / 1357.428358928|预检观测跨度0.841163015秒|
|same-PID exec后entry验证|1357.707236031|owner4259/start135655|
|T0建立|1357.752228527|原窗口1次|
|C00实际服务确认|1358.123037115|PID4322/start135795、同boot|
|READY64收据采样|1367.333902934|47 PASS＋17 MUTATION_DETECTED|
|RootIPC56收据采样|1395.408516584|48 PASS＋8 MUTATION_DETECTED|
|BC40收据采样|1405.657504726|30 PASS＋10 MUTATION_DETECTED|
|Launcher原生waitpid|1406.135674940|PID4314，raw5888/exit23|
|C09退出见证发布采样|1406.287321124|持久ACK/Receiver/Root见证绑定|
|真实C09 PASS|T0+48.592009253|HANDOFF_VERIFIED/classification_count=1|
|同父恢复entry验证|1406.427000870|同owner；新scheduler PID4804|
|恢复健康检查失败|T0+48.699583118至+48.738270904|UNREVIEWED_MANAGER_FAILURE，精确raise时刻未打点|
|原入口返回|host累计50.3556852秒，exit125|时钟域为Windows perf_counter|
|初次事后快照|AWAIT_EXPECTED_RESUME、无CLOSED/原生seal|Payload为空，external-stop4318仍在|
|冻结关闭记录采样|T0+299.567904452|CLOSED=CALDIAG_ABORT_AFTER_RESUME_MANAGER_FAILURE|
|清理确认/冻结seal完成|T0+299.993796083|角色全空，R不变|

失败位于恢复前言，早于launcher.lock及清理try块，后继C10尚未启动。Receiver在等待恢复时清空coordinator_identity；父协调器对普通wait返回的125直接退出，未进入异常清理。因此初始CLOSED和seal均缺失，Root停止器继续等待。本轮保存607份初始文件后，经授权调用原冻结stop_tree/seal完成关闭；保留612份最终快照及两次独立manifest。

关闭后state文档仍保留AWAIT_EXPECTED_RESUME作为原始状态；CLOSED文件为吸收标记，准入函数优先据此拒绝后续工作。本轮没有改写该状态字段来伪造恢复成功或关闭时间。

[启动/失败区间](evidence/BOOT_IDENTITY_AND_FAILURE.json) · [初次审计](evidence/POSTRUN_AUDIT.json) · [冻结补充清理](evidence/FROZEN_FAILURE_CLEANUP.json) · [最终审计](evidence/FINAL_POSTRUN_AUDIT.json)。

CLOSED记录到冻结stop_tree结果采样给出发布完成区间T0+299.567904452–299.596399447秒；预检开始到exec后entry复核为1.120040118秒。各书签按采样语义解释。
