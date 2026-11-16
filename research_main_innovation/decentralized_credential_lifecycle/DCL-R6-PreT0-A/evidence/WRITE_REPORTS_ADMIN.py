"""Author administrative reports from sealed originals; target code stays frozen."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
q=json.loads((E/'ACTUAL_RESULTS.json').read_bytes())
passport='Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。'
gates='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。'
def write(name,title,body):
    text='# '+title+'\n\n'+passport+'\n\n'+body.strip()+'\n\n'+gates+'\n'
    with (O/name).open('x',encoding='utf-8') as f:f.write(text)
write('PTA_AUTHORIZATION_AND_LOCK.md','阶段A授权、版本与隔离锁',r'''
**已按 NORMAL_START 调用冻结入口一次，实际返回125；本批随后自动关闭。** 用户第4节将正常预窗初始化列为最高优先级，第14节要求按初始化、检查点、PT64顺序立即执行；据此选择双方共同允许的较小正常模式。PREWINDOW_ABORT保持UNRUN。本次授权原文没有书写模式字面量，这一选择属于对明确正常初始化目标的执行映射，已在启动前公告并记入回执说明。

|绑定对象|核验结果|
|---|---|
|最终版本|PreT0Recovery-static-1/r3，51文件＝33 Linux程序＋2 host程序＋16输入|
|manifest SHA-256|34c9c4642c4ff8c68183845b66f49f1670efa3349ec82e07d80e8bbabfd86ab7|
|execution_lock SHA-256|af8de2c099813d2e3018c6d46b2e95b435c2e75a122d32b73b3f96e3c47b58ec|
|部署|49份Linux源/输入，Root:Root/0644，目录0755，无额外ACL/pyc；目标模块导入0、33程序原生内存compile通过|
|主机程序|35程序文法/compile通过；主机入口Python3.14，正式Native精确/usr/bin/python3.12 3.12.3|
|boot_id|24fc4fce-f68c-4ab5-8662-261ed17d831b，部署/预检/执行/首次事后审计一致|
|身份|Root827/start6546；child887/start6672；停止服务892/start6693；当前UID999/GID989和组符合合同|
|环境|内核6.18.33.2-microsoft-standard-WSL2；systemd255.4-1ubuntu8.18；cgroup v2；初始failed仅mnt-e.mount|
|独立namespace|/var/lib/dcl-r6/pt01源；/var/lib/dcl-r6/batch11运行；dclr6batch11.slice；启动前运行目录/单位/cgroup均无|
|标签差异|冻结JSON、batch_identity.py和execution_lock一致指定控制目录DCL-R6-PreT0-Fix/authorization/batch11-r5；报告正文称batch11-r3，phase_A_identity_rule另残留r1文字。采用摘要绑定的实际路径，源码版本仍为r3，历史batch10保持关闭|
|历史保护|启动前锁6,522份历史文件，4份根导航另存原字节；误路径副本只读/hash|

回执中的RootIPC/单会话/同父恢复兼容字段按冻结schema置true；实际scope仅PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START，Full/MR诊断/预窗77注入均false。兼容字段不扩展到C09发放权限。完整用户原文与SHA绑定，51份源码、冻结模板、历史锁原件保持。

主机精确入口：`python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\pt01\host\windows_entry.py --activate`，环境PYTHONDONTWRITEBYTECODE=1。唯一active WSL argv与只读post-exit argv见[命令记录](evidence/ACTIVE_ENTRY_INVOCATION.json)及[自动收尾计划](evidence/STARTUP_POSTEXIT_PLAN.json)。共有1次active、1次自动post、4次部署/只读行政WSL调用；行政调用均无测试/恢复/T0创建。

[源码与范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [部署](evidence/DEPLOYMENT_RESULT.json) · [平台](evidence/ENVIRONMENT_AUDIT.json) · [回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json) · [执行后源码](evidence/SOURCE_AFTER_CHECK.json)
''')
write('PTA_INITIALIZATION_RESULTS.md','真实预窗与初始化结果','''
**正常预窗认证已通过，真实初始化推进到RUNTIME_ARMED；首次工作发放前停止。** 本轮没有重现IPC_STATE_MISSING。

|实际阶段|BOOTTIME秒|原始见证|
|---|---:|---|
|启动TCB起点|65.510243359|sealed preflight_deadline−120|
|Native预检qualified|66.403873152|原始stdout的PREFLIGHT_QUALIFIED|
|same-PID入口验证|66.715489008|ENTRY_VERIFIED；Owner仍827/start6546|
|PRE_WINDOW|66.811319376|pt_events序号0，Root保护ctx已建立|
|PREFLIGHT_VALIDATING|66.820658042|序号1；仅认证预窗query scope|
|初始manager健康通过|66.870763982|两次实际query返回0，failed仅mnt-e.mount|
|PREFLIGHT_QUALIFIED|66.874374079|序号2|
|runtime intent采样|66.885179620|独占pt_runtime_intent，当前boot/源/授权绑定|
|RUNTIME_INITIALIZING|66.888638365|序号3，intent已持久化|
|真实T0|66.896850269|batch_state中的真实时钟值|
|RUNTIME_READY|66.914956317|序号4，state/counter/COMMITTED intent已核验|
|RUNTIME_ARMED|67.109909234|序号5；STOP_ARMED已存在，父TasksMax检查通过|
|公开armed检查点采样|67.118473361|PT_RUNTIME_CHECKPOINT.phase=RUNTIME_ARMED|

ctx中的T0/R仍为null，正确表达预窗快照；真实batch_state和预算随后独立建立。窗口deadline=1866.896850269、stop_at=1806.896850269；未重置。初始化intent的hash与公开检查点initialization_id一致，phase链previous_sha256逐项一致。RUNNING没有发生，C00未发放。

预窗health走专用scope并取得真实成功，这为旧循环依赖的拆分提供本次正向证据。严格运行检查点在state/counter建立后被调用，随后暴露跨文件phase快照竞态。运行损坏拒绝、关闭重入和所有故障分支的动态覆盖仍待PT64实际运行。

[实际结果](evidence/ACTUAL_RESULTS.json) · [时序原件索引](evidence/EXECUTION_TIMELINE.json) · [首次反例](PTA_COUNTEREXAMPLES.md)
''')
write('PTA_CHECKPOINT_LIFECYCLE.md','检查点生命周期与顺序证据','''
**intent先于T0、counter先于运行检查点的顺序已取得实际证据；READY→ARMED的跨对象发布暴露并发一致性缺口。**

|对象/动作|实际结果与计时精度|
|---|---|
|sealed capability/一次认领|预检、same-PID exec、Owner/child核验通过；原nonce仅保留私有原件及证据包|
|预窗ctx|绑定本批/boot/manifest/执行锁/授权/Owner，期限185.510243359；T0/R=null|
|runtime intent|sample66.885179620；exclusive存储返回先于INITIALIZING sample66.888638365；fsync完成的精确时点缺少独立打点|
|T0/deadline/state|T0=66.896850269；真实发布先于READY；具体state fsync时点仅由执行顺序及持久原件限定|
|预算账|BRNGv001、used0、cap1,000,000；COMMITTED after0；创建在T0之后、READY之前|
|初次runtime checkpoint|READY事件之后写入，原生停止服务启动之前完成；初次READY文件随后被armed版本更新，原件未提供逐次公开checkpoint历史|
|严格运行检查首次调用|精确调用时间未打点；P.arm及Receiver.poll实际到达，前置真实state/counter存在；预窗manager查询成功发生在T0之前|
|armed/work|phase序号5及公开检查点存在；work服务0、RUNNING0；完整拒绝用例UNRUN|
|关闭后|CLOSED/STOP优先，保留原T0、intent、counter及phase；无新建账或重新初始化|

实际竞态可由以下允许调度解释：停止服务读取公开q.phase=READY；Launcher持久化私有phase=ARMED；停止服务读取新私有phase并比较旧q，抛PT_RUNTIME_PHASE_DRIFT；Launcher完成公开armed检查点。另一允许调度是读取发生在两个文件发布之间。原件没有记录每次读取值，因此具体交错保持推断；最终两个phase均为ARMED、initialization_id一致，且真实trace指向该跨对象比较。

下一静态验收应规定phase与公开checkpoint的统一提交/读取一致性义务，保留真实缺失/损坏拒绝和单调阶段约束。本轮实现改动0。

[初始化结果](PTA_INITIALIZATION_RESULTS.md) · [原生源码锁](evidence/FROZEN_SOURCE_REFERENCE/inputs/static_manifest.json) · [结果重核](evidence/ACTUAL_RESULTS.json)
''')
write('PTA_PREWINDOW_ABORT_RESULTS.md','T0缺失故障与120秒期限覆盖','''
**PREWINDOW_ABORT=UNRUN；T0缺失条件下的真实自动关闭性质仍待验收。**

本批仅运行NORMAL_START。冻结申请把两个A模式绑定到同一未建立实例，首模式认领、创建T0并关闭后，第二模式须新身份、最终摘要与独立授权。本轮没有额外预窗77注入窗口。

|性质|实际覆盖|
|---|---|
|原120秒启动TCB|真实ticket/ctx保存起点65.510243359、deadline185.510243359；初始化T0在起点后1.386606910秒|
|预窗超过120秒时拒绝/停止|UNRUN；本批没有等待或注入到期|
|T0不存在时关键异常自动关闭|UNRUN；本次错误发生在真实T0与预算创建之后|
|PT64的预窗失败/Root失败/账缺失等|0/64；在C00前终止|
|真实77预窗中止与native不适用|UNRUN；实际批次已具备运行对象|
|本批关闭是否早于原预窗deadline|是，但这只说明本批运行态错误的关闭时间，不构成无T0路径通过|

120秒合同和上限保持原样。报告区分“期限真实绑定”“运行态错误自动收敛”“无T0错误动态覆盖”三项。下一独立A所需最小范围见[下一静态审查](NEXT_STATIC_REPAIR_REQUEST.md)。
''')
write('PTA_AUTOMATIC_CLOSURE_RESULTS.md','自动STOP、回收与内部状态','''
**关键错误自动触发STOP/CLOSED，角色和组已空，额外兜底及人工清理均为0。内部状态先出现UNKNOWN，后依据冻结角色退出审查收敛为CLOSED_CLEANUP_CONFIRMED。**

|责任源|实际行为|
|---|---|
|独立Root停止服务892|Receiver.poll抛PT_RUNTIME_PHASE_DRIFT，自动abort发布首个STOP；多层异常wrapper继续执行冻结收敛|
|Launcher child887|观察STOP后root_checkpoint拒绝；异常自动abort，退出125|
|Root协调器827|直接waitpid见证child887/raw32000/125，自动stop_tree，保留首错及关闭记录|
|systemd|当前batch11 slice停止成功；停止服务最终退出125，原journal保留failed记录|
|外部/人工兜底|0；事后只读导出和行政打包没有调用关闭函数|

首个STOP sample67.121192409，reason=MR_CRITICAL:C09_OR_SUPERVISOR_FAILURE。首次持久错误记录在67.129488196，由child先获得锁，保存LAUNCHER_ERROR/IPC_STOP_REQUEST_DOMINATES。它与触发STOP的外部异常属于不同证据层，原件均保留。

CLOSED sample67.139362562；child停止结果67.152813419显示stop_exit0、empty=true、group不存在；父协调器停止结果67.249958981同样成功。child直接waitpid在67.226047790。停止服务journal退出见证为MONOTONIC67.405716，精确内核退出瞬间缺少专门打点。

mr_close_attempts前两条为UNKNOWN：owner退出/child reap仍待定。后续三条依据冻结角色审查记CLOSED_CLEANUP_CONFIRMED，最终sample67.371083714。外部服务67.329851722的记录观察827和887均退出；其自身退出另由systemd见证。所有UNKNOWN原行保留。预算快照中缺少journal的UNKNOWN字段同样保留；关闭成功不授予完整资源资格。

首次独立事后audit在同boot BOOTTIME131.041344651：Root角色0、UID999进程0、parent cgroup不存在；后续只读完整导出再次确认。systemd瞬时show在较晚查询显示inactive/dead与success，原journal中实际125和failed记录保持，判定优先保留该次退出原始见证。

[首次进程审计](evidence/CLOSURE_AUDIT.json) · [导出审计](evidence/POSTRUN_AUDIT.json) · [journal消息索引](evidence/JOURNAL_MESSAGE_INDEX.json) · [自动关闭原件汇总](evidence/ACTUAL_RESULTS.json)
''')
write('PTA_SEALING_RESULTS.md','原生seal、自动收尾与行政封存','''
**真实native ZIP已生成并通过44项逐流校验；冻结host自动行政收尾失败。本轮研究证据包另行行政封存，自动性质保留失败。**

|路径|实际裁决|
|---|---|
|原生seal|NATIVE_SEAL_COMPLETED：真实运行对象齐备，自动原生包44项manifest/45 ZIP entries，CRC/逐流SHA/当前原件均匹配|
|较早原生适用性记录|pt_seal_disposition在67.175611912记NATIVE_SEAL_UNRESOLVED/T0=UNRESOLVED，属于当时关闭仍UNKNOWN的原始分类，原件保持|
|后续native manifest|sample67.382156380；此时最终内部关闭记录67.371083714已confirmed；原生包SHA见下表|
|host自动post-exit|确实调用1次，0.222965900秒返回1，顶层import boot_continuity触发ModuleNotFoundError|
|自动行政状态|原STARTUP_FINALIZATION.json保持ADMIN_EVIDENCE_UNRESOLVED、NATIVE_SEAL_UNRESOLVED；没有startup_snapshot/自动行政manifest/ZIP|
|研究行政收尾|在只读角色空审计后导出46 native原件、51冻结文件，连同原始双流、journal、授权、报告另建PTA_EVIDENCE.zip；分类为显式行政保存|

原生ZIP SHA-256：`16d0fc022ec9cdfb293ce8d44046e7124059589699a1bd31d58eb958a69e6f72`，89,300字节。[独立文件完整性校验](evidence/NATIVE_SEAL_VERIFICATION.json)仅读取原包，生产checker/测试/oracle重跑0。native成功仅表达对应快照的产物完整性，host失败与全链验收缺口继续保留。

自动host记录active返回UTC10:19:59.307345，post触发10:19:59.327527。独立停止服务退出由guest journal在67.405716记录；guest UTC标记约10:19:59.412522。两侧时钟关系缺少专用校准，避免把它们相减作为精确退出后延迟。因果上host只等待active入口结束，停止服务为独立systemd服务；完成屏障应以实际受控角色审计及有界收敛为依据。

本次自动收尾在导入阶段失败，行政文件/manifest落盘时间均为null，收尾退出码1；未手工重放该命令或调用finalize。直接脚本使用`-I -S -B`，sys.path缺少同目录兄弟模块路径，startup_lifecycle.py:11的顶层import失败。下一静态修复须保持原隔离参数和摘要验证，并审查独立服务的退出屏障。

原MRA的NATIVE_SEAL_FAILED、退出125、内部UNKNOWN及行政归档结果完整保留；本批的completed状态只属于batch11。

[自动原始结果](evidence/STARTUP_FINALIZATION.json) · [自动stderr](evidence/STARTUP_POSTEXIT.stderr.raw) · [原生核验](evidence/NATIVE_SEAL_VERIFICATION.json)
''')
write('PTA_REGRESSION_RESULTS.md','PT64与九项变异实际结果','''
**实际执行0/64、接受0/64；变异触发0/9、检出0/9。** C00开始前收到真实STOP，冻结首失败规则已阻断后续资格。

|冻结项目|计划数|实际执行/接受|
|---|---:|---|
|safe夹具|55|0/0，UNRUN_BEFORE_C00|
|mutant夹具|9|0/0，NOT_EXERCISED|
|全部PT64|64|0/0，UNRUN_BEFORE_C00|
|独立oracle|64项原始trace重审|调用0；没有pt_case原件或PT_QUALIFICATION|
|真实C00|1|UNRUN_BEFORE_DISPATCH；ticket/worker/ready原件均无|

九项变异force_runtime_pre、delete_pre_validation、missing_checkpoint_pass、no_auto_stop、missing_deadline、unknown_as_success、admin_as_native、new_budget_after_fail、reactivate_closed均记NOT_EXERCISED。MUTATION_NOT_DETECTED适用于已触发且漏检情形，本批未到达该条件。

现有PT64实现声明origin=PT-SIMULATION/1，在真实C00后同账执行。即使未来全部通过，它也只能证明对应合成状态/事件模型与独立oracle的有限一致性；真实Root/Launcher/fsync/期限/自动post仍需各自进程证据。本批既未运行这些合成夹具，也未运行PREWINDOW_ABORT。

没有将35份语法通过记成测试通过，没有将实际phase序列代入PT64重放，也未在预算窗口外调用独立oracle补结果。

[计划输入原件](evidence/FROZEN_SOURCE_REFERENCE/inputs/startup_contract.json) · [实际数量](evidence/ACTUAL_RESULTS.json)
''')
write('PTA_RESOURCE_ACCOUNTING.md','实际资源与合同边界','''
**本批真实创建预算账，最终R=0；完整资源资格仍未取得。** 这里的0来自BRNGv001原件，和历史MRA的未初始化null分别保留。

|指标|实际观测/边界|
|---|---|
|T0/deadline/stop_at|66.896850269 / 1866.896850269 / 1806.896850269|
|counter|24字节，BRNGv001，used0，cap1,000,000；COMMITTED after0|
|journal|文件尚未创建；实际reserve事务0。关闭预算快照将缺journal记UNKNOWN，原字段保持|
|阶段A访问|实际0；计划正常完成1,090，硬界1,537；专项1,089/1,536均为计划界|
|完整校准访问|65,618硬界保持，当前完整校准UNRUN|
|active host时间|1.918233000秒，仅active WSL；含host启动及自动post总2.438853600秒|
|T0到首STOP|0.224342140秒|
|T0到CLOSED|0.242512293秒|
|T0到child waitpid|0.329197521秒|
|T0到最终内部cleanup采样|0.474233445秒|
|启动TCB|原起点65.510243359、deadline185.510243359；过期故障未测|
|父Payload slice|TasksMax4、MemoryMax4GiB；观察pids.current0、memory.current0、memory.peak0，cgroup populated0|
|单进程RLIMIT_AS|冻结Native预检和独立停止器设置1GiB；实际Payload未启动，无Payload工作进程限额样本|
|Root RSS及全树任务峰值|未采集精确高水位，null；三个已登记Root角色存在并行区间，最大3为结构推断，上限观察不替代全树测量|
|自动post上界|原alarm30秒/host等待35秒保持；实际0.222965900秒导入失败|

Payload空slice的内存0不代表Root、WSL或主机内存0。Root角色在父Payload slice外，其RSS和全任务峰值资料缺失。没有OOM或任务工作量校准证据，完整300秒链时间仍TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。

主机侧检查、部署及只读导出均为授权行政工作；未计为模型访问。原1,000,000/1,800/校准100,000与300/提前1,740/AS1GiB/父4tasks保持，没有第二T0/退款/预算重置。

[原始实际账与资源](evidence/ACTUAL_RESULTS.json) · [停止快照](evidence/CLOSURE_AUDIT.json) · [源锁核验](evidence/SOURCE_AFTER_CHECK.json)
''')
rows=[]
for r in json.loads((E/'EXECUTION_TIMELINE.json').read_bytes())['events']:
    rows.append('|'+r['event']+'|'+format(r['time'],'.9f')+'|'+format(r['T0_offset'],'.9f')+'|')
write('PTA_EXECUTION_TIMELINE.md','执行、异常与关闭时间线','''
以下数值为同boot CLOCK_BOOTTIME及其相对真实T0差值。原生事件sample标记采样时点；精确IO返回和内核退出时刻按缺口保留。

|事件|BOOTTIME秒|T0偏移秒|
|---|---:|---:|
'''+ '\n'.join(rows)+'''

系统journal另用MONOTONIC：停止服务开始66.952658、启动完成66.953482、traceback输出67.396063、错误消息67.397984、systemd退出125见证67.405716。异常打印发生在清理之后，不能将打印时间作为首次抛错时刻。

host active起止UTC10:19:57.389168–10:19:59.307345；post触发10:19:59.327527；post耗时0.222965900秒/exit1；外层全部返回10:19:59.581831。guest/host UTC只作原始观察，精确跨时钟时间差保持未测。

首次独立审计BOOTTIME131.041344651，角色空/父组不存在；这给出事后确认时点，实际退出时间另由waitpid与systemd见证限定。人工cleanup0、测试重跑0。

[完整JSON时间线](evidence/EXECUTION_TIMELINE.json) · [journal摘录](evidence/JOURNAL_MESSAGE_INDEX.json) · [原始stdout](evidence/windows_entry.stdout.raw)
''')
write('PTA_COUNTEREXAMPLES.md','本批反例与证据边界','''
**首次因果错误来自运行态phase发布/读取竞态；独立的自动post导入缺陷随后阻断行政收尾。**

|编号|原始证据|裁决|
|---|---|---|
|PTA-RACE-1|停止服务892的journal栈：guard.py:777→c09_handoff.py:207→guard.py:138→startup_lifecycle.py:184，PT_RUNTIME_PHASE_DRIFT；STOP67.121192409|真实并发接线缺陷。私有phase与公开checkpoint由两次持久发布形成，reader逐次读取后要求相等，存在合法过渡被拒绝的调度|
|PTA-STOP-LATCH-2|STOP reason=C09_OR_SUPERVISOR_FAILURE；mr_first_failure先由887锁存LAUNCHER_ERROR/IPC_STOP_REQUEST_DOMINATES|因果触发和首个持久错误槽位分开记录。原槽位字节保持，journal补足因果来源；首次异常精确抛出时刻缺少独立打点|
|PTA-POST-3|冻结只读post命令exit1，startup_lifecycle.py:11 import boot_continuity失败|直接以-I脚本执行时兄弟模块未进入sys.path。host正常入口导入路径与该直接命令不同，静态compile没有覆盖模块装载|
|PTA-QUIESCENCE-4|active入口先返回，独立systemd停止服务仍有后续journal退出见证|自动finalizer应使用真实角色/写者收敛屏障。该批在顶层import处即失败，有界审计分支尚未运行|
|PTA-LABEL-5|摘要绑定的控制路径batch11-r5、正文r3及规则文字r1并存|路径标签一致性缺口；实际代码/JSON/执行锁和运行batch11互相一致，按冻结原件执行，未绑定旧batch10|

RACE精确读取快照未被记录，以下是与原件一致的最小调度：reader取旧READY公开点→writer持久化ARMED私有phase→reader比较新phase而拒绝→writer发布ARMED公开点。最终phase链与公开点均ARMED、intent hash一致，为过渡竞态解释提供支持；具体调度保持推断，后续静态方案需构造可控复现验收。

本轮源码、判据、预算、C09交接和RootIPC语义保持。上述均属于通用验证基础设施缺陷，没有提出新的D1/D2候选机制或原创性分离声明。历史MRA预窗IPC_STATE_MISSING/native失败与CalDiag真实C09证据继续冻结。

[错误与关闭原件](evidence/ACTUAL_RESULTS.json) · [停止服务journal](evidence/JOURNAL_MESSAGE_INDEX.json) · [自动post stderr](evidence/STARTUP_POSTEXIT.stderr.raw) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)
''')
write('PTA_FINAL_DECISION.md','阶段A最终裁决与十九项回答','''
**阶段A未取得完整动态验收：本批正常预窗及真实初始化推进到RUNTIME_ARMED，随后因PT_RUNTIME_PHASE_DRIFT自动关闭；PT64、九项变异及真实无T0异常路径均未执行。**

|最终问题|实际回答|
|---|---|
|1 是否真实启动|是；新batch11、真实预检/一次认领/same-PID exec/Root child，active入口1次、exit125|
|2 IPC_STATE_MISSING是否再现|本批未观察到；旧MRA失败原件保持|
|3 初始化前提|预窗认证通过；真实intent、state、counter和运行checkpoint按序创建，ARMED后并发一致性失败|
|4 预窗与运行点隔离|正向路径有实际证据；故障拒绝和全部回归覆盖仍缺|
|5 intent|真实exclusive创建，hash与公开initialization_id相符|
|6 armed/work|ARMED真实建立；C00前收到STOP，work/RUNNING0；完整守卫验收未完成|
|7 T0与账|真实T0=66.896850269，counter已建立、R=0、COMMITTED after0；没有重置|
|8 64项|执行0、接受0，UNRUN_BEFORE_C00|
|9 九项变异|触发0、检出0，全部NOT_EXERCISED|
|10 120秒期限|真实绑定原ticket/ctx；过期及无T0异常动态性质UNRUN|
|11 自动停止|实际运行态错误触发STOP/CLOSED，父stop成功，角色最终退出|
|12 外部兜底|额外兜底0、人工清理0；只读导出和行政打包单列|
|13 退出/组空|child直接waitpid125、Root角色退出观察、独立停止服务systemd退出125、停止结果及事后/proc/cgroup核验均保存|
|14 UNKNOWN|前两条关闭UNKNOWN保持；后续按冻结退出审查收敛CLOSED_CLEANUP_CONFIRMED；预算journal缺失UNKNOWN字段保持|
|15 两类封存|native实际包完整性NATIVE_SEAL_COMPLETED；冻结host自动post exit1，ADMIN_EVIDENCE_UNRESOLVED；本研究行政包独立封存|
|16 资源|R=0；active1.918233秒、全部host2.4388536秒；Payload空slice观测memory peak0/tasks0；Root RSS/全树精确峰值未测|
|17 阶段A完整通过|未取得；FIRST_UNEXPECTED_RUNTIME_ARMING_RACE，自动行政路径失败|
|18 恢复C09后MR条件|尚缺本轮缺陷静态修复、正常A/PT64及独立预窗中止证据、完整资格链与新授权|
|19 下一最小修复|phase/checkpoint提交读取一致性、隔离脚本入口导入、自动收尾有界退出屏障及标签/错误来源证据；先静态冻结后新身份授权|

native包44项/45entries校验成功只支持该包完整性；完整资源、全链性能、模型安全及原创性分别裁决。PREWINDOW_ABORT与正常模式互斥，本批已CLOSED且claim消耗，后续保持关闭。

原MRA启动前125/IPC_STATE_MISSING、无T0/R、内部UNKNOWN、native失败和行政归档继续保留；原CalDiag真实C09 PASS、194项/41变异及38,729账保持。r3源码和历史6,522份基线后续完整性核验见[交付核验](evidence/DELIVERY_CHECK.json)。

[首次反例](PTA_COUNTEREXAMPLES.md) · [封存细项](PTA_SEALING_RESULTS.md) · [资源](PTA_RESOURCE_ACCOUNTING.md) · [证据索引](EVIDENCE_INDEX.md) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)
''')
write('NEXT_STATIC_REPAIR_REQUEST.md','下一轮最小静态审查范围','''
当前为请求范围说明，本轮动态批次已经关闭，源码修复及新测试执行均为0。

1. 为phase与公开runtime checkpoint定义可审查的提交、读取与版本一致性合同，构造READY→ARMED及ARMED→RUNNING的reader/writer交错；真实缺点、破损、身份失配和终态守卫继续严格拒绝。
2. 审查冻结post-exit实际`-I -S -B`入口的模块装载路径，保留精确源目录和摘要校验。将“语法可编译”与“精确隔离入口可装载”分别验证；动态测试须下一独立许可。
3. 自动post审计等待真实受控角色/写者收敛时使用原合同的剩余期限及更小行政上界，保留DEFERRED/UNKNOWN，控制导出上限；active调用返回与全部systemd角色退出分别见证。
4. 错误来源补足：保留冻结首错槽位，另外记录触发STOP的角色、原始异常及阶段，使后续的STOP拒绝与最初因果错误可同时审查。
5. 对齐r3版本、控制目录r5和残留r1说明，保持历史原文。若下一修复涉及身份/路径，采用新批次与新摘要，当前batch11维持CLOSED。
6. 保持预算核心、D1/D2、五份业务源、RootIPC权限/C09持久交接、资源限额及原MR审查边界；先提交最小静态差异、保护语义证明、回归清单和锁。

后续正常初始化/PT64与PREWINDOW_ABORT分别需要独立身份/授权，完成后再审查C09后MR及完整资源资格；当前授权不自动延伸。通用基础设施修复不构成原创候选机制实施，STRICT_SEPARATION_INSTANCES仍为0。
''')
write('COMMAND_SUMMARY.md','实际命令与分类','''
部署、平台审计、角色审计、完整原件导出共4次行政WSL调用，精确argv、前后时间、原始双流及SHA见[行政命令计划](evidence/ADMIN_COMMAND_PLAN.json)和evidence/commands/01–04.result.json。行政调用没有导入生产目标或重放checker。

active由冻结host entry执行一次，Native精确argv：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch11
```

冻结host自动post一次：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/startup_lifecycle.py --post-exit-export
```

前者exit125，后者exit1；源码修复/重跑/手工finalize/停止后备0。其余主机操作仅准备授权、hash/内存compile、保存原件、报告与归档。完整源码与运行副本分别保存在FROZEN_SOURCE_REFERENCE及独立batch11导出目录，摘要随包提供。
''')
write('EVIDENCE_INDEX.md','阶段A证据索引','''
|主题|工件|
|---|---|
|总裁决|[十九项回答](PTA_FINAL_DECISION.md)|
|授权/版本|[授权及锁](PTA_AUTHORIZATION_AND_LOCK.md)、[原文](evidence/TASK_REQUEST.txt)、[回执](evidence/execution_authorization.json)|
|实际机器结果|[ACTUAL_RESULTS](evidence/ACTUAL_RESULTS.json)、[源码前置](evidence/SOURCE_AND_SCOPE_ADMISSION.json)、[源码后核](evidence/SOURCE_AFTER_CHECK.json)|
|预检部署|[部署](evidence/DEPLOYMENT_RESULT.json)、[平台](evidence/ENVIRONMENT_AUDIT.json)|
|精确入口|[调用](evidence/ACTIVE_ENTRY_INVOCATION.json)、[外层返回](evidence/ACTIVE_ENTRY_RETURN.json)、[active返回](evidence/WINDOWS_ENTRY_EXIT.json)|
|原始双流|[stdout](evidence/windows_entry.stdout.raw)、[stderr](evidence/windows_entry.stderr.raw)、[journal](evidence/RUN_BOOT_JOURNAL.stdout.raw)|
|自动收尾|[计划](evidence/STARTUP_POSTEXIT_PLAN.json)、[结果](evidence/STARTUP_FINALIZATION.json)、[stderr](evidence/STARTUP_POSTEXIT.stderr.raw)|
|原生封存|[逐流核验](evidence/NATIVE_SEAL_VERIFICATION.json)|
|进程退出|[首次审计](evidence/CLOSURE_AUDIT.json)、[完整导出审计](evidence/POSTRUN_AUDIT.json)|
|原件路径/元数据|[46项Native导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[51项冻结源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)|
|时间/错误|[时间线](evidence/EXECUTION_TIMELINE.json)、[journal消息](evidence/JOURNAL_MESSAGE_INDEX.json)、[反例](PTA_COUNTEREXAMPLES.md)|
|历史/交付|[启动前基线](evidence/BASELINE_LOCK.json)、[旧归档](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

完整原生46项与冻结51项位于D:/毕业设计/DCL-R6-isolated-verification/batch11/native_snapshot及FROZEN_PT；研究最终ZIP同时纳入对应export/native与export/frozen成员，manifest按实际SHA绑定。能力nonce只在私有原件和归档中保留，报告不展开。
''')
write('README.md','DCL-R6-PreT0-A','''
**阶段A未完整通过。** 正常预窗初始化达到RUNTIME_ARMED；独立停止服务发生PT_RUNTIME_PHASE_DRIFT，自动STOP/CLOSED与回收成功，C00/PT64均未执行。原生seal包完整，冻结host自动行政收尾因隔离导入缺陷失败；本次行政证据单独保存。

[最终十九项回答](PTA_FINAL_DECISION.md) · [初始化](PTA_INITIALIZATION_RESULTS.md) · [检查点](PTA_CHECKPOINT_LIFECYCLE.md) · [预窗中止覆盖](PTA_PREWINDOW_ABORT_RESULTS.md) · [自动关闭](PTA_AUTOMATIC_CLOSURE_RESULTS.md) · [封存](PTA_SEALING_RESULTS.md) · [回归](PTA_REGRESSION_RESULTS.md) · [资源](PTA_RESOURCE_ACCOUNTING.md) · [时间线](PTA_EXECUTION_TIMELINE.md) · [反例](PTA_COUNTEREXAMPLES.md) · [授权](PTA_AUTHORIZATION_AND_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)
''')
# Root navigation is extended with an exact byte suffix of its pre-run original.
prefix=('## DCL-R6-PreT0-A 当前增量（2026-11-12）\n\n'
 '**阶段A未完整通过：batch11/r3正常初始化达到RUNTIME_ARMED，PT_RUNTIME_PHASE_DRIFT触发自动关闭；C00/PT64未执行。** '
 'T0/预算真实建立，R=0；角色与组空，额外兜底/人工清理0；native包44/45完整，host自动行政post因ModuleNotFoundError失败。'
 '内部早期UNKNOWN原件保留，最终关闭CLOSED_CLEANUP_CONFIRMED；本轮研究行政包单列。\n\n'
 '下一步限于phase/checkpoint一致性、隔离入口和有界收尾的最小静态审查；batch11保持关闭，后续新身份与动态许可单列。'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 '[最终裁决](DCL-R6-PreT0-A/PTA_FINAL_DECISION.md) · [反例](DCL-R6-PreT0-A/PTA_COUNTEREXAMPLES.md) · '
 '[证据索引](DCL-R6-PreT0-A/EVIDENCE_INDEX.md) · [下一静态范围](DCL-R6-PreT0-A/NEXT_STATIC_REPAIR_REQUEST.md)\n\n---\n\n')
for name in ['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']:
    original=(E/'navigation_before'/name).read_bytes();assert (B/name).read_bytes()==original
    (B/name).write_bytes(prefix.encode('utf-8')+original)
print(json.dumps({'required_reports':11,'markdown_files':len(list(O.glob('*.md'))),'navigation_extended':4},ensure_ascii=False))
