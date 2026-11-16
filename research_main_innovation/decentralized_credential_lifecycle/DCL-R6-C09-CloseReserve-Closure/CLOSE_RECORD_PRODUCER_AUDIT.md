# 关闭记录生产者审计

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

**CRB-1=PROVED，范围为冻结64份源码/输入及其封闭调用域。** 源摘要先核对再分析，见[INITIAL_INPUT_CHECK.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/INITIAL_INPUT_CHECK.json)。共解析204个相关调用点，形成36类生产者；完整矩阵为[CLOSE_PRODUCER_MATRIX.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_PRODUCER_MATRIX.json)，逐行上下文为[SOURCE_EXCERPTS.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/SOURCE_EXCERPTS.json)。

矩阵逐项给出producer、实际进程、trigger、phase、maximum_count、maximum_bytes、persistence、quota_domain、required_for_close、after_closed和failure_behavior。以下汇总保留记录数、写入次数、唯一文件数三种计量的区别。它们均指保守包络，未宣称全部极值可在同一轨迹同时达到。

|ID|真实生产者与位置|记录/对象|次数与字节责任|
|---|---|---|---|
|C00|quota overflow refusal；c09_handoff.py:252-279; previous quota v2|no current quota-rejection producer|current no rejection; draft0 rejection rows；0 rejection-log bytes|
|C01|quota first summary；previous proposal only|new bounded failure summary|draft1；draft334|
|C02|guard.request_stop via M.abort；manager_recovery.py:328; guard.py:545-546|out/STOP_REQUEST.json|<=A writes; one pathname；189 only for reason ASCII<=43; otherwise L_stop(R)|
|C03|guard.halt_budget；guard.py:82-85,688,709; range_core.py:163,192|same out/STOP_REQUEST.json|H writes; same path as C02；error reason lacks explicit encoded width|
|C04|M.abort first failure；manager_recovery.py:355-361|inputs/root_private/boot/mr_first_failure.json|one retained object; <=A put attempts；L_first(R,T,B)|
|C05|M.abort external closing delegate；manager_recovery.py:363-365|inputs/root_private/boot/mr_external_closing.json|<=A writes; one object；L_external fixed ABI conditional|
|C06|M.abort ABORTING；manager_recovery.py:366|same mr_close_state.json|<=A writes; final uses same file；L_aborting fixed ABI conditional|
|C07|guard.stop_tree close marker；guard.py:754-760|inputs/CLOSED.json OR stop_event_<pid>_<ns>.json|<=S marker writes; CLOSED unique<=1; events<=S；L_stop(R)|
|C08|M.abort fallback CLOSED；manager_recovery.py:378-381|same inputs/CLOSED.json|<=A attempts; one shared pathname；L_stop(R)|
|C09|guard.stop_tree result；guard.py:751,766-769|inputs/stop_result_<pid>_<ns>.json|<=S objects；L_result(E,V1..V12)|
|C10|M.abort close attempt；manager_recovery.py:390-397|inputs/root_private/boot/mr_close_attempts.jsonl|<=A rows; one object；L_cleanup(T,B)+1 LF|
|C11|M.abort final state；manager_recovery.py:398-400|same mr_close_state.json as C06|<=A writes; one shared object；L_cleanup(T,B)|
|C12|coordinator waitpid normal；guard.py:1222-1227|inputs/root_private/waitpid_<child>.json|W<=2 phase objects, disjoint from fallback same-phase write；L_waitpid(state) fixed source schema/ABI conditional|
|C13|coordinator waitpid fallback；guard.py:1251-1259|same phase waitpid_<child>.json|mutually exclusive per phase with C12; combined W<=2；L_waitpid_fallback fixed ABI conditional|
|C14|coordinator C09 witness；c09_handoff.py:297-310|inputs/c09_exit_witness.json|<=1; preexisting/read-only during close；fixed identity/window schema; separately bounded width proof|
|C15|M.budget_snapshot；manager_recovery.py:266-280,330,392|embedded before/after hash+size maps|<=2A scans; embedded in C04/C10/C11；B(T) encoded map; full journal only read|
|C16|M.review_case/events；manager_recovery.py:153-188,51-60|mr_events.jsonl; mr_review_C09.json etc|old review credit256; per event checks cap32768; full callers separate；32768 event write cap; stored proof fields need separate schema|
|C17|BC.before_seal；boot_continuity.py:406-412|inputs/root_private/boot/final_before_seal.json|<=Q_s attempts; one object；embeds source state schema|
|C18|G.seal terminal review；guard.py:1009-1018|inputs/root_private/boot/terminal_seal_review.json|<=Q_s create attempts; exclusive, at most1 successful data publication；L_TR unclosed nested report|
|C19|P.defer_startup_seal；startup_lifecycle.py:348-354|inputs/root_private/boot/pt_seal_disposition.json|<=Q_s writes; one object；L_disposition(T), error text <=256 codepoints|
|C20|SEAL_ERROR writer；guard.py:1149,1275|inputs/SEAL_ERROR.json|<=4 writes; one pathname；repr(exc) encoded field has no explicit cap|
|C21|native manifest builder；guard.py:1019-1023|out/EVIDENCE_MANIFEST.json|<=Q_s attempts; one file；M_native(N,F,D) conditional grammar bound|
|C22|native ZIP builder；guard.py:1024-1027|out/EVIDENCE.zip|one x-create archive, not one per raw file；ZIP(R+M,names,codec); raw volume unresolved|
|C23|payload watchdog stop；guard.py:825-841|out/<case>.watchdog_stop.json|<=16 fixed-case writes; one per watchdog；fixed flags/stamp conditional|
|C24|controller finally/monitor；guard.py:861-904|normal_stop/timing/monitor_failure/heartbeat/watchdog.stderr|fixed file slots; timing/error bytes and monitor attempts separate；normal_stop ASCII16; timing repr/stdio volume unresolved|
|C25|P.post_exit_export audit；startup_lifecycle.py:441-491|control/STARTUP_NATIVE_AUDIT.json|one x-create audit；L_admin_audit: ambient role/process/error/member arrays need aggregate bound|
|C26|post-exit raw stdout/stderr；host/startup_finalize.py:65-85|STARTUP_POSTEXIT.stdout.raw / stderr.raw|2 x-create streams, one invocation；no streaming byte cap|
|C27|post-exit plan；host/startup_finalize.py:63-66|STARTUP_POSTEXIT_PLAN.json|1 in once-invocation scope；fixed argv/host time/error scope; schema binding required|
|C28|snapshot exporter；startup_lifecycle.py:493-510|control/startup_snapshot/<raw or native file>|old<=4452 conditional; current guard256；current total accepted<=32MiB; production raw not bounded by that check|
|C29|admin manifest/ZIP；host/startup_finalize.py:109-118|STARTUP_ADMIN_MANIFEST.json / EVIDENCE.zip|one each under once invocation；raw + native archive + host/source sidecars + manifest; byte closure unresolved|
|C30|admin finalization/failure；host/startup_finalize.py:57-61,79-95,119-121|STARTUP_FINALIZATION.json / STARTUP_POSTEXIT_FAILURE.json|one final state + at most1 failure under no re-entry；final embeds native_audit with arrays; full size unresolved|
|C31|frontend_abort；host/startup_finalize.py:23-50|FRONTEND_ABORT + manifest + ZIP + receipt|fixed4 outputs; disjoint attempt scope；error<=4096 codepoints, traceback.format_exc lacks aggregate bound|
|C32|independent oracles；terminal_evidence.py:193-266; maintenance/archive_oracle.py:inspect|returned review objects / separate research receipts|native no own persistent record; future extra oracle objects require delta；O(N+B) for admitted capped archive|
|C33|source/cursor/raw original reuse；guard.py:1019-1026; prior quota proposal|existing C09 state/commit/witness/main/cursor/budget sources|one raw pathname per layer; main already in old4450；345148 main conditional;350166 only declared local subset|
|C34|late native CHECK；c09_handoff.py:261-278|same main c09_events.jsonl|current at most one in-flight Receiver call after marker under single-thread role; draft uses its prior slot；<=1322 conditional already main|
|C35|Windows active-entry host evidence；host/windows_entry.py:35-60|WINDOWS_ENTRY_PLAN/EXIT, windows_entry.stdout/stderr.raw, STARTUP_FINALIZATION_ERROR.json|4 normal inputs; at most1 extra finalization-error file under once invocation；raw streams and repr/audit_error/embedded preserved audit need aggregate bounds|


当前代码没有“第257次配额拒绝日志”生产者；待批v2要求拒绝本身0条新增主日志，首个额度耗尽摘要另占一次。原生CHECK中可能出现FAILED分类，仍属于345148的主日志槽位；HANDOFF_FAILED没有实际publish调用。

关键别名：STOP的Root与budget-halt生产者写同一out/STOP_REQUEST.json；ABORTING与最终cleanup写同一mr_close_state.json；正常waitpid与异常reap分支在同一phase互斥、使用同一路径；mr_close_attempts的多行仍为一个文件。CLOSED首次写入后，[src/guard.py:759](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:759)把新的关闭标记改写到新stop_event路径；stop_result另为独立文件。

外部停止器没有独立Receiver_exit.json生产者。native external-tail允许当前封存者自身尚存活，要求其他已知角色退出；其自身退出与全局quiescence由post-exit行政审计再证明。[src/manager_recovery.py:405](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:405)、[src/startup_lifecycle.py:441](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/startup_lifecycle.py:441)给出两种责任。CLOSED、组空、Root退出和证据完整度分别判断。

预算最终状态属于已存在counter/intent/journal及其hash/size快照，关闭函数不新建预算账。独立terminal reader只返回对象，由sealer保存一份terminal review；未接线的maintenance oracle也没有自动递归生产运行原件。正常关闭缺mr_first_failure或mr_close_state时保留真实内部UNKNOWN，不能为凑齐数量而制造记录。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
