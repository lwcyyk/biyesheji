# B1最小必要关闭证据

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

定义B1_CLOSE_REQUIRED_EVIDENCE为下列事实、来源和实际载体集合。安全关闭原件必须在行政归档工作前已被捕获并具有可用保留来源，索引只定位原件。每项的必要性、持久化、重复规则、主日志归属和独立来源详列于机器矩阵。[B1_CLOSE_REQUIRED_EVIDENCE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/B1_CLOSE_REQUIRED_EVIDENCE.json)

|ID|必要事实/层|实际或拟议载体|生成与丢失裁决|
|---|---|---|---|
|RE01|batch/boot/handoff/source/input/authorization identity，B1_SAFETY|c09_handoff.json/window, STOP_ARMED, protected namespace and proposed cursor|existing Root roles and proposed B1 cursor，before admission，reject/UNKNOWN|
|RE02|quota exhaustion and last raw observation，B1_SAFETY|existing c09_events.jsonl plus proposed cursor|Receiver，full256th PENDING then exhaustion latch，UNKNOWN if partial/unproven|
|RE03|first failure cause/actor/window/budget_before，B1_SAFETY|mr_first_failure.json|M.abort355-361，first eligible close caller，UNKNOWN|
|RE04|shared cancellation，B1_SAFETY|out/STOP_REQUEST.json|M.abort328/guard546，before cleanup，no shared cancellation proof|
|RE05|ABORTING transition，B1_SAFETY_WRITE_COST|mr_close_state.json intermediate version|M.abort366，before cleanup，intermediate history unknown if overwritten|
|RE06|CLOSED and repeat close events，B1_SAFETY|CLOSED.json / stop_event_<pid>_<ns>.json|stop_tree/fallback，under H lock before/while stop，UNKNOWN|
|RE07|payload stop and group-empty confirmation，B1_SAFETY|stop_result files and final MR payload_empty|Root stop_tree and M.abort，after manager stop and observed cgroup empty，resource cleanup UNKNOWN|
|RE08|other controlled Root role exits，B1_SAFETY|MR other_roles target facts, registry, last main exit_observed|Receiver/Root via pidfd and exact identity，during cleanup，other-role cleanup UNKNOWN|
|RE09|closing Receiver own exit，B1_SAFETY_EXTERNAL|no dedicated guaranteed pre-arranged external receipt in current B1; postexit audit may observe later|independent trusted guardian/systemd/host source to be bound，after Receiver exits，caller-exit UNKNOWN|
|RE10|direct waitpid or equivalent exit outcome，B1_SAFETY_AND_NATIVE|waitpid_<child>.json / C09 exit_witness when available|actual direct parent，real waitpid before parent loss，exact code/native readiness UNKNOWN|
|RE11|final budget conservation，B1_SAFETY|original visits.bin/intent/journal plus before/after hash-size maps|existing global ledger and M.budget_snapshot，before/after cleanup，budget UNKNOWN if torn/missing|
|RE12|all actual close attempts and final internal status，B1_SAFETY|mr_close_attempts.jsonl and final mr_close_state.json|M.abort390-400，after cleanup observations，internal completeness UNKNOWN|
|RE13|lock and publication objects，B1_PHYSICAL_METADATA|c09_lifecycle.lock, mr_close.lock, directory/staging objects|existing H/MR/RootIPC/BC helpers，before/during publication，admission/retention UNKNOWN|
|RE14|normal VERIFIED cleanup continuation，B1_NORMAL_HANDOFF|stop_result, updated handoff with cleanup, result_C09, batch_state and later RESUMED|Receiver281-294 and admitted resumed scheduler，successful verification, payload cleanup, then state progression，normal handoff incomplete/UNKNOWN|
|RE15|native prerequisite originals，NATIVE_INPUT_REFERENCES|activation/state/checkpoint/phase/runtime_intent/budget/scheduler/STOP_ARMED/markers/waitpid|existing protected producers，already present or genuinely produced before native readiness，native readiness false/UNKNOWN|
|RE16|native output/defer information，NATIVE_LATER_LAYER|terminal review / pt_seal_disposition / native manifest/ZIP / applicable error|existing sealer，after actual close/quiescence checks，native UNKNOWN/FAILED|
|RE17|minimal administrative reference index，ADMIN_REFERENCE_SPEC|proposed minimal index of original paths/hashes/sizes/roles/outcome axes; current compact writer absent|trusted evidence owner to be identified，reference safety evidence captured before archive work，admin UNKNOWN, core facts cannot be deferred to index generation|
|RE18|v2 fixed quota failure summary，PROPOSED_SUPPLEMENT|prior v2 bounded summary334|future B1 writer if adopted，first resource failure，summary missing => profile-dependent UNKNOWN|


安全最小集合包含身份/绑定、quota与最后raw、首错、共享取消、实际payload/其他Root退出、最终预算及有限关闭尝试/结果。正常VERIFIED路径还保存原cleanup、更新handoff、result_C09和batch_state。native层读取既有activation/checkpoint/phase/runtime-intent/role/budget/marker/waitpid等输入，完整ZIP和行政归档由后层负责。[src/c09_handoff.py:281](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:281) [src/terminal_evidence.py:193](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/terminal_evidence.py:193)

ABORTING与final共用mr_close_state，源代码会覆盖中间版本。其数据写入需要空间，最终集合以实际终态或残留partial/staging为准。现有实现没有为每个被覆盖中间版本另建历史副本。close_attempts的多行同属一个文件。[src/manager_recovery.py:355](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:355) [src/manager_recovery.py:390](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:390)

Receiver的结果含caller_exit_pending=true。当前进程无法在死亡前写入自己的已死亡事实，最终自身退出需要独立guardian/systemd/host的身份绑定观察及保留保障。当前专用、可保证保留的外部渠道为null，后层可能失败的admin任务不足以单独承担这一必要来源。[src/manager_recovery.py:392](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:392) [src/startup_lifecycle.py:386](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/startup_lifecycle.py:386)

资源失败关闭可以用真实pidfd事实证明某目标已经退出，精确退出23和合法handoff仍需其原生来源。父waitpid缺失时保留该精确状态及native readiness的UNKNOWN，禁止重构失去的亲子见证。[src/guard.py:1225](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1225) [src/c09_handoff.py:297](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:297)

旧v2的334字节quota摘要属于待议辅助载体。若最终profile采用它，就计入实际写入/暂存成本。quota事实本身由原始log/cursor及MR首错共同绑定。原commit/resources和全部4,450份全系统原件均按既有原始层保留，B1关闭池仅计其实际必要保护/新增写入责任。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
