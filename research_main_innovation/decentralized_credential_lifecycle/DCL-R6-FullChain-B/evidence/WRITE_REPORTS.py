"""Administrative report generation; reads the static audit, executes no targets."""
from pathlib import Path
import hashlib
import json

P=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
O=P/'DCL-R6-FullChain-B'
E=O/'evidence'
def read(n):return json.loads((E/n).read_text(encoding='utf-8-sig'))
def put(n,s):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s.strip()+'\n')
decision=read('STATIC_DECISION.json')
bound=read('RESOURCE_BOUND_INDEPENDENT.json')
capacity=read('SEAL_CAPACITY_STATIC_WITNESS.json')
source=read('SOURCE_LOCK_VERIFICATION.json')
base=E/'FROZEN_RA_ORIGINALS'
passport='Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。'
common='本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。'
boundary='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。'
def doc(n,title,s):put(n,f'# {title}\n\n{passport}\n\n{s}\n\n{boundary}')

# Exhaustive static input register; timing fields remain null for unrun cases.
register=[]
for i in range(13):register.append({'suite':'C00_C12','case_id':f'C{i:02}','origin':'NATIVE_OS_PLANNED'})
contracts=[('PT64','startup_contract'),('PF48','phase_finalizer_contract'),('TR40','terminal_contract'),
 ('RA32','runtime_regression_contract'),('READY64','readiness_contract'),('MR64','manager_contract'),
 ('C09H34','c09_contract'),('ROOT_IPC56','root_ipc_contract'),('BC40','boot_contract'),('S34','safety_contract'),('LEDGER18_NESTED','ledger_gate_contract')]
for suite,name in contracts:
    cfg=json.loads((base/'inputs'/(name+'.json')).read_text(encoding='utf-8-sig'))
    for j in cfg['jobs']:
        register.append({'suite':suite,'case_id':j['case_id'],'mutant':j.get('mutant'),
                         'variant':j.get('variant'),'origin':'FROZEN_INPUT_PLANNED_ONLY'})
cfg=json.loads((base/'inputs/safety_contract.json').read_text())
for j in cfg['gate_negative_cases']:register.append({'suite':'GATE18','case_id':j['case_id'],'recipe':j['recipe'],'origin':'FROZEN_GATE_PLANNED_ONLY'})
for r in register:r.update(status='UNRUN_STATIC_ADMISSION',begin=None,end=None,elapsed=None,visits_delta=None,
                          fsync_seconds=None,wait_seconds=None,service_seconds=None,cleanup_seconds=None,
                          evidence_check_seconds=None,exit_status=None)
with (E/'PLANNED_CASE_REGISTER.json').open('x',encoding='utf-8') as f:json.dump({'scope':'Planning inventory only; nested LEDGER18 is inside GATE18, not extra independent gate cases','rows':register},f,ensure_ascii=False,indent=2)

doc('FULLCHAIN_AUTHORIZATION_AND_LOCK.md','授权与执行锁裁决',f'''
用户[本轮授权原文](evidence/TASK_REQUEST.txt)允许先审查完整链、再在条件满足时执行F1→F4，并要求关键静态冲突时停止。依据第三节的“若发现代码集成冲突或冻结版本不一致：BLOCKED_STATIC_ADMISSION”以及第一节必需执行清单条件，本轮执行静态拒绝。

|项目|实际结果|
|---|---|
|最新既有基线|RuntimeAdapt-static-1/r1；64/64文件匹配最终静态锁与SOURCE_FINAL_R1|
|程序|42 Linux程序＋2 host程序；44份通过3.12文法及主机内存compile；目标执行0|
|static_manifest SHA-256|`{source['manifest_sha256']}`|
|execution_lock SHA-256|`{source['execution_lock_sha256']}`|
|条件完整scope|CALIBRATE_S1S9_THEN_F1_F4|
|新运行批次/部署目录/动态收据/新执行锁|均未签发；静态冲突已先于身份发布被确认|
|本轮研究身份|DCL-R6-FullChain-B，仅静态证据归档身份|

原锁绑定batch14/ra01及其历史授权路径；历史批次保持CLOSED。新批次原本需要机械重绑定全部路径/单位/授权摘要，静态拒绝发生在该操作之前。原锁的当前授权文字“STATIC_ONLY”、诊断说明及旧65618说明值均作为既有材料保留，具体可达调用由源码核对。

{common}

[逐文件核验](evidence/SOURCE_LOCK_VERIFICATION.json) · [裁决机器记录](evidence/STATIC_DECISION.json)。''')

doc('FULLCHAIN_VERSION_INTEGRATION.md','完整版本集成与首次静态阻断','''
现有源码字节与最终锁一致。功能模块和调用关系已经接线；完整运行的输出规模与最小运行封存合同存在冲突。

|既有修复|当前实际文件及调用点|静态结论|
|---|---|---|
|BootContinuity|boot_continuity.entry→launcher；同Root父进程内部一次resume；guard_admission/child_admission/before_seal|已集成|
|RootIPC|guard.root_checkpoint→root_ipc.checkpoint；Root固定路径/权限/发布/等待|已集成；现绑定batch14|
|C09Fix|guard.launch_one(C09)→sender_prepare→真实exit23；协调者waitpid与交接验证|已集成|
|C00Ready|guard.launch_one(C00/C10)→service_readiness.wait_native与ticket_admit|已集成|
|ManagerRecovery r5|guard._launcher_work→prepay/MR64；恢复调用M.resume；M.formal_gate|已集成；原生异常诊断仅另一scope可达|
|PreT0 r3|P.enter→initial_query_scope/health→qualify→begin_runtime→runtime_ready→arm|已集成|
|PT/PF r3|startup_lifecycle阶段锁/检查点/post_exit_export；PF48|已集成；行政文件cap256与完整链冲突|
|TerminalRead r1|guard.seal→read_terminal_evidence(NATIVE_SEAL)；终态成员上限257|已集成；完整链成员规模冲突|
|RuntimeAdapt r1|manifest/prelaunch/postexec/own-map/native/admin检查；RA32|已集成；来源条件继续保留|
|B09 AdmissionFix r1|root_verify_safety→ledger_gate.require_current；门18→ledger异常聚合→独立oracle|已集成|

首次确认的阻断FC-S01：完整scope在C00后依次保存PT64/PF48/TR40/RA32/READY64/MR64的独立文件，共312个；startup_lifecycle.py:496–503遍历全部运行目录，256份上限在成功轨迹下必被越过。仅原始case文件就超出56份，辅助材料与后续测试尚未计入。

FC-S02：guard.py:1019–1026将上述全部原件放入native ZIP并添加manifest；最低313个成员。terminal_evidence.py:158要求成员≤257，最低超出56个。ZIP创建和终态独立接受是两个环节；本轮只证明后者与完整规模冲突，实际ZIP生成保持UNRUN。

FC-S03：完整scope缺少本次第7.4节要求的原生异常关闭验收路径。MR64通过进程内Subject改变布尔状态，其origin明确为MR-SIMULATION/1。原生fault78诊断受MR_RECOVERY_DIAGNOSTIC_ONLY分支限制，随后永久关闭，无法在同一完整scope内形成该项验收并继续S34/模型。

最小差异范围：完整链封存容量合同及其读取/导出守卫；原生异常路径的独立执行清单/计费/停止与验收边界。调整这些内容属于下一轮静态修复工作。本轮保留全部冻结字节，动态启动0。

[312条静态路径证据](evidence/SEAL_CAPACITY_STATIC_WITNESS.json) · [源码行摘录](evidence/SOURCE_EXCERPTS.json) · [原生覆盖分析](evidence/NATIVE_ANOMALY_COVERAGE.json)。''')

doc('FULLCHAIN_RUNTIME_AND_BOOT.md','运行时与启动代次边界',f'''
本轮停止于主机静态准入；当前Linux平台、boot_id、UID/GID和实际加载映射均为UNRUN_STATIC_ADMISSION。既有运行时锁得到字节核验，表中摘要为冻结期望，当前平台观测列保持空值。

|对象|冻结期望|本轮观测|
|---|---|---|
|GNU libc/Ubuntu包|2.39 / 2.39-0ubuntu8.12|UNRUN|
|Python|/usr/bin/python3.12；3.12.3；SHA e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f|UNRUN|
|loader SHA|5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f|UNRUN|
|libc SHA|755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a|UNRUN|
|libm SHA|5dcc4d25466e29ca390ed6fabb371c69b65dff6fa4e91c34561057a020d6994a|UNRUN|
|systemd/kernel|255.4-1ubuntu8.18 / 6.18.33.2-microsoft-standard-WSL2|UNRUN|
|Payload UID/GID/cgroup|999 /989 /v2；父TasksMax4|UNRUN|
|本轮boot_id/进程/单位|未创建运行实例|N/A|

继承来源裁决：Root/dpkg/keyring受信且执行中无并发特权更新；新8.12 .deb payload尚缺独立再提取。既有包目录/签名/索引及已观测maps只支持既有条件性来源结论。path→exec原子性和后续特权替换边界保持。本轮授权原文保存了“保留现有运行时来源的条件性证明”的要求；执行收据因静态拒绝保持未签发。

TR-A2历史boot `27e8416d-3ba4-46fd-8b42-75e983f2dcfa`、R3133及实际映射结果只属于batch14。当前boot字段null，旧boot与旧nonce保持历史身份。

{common}

[冻结运行时合同](evidence/FROZEN_RA_ORIGINALS/inputs/runtime_identity_contract.json) · [来源条件原件](evidence/HISTORICAL_REFERENCES/DCL-R6-RuntimeAdapt-Fix/evidence/PROVENANCE_DECISION.json)。''')

doc('FULLCHAIN_C00_C09_RESULTS.md','C00–C09前置校准',f'''
当前C00–C09各项均为UNRUN_STATIC_ADMISSION。WORK、单会话预检、sealed capability、一次性认领、同进程exec、PreT0初始化、T0与预算建立、检查点和当前管理器健康均保持未观测。

|冻结阶段|主检查|当前结果|
|---|---|---|
|C00|内核身份/AS/cgroup/票据/映射等启动资格|UNRUN|
|C01|watchdog与当前组观测|UNRUN|
|C02|32896操作上界预付，96MiB受限内存子进程|UNRUN|
|C03|16MiB共享映射、4096页操作预付|UNRUN|
|C04|第5任务拒绝，task credit1|UNRUN|
|C05|local cap17、并发18次尝试与1次拒绝|UNRUN|
|C06|真实watchdog超时终止；MR审查预期退出|UNRUN|
|C07|controller exit23；MR审查预期退出|UNRUN|
|C08|watchdog死亡、后续grant拒绝/监视退出|UNRUN|
|C09前回归|C09H34→Root原件oracle→IPC56→BC40|UNRUN|
|真实C09|持久交接与直接父进程退出见证|UNRUN|

C00后的PT64/PF48/TR40/RA32/Ready64/MR64属于当前冻结完整路径中的必需回归，因容量冲突停在执行前。逐case开始/结束/耗时/访问/持久化/等待/切换/清理/检查/退出字段均以null记入[计划登记表](evidence/PLANNED_CASE_REGISTER.json)，没有以0秒代替测量缺失。

历史CalDiag C00–C09及真实交接PASS、TR-A2 WORK/C00 PASS分别保留其旧身份。

{common}''')

doc('FULLCHAIN_REAL_C09_RESULTS.md','真实C09交接证据',f'''
当前真实C09=UNRUN_STATIC_ADMISSION。当前intent、Receiver接收、持久ACK、Receiver确认、Launcher实际退出、waitpid、fresh-read、一次性分类及监督责任转移的证据数量均为0。

冻结依赖为：前置C00–C08及兼容回归→C09H34/Root oracle→IPC56→BC40→C09启动→Root sender_prepare→Launcher子进程exit23→协调者直接waitpid见证/持久交接验证→同Root父进程内部一次resume→M.health(True)/M.resume。T0、deadline、stop_at和交接计数应保持同一身份；当前实例未建立。

CalDiag历史真实C09 PASS与R38729、随后UNREVIEWED_MANAGER_FAILURE保持原记录。历史ACK和合成C09H记录均按原身份引用。

{common}

[当前源码摘录](evidence/SOURCE_EXCERPTS.json) · [既有交接模块](evidence/FROZEN_RA_ORIGINALS/src/c09_handoff.py)。''')

doc('FULLCHAIN_MANAGER_RECOVERY_RESULTS.md','ManagerRecovery恢复与异常路径',f'''
本轮MR64实际完成0/64、变异检出0/8（状态UNRUN）、RECOVERY_HEALTH_PASS未取得、当前failed-unit集合审查未执行、原生异常关闭未执行。计数0说明运行数量，覆盖结论保持UNRUN。

冻结完整路径在C00后先运行MR64合成有限夹具；真实C09后再通过M.resume完成原生恢复审查。M.health(True)验证handoff事实、审查C06/C07/C09的InvocationID/退出码/时间/身份/收据，随后双读failed-unit集合；已有历史单位按精确关闭证明只读分类，查询失败/陈旧事件/未审查失败继续拒绝。`mnt-e.mount`为既有规则中的固定排除，当前集合尚未读取。

MR64的Subject只维护进程内closed/stop/T0/R等字段；独立oracle读取MR-SIMULATION/1原始轨迹。该层用于分类/幂等/UNKNOWN等有限语义覆盖。真实Root停止、pidfd退出、cgroup清空和native/admin闭合需另有原生证据。

FC-S03的具体见证：guard.py:1099仅在MR_RECOVERY_DIAGNOSTIC_ONLY的C10后调用diagnostic_marker；manager_recovery.py:483–491再次校验scope，写入注入记录并触发预期78退出；协调者仅在该scope/退出78调用diagnostic_report。完整scope通过相同C10位置时继续后续流程，原生诊断分支不可达。

本次第7.4节要求的隔离原生异常路径缺少完整scope中的执行/计费/验收清单。切换诊断scope会提前关闭当前批次；额外批次或修改诊断分支均超出本轮冻结执行路径。下一轮可先静态构造独立的原生异常验收计划，保持第一次失败即关闭及单窗口边界。

历史MR-A被pre-T0故障阻断；TR-A2只证明正常最小路径及封存能力，内部UNKNOWN继续保留。当前internal状态为NOT_CREATED。

{common}

[覆盖机器记录](evidence/NATIVE_ANOMALY_COVERAGE.json) · [MR64冻结夹具](evidence/FROZEN_RA_ORIGINALS/inputs/manager_contract.json) · [独立oracle](evidence/FROZEN_RA_ORIGINALS/src/manager_recovery_oracle.py)。''')

doc('FULLCHAIN_C10_C12_RESULTS.md','C10–C12资格结果',f'''
|case|冻结检查|本轮结果|静态全局访问界|
|---|---|---|---:|
|C10|提升AS/写cgroup/访问manager socket/AF_INET拒绝；Ready屏障|UNRUN_STATIC_ADMISSION|1|
|C11|PREPARED、short_write、counter_fsynced、journal_fsynced本地镜像故障；后续信用拒绝|UNRUN_STATIC_ADMISSION|5|
|C12|错误boot、deadline、CLOSED、root、重复初始化和独立formal拒绝；实际状态保持|UNRUN_STATIC_ADMISSION|7|

C10仅在真实C09恢复健康成立后进入。C11局部账故障与MR原生异常关闭验收分别登记；C12中的CLOSED文档测试与真实CLOSED后的只读证据也分别登记。当前清理幂等、预算保持及终态读取均无本批动态证据。

{common}

[冻结probe](evidence/FROZEN_RA_ORIGINALS/src/guard_probe.py) · [逐case登记](evidence/PLANNED_CASE_REGISTER.json)。''')

doc('FULLCHAIN_S1_S9_RESULTS.md','S1–S9专项结果',f'''
当前完成0/34；safe夹具17项、mutant夹具17项均为UNRUN_STATIC_ADMISSION。PREPARED/COMMITTED、持久与并发预留、重复task_id、故障恢复、journal短写/EIO、N+1拒绝、CLOSED与身份拒绝各项覆盖均待当前批运行。

冻结RANGE驱动逐job建立独立local ledger，保留原始counter/intent/journal/事件及实际退出；即时range_evidence.check_job后，再由Root重新读取每个原始job。当前脚本只解析静态JSON/AST，生产checker、fixture、oracle调用数均0。

保守成功路径每actor界281=256事件＋19次API＋1部分写捕获＋5语义操作；总actor上界68。RANGE总20,000收费封套同时覆盖S34、Root重查、门18、预算聚合及两次重审，其完整静态推导见[预算核算](FULLCHAIN_RESOURCE_ACCOUNTING.md)。实际耗时、访问增量、退出状态均为null。

{common}

[S34冻结输入](evidence/FROZEN_RA_ORIGINALS/inputs/safety_contract.json) · [完整静态登记](evidence/PLANNED_CASE_REGISTER.json)。''')

doc('FULLCHAIN_GATE18_RESULTS.md','门18与预算异常聚合',f'''
门18完成0/18，全部UNRUN_STATIC_ADMISSION；预算聚合完成0/18子例、变异检出0/4，健康控制与13类异常均未执行。本轮无实际预算账，当前真实预算改动0。

现有root_verify_safety在S34原始重算成功后检查当前账健康，再执行gate_negative_cases。原17项覆盖错误status、缺job/raw、hash、绑定、checker与伪造PASS；第18项GATE-LEDGER-ANOMALY强制调用ledger_gate_regression.run_suite。

聚合内部为1个健康控制＋13类异常＋4个mutant，合计18：缺COMMIT、重复COMMIT、pair mismatch、顺序、overflow、batch、boot、sequence gap、截断、lock绑定、foreign journal、digest、缺证据。4项mutant分别吞掉缺COMMIT、累计overflow、batch mismatch和日志digest拒绝。

即时独立oracle逐job核对；整套oracle初审后，Root在run_suite返回与verify_gate_audit处各重新收费18并复读原始字节，完成收费595＋36=631，专项硬cap640。其动态通过及变异检出必须来自真实原件。本轮仅确认强制调用仍存在。

require_formal_admission再次核对门18、聚合资格摘要和当前真实全局账，随后检查真实C09、MR和PreT0资格；受控FORMAL入口与run_batch在语义导入前各调用一次。静态缺口保持RESOURCE_GATE_PASS关闭。

{common}

[聚合合同](evidence/FROZEN_RA_ORIGINALS/inputs/ledger_gate_contract.json) · [强制调用摘录](evidence/SOURCE_EXCERPTS.json)。''')

doc('FULLCHAIN_TIME_FEASIBILITY.md','完整校准时间可行性',f'''
当前完整校准耗时=null；300秒判断=UNRUN_STATIC_ADMISSION。TIME_FEASIBILITY_OBSERVED_PASS尚未取得；本轮也没有触发INCONCLUSIVE_LIMIT，静态拒绝为实际裁决。

完整校准的300秒软截止从唯一T0起算；总墙钟1800秒、提前停止1740秒、pre-T0 TCB120秒保持冻结。访问上界不能推出存储I/O、调度、systemd切换和原始证据重查的严格时间上界。

历史CalDiag的C00–C09通过、C09H服务包络7.135260秒、IPC56跨度11.392948秒、BC40跨度10.200091秒及Ready64跨度8.899268秒继续属于旧轨迹。部分区间相互嵌套，原始fsync累计也可能与服务包络重叠；其合计无法给出当前完整链的300秒证明。历史在C09后恢复失败，C10–C12/S34/门18保持未完成。

当前[逐case登记](evidence/PLANNED_CASE_REGISTER.json)将开始/结束/耗时/访问增量/持久化/等待/服务切换/清理/证据检查/退出状态均保存为null。字段完整性与测量完成度分别判定。

{common}

[历史测量原文](evidence/HISTORICAL_REFERENCES/DCL-R6-CalDiag/CALDIAG_CASE_DURATION_REPORT.md)。''')

parts_table='\n'.join(f"|{r['phase']}|{r['hard']:,}|" for r in bound['parts'])
doc('FULLCHAIN_RESOURCE_ACCOUNTING.md','资源预算独立核算',f'''
冻结可达完整校准访问硬界独立重算为68,498≤100,000，余量31,502；总1,000,000内余量931,502。这个数值覆盖现有路径；FC-S03缺失的原生异常清单尚无额外预算证明。

|阶段|保守访问硬界|
|---|---:|
{parts_table}
|合计|68,498|

C00–C12：13次入口访问＋C02预留128×(1＋1MiB/4096)=32,896＋C03预留16MiB/4096=4,096＋C04预留1＋C05尝试18＋C11循环4＋C12拒绝6=37,034。page4096为该算式前提，本批实际page查询尚未执行。

C09H成功路径精确273，冻结max_events64推得上界2,245；IPC完成收费505/硬512，BC完成481/硬512。联合保守上界3,269低于保留的5,000封套，避免再次叠加共同费用。真实C09入口访问计入C00–C12；原生恢复审查在C00后预付256，MR回归完成833，合计1,089；保守专项硬界1,536。

RANGE成功上界：1＋68×281＋2×34＋34＋1＋18＋631=19,861。分别覆盖driver入口、两actor上界、job设置/即时checker、Root原件checker、健康控制、门18循环和ledger聚合。聚合595=1＋18×(32＋1)，两次Root重审36，合计631；以硬640替换后为19,870≤20,000。独立生产oracle只在未来受控计费路径调用，本轮调用0。

PT/PF/TR/RA的固定成功收费分别1,089/817/681/545，由1＋jobs×(driver_prepay＋1)推得；上表采用各自更保守硬界。FORMAL控制器与run_batch重复准入另收费2，发生在校准结束后的同一全局剩余预算中。模型本体访问预算服从全局剩余额度和原deadline。

旧boot/root_ipc/readiness合同内仍保留65,618描述字段；本轮根据实际新增套件重算为68,498，与当前manifest/execution_lock的完整硬界一致。旧描述与现路径数值差2,880记入机器证据；相关字段的运行时引用扫描没有发现其作为动态上限被使用。本轮保持原字节。

资源合同：AS1GiB/进程、Payload父TasksMax4、墙钟1800/提前1740、校准300、TCB120。实际T0/deadline/R、内存峰值、进程峰值、I/O耗时均null；新增已消费访问为0。访问上界合格与封存容量准入分别裁决。

[完整算式与逐case收费](evidence/RESOURCE_BOUND_INDEPENDENT.json) · [容量冲突](evidence/SEAL_CAPACITY_STATIC_WITNESS.json)。''')

doc('FULLCHAIN_F1_RESULTS.md','F1有界模型检查',f'''
F1实际执行0，状态UNRUN_RESOURCE_GATE；状态空间访问量、覆盖率、变异检测与反例重放均为null/UNRUN。INV1 UniqueHistory、INV2 UniqueChild、INV3 SealSafety、INV4 RHOConservation、INV5 BudgetConservation、INV6 OriginPreservation、INV7 ReadySeparation、INV8 CurrentAuthority均未授予PASS_BOUNDED。

冻结run_batch按顺序列出6项基线：SMOKE_UNKNOWN、RELEASE_EMPTY、BRANCH_UNKNOWN、POST_TAKEOVER_B、CHAIN、RECOVERY_ABORT；9项mutant：double_child、drop_rho、drop_hist、drop_dedup、stale_cache、reset_budget、ready_confusion、rollback、relabel_origin。每个基线软访问12,000、mutant8,000；实际发现轨迹才使用同预算重放。KEY枚举3×2×2×3×2=72行认证谓词。

模型包含有限Cfg O/C、分支O→C/D、链O→C→E等；每Cfg4成员、f=1及受界应用状态。模型使用静态PBFT提交oracle假设，所获有限性质仍需精确有限域与穷尽证据。本轮仅解析该源码，语义模块导入和状态枚举均0。

五业务源f1_model.py/f1_check.py/compare.py/f4_dp.py/f4_reference.py摘要均与原最终锁相同。资源资格是唯一正式进入条件；当前静态拒绝阻止该链激活。

{common}

[冻结runner](evidence/FROZEN_RA_ORIGINALS/src/run_batch.py) · [源码摘要](evidence/SOURCE_LOCK_VERIFICATION.json)。''')

doc('FULLCHAIN_F4_RESULTS.md','F4动态规划与独立参考检查',f'''
F4实际执行0，状态UNRUN_RESOURCE_GATE；Soundness、Completeness、CostAccuracy、ObservationUniformity、TerminalCorrectness、CompressionCorrectness均无当前PASS_BOUNDED证据。

静态输入清单为13个fixture：COST1、CE5_FULL、COMP_SAME_X、EMPTY_POST_INVALID、PARTIAL_POST_INVALID、OPEN_UNKNOWN、NONUNIFORM、REAL_QUERY_COST、ZERO_INTERNAL、PREFIX_BAD、VISIBLE_COST、QUOTA_MODE、MISSING_OBSERVATION。G64来自16组费用×2个替代成本×2种可见性，共64；总77个基线游戏。此处为源码计划计数，输入构造函数执行0。

每个游戏计划h∈{{0,1,2}}、m∈{{0,…,20}}，普通DP与compression分别比较；参考solve按具体策略表/轨迹独立穷举，DP可行证据由REF.interpret重放。DP.decide和REF.solve各在输入状态验证前预付len(states)访问，语义文件字节隔离保持。计划10项mutant包括stagewise_max、drop_mode、两种empty_post、ignore_unknown、worldwise、zero_query_cost、ignore_prefix、drop_permission和omit_observation。

当前耗时、访问、参考策略数量、DP/REF一致性、压缩比较与最小反例均UNRUN；业务轨迹文件数量0。计划域和既有设计假设保留其研究边界。

{common}

[冻结比较器](evidence/FROZEN_RA_ORIGINALS/src/compare.py) · [DP](evidence/FROZEN_RA_ORIGINALS/src/f4_dp.py) · [独立参考](evidence/FROZEN_RA_ORIGINALS/src/f4_reference.py)。''')

doc('FULLCHAIN_TERMINAL_AND_SEAL.md','终态、封存与证据归档',f'''
当前运行实例未建立，native seal=NOT_APPLICABLE_NO_RUNTIME，自动行政finalizer=NOT_APPLICABLE_NO_ENTRY，STOP/CLOSED/roles/cgroup为NOT_CREATED。兜底清理0。研究交付ZIP属于主机行政归档，与native/自动行政运行结果分别登记。

FC-S01可构造静态轨迹：成功C00→PT64→PF48→TR40→RA32→Ready64→MR64。六组Store.put使用不同固定前缀，i与case逐一对应；所有文件保留在inputs/root_private/boot。312条路径在[静态容量见证](evidence/SEAL_CAPACITY_STATIC_WITNESS.json)中穷举。文件删除/合并/跳过会改变冻结原件合同与本次执行要求。

行政导出按root.rglob遍历所有常规文件，count>256即PT_ADMIN_EVIDENCE_BOUND；仅这312份case原件已超限。native创建也递归包含全部原件并增加manifest，成员数至少313；终态_reader对len(names)>257报TR_NATIVE_MEMBER_SET。成功最小A2只有233份manifest/234成员，恰好处于旧容量内；其历史成功无法覆盖该完整链规模。

本轮容量见证属于静态配置反例。没有执行目标封存函数、改变cap、生成运行伪件或预发动态收据。未来静态修复需要从完整C/S/门18/模型输入、输出和账字节上界重建容量及时间证明，保留明确硬界、流式读取、首错停止和权限合同。

已保存64份冻结源码/输入副本、历史重点文件与ZIP复核、9,313份既有文件基线摘要、47份误路径只读核验和四份导航原件。最终交付核验见[交付收据](evidence/DELIVERY_CHECK.json)，原件保持性通过前后hash及导航原字节后缀核对。

{common}''')

doc('FULLCHAIN_COUNTEREXAMPLES.md','静态见证与研究证据边界','''
|标识|可构造输入/轨迹|度量与触发|结论|
|---|---|---|---|
|FC-S01|冻结完整scope，六个C00后必需套件全部完成且保留原件|至少312常规文件>行政cap256|成功轨迹与自动行政导出合同冲突|
|FC-S02|相同原件集由guard.seal按冻结逻辑打包|至少313 ZIP成员>终态reader cap257|生成后的native包与终态接受合同冲突|
|FC-S03|scope=CALIBRATE_S1S9_THEN_F1_F4，C10成功|诊断注入分支scope条件为False|本次必需原生异常路径缺覆盖|

前两项共享同一312路径构造，属于两个合同位置的容量矛盾；第三项属于任务覆盖缺口。全部结论由静态源码与锁定输入导出，实际运行反例数量0、协议反例数量0。

这些见证针对验证基础设施。当前最强通用方法G与D1/D2间的严格分离实例仍为0；这批静态见证没有形成新的候选机制分离声明。研究实现门保持CLOSED。

UNKNOWN边界：历史TR-A2 mr_close_state缺失而internal UNKNOWN原样保存；当前internal字段NOT_CREATED；正式M.formal_gate需要MR_QUALIFICATION和MR_RECOVERY_REVIEW，当前材料缺失。当前资源门保持未取得。

后续最小工作为独立静态修复：完整输出规模/容量/字节/时间证明与终态/admin一致化；原生异常验收执行清单与隔离/计费/退出/接受条件；完成摘要重冻结后再决定新的动态身份。当前授权已按照静态失败分支结束，追加修复与重跑均为0。

[路径构造](evidence/SEAL_CAPACITY_STATIC_WITNESS.json) · [覆盖构造](evidence/NATIVE_ANOMALY_COVERAGE.json)。''')

answers=[
 ('最新完整执行锁是否通过','既有64文件锁PASS_STATIC_BYTES；新完整动态锁未签发，准入BLOCKED'),
 ('当前新运行时是否符合冻结合同','UNRUN_STATIC_ADMISSION；冻结2.39/8.12基线与来源条件保留'),
 ('WORK/C00是否通过','当前UNRUN；历史TR-A2 PASS保留'),
 ('C00–C09完成情况','当前0/10；前置合成兼容回归均UNRUN'),
 ('真实C09是否通过','当前UNRUN；历史CalDiag PASS保留'),
 ('ManagerRecovery64完成数量','0/64，UNRUN'),
 ('8项变异检出数量','0/8，UNRUN；没有执行检测'),
 ('systemd失败单位审查是否正确','本轮未查询；静态逐实例审查逻辑仍在'),
 ('自动关闭异常路径是否通过','UNRUN；完整scope缺原生诊断路径FC-S03'),
 ('C10–C12是否通过','0/3，UNRUN'),
 ('S1–S9是否通过','0/34，UNRUN'),
 ('18项负向门是否通过','0/18，UNRUN；内部ledger子例0/18、mutant0/4'),
 ('完整校准实际耗时','null，尚未建立T0'),
 ('是否满足300秒软窗口','UNRUN；没有授予OBSERVED_PASS，也没有发生动态超时'),
 ('最终访问量和资源峰值','R=null，新增消耗0；AS/RSS/任务峰值null；静态校准界68498'),
 ('RESOURCE_GATE_PASS是否取得','NOT_OBTAINED'),
 ('F1实际执行范围和结果','0；UNRUN_RESOURCE_GATE'),
 ('F4实际执行范围和结果','0；UNRUN_RESOURCE_GATE'),
 ('PASS_BOUNDED具体授予哪些性质','[]'),
 ('是否出现真实协议反例','0；静态容量配置见证2项、覆盖缺口1项'),
 ('native seal和行政封存实际结果','均N/A，无运行实例；本轮主机研究ZIP另行封存'),
 ('内部UNKNOWN是否仍存在','历史UNKNOWN保持；当前内部状态NOT_CREATED'),
 ('是否具备进入下一研究阶段的条件','可进入独立静态修复准备；当前动态/F1/F4准入继续关闭')]
table='\n'.join(f'|{i}|{q}|{a}|' for i,(q,a) in enumerate(answers,1))
doc('FULLCHAIN_FINAL_DECISION.md','FullChain-B最终裁决',f'''
**BLOCKED_STATIC_ADMISSION。** 冻结完整链在C00后的六组回归即产生至少312份原件，超出行政cap256；native归档最低313成员，超出终态reader cap257。当前完整scope也缺本次要求的原生异常关闭验收路径。按本轮明确授权，关键静态冲突发生后停止动态启动，执行源码保持冻结。

64/64最终文件摘要及44程序静态文法/compile核验通过；访问硬界独立重算68,498≤100,000。预算结论支持既有可达校准路径的静态上限，输出容量与原生异常覆盖仍阻断整个任务准入。300秒时间可行性保持UNRUN。

{common}

|序号|验收问题|实际答复|
|---:|---|---|
{table}

本轮16份专项报告、静态输入登记/容量路径见证、源码/输入副本、预算推导与重点历史引用已形成。[证据索引](EVIDENCE_INDEX.md) · [机器裁决](evidence/STATIC_DECISION.json) · [交付核验](evidence/DELIVERY_CHECK.json)。

下一步仅针对封存容量与原生异常验收清单准备独立静态修复；本轮追加实现、修复后执行、自动下一批次均为0。历史CLOSED、旧账、失败和UNKNOWN及原创性裁决原样保留。''')

report_names=sorted(p.name for p in O.glob('FULLCHAIN_*.md'))
assert len(report_names)==16
put('EVIDENCE_INDEX.md','''# FullChain-B证据索引

结论：BLOCKED_STATIC_ADMISSION。当前结果均为主机静态核验，运行时实例尚未建立。

'''+ '\n'.join(f'- [{n}]({n})' for n in report_names)+'''

证据：

- [原始授权](evidence/TASK_REQUEST.txt)
- [机器裁决](evidence/STATIC_DECISION.json)
- [源文件锁与44程序静态检查](evidence/SOURCE_LOCK_VERIFICATION.json)
- [64份冻结原件副本](evidence/FROZEN_RA_ORIGINALS/inputs/static_manifest.json)
- [312条静态输出路径与容量不等式](evidence/SEAL_CAPACITY_STATIC_WITNESS.json)
- [MR原生异常覆盖](evidence/NATIVE_ANOMALY_COVERAGE.json)
- [源码行证据](evidence/SOURCE_EXCERPTS.json)
- [独立资源核算](evidence/RESOURCE_BOUND_INDEPENDENT.json)
- [完整静态用例登记及空测量字段](evidence/PLANNED_CASE_REGISTER.json)
- [历史重点引用摘要](evidence/HISTORICAL_REFERENCE_INDEX.json)
- [TR-A2 ZIP逐成员核验](evidence/TRA2_ZIP_RECHECK.json)
- [历史文件前态](evidence/HISTORY_BASELINE.json)
- [历史文件后态与导航后缀核验](evidence/HISTORY_AFTER_CHECK.json)
- [47份误路径只读核验](evidence/MISPATH47_READ_ONLY_CHECK.json)
- [行政审计脚本](evidence/AUDIT_STATIC.py)
- [报告生成脚本](evidence/WRITE_REPORTS.py)
- [归档/交付脚本](evidence/SEAL_DELIVERY.py)
- [交付核验收据](evidence/DELIVERY_CHECK.json)
- [交付manifest](FULLCHAIN_MANIFEST.json)
- [研究证据ZIP](FULLCHAIN_EVIDENCE.zip)及[SHA-256](FULLCHAIN_EVIDENCE.zip.sha256)

交付收据、ZIP及其SHA文件独立于manifest归档对象，避免自摘要循环。研究归档与native/admin运行结果分别裁决。
''')

prefix='''## DCL-R6-FullChain-B 静态准入增量（2026-11-13）

**BLOCKED_STATIC_ADMISSION。** 完整冻结链C00后六组回归至少312份独立原件，超出自动行政cap256；native ZIP最低313成员，超出终态reader cap257。MR64为MR-SIMULATION/1，完整scope另缺原生异常关闭验收路径。64/64原文件锁和44程序静态检查通过；独立校准硬界68,498≤100,000。依本轮授权停在静态阶段，WSL/部署/active entry/源码修订/重跑均0，T0/deadline/R=null，300秒性能UNRUN。

新运行身份/动态收据/执行锁均未签发；历史batch14保持CLOSED，旧账/失败/UNKNOWN原样保留。下一步可准备独立静态修复，具体范围为完整输出封存容量合同与原生异常验收清单。RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。

[本轮裁决](DCL-R6-FullChain-B/FULLCHAIN_FINAL_DECISION.md) · [集成冲突](DCL-R6-FullChain-B/FULLCHAIN_VERSION_INTEGRATION.md) · [预算复算](DCL-R6-FullChain-B/FULLCHAIN_RESOURCE_ACCOUNTING.md) · [证据索引](DCL-R6-FullChain-B/EVIDENCE_INDEX.md)

以下逐字节保留先前记录。

---

'''.encode('utf-8')
for n in ['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']:
    original=(E/'NAV_ORIGINALS'/n).read_bytes()
    assert (P/n).read_bytes()==original
    (P/n).write_bytes(prefix+original)
    assert (P/n).read_bytes().endswith(original)
print(json.dumps({'reports':len(report_names),'planned_rows':len(register),'navigation_prefix_updates':4,'target_execution':0},ensure_ascii=False))
