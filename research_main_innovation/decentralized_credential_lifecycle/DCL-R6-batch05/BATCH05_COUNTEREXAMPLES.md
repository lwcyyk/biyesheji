# batch05 首次失败、权限反例与生命周期缺陷

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

## CE-B05-01：特权审查替换共享 intent，payload 后续读取失败

可复核输入轨迹：新batch05/uid999账 → C00–C08通过 → C09H34完成 → Root独立审查用euid0执行34次全局 `reserve_counter` → 共享intent被替换 → C09 uid999入口读取intent → EACCES → BUDGET_HALTED/STOP_REQUEST → CLOSED/组空。

原始STOP_REQUEST（boottime3898.529937533）：

```text
BUDGET_HALTED:[Errno 13] Permission denied: '/var/lib/dcl-r6/batch05/out/visits.bin.intent.json'
```

源码对应：guard.py:285–307 `root_verify_c09h` 逐job通过 `c09h_charge()` 调用全局账；guard.py:119–135 `atomic(...,root_record=False)` 以当前writer创建0600临时文件，replace后保留writer所有权；共享intent路径使用该默认分支。guard.py:491–512 `_counter_lock` 在新事务前读取intent。native stat命令26确认intent=0:0/0600，counter/journal=999:989/0600。

上述控制流、最后34笔特权审查与实际owner/mode/错误路径相互吻合，支持主根因为 **ROOT_AUDIT_REPLACED_SHARED_INTENT_WITH_ROOT_0600**。内容配对错误0，入口拒绝发生于新事务之前。该反例针对监督器跨身份可用性和权限保持，尚未形成F1/F4协议模型反例或原创性分离实例。

## CE-B05-02：C09 ready 等待延迟观察 CLOSED

guard.py:834–835 等待条件只有ready是否存在与case limit。payload在T0+20.927591657已清空；Root scheduler仍等到T0+300，抛出 `C09_NOT_READY`，最终清理在+300.043546214，外层exit125。源码与命令24/stop_event/stop_result一致。停止协议及时终止了payload；Root管理组件的终止响应存在约279秒延迟。

## 修复候选与后续静态验收范围

仅提出审查目标，本轮实现修改0、权限修复0、重试0：明确全局持久账唯一writer身份，或在临时文件对外发布前保持所需owner/mode与持久化顺序；检查全部Root全局记账调用（C09H、S独立检查、门审查）；加入Root→payload与payload→Root身份切换、读写/replace故障、闭合竞态的权限回归。C09等待需统一观察CLOSED/STOP_REQUEST及受控进程退出，并保留绝对期限与已收集首次失败。修复应在独立静态版本冻结后再申请匹配动态范围；本轮batch05持续CLOSED，batch06未创建。

任何新的研究候选机制仍先完成“具体输入族＋度量＋最强通用方法＋预测差距”的可证伪分离声明及严格实例，再考虑实现。当前严格分离0，IMPLEMENTATION_GATE=CLOSED。

[因果汇总](evidence/ROOT_CAUSE.json)、[首次失败](evidence/FIRST_FAILURE.json)、[冻结源码摘录](evidence/FAILURE_SOURCE_EXCERPTS.txt)、[原始权限](evidence/commands/26.result.json)、[实际双流/退出](evidence/commands/24.result.json)。全部首次失败原件保持。
