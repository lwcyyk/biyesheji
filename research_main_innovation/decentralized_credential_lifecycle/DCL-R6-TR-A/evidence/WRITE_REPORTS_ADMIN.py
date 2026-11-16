"""Report actual preflight rejection and automatic evidence; no target replay."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;O=E.parent
R=json.loads((E/'ACTUAL_RESULTS.json').read_bytes());D=R['runtime_drift'];A=R['automatic_finalization']
passport='Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。'
gates='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。'
def report(name,title,body):
    with(O/name).open('x',encoding='utf-8') as f:f.write('# '+title+'\n\n'+passport+'\n\n'+body.strip()+'\n\n'+gates+'\n')
report('TRA_AUTHORIZATION_AND_LOCK.md','TR-A授权、源码与批次锁','''
**PREFLIGHT_FAILED_RUNTIME_DRIFT：主机静态准入通过，唯一原生入口在运行时摘要检查处拒绝。** 本批没有建立正式运行实例或预算窗口。

|绑定|核验结果|
|---|---|
|版本|TerminalRead-static-1/r1；59文件/41程序，Linux部署57项|
|manifest SHA|d2a6f4f58d7afd5a14287cea1c86da76d137e80dea2b64b35535fd2b145f7aac|
|execution_lock SHA|43f362a064209ff8359e410301017741d787cb3acd272d40c75d447820671878|
|静态源/输入/副本|最终锁、当前tr01、最终静态副本和退出后Linux导出59项匹配|
|规划源/实例|/var/lib/dcl-r6/tr01；/var/lib/dcl-r6/batch13；dclr6batch13.slice|
|control|DCL-R6-TerminalRead-Fix/authorization/batch13-r1，新回执绑定真实用户原文及两锁|
|boot|ef808858-4c80-4fd8-ac74-25a41b5b99ef，预检、拒绝及自动行政审计一致|
|批准范围|PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START；PT64/PF48/TR40；Full/MR/预窗注入false|
|原生基础环境|Ubuntu-24.04/Python3.12.3、原kernel/systemd、UID999/GID989/cgroup基础检查匹配；完整runtime闭包失败|
|历史保护|执行前8017文件基线，原始导航字节另存；误路径47只读/hash|

静态计费重算为C00=1、PT1089、PF817、TR681，完成2588/硬3649，完整硬67730。152项已包括25变异，预算证明齐备。本次未执行这些测试，R/T0仍null。

兼容SameProcess_C09位满足冻结schema，scope保持最小A，没有C09发放。回执、源码和执行锁均未现场改写；失配来自系统运行库。当前control已记录一次失败及自动封存，保留该attempt，不以没有T0为由重用回执或重启。

[源码/范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json) · [资源准入](evidence/RESOURCE_ADMISSION_PROOF.json) · [源后核](evidence/SOURCE_AFTER_CHECK.json)
''')
report('TRA_BOOT_AND_WORK_RESULTS.md','原生启动、预检与WORK结果','''
**入口实际运行，正式启动停于PREFLIGHT_BEGIN；WORK/C00=UNRUN_PREFLIGHT_FAILED。**

实际Bootstrap为PID2271/start43611，boot ef808858-4c80-4fd8-ac74-25a41b5b99ef，PREFLIGHT_BEGIN sample436.167570765。boot_continuity.artifact_check检查当前文件时抛Rejected('BC_ARTIFACT_DRIFT:/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2')，active退出125。

原始stdout仅有PREFLIGHT_BEGIN，没有PREFLIGHT_QUALIFIED、ACTIVATION_REQUESTED_ONLY或ENTRY_VERIFIED。运行目录、service/slice安装、cgroup、claim、memfd激活能力、scheduler/stopper、T0、counter均未创建；主机授权文件和Linux源部署是已获批的前置行政准备。

基础只读环境核验只证明Python/kernel/systemd/身份等当时字段匹配，完整Native资格还需要全部运行时字节匹配。加载器失配先于准备命令与运行窗口，因此未进入C00八项资源检查。

[首错/抛出位置](evidence/FIRST_FAILURE.json) · [真实stderr](evidence/windows_entry.stderr.raw) · [真实stdout](evidence/windows_entry.stdout.raw)
''')
report('TRA_TERMINAL_READ_RESULTS.md','终态只读接口实际覆盖','''
**TR-A1=UNRUN。** 原生预检已拒绝，批次没有WORK、T0、正式CLOSED或budget，read_terminal_evidence未被调用。

batch13、原boot与源/执行锁由本次调用原件明确；T0/deadline/stop_at/R、journal状态、关闭原因、阶段版本和退出见证均属于未初始化或未到达字段，值保留null/UNRUN。没有构造默认期限、R=0或假的CLOSED来调用接口。

自动行政审计确认runtime_intent/state/counter/checkpoint全false，closed_marker=false。该审计是冻结故障收尾，无法替代CLOSED后的终态读取测试。接口读取前后业务对象比较也保持UNRUN；源码摘要前后保持有独立证据。

[实际审计与空对象](evidence/ACTUAL_RESULTS.json) · [终态读取计划](evidence/UNRUN_CASE_REGISTER.json)
''')
report('TRA_ACTIVE_GUARD_RESULTS.md','活动态守卫与安全边界覆盖','''
**TR-A2/TR-A3=UNRUN。** 本批没有发布CLOSED，原生CLOSED后新工作、预算、T0、Launcher、WORK修改和活动健康检查均未到达。

此次确实观察到运行时摘要守卫拒绝不匹配环境，原执行锁保持。这项准入拒绝不能计作CLOSED后活动态拒绝、跨batch终态读取或只读不变性的动态通过。

未修改当前或历史预算，未产生任何新的运行状态对象；没有跨批次证据作为本批运行资格使用。历史PFA实际WORK与112项通过继续只属于旧batch12/r3。

[首错](evidence/FIRST_FAILURE.json) · [源不变](evidence/SOURCE_AFTER_CHECK.json)
''')
report('TRA_TR40_RESULTS.md','TR40与八项变异结果','''
**TR-A4=UNRUN：TR40执行0/40，8项变异触发0/8、检出0/8。** 原生窗口未创建，独立oracle调用0。

grant_terminal_work、rebuild_budget、skip_identity、default_deadline、ignore_journal、upgrade_unknown、false_seal、write_original全部NOT_EXERCISED；不存在已触发漏检的本轮结果。所有safe项记UNRUN_PREFLIGHT_FAILED。

冻结输入、safe控制配对、source/oracle SHA均匹配。输入中预期结果未当作实际执行结果；未在窗口外运行subject、reference或checker补数据。

[152项逐项未执行登记](evidence/UNRUN_CASE_REGISTER.json) · [源码锁](evidence/SOURCE_AND_SCOPE_ADMISSION.json)
''')
report('TRA_COMPATIBILITY_RESULTS.md','PT64/PF48兼容回归结果','''
冻结申请要求本轮全量PT64及PF48，合计112项/17变异。本次两套兼容回归执行均0，全部UNRUN_PREFLIGHT_FAILED；25项总变异中另含TR8，均NOT_EXERCISED。

旧batch12的PT55 PASS＋9变异、PF40 PASS＋8变异与R1907保持为历史事实。当前版本source/输入虽与最终r1锁匹配，运行库闭包发生变化，历史动态通过未升级为TerminalRead当前资格。

本轮无测试重跑、无预算账初始化、无附加免费窗口。兼容性回归和真实终态联调需要先完成运行时重新审查及新的独立版本/执行身份授权。

[未执行明细](evidence/UNRUN_CASE_REGISTER.json) · [运行时变化](evidence/RUNTIME_DRIFT_AUDIT.json)
''')
report('TRA_NATIVE_SEAL_RESULTS.md','native seal结果','''
**本次实际分类NATIVE_SEAL_NOT_APPLICABLE；TR-A5=UNRUN。** 原生预检失败早于runtime intent、T0、counter和checkpoint，native seal及其终态读取前提未进入。

自动post原件的runtime_objects四项均false、T0/R=null、closed_marker=false。没有native ZIP/manifest，且缺少可供原生seal的运行实例；不能将这一前置失败记成终态接口或native写入的真实失败。

旧PFA native UNRESOLVED保持；本轮NA只属于此次没有运行对象的attempt。自动行政包成功独立记录，不推导native已完成。

[原生分类原件](evidence/STARTUP_FINALIZATION.json) · [空对象与未调用状态](evidence/ACTUAL_RESULTS.json)
''')
report('TRA_ADMIN_FINALIZER_RESULTS.md','自动行政finalizer与保全结果','''
**冻结自动行政流程实际完成，ADMIN_EVIDENCE_SEALED；TR-A6=CONDITIONAL_PASS，范围为预检失败的故障保全。**

active结束后，原host自动执行固定tr01/src/admin_postexit.py --post-exit-export，Root actor2275/start43638，boot ef808858…、UID0。post exit0、客户端reaped=true，耗时0.241365600秒。主入口原AS1GiB/单次30秒与继承检查流程保持，live RLIMIT/GID/cwd/import起点没有额外原始回执。

原生审计BOOTTIME436.452127342确认当前batch角色0、UID999进程0、父组不存在、runtime对象均无；导出native文件0。host封存14清单成员/15 ZIP entries，34735字节。完整stdout/stderr、真实请求/回执、退出、post计划/审计和4项源锁入包，CRC/逐流SHA/manifest原字节验证通过。

自动行政ZIP SHA-256：`871baaef3babeb15e441bb3f60955228cf25fa3b25c68e230a04f0efc2ef20e8`。没有手工finalize、冻结后备或人工归档替代自动成功；最终研究汇总包只保存这些既有事实和分析。

当前系统runtime闭包未通过资格审查，自动包完整性仅支持故障证据保全。它不验证CLOSED后Reader兼容性、变更glibc的完整安全属性或新的资源资格。

[自动原始结果](evidence/STARTUP_FINALIZATION.json) · [独立逐流核验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json) · [post双流](evidence/STARTUP_POSTEXIT.stdout.raw)
''')
report('TRA_INTERNAL_STATE_RESULTS.md','内部状态与进程退出分项裁决','''
**TR-A7=UNKNOWN。** 本批应用尚未初始化，原行政结果internal_cleanup_status=UNKNOWN保持。

|轴|实际结果|
|---|---|
|受控工作角色|未启动，自动与独立审计均空|
|cgroup/slice|未创建，事后不存在|
|CLOSED/STOP_REQUEST|未创建；没有虚构关闭对象|
|T0/预算/journal|未初始化，null/不存在|
|native seal|NOT_APPLICABLE，正式调用未到达|
|行政封存|自动SEALED14/15|
|应用内部终态|无对应运行状态或关闭收据，原字段UNKNOWN|

本批bootstrap进程exit125，行政进程成功结束；这与正常Root scheduler/worker的回收测试属于不同范围。没有受控树需要清理，人工/后备停止0。封存的是一次已结束的预检失败attempt，保留原control和退出记录，不以T0未建立为由重新使用本批窗口。

[实际对象与审计](evidence/ACTUAL_RESULTS.json) · [基础平台/当前空角色](evidence/RUNTIME_DRIFT_AUDIT.json)
''')
report('TRA_RESOURCE_ACCOUNTING.md','资源准入、未初始化预算与环境漂移','''
**TR-A8=FAIL：完整运行时摘要合同未满足，正式资源窗口未建立。**

|指标|实际值|
|---|---|
|计划完成/阶段A硬界|2588 / 3649；完整硬67730≤100000，静态证明已核齐|
|实际T0/deadline/stop_at/R|全部null，counter/journal未创建|
|PT/PF/TR/变异/模型运行|全部0；没有给未初始化账填0|
|active host|0.259492000秒，原生exit125|
|自动post|0.241365600秒，exit0|
|全部host入口|0.873294800秒|
|Payload资源|无工作负载；峰RSS/charged memory/tasks不适用，Root高水位未测|
|原合同|1000000/1800、校准100000/300、预T0120、提前1740、AS1GiB、父TasksMax4均未放宽|

只读审计核对1241个冻结运行时文件，3项不同，源/输入0失配。当前Python3.12.3、kernel/systemd/UID/GID基础字段仍匹配；加载器/libc/libm变化足以拒绝整个闭包，基础字段相同不能取代字节资格。

当前包查询libc6及libc-bin均2.39-0ubuntu8.12。dpkg.log原文记录2026-11-13 13:26:52–53从2.39-0ubuntu8.9升级至8.12，日志时区没有单列，按原样保存；本轮只做读取/hash/包元数据查询，没有安装、降级、更新源锁或重启。辅助/lib路径包归属查询未命中，完整版本和升级日志独立保留。

新环境下映射、启动、资源与协议前提尚未重新审查。没有进入完整300秒校准，性能可行性仍UNRESOLVED。

[准入预算证明](evidence/RESOURCE_ADMISSION_PROOF.json) · [全部实际差异与包日志](evidence/RUNTIME_DRIFT_AUDIT.json) · [3份现行二进制导出锁](evidence/DRIFTED_RUNTIME_EXPORT_LOCK.json)
''')
report('TRA_EXECUTION_TIMELINE.md','预检失败与自动封存时间线','''
|事件|原始时间|事实|
|---|---|---|
|外层host开始|UTC2026-11-13 09:28:55.656703|冻结入口唯一一次|
|active WSL开始|UTC09:28:55.908611|--activate固定argv|
|PREFLIGHT_BEGIN|BOOTTIME436.167570765；guest UTC ns1794562136086751893|Root2271/start43611；120秒deadline来源已开始|
|hash拒绝|精确抛出时刻UNKNOWN|ld-linux摘要不符；stderr保存原错误|
|active返回|UTC09:28:56.168099|exit125；0.259492秒|
|自动行政进程|PID2275/start43638|固定Root入口，post exit0|
|行政审计|BOOTTIME436.452127342|无runtime对象、角色/组空|
|自动封存|UTC09:28:56.510318|行政14/15，SEALED|
|外层返回|UTC09:28:56.529977|exit125，总0.8732948秒|

工作、TR/PT/PF、CLOSED后读取、原生seal时间均未产生。guest BOOTTIME/UTC、host UTC和包日志时间分开保留；不由包日志未记录的时区推定精确跨时钟先后。

[原始全量时间线](evidence/EXECUTION_TIMELINE.json) · [active退出](evidence/WINDOWS_ENTRY_EXIT.json) · [自动post计划](evidence/STARTUP_POSTEXIT_PLAN.json)
''')
diffrows='\n'.join('|'+x['path']+'|'+x['expected_sha256']+'|'+x['actual_sha256']+'|' for x in D['differences'])
report('TRA_COUNTEREXAMPLES.md','首次失败、具体环境差异与后续边界','''
**首次关键失败是BC_ARTIFACT_DRIFT，发生在artifact_check的运行时字节核验，早于实例准备和一次认领。**

|原路径|冻结SHA-256|实际SHA-256|
|---|---|---|
'''+diffrows+'''

当前加载器/libc/libm均为Root所有的普通系统文件；Python、源码和冻结输入保持。包日志记录glibc8.9→8.12，与当前3项运行库变化同时形成环境资格缺口。没有将来源猜成代码缺陷、攻击或某个更新执行者；本轮安装操作0。

冻结预检在首个loader差异即拒绝；后续1241对象/3差异统计属于独立只读故障诊断。未通过改hash、放宽规则、使用旧RESOURCE_GATE_PASS或重跑避开失败。原TerminalRead语义仍未动态验收。

最小后续工作是运行时适配与资格审查：保存8.12实际字节/包来源，评估CPY312/AS4及原TCB假设影响，更新新独立版本的runtime闭包和依赖摘要，再新身份/执行锁申请有限验收。当前r1保持冻结；不直接把3个hash换成现值后继续本批。

[首错](evidence/FIRST_FAILURE.json) · [完整环境差异](evidence/RUNTIME_DRIFT_AUDIT.json) · [后续具体范围](NEXT_PLATFORM_ADMISSION_REQUEST.md)
''')
report('TRA_FINAL_DECISION.md','TR-A最终裁决与二十项回答','''
**整体PREFLIGHT_FAILED_RUNTIME_DRIFT，有限阶段A未取得动态验收。** 系统加载器/libc/libm摘要与冻结闭包失配，主实例和预算未创建；自动行政故障封存成功。

|门|状态|实际范围|
|---|---|---|
|TR-A1 终态读取|UNRUN|CLOSED及Reader未到达|
|TR-A2 只读/身份|UNRUN|源hash保持，终态接口未执行|
|TR-A3 活态守卫|UNRUN|没有CLOSED后守卫调用|
|TR-A4 TR40|UNRUN|0/40，8变异NOT_EXERCISED|
|TR-A5 native seal|UNRUN|原分类NOT_APPLICABLE，无运行对象|
|TR-A6 自动行政|CONDITIONAL_PASS|故障保全原生自动14/15完成；非CLOSED联调、runtime仍不合格|
|TR-A7 内部状态|UNKNOWN|应用未初始化，原UNKNOWN保留|
|TR-A8 预算资源|FAIL|运行时字节合同失败；预算静态界齐备，实际R=null|

|最终问题|真实回答|
|---|---|
|1 原生启动|入口实际运行，PREFLIGHT_BEGIN后exit125，正式初始化未完成|
|2 WORK/C00|UNRUN_PREFLIGHT_FAILED|
|3 CLOSED后期限读取|UNRUN|
|4 T0/deadline/stop_at|未创建，null|
|5 完全只读|终态接口未调用，性质UNRUN；源与历史字节保持|
|6 CLOSED后工作拒绝|UNRUN，不能用环境准入拒绝代替|
|7 跨批复用|未使用历史账/能力/资格；终态跨批拒绝case未执行|
|8 TR40完成|0/40|
|9 8变异检出|0/8，NOT_EXERCISED|
|10 PT/PF兼容|0/64、0/48，17变异未触发；旧112通过保持历史范围|
|11 native最终状态|NATIVE_SEAL_NOT_APPLICABLE|
|12 native完整原始证据|只有无runtime对象的适用性事实，无原生seal调用或ZIP|
|13 内部UNKNOWN|继续UNKNOWN，应用/关闭收据均未建立|
|14 自动行政|成功，post0、14清单/15ZIP entries、CRC/SHA通过|
|15 兜底归档|0；独立只读导出与研究汇总单列|
|16 进程/组空|实际Root/Payload工作角色未启动，自动与独立审计为空，后备清理0|
|17 R/时间/内存/tasks|R=null；active0.259492秒/全部host0.8732948秒；无Payload工作负载，峰数据不适用/未测|
|18 完整A验收|未取得，PREFLIGHT_FAILED|
|19 首次失败/最小修复|冻结ld-linux hash不符；共3项glibc文件变更，先静态运行时适配/重锁，当前source不修复、不重跑|
|20 恢复MR条件|尚缺新运行时资格和TerminalRead真实验收；不恢复后续链|

控制目录保留本次请求、回执、退出和自动包，运行目录/CLOSED/claim/T0均未创建。该attempt不自动复用；后续需新的审查、身份、最终锁与许可。旧PFA R1907/native UNRESOLVED/internal UNKNOWN/admin成功及更早历史保持。

[具体差异](TRA_COUNTEREXAMPLES.md) · [行政验证](TRA_ADMIN_FINALIZER_RESULTS.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('NEXT_PLATFORM_ADMISSION_REQUEST.md','下一轮运行时适配与准入范围','''
本文件为具体后续请求，当前没有修改、安装、降级或新执行授权。

1. 以只读导出的3个现行文件、1241对象核对和包日志为依据，审查glibc2.39-0ubuntu8.12及其相关ABI/映射/资源计量/信号与Root TCB假设。验证当前包来源与完整闭包，必要时补齐/lib与/usr/lib合并路径的元数据归属。
2. 保持旧r1及历史所有hash冻结，在独立候选中更新受影响runtime_files/runtime_critical/runtime_tree_lock、相关输入与执行锁DAG；不能只改第一次命中的一个loader hash。
3. 证明原CPY312-UBU24/1、AS4-PAYLOAD/1、1GiB/父4tasks、1800/300/120与访问界的适用范围。若合同影响超出有限适配，明确提交补充授权。
4. 终态读取/活动态拒绝/native/admin原有源码及PT/PF/TR判据优先保持；如需更改代码另列最小diff与原因。
5. 重新静态核验、冻结新独立身份与准确argv，再申请正常WORK/C00/PT64/PF48/TR40/CLOSED/readonly/native/admin的有限动态验收。

当前batch13/control保留为已执行且封存的预检失败attempt。新运行时资格未审查前，不能继续现回执、重置预算或执行MR/C09/S34/门18/F1/F4。当前Source未进入运行窗口，这一事实不构成额外免费重跑许可。
''')
report('COMMAND_SUMMARY.md','实际命令及分类','''
唯一active：冻结Windows入口调用Ubuntu-24.04/root的/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/tr01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch13，exit125。

唯一自动post：admin_postexit.py --post-exit-export，原冻结host在active返回后真实发起，exit0。确切argv见[active调用](evidence/ACTIVE_ENTRY_INVOCATION.json)和[post计划](evidence/STARTUP_POSTEXIT_PLAN.json)。

另有4次行政WSL调用：57文件部署/原生语法；基础只读平台预检；拒绝后的1241运行时hash/包日志/空对象审计；57源＋3现行库只读导出。全部精确argv/双流/耗时/SHA见[行政命令计划](evidence/ADMIN_COMMAND_PLAN.json)及commands/01–04.result.json。

共6次WSL调用＝1 active＋1自动post＋4行政。没有依赖安装、系统配置修改、reset-failed、WSL重启、手工seal或目标重跑。其余主机步骤仅授权/摘要、原件审查、报告与包验证。
''')
report('EVIDENCE_INDEX.md','TR-A证据索引','''
|主题|工件|
|---|---|
|20项回答|[TRA_FINAL_DECISION](TRA_FINAL_DECISION.md)|
|授权/锁|[原文](evidence/TASK_REQUEST.txt)、[回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json)、[59项准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json)|
|资源静态界|[预算重算](evidence/RESOURCE_ADMISSION_PROOF.json)|
|实际结果/首错|[ACTUAL_RESULTS](evidence/ACTUAL_RESULTS.json)、[FIRST_FAILURE](evidence/FIRST_FAILURE.json)|
|原始双流|[active stdout](evidence/windows_entry.stdout.raw)、[active stderr](evidence/windows_entry.stderr.raw)、[post stdout](evidence/STARTUP_POSTEXIT.stdout.raw)、[post stderr](evidence/STARTUP_POSTEXIT.stderr.raw)|
|调用时间|[active调用](evidence/ACTIVE_ENTRY_INVOCATION.json)、[active退出](evidence/WINDOWS_ENTRY_EXIT.json)、[时间线](evidence/EXECUTION_TIMELINE.json)|
|行政包|[原结果](evidence/STARTUP_FINALIZATION.json)、[14/15逐流验证](evidence/AUTOMATIC_ADMIN_VERIFICATION.json)|
|未执行项|[152项/25变异登记](evidence/UNRUN_CASE_REGISTER.json)|
|环境差异|[1241运行时核对/包日志](evidence/RUNTIME_DRIFT_AUDIT.json)、[3份实际文件导出锁](evidence/DRIFTED_RUNTIME_EXPORT_LOCK.json)|
|源码保持|[59项导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[源后核](evidence/SOURCE_AFTER_CHECK.json)|
|历史/交付|[旧归档](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[8017基线](evidence/BASELINE_LOCK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

Windows行政保存目录D:/毕业设计/DCL-R6-isolated-verification/batch13仅包含FROZEN_TR及preflight_runtime_snapshot，实际Linux /var/lib/dcl-r6/batch13不存在。最终研究包包含export/frozen与export/current-runtime成员，避免将主机保存目录解释为正式实例。
''')
report('README.md','DCL-R6-TR-A','''
原生预检拒绝运行时闭包漂移：ld-linux/libc/libm三项hash不符，冻结入口exit125。T0/R/claim/正式实例未创建，PT/PF/TR及25变异全部未执行。

自动行政故障封存14/15成功，native NOT_APPLICABLE、内部UNKNOWN。源不变、重跑0、安装/重锁/清理0。后续先做独立运行时适配与资格审查，当前attempt保留。

[最终20问](TRA_FINAL_DECISION.md) · [授权](TRA_AUTHORIZATION_AND_LOCK.md) · [启动](TRA_BOOT_AND_WORK_RESULTS.md) · [终态读取](TRA_TERMINAL_READ_RESULTS.md) · [活动守卫](TRA_ACTIVE_GUARD_RESULTS.md) · [TR40](TRA_TR40_RESULTS.md) · [兼容回归](TRA_COMPATIBILITY_RESULTS.md) · [native](TRA_NATIVE_SEAL_RESULTS.md) · [行政](TRA_ADMIN_FINALIZER_RESULTS.md) · [内部](TRA_INTERNAL_STATE_RESULTS.md) · [资源](TRA_RESOURCE_ACCOUNTING.md) · [时间](TRA_EXECUTION_TIMELINE.md) · [差异](TRA_COUNTEREXAMPLES.md) · [证据索引](EVIDENCE_INDEX.md) · [下一适配范围](NEXT_PLATFORM_ADMISSION_REQUEST.md)
''')
print(json.dumps({'required_reports':13,'markdown_files':len(list(O.glob('*.md'))),'overall':R['overall'],'tests_executed':0,'automatic_admin':'SEALED14/15'},ensure_ascii=False))
