# BC-1至BC-8安全性质与未决证明责任

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

|性质|实现谓词|检查点|未来验证|
|---|---|---|---|
|BC-1 SameBoot|chain boot相等、ticket/Owner/current boot相等，继承cap属于原实例|[boot_continuity.py:115 eligibility](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.after_first/during_prepare/after_final/during_exec/old_receipt，M.epoch/snapshot|
|BC-2 FreshRuntime|当前source/runtime/UID/cgroup/manager fresh；Guard接入再次读取|[boot_continuity.py:186 runtime_snapshot](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.resources/identity/artifact_drift；M.resources/cache；真实入口|
|BC-3 NoStaleAuthorization|新boot/新Owner/错binding/无cap/旧窗口拒绝|[boot_continuity.py:125 ticket_policy](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.bad_batch/bad_lock/old_receipt；M.binding/epoch/snapshot|
|BC-4 SingleActivation|O_EXCL claim＋锁＋持久entered位；初始一次/同窗resume一次|[boot_continuity.py:299 guard_admission](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.duplicate；M.duplicate；实际同时启动/复用待测|
|BC-5 FailClosed|不确定/缺证/STOP/CLOSED/时间失效异常退出；无fallback放行|[boot_continuity.py:225 prepare_activation](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.stop/closed；M.closed/resources/cache|
|BC-6 NoBudgetReset|既存Root/state/counter拒绝；24预算函数保持；恢复原window核验|[boot_continuity.py:386 entry](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.old_window；M.budget；真实C09恢复|
|BC-7 NoFalseStart|请求与实际服务分开，实际身份/active/资源检查后发布证据|[boot_continuity.py:330 service_confirmed](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.request_only/launcher_exit；M.request；真实C00/C10|
|BC-8 TCBBoundary|单会话Root Owner/封印fd；Windows记录器、既有TCB责任显式|[boot_continuity.py:284 read_capability](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)|P.orchestrator_exit/identity；M.identity/snapshot；实际故障责任待测|

证明边界：同一存活Linux进程的exec交接、不可变cap与持久认领提供可检查的代次和一次性边界；系统重启无法把原进程/原fd带入新实例。该论证依赖可信内核/Root/部署及文档接口，当前没有原生行为测试。跨systemd、磁盘和调度的全局原子事务及严格实时性继续CONDITIONAL/UNRESOLVED。

BC40只证明模拟重启模型中的检测责任；模型会改变epoch、杀死旧actor、丢弃cap/manager活动状态并保留持久账与闭合，不能据此写出本机物理重启PASS。真实启动、服务、原C09及资源资格另取当前证据，接口或阶段缺失均阻断。

[启动凭据](BOOT_BOUND_AUTHORIZATION.md)、[回归计划](BOOT_CONTINUITY_REGRESSION_PLAN.md)、[静态检查](STATIC_VERIFICATION_RESULTS.md)。
