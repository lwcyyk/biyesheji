"""Administrative reports from actual frozen-run evidence; no target replay."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent;R=json.loads((E/'ACTUAL_RESULTS.json').read_bytes())
passport='Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。'
gates='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。'
def report(name,title,body):
    with (O/name).open('x',encoding='utf-8') as f:f.write('# '+title+'\n\n'+passport+'\n\n'+body.strip()+'\n\n'+gates+'\n')
report('PFA_AUTHORIZATION_AND_LOCK.md','执行授权、源码锁与独立身份','''
**已执行获批的最小正常A一次：C00 → PT64 → PF48 → 关闭 → 适用性审查 → 自动行政收尾。** 实际active和外层入口均返回0；完整验收另按封存与观测证据裁决。

|绑定|实际结果|
|---|---|
|最终版本|PTA-PhaseFinalizer-static-1/r3；55文件/38程序；Linux部署53项|
|manifest SHA|31be4cdcf2bebff97b8eca38fe1b4b606b7499921ff6babd1da23fd2c6f91c1d|
|execution_lock SHA|31c6fe1ba61cd9acbc4c4c1d62f5f641a0d0be8c0ac6ca816df88cbebec0b0a7|
|源/实例/slice|/var/lib/dcl-r6/pf01；/var/lib/dcl-r6/batch12；dclr6batch12.slice|
|控制目录|DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r3，启动前新建授权文件，原模板保持|
|boot|6b12daf8-f8cc-4788-bcaa-382f2d3407fb；新预检、运行与自动post一致|
|平台|Ubuntu-24.04、CPython3.12.3、原内核/systemd摘要、UID999/GID989/cgroup v2核验通过|
|预检隔离|运行目录/新slice/service/cgroup尚无；Root/Payload残留为空，failed仅mnt-e.mount|
|Root身份|Owner445/start8616，scheduler838/start8801，停止器849；原始start_ticks/boot见实际结果|
|历史保护|执行前锁7236份既有文件；4份根导航另存原字节，后续只追加当前记录|

授权scope=PT_STARTUP_DIAGNOSTIC_ONLY、mode=NORMAL_START，RootIPC/单会话/PreT0/PF及Calibrate-only必要批准位true；Full、MR诊断、预窗77注入false。SameProcess_C09兼容位满足冻结schema，实际C09发放仍由最小scope排除。真实用户原文逐字节复制并绑定SHA，回执绑定两锁及PF合同。

资源重新核算：C00=1，PT64完成1089/硬1536，PF48完成817/硬1152；正常A完成1907/硬2689。17变异包含在112jobs内。原完整硬65618加PF硬1152＝66770，距软访问100000余33230。失败关闭、hash及只读审计沿用冻结有限TCB，未重放搜索状态或窗口外checker。

冻结程序缺少逐次成功锁时间、完整导入起始/Live RLIMIT回执等观测项，执行前已记录此边界；相应结论保持条件性。本批没有加入观测代码或改变判据。

[源码与范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [资源准入](evidence/RESOURCE_ADMISSION_PROOF.json) · [部署](evidence/DEPLOYMENT_RESULT.json) · [当前环境](evidence/ENVIRONMENT_AUDIT.json) · [执行后源码](evidence/SOURCE_AFTER_CHECK.json)
''')
timeline=json.loads((E/'EXECUTION_TIMELINE.json').read_bytes())['native_boottime']
phase_rows='\n'.join('|'+x['event']+'|'+format(x['boottime'],'.9f')+'|'+format(x['T0_offset'],'.9f')+'|' for x in timeline if x['event'] in ['PRE_WINDOW','PREFLIGHT_VALIDATING','PREFLIGHT_QUALIFIED','RUNTIME_INITIALIZING','RUNTIME_READY','RUNTIME_ARMED','RUNNING','T0','C00 PASS'])
report('PFA_NATIVE_PHASE_RESULTS.md','原生阶段转换结果','''
**PF-A1=PASS_DYNAMIC（本批真实正常路径）。** 初始化成功越过历史失败位置，ARMED合法进入RUNNING，实际C00八项检查全部MATCH。本批实际进程stderr/journal未观察到PT_RUNTIME_PHASE_DRIFT。

|事件|BOOTTIME秒|T0偏移秒|
|---|---:|---:|
'''+phase_rows+'''

私有phase链完整0–6、previous_sha256逐项匹配；最终公开/私有均RUNNING、seq6，phase_record_sha256与初始化ID匹配。真实T0=88.190295781、deadline=1888.190295781、stop_at=1828.190295781，counter只建立一次并单调到1907。

实际发布者由当前scheduler身份守卫与持久状态838/start8801绑定；Root读取者包括停止器849及Root工作流程。phase事件没有独立actor字段，主体映射来自相同批次的角色记录与冻结调用链，精确逐次读写主体时间仍按观测边界保留。

本批结果只属于batch12。旧batch11的精确q/private读取值继续UNKNOWN；新批次正常成功不倒填旧字段。

[原生phase/lock证据](evidence/LOCK_AND_PHASE_EVIDENCE.json) · [C00八项原始比较](evidence/C00_READINESS_SUMMARY.json) · [完整实际结果](evidence/ACTUAL_RESULTS.json)
''')
report('PFA_LOCK_AND_VERSION_RESULTS.md','有界锁、版本与观测范围','''
**同锁接线得到冻结源码与实际正常调用路径支持；逐次flock时间、竞争及中断性质保持条件性。**

锁实际路径为/var/lib/dcl-r6/batch12/inputs/root_private/boot/pt_phase.lock。原生导出保存device/inode、Root:Root/0600、nlink1、ACL空；具体元数据保留原字段，见下方JSON。公开点和私有phase在最终快照均RUNNING/6，record digest及初始化ID一致。

|要求字段|原字段/实际观测|
|---|---|
|observed_phase|PT_RUNTIME_CHECKPOINT.phase=RUNNING，最终持久快照|
|expected_phase|pt_phase.phase=RUNNING，最终私有快照；各次读取期望未单列|
|phase_version|两侧sequence=6；私有完整事件seq0–6|
|batch_id/boot_id|batch12 / 6b12daf8-f8cc-4788-bcaa-382f2d3407fb|
|process_identity|scheduler838、Owner445、stopper849，start_ticks与boot见原件|
|lock_acquire_time/release_time|UNKNOWN，冻结程序没有相应逐次日志|
|read_result/decision|真实WORK、C00与112模型检查成功，最终状态一致；逐次读判定日志UNKNOWN|
|竞争次数|UNKNOWN；PF延迟/等待帧属于合成策略测试|
|超时/死锁|实际工作路径没有观察到锁超时错误或持续死锁；43秒前缀完成。锁故障/中断行为的真实OS测试未执行|

Root的读和成对发布均执行同一有界锁路径；批准代码字节、实际角色路径和最终版本链一致支持这一结论。中间半更新是否曾出现、每个读方的具体等待与锁释放时点缺少独立原生观测。代码在本次正常运行中完成不能替代所有调度的证明。

PF-A2=CONDITIONAL_PASS：冻结合成非法版本、错误身份、终态和WORK拒绝均按独立oracle接受；主实例没有被破坏或注入真实flock/IO故障。

[字段映射及UNKNOWN](evidence/FIELD_MAPPING_AND_UNKNOWN.json) · [锁元数据/phase链](evidence/LOCK_AND_PHASE_EVIDENCE.json)
''')
report('PFA_WORK_GUARD_RESULTS.md','WORK守卫与C00结果','''
**实际WORK成功，原资源与终态守卫继续保留。** Root在同一真实window中由ARMED/5进入RUNNING/6，随后发放dclr6batch12-c00.service。C00返回PASS，八项主检查及辅助资源比较均MATCH。

运行点committed=true、当前boot/授权/源摘要、phase_record_sha256、initialization_id及counter不可变身份均有持久原件。T0/counter建立在先，当前scheduler身份838与Root state一致；先取得资格再发放服务的路径由冻结launch_one/require_work及实际事件序列支持。

C00当前Payload实际RLIMIT_AS两侧均1GiB，parent TasksMax/pids.max4；实际执行UID999/GID989与NoNewPrivileges等按readiness记录MATCH。C00资格仅属于该测试，不授予完整RESOURCE_GATE_PASS。

非法WORK、旧phase/seq、身份/跨批/终态等测试实际在PT/PF隔离Subject中执行。主执行账、检查点或无关systemd单位未被故意损坏。CLOSED后本批保持关闭；没有继续发放C01、C09、MR或模型。

[八项原始比较](evidence/C00_READINESS_SUMMARY.json) · [112项实际输入与原件定位](evidence/TEST_CASE_RESULTS.json) · [预算完整性](evidence/BUDGET_AUDIT.json)
''')
report('PFA_PT64_RESULTS.md','PT64与九项变异实际结果','''
**PF-A3=PASS_DYNAMIC，范围为PT-SIMULATION/1。** 冻结64项全部完成并由原生独立oracle接受：55 PASS＋9 MUTATION_DETECTED，缺件/未触发/漏检0。

该suite在真实C00后执行，预算before1、after1090，消费1089：entry1＋64×(driver预付16＋Root审查1)。64份pt_case_000–063原始文件、冻结input SHA、trace.actual_input、绑定、oracle结果及raw_sha逐项对应，执行后仅做文件/结构核验，checker重放0。

9项变异force_runtime_pre、delete_pre_validation、missing_checkpoint_pass、no_auto_stop、missing_deadline、unknown_as_success、admin_as_native、new_budget_after_fail、reactivate_closed均实际命中预期违规，且没有越过冻结allowed_violations。计数包含这些变异，未追加免费窗口。

这些结果覆盖冻结预窗/初始化/检查点/自动停止/native-admin/UNKNOWN/终态的模型事实。Subject中的T0/R等是明确标记的合成值，不写入正式账；真实120秒到期、Root崩溃及真实无T0终止并未在本次正式实例额外注入。

每项实际输入/状态/违规、原始路径、SHA、前后访问、Root审查预付与时间字段见[112项明细](evidence/TEST_CASE_RESULTS.json)。原件只有sample时点，完整每case/每oracle耗时UNKNOWN；所列prepare→raw sample间隔包含预算IO并排除后续持久化/重审，不能当作完整case耗时。
''')
report('PFA_PF48_RESULTS.md','PF48与八项变异实际结果','''
**PF-A4=PASS_DYNAMIC，范围为PF-SIMULATION/1。** 冻结48项全部完成并由独立原生oracle接受：40 PASS＋8 MUTATION_DETECTED，NOT_EXERCISED/MUTATION_NOT_DETECTED均0。

预算before1090、after1907，消费817：entry1＋48×(driver16＋Root审查1)。48份pf_case_000–047原件与合同、资格文件和checker SHA对应。oracle只导入stdlib，按真实原始trace独立分类违规，再比对预期及允许伴随集合；执行后没有重跑该oracle。

|变异|实际检出目标|
|---|---|
|allow_illegal_phase|ILLEGAL_PHASE_ACCEPTED|
|skip_work|PREMATURE_WORK|
|stale_snapshot|STALE_SNAPSHOT_ACCEPTED|
|ignore_version|VERSION_MISMATCH_ACCEPTED|
|no_auto_stop|NO_AUTO_STOP|
|swallow_import_error|IMPORT_ERROR_SWALLOWED|
|overwrite_native|NATIVE_RESULT_OVERWRITTEN|
|reactivate_closed|REACTIVATION|

前四项允许放行造成的NO_AUTO_STOP伴随，原结果违规集合保持。锁竞争/延迟、身份、导入/权限/未知和关闭等帧是受冻结模型输入驱动的真实策略调用，无法替代真实OS注入；新模块的真实成功加载另见[行政收尾结果](PFA_ADMIN_FINALIZER_RESULTS.md)。

[逐项实际结果/原件/预算/时间范围](evidence/TEST_CASE_RESULTS.json) · [源与checker保持](evidence/SOURCE_AFTER_CHECK.json)
''')
report('PFA_AUTOMATIC_CLOSURE_RESULTS.md','自动关闭与真实退出','''
**正常结束自动关闭和回收确认；PF-A5=CONDITIONAL_PASS，正式Root异常关闭未额外注入。** 本批extra fallback cleanup0、人工清理0。

PF48资格形成后，冻结流程自动调用stop_tree(PT_MINIMAL_RUNTIME_DIAGNOSTIC_COMPLETE)。CLOSED在BOOTTIME131.278564941落记录；child838停止结果131.292400647为stop_exit0/empty=true/父组不存在。独立停止器849看到CLOSED后继续冻结清理，停止结果131.318848141同样成功。

协调器445对child838直接waitpid，raw_wait_status0/exit0。系统journal记录C00服务与停止服务均Deactivated successfully；精确kernel退出瞬间与最后Owner死亡时点没有单独打点。自动post同boot在131.528678948确认角色0、UID999进程0、父组不存在，读取已登记PID/starttime/boot核验无错误；其WSL客户端随后已reaped。事后独立只读导出再次确认角色/组空。

正常关闭没有产生STOP_REQUEST，CLOSED为实际终态支配对象。没有人为补STOP或伪造异常。17项异常变异都只作用于冻结合成Subject；主实例实际正常结束。

内部mr_close_state未生成，自动审计保持internal_cleanup_status=UNKNOWN；batch_state仍CALIBRATING、phase仍RUNNING，CLOSED对其继续发放具有支配作用。进程组空没有被用来改写内部状态或授予资源资格。

[实际关闭/退出原件汇总](evidence/ACTUAL_RESULTS.json) · [journal消息索引](evidence/JOURNAL_MESSAGE_INDEX.json) · [自动审计/独立导出](evidence/POSTRUN_AUDIT.json)
''')
report('PFA_ADMIN_FINALIZER_RESULTS.md','原生自动行政收尾结果','''
**固定源入口在原生环境成功加载并自动生成ADMIN_EVIDENCE_SEALED；PF-A6整体保留CONDITIONAL_PASS，资源/导入精细时点缺少独立回执。**

实际唯一post命令为：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pf01/src/admin_postexit.py --post-exit-export
```

Root actor1130/start13146，boot6b12daf8…，实际administrative_uid0；post exit0、WSL客户端reaped=true。固定源及模块origin核验已在成功路径执行，Source manifest/执行锁/当前回执匹配。模块加载没有重现ModuleNotFoundError。实际GID、cwd、完整sys.path、导入起始时点和post所在cgroup未单列记录，保持UNKNOWN。

冻结hash-bound主入口先调用setrlimit(AS1GiB)，建立唯一30秒alarm及deadline，再做source检查和load_target；原生post成功还经过继承timer/AS条件核验。administrative_deadline实际161.496699746；减30推得主入口参考时点131.496699746，audit sample131.528678948。该差值是控制流时段线索，live RLIMIT数值与具体导入起始时点没有独立日志。Payload的实际1GiB记录另属C00，不移作行政进程回执。

host在active返回后自动触发post，实际post3.890178100秒，少于30/35秒；原生组/角色只采样一次即空，没有等待竞争。导出157项原件，host行政manifest171项、ZIP172 entries，356682字节。逐流SHA/CRC及manifest字节一致；自动快照与独立只读导出157项均匹配。

自动行政ZIP SHA-256：`e4bb3cb9e66c179027d3d8bd2313fdeef14ba8d4d2d5bc5da10817b5d1da0c6b`。原始stdout/stderr完整入包，WSL代理提示保留原始混合编码字节。额外兜底归档0；后续研究ZIP只汇总已完成的自动包、原件和分析报告，未替代或重放自动finalize。

该行政包如实记录native UNRESOLVED和internal UNKNOWN。行政成功没有升级native状态，旧batch11自动post失败也保持。

[自动结果原件](evidence/STARTUP_FINALIZATION.json) · [逐流校验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json) · [字段映射](evidence/FIELD_MAPPING_AND_UNKNOWN.json) · [post原始双流](evidence/STARTUP_POSTEXIT.stdout.raw)
''')
report('PFA_NATIVE_SEAL_RESULTS.md','原生封存状态与终态前置缺口','''
**本批NATIVE_SEAL_UNRESOLVED；native ZIP/manifest均未生成。** 已保存适用性分类和完整行政证据，原生seal完成条件未满足。

CLOSED已在131.278564941建立，pt_seal_disposition在131.332716174记录UNRESOLVED。没有SEAL_ERROR或独立首次异常JSON；原始流程在适用性层安全拒绝后返回，不进入底层G.seal打包。

冻结源码的确定性依赖链为：M.seal → P.seal_applicability → runtime_checkpoint(terminal_inspection=True) → _phase_guard → _phase_deadline → G.state → validate_state_document → stopped()。G.state在看到CLOSED时抛AdmissionBlocked(BATCH_STOPPED)；terminal_inspection只传到_cancel和运行点比较，未传到读取deadline的辅助路径。seal_applicability捕获该AdmissionBlocked并返回UNRESOLVED，随后defer写入现存分类原件。

上述为CLOSED存在与冻结调用图支持的确定性源码追溯；被捕获异常没有独立traceback，报告没有将推断伪装成实际异常日志。该缺口解释正常运行对象齐备、两侧RUNNING/6和预算有效时仍不进入native打包。既有T0/R原件可读，pt_seal_disposition中的T0='UNRESOLVED'仍按原字节保存。

本次没有人工重放seal、没有补写state或改源码。历史batch11的native成功44/45与其SHA保持；新版本当前缺口单独登记。本批自动行政包成功，只代表其171项证据完整性。

[具体调用链/原始分类](evidence/NATIVE_SEAL_GAP.json) · [当前完整运行对象](evidence/ACTUAL_RESULTS.json) · [下一最小静态范围](NEXT_STATIC_REPAIR_REQUEST.md)
''')
report('PFA_RESOURCE_ACCOUNTING.md','访问账、时间与资源观测','''
**实际R=1907，等于冻结正常完成计费，低于阶段A硬界2689。** 预算只建立一次，未重置或追加窗口。

|指标|实际值/范围|
|---|---|
|C00/PT64/PF48|1 / 1089 / 817；17变异已包含在两套suite|
|journal|1907 PREPARED/COMMITTED事务，3814行，831310字节；每次amount1，连续0→1907|
|counter/intent|BRNGv001/24字节，cap1000000，used1907，COMMITTED after1907；与自动快照和独立导出一致|
|T0/deadline/stop_at|88.190295781 / 1888.190295781 / 1828.190295781|
|T0→CLOSED|43.088269160秒|
|active WSL host耗时|48.559493700秒，含其启动开销；外层host含自动收尾52.982416秒|
|自动post|3.890178100秒；正式窗口与单独行政30/35秒界分别保留|
|Payload charged memory峰观测|44924928字节＝42.84375MiB，parent该代memory.peak；与RSS分别统计|
|Payload tasks最大已保存观测|3；parent TasksMax/pids.max4，实际第五任务拒绝测试本轮未执行|
|C00 Payload RLIMIT_AS|实际soft/hard均1073741824；process RSS异步观测见原件|
|Root/全树RSS或tasks高水位|UNKNOWN；Root角色在Payload slice外|
|行政Root RLIMIT直接数值|UNKNOWN；设置先行由成功控制流与继承检查支持，实际Live字段未单列|
|120秒预窗TCB|原ticket/ctx真实绑定；本次T0正常创建，真实到期故障未额外注入|

资格文件预算区间PT1→1090、PF1090→1907。每项raw记录driver16，另外Root审查1与suite entry1均由同账预付。独立审计只验证pair/连续性/原件hash及输入映射，正式oracle/参考重放0。

完整校准访问硬界仍66770，软界100000；全批1000000/1800、校准300、提前1740、AS1GiB/父4tasks保持。43秒是当前最小前缀，无法直接按访次数量线性外推完整校准；C09/MR/S/门18及完整300秒可行性继续UNRESOLVED。

[完整账审计](evidence/BUDGET_AUDIT.json) · [准入界证明](evidence/RESOURCE_ADMISSION_PROOF.json) · [112项预算/时间细目](evidence/TEST_CASE_RESULTS.json) · [实际资源](evidence/ACTUAL_RESULTS.json)
''')
rows='\n'.join('|'+x['event']+'|'+format(x['boottime'],'.9f')+'|'+format(x['T0_offset'],'.9f')+'|' for x in timeline)
report('PFA_EXECUTION_TIMELINE.md','完整执行与收尾时间线','''
下表保留原生CLOCK_BOOTTIME采样及其相对T0偏移。采样、IO完成及内核退出时刻按各自证据区分。

|事件|BOOTTIME秒|T0偏移秒|
|---|---:|---:|
'''+rows+'''

host active UTC14:27:25.646908–14:28:14.205236；全部host调用UTC14:27:25.421390–14:28:18.402537。自动行政封存落盘UTC14:28:18.387592。所有时间均为2026-11-12，报告文件日期Asia/Shanghai对应当晚。

journal用MONOTONIC：停止器Started88.261034，C00 Started88.533253、Deactivated88.900931，停止器Deactivated131.334190。Root child直接waitpid0、后续同boot角色/组空已保存。精确最后kernel exit、flock取得释放、import开始、manifest独立生成时刻缺少单独打点，保留UNKNOWN。

每case仅保存raw sample及相应预算PREPARE/COMMIT时间；其可审查前缀间隔见明细。host、guest UTC和BOOTTIME/MONOTONIC分别保留，不构造跨时钟精确时延证明。

[全量JSON时间线](evidence/EXECUTION_TIMELINE.json) · [journal消息](evidence/JOURNAL_MESSAGE_INDEX.json)
''')
report('PFA_COUNTEREXAMPLES.md','新缺口、首个失败验收项与证据边界','''
**运行与模型检查全部完成；首个未满足的验收项是正常CLOSED之后的native seal。** 实际最早明确分类原件为131.332716174的pt_seal_disposition=UNRESOLVED。active exit0不是完整A通过的替代条件。

|登记|实际证据与结论|
|---|---|
|PFA-SEAL-1|CLOSED先建立；终态只读phase guard仍经G.state读取期限，触发其stopped拒绝；适用性层捕获后native UNRESOLVED，底层原生包未创建|
|PFA-OBS-2|冻结版本没有逐次锁acquire/release、竞争计数和各次读判定；最终版本/工作成功保留，锁故障覆盖保持条件性|
|PFA-OBS-3|Root行政post原生成功并有UID/PID/deadline，精确导入时刻、Live RLIMIT、完整sys.path/cwd/cgroup字段缺失，未用Payload或其他PID补值|
|PFA-CLOSE-4|正常路径没有mr_close_state，内部UNKNOWN保持；CLOSED/组空不能推导全部持久状态成功|

PFA-SEAL-1是冻结新辅助路径的活动态/终态前提混用。相关BATCH_STOPPED异常被源码catch，没有独立记录该异常的traceback，报告保留这一来源差异。没有重现旧的PT_RUNTIME_PHASE_DRIFT或ModuleNotFoundError。

本批不现场修复、重跑、手工seal或追加免费预算窗口。自动行政证据完整保存，原生包UNRESOLVED、内部UNKNOWN分别保持。旧batch11的漂移精确值UNKNOWN及native成功、旧MRA失败、CalDiag真实C09与旧账都保持。

[原生封存缺口](evidence/NATIVE_SEAL_GAP.json) · [观测字段映射](evidence/FIELD_MAPPING_AND_UNKNOWN.json) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)
''')
report('PFA_FINAL_DECISION.md','阶段A最终裁决与二十一项回答','''
**完整阶段A验收未取得，整体INCONCLUSIVE。真实WORK/C00与112项合成检查成功，17项变异检出；自动行政封存成功，native seal保持UNRESOLVED。**

|验收门|状态|范围|
|---|---|---|
|PF-A1 真实阶段转换|PASS_DYNAMIC|ARMED→RUNNING、当前身份/版本与真实C00|
|PF-A2 非法阶段拒绝|CONDITIONAL_PASS|冻结合成输入接受，实际OS锁/损坏注入未执行|
|PF-A3 PT64|PASS_DYNAMIC|PT-SIMULATION/1：55 PASS＋9变异检出|
|PF-A4 PF48|PASS_DYNAMIC|PF-SIMULATION/1：40 PASS＋8变异检出|
|PF-A5 自动关闭|CONDITIONAL_PASS|真实正常关闭/回收确认，正式Root异常路径未额外注入|
|PF-A6 自动行政收尾|CONDITIONAL_PASS|实际自动装载/导出/171项归档成功；精细资源/导入时点资料缺失|
|PF-A7 封存边界|PASS_DYNAMIC|native UNRESOLVED、admin SEALED、internal UNKNOWN和进程空分别记录，未升级任一结果|

|最终问题|实际回答|
|---|---|
|1 新批次预检|主机静态、原生预检及same-PID exec通过；batch12-r3独立身份|
|2 ARMED到WORK|成功，RUNNING/6并真实C00 PASS|
|3 漂移是否再现|本批真实进程没有观察到PT_RUNTIME_PHASE_DRIFT|
|4 若漂移的精确值|本批未触发；旧batch11对应读值仍UNKNOWN|
|5 同锁生效|同一路径/原生锁元数据、成功冻结调用链和最终版本一致支持；逐次锁原始日志缺失，条件性|
|6 竞争/超时/死锁|竞争计数UNKNOWN；工作路径未观察到超时或持续死锁，锁故障/退出中断的真实注入未做|
|7 版本/身份|私有seq0–6、最终公开/私有RUNNING/6、record/init hash和当前角色绑定一致|
|8 PT64实际数量|64/64接受|
|9 PT变异|9/9检出|
|10 PF48实际数量|48/48接受|
|11 PF变异|8/8检出|
|12 行政原生模块|成功，Root actor1130，post exit0|
|13 资源先于装载|冻结成功控制流与继承检查支持；单独Live RLIMIT数值/导入起始回执UNKNOWN|
|14 自动触发|是，由冻结host在active返回后自动执行，未手工调用finalize|
|15 native结果|NATIVE_SEAL_UNRESOLVED，未生成原生ZIP/manifest；终态期限辅助路径存在依赖缺口|
|16 行政归档/独立校验|自动ADMIN_EVIDENCE_SEALED，manifest171/ZIP172，逐流CRC/SHA及独立导出一致|
|17 额外兜底归档|0；仅获批的只读证据导出和最终研究汇总包|
|18 退出/组空|正常stop_exit0、child waitpid0、systemd成功退出与自动/独立审计确认；人工清理0|
|19 资源|R1907，1907事务/3814行；T0到CLOSED43.088269160秒，active48.5594937秒；Payload charged峰42.84375MiB、最大保存观测3tasks；Root精确峰未知|
|20 完整A动态验收|未取得；native封存及观测覆盖缺口保留|
|21 能否恢复MR有限验证|先最小静态修复终态只读期限与补足必要观测，冻结新身份/版本并完成独立验收，再审阅MR有限授权|

本批已CLOSED，R/T0/claim保留；现场源码修改、测试重跑、Root异常强行注入、手工seal、预算重置及自动下一批均0。113? 数量口径明确为真实C00一项＋PT64/PF48共112项，其中17变异；C00不纳入112。

历史7236份文件与原源/旧包后核见交付检查。当前prefix结果不扩展完整资源资格、F1/F4安全结论或原创性声明。

[新缺口](PFA_COUNTEREXAMPLES.md) · [封存](PFA_NATIVE_SEAL_RESULTS.md) · [自动行政](PFA_ADMIN_FINALIZER_RESULTS.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('NEXT_STATIC_REPAIR_REQUEST.md','下一最小静态审查范围','''
当前为具体补缺请求，未执行代码修复或新动态批次。

1. 修复terminal_inspection到期限读取的接线：只有已认证当前批次的终态只读审查可读取已有state/window；保留boot/身份/源/授权/检查点和期限核验。正常work继续使用严格G.state/stopped守卫。
2. 对CLOSED、STOP_REQUEST、部分初始化、缺checkpoint/错误boot/预算身份及正常active建立相应最小静态回归与独立oracle；禁止靠删除终态守卫或补假T0取得seal。
3. 在源级定义有限的逐次锁版本/取得释放及Root决策日志、行政装载前实际RLIMIT/身份/cgroup/cwd/源和导入时点回执；限制记录数量/字节与原时间合同，重新核算观测成本。
4. 明确正常关闭内部UNKNOWN的含义；如需新增终态状态收敛，必须由原waitpid/角色/预算/原件证据证明，保持旧UNKNOWN记录及native/admin分项规则。
5. 保持预算核心、RootIPC权限、sealed/一次认领、MR管理审查、C09持久ACK、业务源与原资源上限；完整diff/hash/保护语义及新身份模板先静态冻结。

batch12保持关闭，原PT/PF动态通过仅归本次模型/输入范围。后续真实正常关闭/native seal与观测验收需要新独立身份、锁和明确授权。当前不自动恢复C09、MR64、S34、门18或F1/F4。
''')
report('COMMAND_SUMMARY.md','实际命令与调用次数','''
实际共有3次行政WSL调用：53文件静态部署/原生compile、只读平台与独立实例预检、退出后的完整原件/源/journal导出。argv、双流、SHA及耗时位于[行政命令计划](evidence/ADMIN_COMMAND_PLAN.json)及evidence/commands/01–03.result.json。

冻结host入口调用一次，active Native argv为：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pf01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch12
```

冻结host自动post一次，目标admin_postexit.py --post-exit-export；active/post/外层均exit0。确切原始计划见[active调用](evidence/ACTIVE_ENTRY_INVOCATION.json)与[自动post计划](evidence/STARTUP_POSTEXIT_PLAN.json)。

统计为1 active＋1自动post＋3行政WSL，共5次；目标角色/测试重跑0。其他主机操作仅摘要、账/结构审查、报告及行政汇总。没有Root seal手工重放、管理器恢复或未来批次自动启动。
''')
report('EVIDENCE_INDEX.md','阶段A证据索引','''
|主题|工件|
|---|---|
|总裁决/21问|[PFA_FINAL_DECISION](PFA_FINAL_DECISION.md)|
|授权/准入|[原文](evidence/TASK_REQUEST.txt)、[回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json)、[范围/55项锁](evidence/SOURCE_AND_SCOPE_ADMISSION.json)、[资源界](evidence/RESOURCE_ADMISSION_PROOF.json)|
|部署/原生预检|[53项部署](evidence/DEPLOYMENT_RESULT.json)、[环境](evidence/ENVIRONMENT_AUDIT.json)、[active stdout](evidence/windows_entry.stdout.raw)|
|实际全量结果|[ACTUAL_RESULTS](evidence/ACTUAL_RESULTS.json)、[字段/UNKNOWN](evidence/FIELD_MAPPING_AND_UNKNOWN.json)、[phase及锁](evidence/LOCK_AND_PHASE_EVIDENCE.json)|
|C00|[八项比较](evidence/C00_READINESS_SUMMARY.json)|
|PT64/PF48|[112项input/状态/oracle/hash/预算/时间细目](evidence/TEST_CASE_RESULTS.json)|
|预算|[1907事务独立结构审计](evidence/BUDGET_AUDIT.json)|
|自动行政|[原计划](evidence/STARTUP_POSTEXIT_PLAN.json)、[原结果](evidence/STARTUP_FINALIZATION.json)、[逐流校验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json)|
|原生封存|[缺口/原分类](evidence/NATIVE_SEAL_GAP.json)|
|时间/退出|[时间线](evidence/EXECUTION_TIMELINE.json)、[journal消息](evidence/JOURNAL_MESSAGE_INDEX.json)、[完整原journal](evidence/RUN_BOOT_JOURNAL.stdout.raw)|
|完整原件|[157 Native导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[55源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[退出后审计](evidence/POSTRUN_AUDIT.json)|
|源/历史|[执行后55项保持](evidence/SOURCE_AFTER_CHECK.json)、[历史包](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

完整157项Native原件和55项源位于D:/毕业设计/DCL-R6-isolated-verification/batch12/native_snapshot及FROZEN_PF；最终研究ZIP另纳入export/native与export/frozen成员。自动行政原包由冻结程序真实产生，保留在control及evidence/STARTUP_ADMIN_EVIDENCE.zip。能力nonce仅保留私有原件/本地归档，报告不展开。
''')
report('README.md','DCL-R6-PTA-PF-A','''
真实正常运行达到RUNNING并通过C00；PT64为55 PASS＋9变异检出，PF48为40 PASS＋8变异检出。R=1907，自动正常关闭、角色/组空，自动行政包171/172完整。

完整验收保持INCONCLUSIVE：native seal在CLOSED后期限读取路径被活动态守卫拒绝，状态UNRESOLVED；内部UNKNOWN和锁/导入精细观测缺口保留。当前源码冻结，原生/测试重跑0。

[最终裁决及21问](PFA_FINAL_DECISION.md) · [阶段](PFA_NATIVE_PHASE_RESULTS.md) · [锁/版本](PFA_LOCK_AND_VERSION_RESULTS.md) · [WORK](PFA_WORK_GUARD_RESULTS.md) · [PT64](PFA_PT64_RESULTS.md) · [PF48](PFA_PF48_RESULTS.md) · [关闭](PFA_AUTOMATIC_CLOSURE_RESULTS.md) · [自动行政](PFA_ADMIN_FINALIZER_RESULTS.md) · [native](PFA_NATIVE_SEAL_RESULTS.md) · [资源](PFA_RESOURCE_ACCOUNTING.md) · [时间](PFA_EXECUTION_TIMELINE.md) · [反例](PFA_COUNTEREXAMPLES.md) · [授权](PFA_AUTHORIZATION_AND_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)
''')
print(json.dumps({'required_reports':13,'markdown_files':len(list(O.glob('*.md'))),'tests':112,'mutants_detected':17,'native':'UNRESOLVED','auto_admin':'SEALED'},ensure_ascii=False))
