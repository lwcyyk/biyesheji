"""Administrative research reports; no target module imports or native calls."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
R=json.loads((E/'STATIC_RESULT.json').read_bytes())
passport='Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。'
gates='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。'
def report(name,title,body):
    with (O/name).open('x',encoding='utf-8') as f:f.write('# '+title+'\n\n'+passport+'\n\n'+body.strip()+'\n\n'+gates+'\n')
report('PHASE_DRIFT_ROOT_CAUSE.md','阶段漂移根因与证据强度','''
**源码中的跨文件一致性缺陷已由具体合法交错证明。历史抛错瞬间的操作数缺少记录，精确历史根因保留PT_RUNTIME_PHASE_DRIFT_ROOT_CAUSE_UNRESOLVED；PF-G1=PARTIAL。**

|必须恢复的字段|证据支持的结论|
|---|---|
|产生错误的函数|旧startup_lifecycle.runtime_checkpoint，第184行|
|失败调用链|Root停止服务892 → guard._external_stop_impl:777 → Receiver.poll:207 → G.root_checkpoint:138 → P.runtime_checkpoint:184|
|调用时阶段|正常初始化已推进到ARMED发布附近；精确读取瞬间阶段值UNKNOWN|
|检查器期望|条件要求sha(runtime intent)==q.initialization_id且私有phase.phase==q.phase；q读值未逐次记录|
|实际观测操作数|q.phase、当次private.phase及该次digest比较结果均UNKNOWN；组合OR异常没有区分分支|
|持久位置|inputs/root_private/boot/pt_phase.json、pt_events.jsonl；inputs/PT_RUNTIME_CHECKPOINT.json；pt_runtime_intent.json|
|更新者|Launcher child887/start6672，boot24fc4fce-f68c-4ab5-8662-261ed17d831b|
|核验者|独立停止服务892/start6693，同boot；其Receiver在没有收到C09请求时也轮询运行点|
|持久顺序|_set_phase持锁写events/私有phase并释放；之后单独读取/发布公开q；reader没有共同锁|
|运行对象一致性|最终原件T0=66.896850269、R=0、COMMITTED after0；公开/私有均ARMED、sequence5，intent digest匹配；这些是封存时快照|

源码反例输入是同批、同boot、同intent的READY→ARMED转换，调度如下：reader取公开READY/4；writer持久化私有ARMED/5；reader比较旧q与新私有phase并抛错；writer发布公开ARMED/5。所有写入都遵守旧状态机。此四步是SOURCE_SCHEDULE_WITNESS_ONLY，本轮没有执行重放。它证明旧程序存在合法转换被错误拒绝的输入调度。

|情况|裁决|
|---|---|
|A 合法转换未完成|源码顺序允许；原始记录与此相容，精确发生情况UNKNOWN|
|B 跨时刻拼接/旧快照|源码确定存在该读取风险；历史精确交错UNKNOWN|
|C 真实非法转换|持久phase链未显示回退或跳转；历史瞬时损坏或组合条件另一分支缺少排除证据|

本轮修复已证明存在的源码一致性缺口，并为新版本异常增加公开/私有phase、sequence及digest比较布尔值，供下一批定位。保持旧首错槽位和旧报告原文；本轮对证据强度的精化单独登记。

[恢复事实和原件SHA](evidence/HISTORICAL_FAILURE_FACTS.json) · [源码diff](evidence/FULL_DIFF.patch) · [时间线](PHASE_TRANSITION_TIMELINE.md)
''')
report('PHASE_TRANSITION_TIMELINE.md','阶段转换与真实失败时间线','''
真实状态机继续采用七个原阶段：PRE_WINDOW → PREFLIGHT_VALIDATING → PREFLIGHT_QUALIFIED → RUNTIME_INITIALIZING → RUNTIME_READY → RUNTIME_ARMED → RUNNING。INITIALIZATION_INTENT是持久对象，WORK是受守卫的动作；本轮未另造WORK_ENABLED状态。

|转换|前提/主体|持久动作、版本及读取|失败行为|
|---|---|---|---|
|初始→PRE_WINDOW|活体sealed/claim、Owner/child正确；初始Root child|exclusive ctx；phase/events seq0|异常经原wrapper自动abort，保留无T0状态|
|→VALIDATING|专用认证预窗scope|私有phase seq1、previous SHA；manager只读预窗查询|失败停止，不取得运行资格|
|→QUALIFIED|真实health与身份通过|私有phase seq2|停止/期限优先|
|→INITIALIZING|新实例、无运行对象；单次初始化|exclusive runtime intent先持久化，phase seq3|部分对象保留，原claim消耗，拒绝回退|
|→READY|真实state/counter/COMMITTED intent完成|同一phase_guard内发布私有seq4与Root公开checkpoint/record digest|IO或发布中断后保留不一致原件并拒绝工作|
|→ARMED|原停止器活体、boot/stop_at匹配、原父资源检查；当前scheduler|同锁校验旧READY，私有seq5及公开q一起完成后解锁|超时/非法阶段/终态失败即abort|
|→RUNNING（WORK）|当前scheduler；q确为ARMED；原C00/后继资格仍各自要求|require_work同锁校验并发布seq6；成功返回后原launch_one继续|READY/未知点/损坏/关闭均拒绝发放|

每个阶段记录的序号等于状态机中的固定索引；Root校验公开phase/seq、私有phase/seq、phase记录SHA及初始化ID。发布者与Root读取者使用同一把Root私有锁，读方在锁外等待时不拼接检查点。

历史batch11的实际BOOTTIME：PRE_WINDOW66.811319376；VALIDATING66.820658042；QUALIFIED66.874374079；intent sample66.885179620；INITIALIZING66.888638365；T0=66.896850269；READY66.914956317；私有ARMED67.109909234；公开armed checkpoint sample67.118473361；STOP67.121192409；CLOSED67.139362562；child waitpid125在67.226047790；最终内部关闭confirmed67.371083714；native manifest67.382156380。

停止服务异常在清理后输出到journal，MONOTONIC67.397984出现PT_RUNTIME_PHASE_DRIFT、67.405716为systemd退出125见证。打印时间和精确抛错时刻分别保留。新版本全部上述转换和并发调度实际UNRUN。

[历史原始phase链](evidence/PTA_ORIGINALS/native/inputs/root_private/boot/pt_events.jsonl) · [持久点](evidence/PTA_ORIGINALS/native/inputs/PT_RUNTIME_CHECKPOINT.json) · [原始journal](evidence/PTA_ORIGINALS/host/RUN_BOOT_JOURNAL.stdout.raw)
''')
report('PHASE_CONSISTENCY_CONTRACT.md','阶段一致性合同','''
**Root的phase读取和成对发布共享原pt_phase.lock，只有完整、匹配且可用的运行检查点允许后续动作。**

锁限定Root当前批次的root_private/boot；文件仍为Root:Root/0600，无ACL或UID权限扩展。获取使用非阻塞flock，最多512次尝试，截止取now+2秒与已有预窗/运行期限的较小值。每轮先查STOP/CLOSED和期限，只有锁竞争时进行短轮询。sleep没有提供任何状态有效性证据。

Root持锁后校验当前身份、window、counter不可变身份、初始化ID、phase、sequence及phase_record_sha256。writer仅在同一临界区内依序持久化phase/events与公开q，完成原RootIPC文件/目录同步后释放锁。Root reader使用同一锁覆盖两份记录的读取和比较。稳定失配、缺件和IO错误立即拒绝；writer中途失败留下的部分提交不会被读方补写或猜测修复。

线性化依据为公开Root记录完成发布并在临界区结束后可供Root读方验证。phase与q之间的暂态只有writer持锁期间可出现，其他Root读方等待获取该锁。进程崩溃后若文件留下稳定失配，后续校验拒绝并交给原关闭路径。kernel flock、原子rename、fsync、受信存储与正常返回/调度属于明确环境前提，未获得实时系统证明。

Payload继续只读Root:989/0640的原子公开点，验证固定phase/seq、身份/window/counter及committed字段，保留运行检查点缺失拒绝。Payload没有Root锁或私有目录权限，阶段更新仅由当前Root scheduler完成；首个工作服务在Root require_work成功、提交完成之后启动。CLOSED/STOP仍由原RootIPC检查和新守卫支配，ARMED不替代C00、S套件或资源资格。

2秒限定的是锁重试/许可时段，消耗同一运行墙钟；发生阻塞IO或不可调度时仍依赖原停止TCB与环境响应假设。全链300秒性能及真实锁等待、IO中断和调度均待动态核验。终态只读seal适用性检查使用显式terminal_inspection，保留阶段完整性核验；它没有工作发放动作。

[实现](evidence/SOURCE_FINAL_R3/src/startup_lifecycle.py) · [28项静态检查](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)
''')
report('ADMIN_FINALIZER_IMPORT_ROOT_CAUSE.md','自动行政入口导入根因','''
**历史异常为ModuleNotFoundError: No module named 'boot_continuity'。旧锁直接以-I脚本运行startup_lifecycle.py，其第11行在设置同目录模块路径前执行绝对导入。**

历史精确argv：`C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/startup_lifecycle.py --post-exit-export`。入口文件和boot_continuity.py均在49文件部署快照中，解释器为合同绑定的CPython3.12.3，调用身份由--user root指定。traceback没有权限错误；post执行前的实际cwd和sys.path完整快照均UNKNOWN。

CPython隔离参数-I排除脚本目录/当前目录及用户环境路径。旧脚本在绝对import boot_continuity时尚无对应sys.path插入，导致源文件存在仍无法解析。boot_continuity自身虽然有固定SOURCE引导，导入解析失败使其代码尚未执行；host正常入口先放入src路径的方式没有覆盖该直接Native脚本路径。旧compile只验证文法，无法检出这一导入阶段错误。

该布局原本由平铺src模块组成，没有包__init__.py。改为-m需要稳定可发现包或额外路径配置；本轮采用独立stdlib引导文件admin_postexit.py，保持-I -S -B与平铺部署结构，校验固定Root源目录/文件及摘要后加载兄弟模块，并检查真实模块origin。生产入口不依赖PYTHONPATH、cwd或systemd WorkingDirectory；Native post是host发起的独立WSL调用，未使用业务服务的Environment。

最终r3主机受控探针5项：两种cwd的惰性入口装载、固定可信兄弟stub优先于cwd诱饵、主机身份拒绝、缺模块错误传播。三个候选累计15项受控探针，均未调用入口main或真实生命周期模块。它们仅是主机环境证据；原生3.12装载、Root元数据和实际post调用仍UNRUN。

[历史stderr原件](evidence/PTA_ORIGINALS/host/STARTUP_POSTEXIT.stderr.raw) · [379项起的导入关系清单](evidence/IMPORT_GRAPH.json) · [最终受控导入结果](evidence/CONTROLLED_IMPORT_RESULTS.json)
''')
report('ADMIN_FINALIZER_EXECUTION_CONTRACT.md','自动行政收尾执行与权限合同','''
可信执行者为冻结Windows入口及其finalizer、Ubuntu-24.04下Root行政Python进程。新Native命令精确绑定为：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pf01/src/admin_postexit.py --post-exit-export
```

|范围|允许行为|
|---|---|
|固定pf01源/输入|Root受信元数据/摘要/解释器核验后只读；module origin必须为该src|
|当前batch12|只读当前state/counter、Root私有记录、native ZIP/manifest和已存在日志|
|进入私有审计前|runtime回执必须与当前control回执同SHA；activation的boot/批次/源/执行锁/回执绑定一致；错配即拒绝导出|
|角色/组|读取/proc、当前父cgroup与已登记Owner/child/停止器PID/starttime/boot；空cmdline仍由已登记身份核验；错误保留UNKNOWN|
|可写位置|本批固定control下独立STARTUP_NATIVE_AUDIT、startup_snapshot、post计划/双流/错误/manifest/ZIP与host结果|
|历史批次/原账|不写入、不重置、不恢复；实例固定为batch12，错配记录原样保留|

主入口在源摘要读取和目标模块装载前设置AS硬界1GiB及唯一30秒alarm，记录原行政deadline；export继承剩余时间并核验timer/AS，避免重新开始30秒。独立角色收敛等待最多5秒/128次采样，且受原行政deadline、已有预窗120秒或运行deadline剩余值进一步限制。此过程不延长业务/校准/启动窗口。

host对post正常wait使用32秒，超时后仅终止并尝试在总35秒剩余内回收该WSL客户端，记录客户端是否reaped。Root行政进程的30秒alarm、主机调用/存储/调度延迟与客户端到Native退出的对应关系仍需Native证据；这些界不构成Windows/WSL实时调度保证。

实际T0/预算存在则读取，缺失继续null，部分对象保持UNRESOLVED。native ZIP流验证成功记COMPLETED，真实seal error记FAILED，其余保留UNRESOLVED或纯预窗NOT_APPLICABLE。该状态先落盘为单独行政audit；后续导出失败时host仍可保存这份有当前回执绑定的native事实。

native完成后仍生成独立行政快照和host行政ZIP，包含原始错误、双流、回执、退出、native包与manifest。复制上限256文件/32MiB；host再核数量/字节/相对路径与SHA。权限/模块/IO失败经独立FAILURE或FINALIZATION_ERROR保留；重复收尾只验证并返回已有manifest/ZIP事实，不创建新的运行资格或覆盖原生结果。

适用表：无T0、已有T0、native成功/失败/未知、内部UNKNOWN、Root正常/异常退出、业务服务结束、CLOSED均有只读分支。仍有角色/组或读取错误则DEFERRED/CLEANUP_UNKNOWN。当前默认ACL、真实回收延迟、原生AS及所有条件的实际IO行为均待下一动态验收。

[新入口](evidence/SOURCE_FINAL_R3/src/admin_postexit.py) · [Native导出](evidence/SOURCE_FINAL_R3/src/startup_lifecycle.py) · [host收尾](evidence/SOURCE_FINAL_R3/host/startup_finalize.py)
''')
report('AUTOMATIC_SHUTDOWN_AUDIT.md','PF-1至PF-10安全性质与关闭审查','''
|性质|源码/字段与静态断言|证据范围|
|---|---|---|
|PF-1 PhaseMonotonicity|_set_phase_locked；PHASES、sequence、previous_sha256；固定seq索引和相邻转换检查|PASS_STATIC，Native转换UNRUN|
|PF-2 RuntimeIdentityConsistency|binding、window、initialization_id、counter身份；scheduler pid/starttime/boot；当前回执导出绑定|PASS_STATIC，真实跨进程检查待验|
|PF-3 NoPrematureWork|require_work只允许ARMED/RUNNING；当前scheduler；原launch_one/C00资格保持|PASS_STATIC，原守卫接线保留|
|PF-4 IllegalDriftRejected|同锁读取；phase/sequence/record SHA/初始化ID匹配；缺件和错误抛出|PASS_STATIC，真实损坏注入UNRUN|
|PF-5 BoundedPhaseTransition|原pt_phase.lock，512尝试/2秒及原期限取小；STOP/CLOSED每轮优先|CONDITIONAL_PASS，OS响应/性能待验|
|PF-6 AutomaticShutdown|新异常向原_launcher_body/launcher/外部停止wrapper传播，M.abort路径保持|PASS_STATIC，新增错误真实关闭UNRUN|
|PF-7 NoFalseCleanupSuccess|角色/组、internal_status、native、admin四轴；进程组空不覆盖内部UNKNOWN|PASS_STATIC，部分身份未知时拒绝确认|
|PF-8 AdministrativeFinalization|固定Root源引导、隔离argv、模块origin；主机受控装载5项|CONDITIONAL_PASS，Native导入与IO待验|
|PF-9 EvidenceIntegrity|post仅写当前control；原生对象只读；回执/boot绑定、manifest/ZIP双重SHA|PASS_STATIC，源/历史摘要另核|
|PF-10 NoReactivation|原claim/exclusive intent/T0/counter核心保持；CLOSED/STOP支配及writer身份|PASS_STATIC，回归实际UNRUN|

原guard的_launcher_body、协调器、external_stop异常路径维持M.abort，停止、回收及seal调用不更换。新增PF48缺件、未检出或越界时抛关键错误并进入同一wrapper。新增锁在异常中finally解锁，IO部分发布保持原件；稳定非法状态获得锁后立即拒绝。terminal_inspection仅用于关闭后只读适用性审查，没有工作发放能力。

历史batch11确实自动STOP/CLOSED、child waitpid125、父stop_exit0及角色/组空，额外兜底0；早期内部UNKNOWN原件保留，后续按冻结角色证据收敛。该事实作为历史记录，无法直接给新版本动态PASS。旧native封存成功44/45及自动post失败均保持。

[静态断言及源码行](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json) · [13文件/57成员保持](evidence/PROTECTED_SEMANTICS_CHECK.json) · [补充身份审查](evidence/FINAL_REVIEW_SUPPLEMENT.json)
''')
report('PHASE_FINALIZER_FIX_IMPLEMENTATION.md','有限修复实现与差异说明','''
**最终冻结r3：55份文件、38份程序；新增3份Linux程序及1份输入。** 新程序为admin_postexit、phase_finalizer_regression及其独立oracle。所有新实现均在独立pf01，原pt01和batch11保持原样。

|变更位置|理由与行为|
|---|---|
|startup_lifecycle|同一Root锁覆盖phase写入/公开点发布和Root读取；加入seq/record digest与具体异常操作数；WORK身份检查；终态只读seal分支|
|admin_postexit（新增）|stdlib bootstrap；先设置单次行政AS/时间界，再验证固定源/摘要并载入模块，保持-I -S -B|
|Native post|当前回执/activation/boot绑定；已登记角色核验与有界收敛；native结果先单独保存；native完成也独立行政归档|
|host/startup_finalize|原始双流结束后审计/打包；失败独立记录；保持已审查native状态；重复包/manifest和路径/字节界核验|
|host/windows_entry、boot_continuity、guard授权接口|绑定新增测试合同及显式PF批准位；入口/预检在发放前拒绝缺授权|
|guard C00分支|原PT64之后同步执行PF48，然后按最小A关闭；不进入MR/C09或模型|
|phase_finalizer_regression/oracle/contract|48项（40safe＋8mutant），同一原预算计费；oracle独立分类实际差异，再检查声明的预期违规和伴随集合|
|部署/输入/执行锁|新pf01/batch12-r3身份、53项Linux部署、精确新入口、摘要DAG与访问硬界；执行计划元数据对齐实际顺序|

13份关键程序逐字节相同，包括五业务、预算range_core、probe、S驱动、runner、C00Ready、C09、MR驱动/oracle。57项原预算/Boot/门18/MR/RootIPC/C09成员AST在必要namespace归一后保持；整个RootIPC AST另核一致。原slice文件字节相同，UID/GID/ACL语义、sealed、一次认领、MR管理审查和C09持久ACK语义保持。

r1候选与r2候选的完整源码/锁/检查结果均保留。r2补齐当前回执和已登记角色绑定；最终r3将1GiB/单次30秒行政界移至bootstrap之前，并继承剩余期限。最终r3是唯一下一申请目标，候选版本均无动态执行。

[全部源码路径/前后SHA](evidence/FILE_DIFF_INDEX.json) · [完整diff](evidence/FULL_DIFF.patch) · [版本记录](evidence/REVISION_LOG.json) · [最终55项锁](evidence/STATIC_WORKSPACE_LOCK.json)
''')
report('REGRESSION_AND_MUTATION_PLAN.md','静态回归、PF48与变异计划','''
**原PT64/9mutant输入jobs保持；新增PF48/8mutant，全部实际UNRUN。** 独立oracle没有导入生产lifecycle、subject、guard或预算核心，按原始input/trace/binding/SHA重算差异类别。

|集合|内容|本轮检查范围|
|---|---|---|
|原PT64|55safe＋9mutant，原jobs相同，历史原件保留|输入等价与源保持；实际执行0|
|PF基础32|14 phase、12 admin、6 closure；含合法WORK、锁竞争/延迟观测、旧版本/跨批/回退/终态/非法阶段、导入/身份/无T0/native/UNKNOWN/权限/异常/重复及关闭分轴|schema、最多4帧、唯一ID、调用接线及静态路径审查|
|8组配对|每组同输入safe/mutant，各16项；总PF48＝40safe＋8mutant|输入配对与违规集合一致性静态审查|
|导入探针|最终5项，三个候选累计15项；惰性入口及可信stub，非默认cwd和错误传播|PASS_HOST_CONTROLLED；真实生命周期导入0|

八项变异：放行非法阶段（ILLEGAL_PHASE_ACCEPTED）、跳过WORK（PREMATURE_WORK）、旧快照（STALE_SNAPSHOT_ACCEPTED）、忽略版本（VERSION_MISMATCH_ACCEPTED）、不触发关闭（NO_AUTO_STOP）、吞导入错误（IMPORT_ERROR_SWALLOWED）、覆盖native（NATIVE_RESULT_OVERWRITTEN）、关闭后重入（REACTIVATION）。前四项允许与放行相伴的NO_AUTO_STOP，其余意外违规均拒绝接受。oracle先独立分类观测差异，再比对目标与允许集合，源码构造不会预填实际检出结果。

未来每job先预付16次，再持久化真实模型trace并由独立oracle重审；suite另有entry1和每job审查1。PF完成计费817，硬界1,152。首次缺件、错误safe、未检出或意外违规立即停止；原guard关闭链负责清理。没有窗口外重放checker或退费。

PF48的origin明确为PF-SIMULATION/1，只覆盖对应纯策略/合成观察轨迹。锁竞争/延迟帧表达观察合同，尚不等同于真实flock/fsync调度注入；admin导入失败帧也不等同于真实Root模块失败。实际锁、进程、文件权限、自动停止/导出/归档及无T0终止必须分别取得Native证据。下一正常A只覆盖真实正向最小链；独立真实预窗中止仍需新身份和授权。

[PF48输入](evidence/SOURCE_FINAL_R3/inputs/phase_finalizer_contract.json) · [独立oracle](evidence/SOURCE_FINAL_R3/src/phase_finalizer_oracle.py) · [静态变异矩阵](evidence/FIXTURE_ORACLE_STATIC_CHECK.json)
''')
report('STATIC_VERIFICATION_RESULTS.md','静态验证结果与动态缺口','''
|核验|结果|
|---|---|
|55项冻结源码/输入|最终摘要DAG完整；36 Linux程序＋2 host程序＋17输入；未来Linux53项|
|38程序文法/compile|PASS_STATIC；主机CPython3.14执行AST/内存compile，3.12文法解析；目标角色执行0|
|控制流/生命周期|28项AST断言，Root发布/读锁、顺序/身份/WORK、终态/异常传播和入口均通过|
|实际导入关系|完整AST边清单；本地模块均部署，其他为stdlib；受控入口5项通过，原生3.12导入UNRUN|
|保护语义|13文件字节保持、57成员归一AST保持、整个RootIPC归一AST相同；slice字节保持|
|原PT64与新增PF48|64jobs保持；48唯一ID/8mutant/固定帧界/独立参考及允许违规集合静态核验；实际套件/oracle执行0|
|资源|PF完成817/硬1152，正常A完成1907/硬2689，完整硬66770≤100000；全链时间UNRESOLVED|
|历史|预先锁6825份；原PTA/PreT0/MRA/Manager包逐流核验；旧native成功与旧post失败均保留|
|本轮Native动作|WSL0、服务/Launcher0、T0/R=null、正式授权回执0|

PF-G1=PARTIAL：源码交错缺陷有具体反例，历史精确读取值和OR分支继续UNKNOWN。PF-G2/3/4=CONDITIONAL_PASS：静态义务与主机探针满足相应范围，真实并发/模块/IO/退出/封存待动态。PF-G5=PASS_STATIC：最小申请、回归、访问界和锁齐备；不赋予动态执行资格。

静态验证器曾因历史审查标签boot/gate18/MR与文件名别名不同而读取boot.py失败，修正别名映射后完成检查；该过程没有导入或运行目标。受控导入使用单独保留的stub和cwd诱饵，入口main始终未调用。source-only目录无pyc。

[最终机器结果](evidence/STATIC_RESULT.json) · [静态断言](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json) · [导入探针](evidence/CONTROLLED_IMPORT_RESULTS.json) · [资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)
''')
report('SOURCE_AND_INPUT_LOCK.md','最终r3源码、输入与执行锁',f'''
最终版本：PTA-PhaseFinalizer-static-1/r3。主机工作区D:/毕业设计/DCL-R6-isolated-verification/pf01；静态副本evidence/SOURCE_FINAL_R3。规划Linux源/var/lib/dcl-r6/pf01，规划实例/var/lib/dcl-r6/batch12，slice=dclr6batch12.slice，未来control位于DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r3。

|对象|SHA-256|
|---|---|
|static_manifest.json|{R['manifest_sha256']}|
|execution_lock.json|{R['execution_lock_sha256']}|

55项＝36 Linux程序＋2 host程序＋17输入；Linux部署53项。输入摘要→manifest、source/host程序摘要→相应manifest/执行锁、manifest→execution_lock、回执最终绑定两锁与用户原文。原模板始终TEMPLATE_UNAPPROVED，所有批准位false，authorization_text_sha256=null；没有生成实际回执、Linux实例或运行账。

旧r3的控制路径batch11-r5/正文r3标签差异在新版本统一为batch12-r3；历史原文件保持。r1/r2候选、各自源码锁/结果和diff均保留，不作为下一入口。

13文件/57成员保护清单、55项精确字节/摘要和所有变更前后SHA分别见下列工件；当前新Linux平台、boot及Native程序装载仍需下一授权内fresh核验。历史boot24fc4fce…仅属于batch11，本轮不将其冒充新执行boot。

[最终55项锁](evidence/STATIC_WORKSPACE_LOCK.json) · [最终源manifest](evidence/SOURCE_FINAL_R3/inputs/static_manifest.json) · [实际argv锁](evidence/SOURCE_FINAL_R3/inputs/execution_lock.json) · [全部diff](evidence/FULL_DIFF.patch) · [未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)
''')
report('NEXT_DYNAMIC_AUTHORIZATION.md','下一独立有限动态验收申请',f'''
**REQUEST_ONLY；本轮动态授权0。** 唯一申请目标PTA-PhaseFinalizer-static-1/r3，55项/38程序，manifest `{R['manifest_sha256']}`，execution_lock `{R['execution_lock_sha256']}`。

规划batch12-r3、scope=PT_STARTUP_DIAGNOSTIC_ONLY、startup_probe_mode=NORMAL_START。预检fresh核当前3.12.3/boot/源与工具/Root元数据/UID/GID/cgroup/systemd/资源及实例全新；原batch11维持CLOSED。部署仅53项Linux源/输入，不包含host目录或pyc。

```text
python -X utf8 D:\\毕业设计\\DCL-R6-isolated-verification\\pf01\\host\\windows_entry.py --activate
```

环境PYTHONDONTWRITEBYTECODE=1。唯一active argv：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pf01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch12
```

真实顺序：独立预检/同PID sealed认领 → 认证预窗 → exclusive intent → 原T0/state/counter → READY一致点 → 停止器/父资源 → ARMED → require_work/RUNNING → 真实C00八字段 → 原PT64/9mutant → PF48/8mutant → 正常关闭/native seal → host自动新admin_postexit入口 → 有界角色/组/已登记身份审计 → 独立行政manifest/ZIP及SHA。

请求同时覆盖自动post只读调用，精确命令见[行政执行合同](ADMIN_FINALIZER_EXECUTION_CONTRACT.md)：Root行政主入口先AS1GiB/唯一30秒，5秒/128采样收敛，host wait32与剩余回收预算总35秒，最多256文件/32MiB。请求必要的冻结本批关闭后备，真实使用时单列并保留自动性质裁决；不允许将人工命令算自动成功。

访问界：PF817完成/1152硬；正常A1907完成/2689硬；含新增测试的完整校准硬66770。继续总1,000,000/1800秒、校准100,000/300秒、stop_at=T0+1740、原预T0 TCB120秒、AS1GiB/父TasksMax4。phase锁每次最多2秒/512尝试，取原剩余期限更小值，消耗同一墙钟，无第二T0或退费。

未来回执须绑定用户真实原文SHA、最终两锁、PF合同与显式PhaseFinalizer诊断批准位，原RootIPC/单会话/同父兼容字段按schema核齐；实际scope继续只覆盖本申请，Full/MR/预窗77注入位保持false。模板目前全部批准位false，当前control与实际回执尚未创建。

首次非预期关键失败停止资格发放，自动关闭、保存具体phase/seq/digest诊断及原始双流，必要后备如实登记，关闭封存；禁止现场修改、自动重跑、预算重置或下一批。实际prewindow失败、稳定非法漂移、native与admin封存分项裁决，UNKNOWN保留。

本申请不进入READY64/MR64、C01–C12/C09、S34、门18、F1/F4、F2/F3或主系统实施。独立真实PREWINDOW_ABORT和后续完整链须新身份/摘要/授权。即使最小A全部通过，完整资源资格仍NOT_OBTAINED。

[未批准回执模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json) · [执行锁原件](evidence/SOURCE_FINAL_R3/inputs/execution_lock.json)
''')
report('FINAL_DECISION.md','最终静态裁决','''
**已完成两个已观察缺陷的有限静态修复并冻结PTA-PhaseFinalizer-static-1/r3；全部新Native行为仍待独立授权。**

|验收门|结果|范围|
|---|---|---|
|PF-G1 阶段根因|PARTIAL|抛错位置/角色/组合条件和合法源码反例已定位；历史精确操作数继续UNKNOWN，保留PT_RUNTIME_PHASE_DRIFT_ROOT_CAUSE_UNRESOLVED|
|PF-G2 阶段一致性|CONDITIONAL_PASS|Root成对发布/读取同锁，seq/digest/writer/WORK/终态条件保留；OS并发与性能待验|
|PF-G3 行政收尾|CONDITIONAL_PASS|固定隔离入口、装载前资源界、当前回执/角色身份、独立native/admin保存及主机5探针齐备；Native导入/IO待验|
|PF-G4 自动关闭|CONDITIONAL_PASS|原M.abort/stop/reap/seal异常链保持；新错误及post退出条件未动态验收|
|PF-G5 执行准备|PASS_STATIC|55文件/38程序、PT64保持、PF48/8mutant、独立oracle、访问界及最小下一申请完整|

最终38程序语法及3.12文法/内存compile通过，28项静态断言、最终5项主机惰性/受控导入通过；三个候选累计15项主机探针。13关键文件字节及57成员AST保持，整个RootIPC归一AST和原slice字节保持。没有把静态构造或主机stub装载计为PT/PF动态结果。

本轮WSL、部署、Launcher/服务、真实预算、PT64、PF48、独立oracle及模型执行均0；本轮T0/R=null。55份最终源仅存在Windows工作区与静态交付副本。完整访问硬界66770≤100000，正常A硬2689；真实300秒全链时间继续UNRESOLVED。

历史batch11的native seal成功、R=0、早期UNKNOWN与后续关闭confirmed、自动post导入失败均保留；原MRA预T0失败与native失败、CalDiag真实C09及旧预算同样保留。旧报告较强的“竞态根因”表述未重写，本轮对原始操作数缺口作独立审计裁决。

下一步仅审阅[新的正常A申请](NEXT_DYNAMIC_AUTHORIZATION.md)。根因细化、锁/IO、模块装载、真实自动关闭及行政完整性都须按具体证据独立裁决。后续原生批次和完整资格链需要新的明确授权。

[根因](PHASE_DRIFT_ROOT_CAUSE.md) · [实现](PHASE_FINALIZER_FIX_IMPLEMENTATION.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('EVIDENCE_INDEX.md','研究证据索引','''
|主题|工件|
|---|---|
|总裁决|[FINAL_DECISION](FINAL_DECISION.md)、[机器结果](evidence/STATIC_RESULT.json)|
|授权/边界|[用户原文](evidence/TASK_REQUEST.txt)、[实施门边界](SCOPE_BOUNDARY.md)|
|历史真实事实|[原始错误字段](evidence/HISTORICAL_FAILURE_FACTS.json)、evidence/PTA_ORIGINALS下23份逐字节原件副本|
|旧归档|[逐流核验](evidence/HISTORICAL_ARCHIVE_CHECK.json)|
|源码历史|evidence/SOURCE_BEFORE、SOURCE_FINAL_R1/R2/R3；[修订记录](evidence/REVISION_LOG.json)|
|最终锁/差异|[55项锁](evidence/STATIC_WORKSPACE_LOCK.json)、[diff](evidence/FULL_DIFF.patch)、[前后SHA](evidence/FILE_DIFF_INDEX.json)|
|静态控制流|[语法/28断言/行号](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json)、[13文件/57成员](evidence/PROTECTED_SEMANTICS_CHECK.json)|
|导入|[AST关系图](evidence/IMPORT_GRAPH.json)、[最终受控探针](evidence/CONTROLLED_IMPORT_RESULTS.json)、[最终补充审查](evidence/FINAL_REVIEW_SUPPLEMENT.json)|
|回归/资源|[PF48/8静态矩阵](evidence/FIXTURE_ORACLE_STATIC_CHECK.json)、[资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)|
|下一授权|[未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)、[有限申请](NEXT_DYNAMIC_AUTHORIZATION.md)|
|历史/交付完整性|[基线](evidence/BASELINE_LOCK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[最终交付](evidence/DELIVERY_CHECK.json)|

版本r1/r2的锁/检查结果和探针保留在evidence/versions及各自controlled_import_probes目录。最终只使用SOURCE_FINAL_R3与当前STATIC_WORKSPACE_LOCK。正式控制目录尚未建立，全部执行模板未批准。
''')
report('README.md','DCL-R6-PTA-PhaseFinalizer-Fix','''
最终版本PTA-PhaseFinalizer-static-1/r3：阶段发布/读取共享有界Root锁；行政收尾改用受信固定源bootstrap，并在装载前建立单次资源界，保留native与行政状态。

源码交错缺陷已静态证明，历史精确读取值继续UNKNOWN；PF-G1=PARTIAL，G2–4=CONDITIONAL_PASS，G5=PASS_STATIC。本轮Native/套件/模型执行0，下一有限动态申请尚未批准。

[最终裁决](FINAL_DECISION.md) · [阶段根因](PHASE_DRIFT_ROOT_CAUSE.md) · [时间线](PHASE_TRANSITION_TIMELINE.md) · [一致性合同](PHASE_CONSISTENCY_CONTRACT.md) · [导入根因](ADMIN_FINALIZER_IMPORT_ROOT_CAUSE.md) · [行政合同](ADMIN_FINALIZER_EXECUTION_CONTRACT.md) · [关闭性质](AUTOMATIC_SHUTDOWN_AUDIT.md) · [实现](PHASE_FINALIZER_FIX_IMPLEMENTATION.md) · [回归计划](REGRESSION_AND_MUTATION_PLAN.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [下一申请](NEXT_DYNAMIC_AUTHORIZATION.md) · [证据索引](EVIDENCE_INDEX.md)
''')
print(json.dumps({'required_reports':12,'markdown_files':len(list(O.glob('*.md'))),'final_revision':R['version'],'native_runs':0},ensure_ascii=False))
