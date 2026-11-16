# batch07首次失败、启动就绪缺口与未决字段

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

## CE-B07-01：C00复核在票据前拒绝

真实路径：单会话PREFLIGHT_QUALIFIED → seal/claim → same-PID exec → ENTRY_VERIFIED → 子Launcher初始化T0/预算 → 外部stop启动 → C00 systemd-run --no-block → MainPID轮询非零即退出 → service_confirmed复核 → `BC_SERVICE_IDENTITY_OR_LIMITS` → LAUNCHER_ERROR/CLOSED → 组空/父waitpid125/原生seal。

错误出自boot_continuity.py:338；8路OR涉及Uid、Gid、Groups、CapEff、NoNewPrivs、LimitAS、LimitASSoft和ControlGroup。错误字段值没有持久化，ticket_C00与BOOT_START也尚未发布，实际unit_before_ticket和/proc/status仅位于丢失的局部frame。因此**具体失配项UNRESOLVED**；当前无法把某个UID/限额值写成已观测原因。

源码确认的缺口：guard.py launch_one在--no-block后只等MainPID>0，尚无Type=exec/ActiveState就绪屏障，就要求进程具备最终UID/能力/AS/cgroup。该时序存在合法启动中的临态误拒绝实例。运行journal仅Starting→KILL，缺Started；charged peak仅782336B/1task，也与早期启动相符。这支持“过早检查exec后属性”的竞态假设，未形成具体失败字段的完整因果证明。

## 证据与时钟边界

运行boot始终060a08fc-fceb-48ff-a264-50c34312f97a，前缀Owner始终828/start7252；故障类型并非BC_BOOT_CHAIN/STALE_BOOT。CLOSED在BOOTTIME74.078122459，父waitpid/组空/封存均成功。journal的MONOTONIC序列只在自身时钟域计算，不能据未校准MONOTONIC和BOOTTIME差值推导精确错误发生时刻。

事后boot为786c0971-c8ca-4a10-8c0d-a62817ae0a17，manager查到的not-found/default属性不参与运行因果判定。首次journal读取的带连字符UUID被解析拒绝，原件保留；同一运行boot改用32-hex格式只读补导出，取得7条限定unit消息。该行政读取修正没有重跑任何case或更改目标代码。

## 下一阶段最小静态修复方向

先在冻结startup接线内补有界exec-ready屏障：等待Type=exec进入允许active状态，再fresh读取稳定MainPID/start_ticks、实际/proc身份、资源属性和cgroup；期限仍绑定当前case/deadline。此屏障不能等待依赖尚未发放ticket的应用ready，以免形成票据前死锁。保留全部原UID/AS/能力/ACK/闭合断言，失败或退出直接停止。

在判定前持久保存每个期望/实际值、采样起止、boot/身份、unit状态与确切失败predicate，使下次失败可独立重算。需要声明合法activating→exec、临态UID变化、早退出、属性漂移、超时及STOP交错的正反见证，再冻结新版本与匹配执行申请。本轮源码/权限修复0、case重试0、预算/期限重置0、batch08创建0。

该失败属于验证基础设施的启动准入，未运行F1/F4，未形成协议模型反例或原创性分离实例。[源码原段](evidence/FAILURE_SOURCE_EXCERPTS.txt)、[原始trace解码](evidence/STDERR_DECODE.json)、[因果评估](evidence/CAUSE_ASSESSMENT.json)、[运行journal](evidence/JOURNAL_SUMMARY.json)。
