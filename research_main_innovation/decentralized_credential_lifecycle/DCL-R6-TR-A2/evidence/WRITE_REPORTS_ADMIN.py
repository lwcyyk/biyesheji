"""Reports of actual normal A2 execution; no checker/API/seal replays."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;O=E.parent
def load(name):return json.loads((E/name).read_bytes())
R=load('ACTUAL_RESULTS.json');N=load('NATIVE_SEAL_VERIFICATION.json');A=load('AUTOMATIC_ADMIN_VERIFICATION.json')
passport='Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。'
gates='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。'
def report(name,title,body):
    with(O/name).open('x',encoding='utf-8') as f:f.write('# '+title+'\n\n'+passport+'\n\n'+body.strip()+'\n\n'+gates+'\n')
report('TRA2_AUTHORIZATION_AND_LOCK.md','A2授权、来源前提与执行锁','''
**已在授权声明的TCB前提下完成正常最小A2：新运行时预检、WORK/C00、PT64/PF48/TR40/RA32、CLOSED/只读/活动拒绝、native及自动行政封存。** 来源条件独立保留。

|绑定|实际结果|
|---|---|
|版本|RuntimeAdapt-static-1/r1，64项/44程序，Linux部署62项|
|manifest SHA|738eb2982953971f94019b913f6b302808f9b7a8d29e784038e8e6babb50de89|
|execution_lock SHA|691f2503f2db6906552241692db0b27ec6a982a7c738839d99f3cd93f3729da6|
|源/实例/slice|/var/lib/dcl-r6/ra01；/var/lib/dcl-r6/batch14；dclr6batch14.slice|
|control|DCL-R6-RuntimeAdapt-Fix/authorization/batch14-r1，新建真实原文/回执|
|boot|27e8416d-3ba4-46fd-8b42-75e983f2dcfa，实际预检/运行/post一致|
|身份|Root Owner449/start3530；当前scheduler/stopper及Payload身份见原始实际结果|
|隔离预检|新运行目录/单位/组尚无，Root/Payload残留0；初始failed仅mnt-e.mount|
|历史保护|执行前8605份文件锁，4根导航另存原字节，误路径47只读/hash|

用户第三节允许在冻结声明的Root/dpkg/keyring及无并发特权运行时更新条件下验证；回执据此将RuntimeAdapt_provenance_assumptions位设true。缺独立8.12 .deb payload事实保持，不宣称来源完全独立。scope仅PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START，Full/MR/预窗注入false；C09兼容位只是冻结schema字段。

完整静态计费：C00=1、PT1089、PF817、TR681、RA545，完成3133、阶段A硬4417、完整硬68498。184合成job含33变异。实际R3133，已按同一账完成，无预算重置或第二窗口。

[源码与范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [原文](evidence/TASK_REQUEST.txt) · [回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json) · [计费准入](evidence/RESOURCE_ADMISSION_PROOF.json) · [源后核](evidence/SOURCE_AFTER_CHECK.json)
''')
report('TRA2_RUNTIME_IDENTITY_RESULTS.md','新运行时磁盘与实际加载身份','''
**RA-D1=PASS_DYNAMIC，范围为本批已观察检查点。RUNTIME_PROVENANCE_CONDITIONAL继续保留。**

|组件|SHA-256|Build-ID|
|---|---|---|
|ld-linux-x86-64.so.2|5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f|231ab65dd867a89dce29cb958fd5ca50abb1aa34|
|libc.so.6|755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a|8cebda42d140fc2b09639f8b13a5d5f2e617ef09|
|libm.so.6|5dcc4d25466e29ca390ed6fabb371c69b65dff6fa4e91c34561057a020d6994a|f772fc0c42a75e38f138f8b66f1ebc8aad060525|

原生static_A runtime_identity保存Root449的full bytes/build-id/packages/maps结果，三项每个5个映射段均与磁盘inode/device一致。C00启动/探针结果保存Payload实际pid的包和自身映射检查；观察位置、pid/boot、inode/device与scope原字段保留在下方JSON。

GNU libc上游2.39、Ubuntu精确2.39-0ubuntu8.12。libc6/libc-bin状态install ok installed/amd64及已安装目录匹配；Python3.12.3执行文件身份和原锁一致。基础环境和完整原生runtime预检实际通过，旧TR-A失配记录不追溯修改。

full观察中SHA/Build-ID重新读取；服务内full=False路径输出的SHA为已绑定合同值、字节由先行原Guard manifest循环核验，再校自身映射。报告区分这两种verification_scope，未把合同值伪装成重复独立计算。

点位检查不提供path→exec原子性、永久身份或Root特权更新阻断；缺新.deb独立payload再现和信任Root/dpkg/keyring条件保持。

[所有实际运行时回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json) · [实际预检stdout](evidence/windows_entry.stdout.raw) · [绑定合同](evidence/FROZEN_SOURCE_REFERENCE/inputs/runtime_identity_contract.json)
''')
report('TRA2_NATIVE_COMPATIBILITY_RESULTS.md','原生兼容性与资源接口结果','''
**RA-D2=PASS_DYNAMIC，范围为获批正常A2路径。** 新运行时下CPython、单会话启动、当前映射与C00资源接口实际运行，未观察到动态链接/符号加载错误。

原生预检两侧完成、Root449同PID进入ENTRY_VERIFIED，sealed capability/一次认领保持，随后原Root/scheduler/停止器关系建立。C00八项主比较及辅助资源检查均MATCH，实际工作进入RUNNING。

C00实际Payload RLIMIT_AS软/硬1GiB，任务/身份/cgroup/NoNewPrivileges等按原readiness比较通过。Node-free包读取没有增加Payload子进程；捕获的任务最大观测为3，父limit4。hash读取、flock、fsync、waitpid、终态共享锁及ZIP写读在相应真实路径被执行。

这不等同于C01–C12/S34/门18完整资源资格、全部ABI行为或完整300秒性能通过。未故意破坏系统库/包/加载路径测试故障，也没有旧ELF的执行或安装操作。

[实际C00比较](evidence/C00_READINESS_SUMMARY.json) · [运行时回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json) · [完整实际资源](evidence/ACTUAL_RESULTS.json)
''')
report('TRA2_BOOT_AND_WORK_RESULTS.md','独立启动、WORK/C00与正常关闭','''
**新batch14完成真实预检、一次初始化、ARMED→RUNNING及C00，active/外层均exit0。**

Root449/start3530，PREFLIGHT_BEGIN BOOTTIME35.607296158，QUALIFIED36.627432549，ACTIVATION_REQUESTED_ONLY36.652742307，ENTRY_VERIFIED37.020294117。当前boot27e8416d…贯穿执行和自动post。

真实T0=37.238567090，deadline=1837.238567090，stop_at=1777.238567090，counter一次建立并最终3133。私有phase版本0–6、最终公开/私有RUNNING/6及Root当前身份保留原件，C00实际PASS。旧TR-A未运行的程序和预算未被恢复。

执行顺序严格为C00、PT64、PF48、TR40、RA32，随后正常CLOSED，未进入READY64/MR/C09/C01–C12/S34/门18或模型。正常结束原stop_tree原因PT_MINIMAL_RUNTIME_DIAGNOSTIC_COMPLETE。

[实际结果/角色身份](evidence/ACTUAL_RESULTS.json) · [完整时间线](evidence/EXECUTION_TIMELINE.json) · [C00八项](evidence/C00_READINESS_SUMMARY.json)
''')
report('TRA2_TR40_RESULTS.md','TR40与八项变异原生结果','''
**TR-D3=PASS_DYNAMIC，范围TR-SIMULATION/1。** 40/40接受：32 PASS＋8 MUTATION_DETECTED；未触发/漏检0。

预算before1907、after2588，消费681＝entry1＋40×(driver16＋Root审查1)。实际40份tr_case、input SHA、raw trace、binding、native oracle结果和raw_sha逐项对应，退出后只核验字节/结构，没有重放checker。

grant_terminal_work、rebuild_budget、skip_identity、default_deadline、ignore_journal、upgrade_unknown、false_seal、write_original均实际命中各冻结目标违规。主实例预算和状态没有为合成故障被修改。

TR40提供策略和观察模型覆盖，真实CLOSED后的读取另有独立terminal_seal_review、native输入摘要和活动拒绝回执。每case提供driver访问区间、审查预付、raw sample及charged-prefix时间，完整独立case/oracle耗时未打点，保持UNKNOWN。

[184项逐项输入/结果/路径/SHA/预算/时间范围](evidence/TEST_CASE_RESULTS.json) · [真实终态读取](TRA2_TERMINAL_READ_RESULTS.md)
''')
report('TRA2_PT_PF_COMPATIBILITY.md','PT/PF及RA32兼容回归','''
**TR-D4=PASS_DYNAMIC（本批冻结合成范围）。** PT64=55 PASS＋9变异检出，PF48=40 PASS＋8变异检出。当前源码/运行时/身份重新取证，未借用旧112项资格。

PT预算1→1090，消费1089；PF1090→1907，消费817。新增RA32在TR之后执行，24 PASS＋8变异检出，预算2588→3133消费545。新RA32范围RA-SIMULATION/1，包/路径/Build-ID/预加载/新旧混用/跨batch/漂移决策为合成输入，实际系统库没有被破坏。

四套总184job＝151safe＋33mutant，均由原生独立oracle接受。Root资格绑定源/contract/checker/raw/input哈希，完整集合和计数匹配。数据审查没有修改allowed_violations或将预期填充为结果。

此前PT/PF历史通过原样保留；本批兼容通过只覆盖当前四个版本化模型/清单，无法替代未来版本fresh资格和完整资源链。

[全部实际原件定位](evidence/TEST_CASE_RESULTS.json) · [计费一致性](evidence/BUDGET_AUDIT.json)
''')
report('TRA2_TERMINAL_READ_RESULTS.md','真实CLOSED后的终态只读结果','''
**TR-D1=PASS_DYNAMIC（本批正常终态）。** CLOSED后原生调用read_terminal_evidence(...NATIVE_SEAL)实际返回VALID，原window、R和journal完整可读。

|字段|实际值/原名|
|---|---|
|batch/original boot|batch14 / 27e8416d-3ba4-46fd-8b42-75e983f2dcfa|
|读取者|review.exit_evidence.reader，当前Root协调器449/start3530|
|生命周期/版本|CLOSED存在，原phase=RUNNING/sequence6；未改写原phase|
|T0/deadline/stop_at|37.238567090 / 1837.238567090 / 1777.238567090|
|最终R/事务|3133 / 3133，journal_status=CONSISTENT|
|关闭原因|PT_MINIMAL_RUNTIME_DIAGNOSTIC_COMPLETE|
|CLOSED sample|102.107384106|
|读取完成sample|102.254985296，晚于CLOSED|
|返回|decision.read_status=VALID，runtime_authority=NONE|
|工作/预算/phase/Launcher|四项allowed均false；native_ready仅为封存前提|

原记录摘要由实际读取生成，之后与原生包成员和退出后独立导出逐项相同。T0/deadline/stop_at、R、journal、CLOSED、运行点及Source执行锁绑定均未变。调用者另写Root私有terminal_seal_review，stage=PRE_NATIVE_ARCHIVE_READ_ONLY_REVIEW，属于获批审查证据输出，接口本体没有写入原运行记录。

receipt内native_status=UNRESOLVED属于当时尚未生成ZIP的事实；真实完成状态由后续原生ZIP/manifest及独立校验确认，未倒填该pre-native原件。

每字段沿用同一个read sample与原evidence_digests，逐文件读取起止未打点。该范围的字节比较与冻结只读控制流支持不变性；未额外声称排除未经观察的特权瞬态修改。

[只读前后摘要比对](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json) · [完整原读取回执](evidence/ACTUAL_RESULTS.json)
''')
report('TRA2_ACTIVE_GUARD_RESULTS.md','CLOSED后活动态拒绝与权限边界','''
**真实活动接口拒绝已取得，TR-D2=CONDITIONAL_PASS，范围边界分别保留。**

只读返回后，冻结caller执行check_active_runtime→原G.root_checkpoint，实际抛IPC_CLOSED_DOMINATES，sample102.255073341；原异常码和读取者身份保存。CLOSED在102.107384106已持久化，该拒绝没有发放工作或修改预算。

terminal decision中work_allowed/budget_init_allowed/phase_write_allowed/launcher_allowed全false，runtime_authority=NONE；原G.state/预算/一次认领/phase保护代码保持。TR40与PT/PF/RA模型覆盖闭态预算重建、信用、状态恢复、身份/损坏等拒绝。

主实例未在CLOSED后直接调用真实Budget初始化/预留、Launcher重启或真实WORK写入制造破坏；这些实际写路径的强行负向执行保持未覆盖。实际健康/RootIPC拒绝与合成权限模型分开，保持条件性结论。

[实际拒绝与不变性](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json) · [TR40/其他合成结果](evidence/TEST_CASE_RESULTS.json)
''')
report('TRA2_NATIVE_SEAL_RESULTS.md','native seal真实执行与独立核验',f'''
**TR-D5=PASS_DYNAMIC，NATIVE_SEAL_COMPLETED。** 原停止器等待后，真实终态输入完整、活动拒绝证明保存，原生manifest/ZIP实际生成。

pre-native review sample102.254985296、active拒绝102.255073341；manifest sample102.273823167。sealer为当前Root协调器，直接waitpid和角色/组证据在原件中；G.seal按原格式返回ZIP摘要，active进程最终exit0。单独的精确G.seal函数入口/返回时刻未打点，实际receipt/产物/自动审计提供区间与结果。

原生manifest233项，ZIP234 entries，{N['ZIP_bytes']}字节。CRC、全部成员bytes/SHA、内嵌manifest原字节与当前独立导出均一致。ZIP SHA-256：`{N['ZIP_sha256']}`。

Native输入包含真实window、3133最终账及journal、CLOSED、phase/version、Source/锁/回执、直接waitpid/停止记录，以及Root私有只读review。review中的evidence_digests与归档及最终导出精确一致；没有Source/账修复或手工seal重放。

原PFA native UNRESOLVED保持，旧TR-A无窗口NOT_APPLICABLE保持。本批native完成只证明当前原件封存，不升级内部UNKNOWN、来源可信等级或资源总资格。独立行政结果另列。

[完整逐流校验](evidence/NATIVE_SEAL_VERIFICATION.json) · [终态输入比对](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json) · [157?原件导出锁](evidence/NATIVE_EXPORT_LOCK.json)
''')
report('TRA2_ADMIN_FINALIZER_RESULTS.md','自动行政finalizer结果',f'''
**自动行政流程原生完成ADMIN_EVIDENCE_SEALED，TR-D6整体CONDITIONAL_PASS。** 完整产物和触发得到直接证据，精细资源前后遥测仍缺少原始字段。

冻结host在active返回后自动执行固定ra01/src/admin_postexit.py --post-exit-export；Root actor938/start10246、boot27e8416d…、UID0，post exit0、WSL客户端reaped=true。新匹配器在目标模块加载前核运行时，源/合同/Root映射路径检查正常，未出现链接或导入错误。

原AS1GiB/单次30秒在源/模块装载之前设置，原生继承timer/AS条件检查成功；实际admin deadline132.492325035，审计sample102.546541884。精确Live RLIMIT数值、导入开始、cwd/GID/cgroup没有单列原始回执，不能用Payload数值补充。host post耗时6.610676100秒，低于30/35秒界。

导出235项Native原件，行政manifest249项、ZIP250 entries，{A['ZIP_bytes']}字节。全部CRC/SHA、内嵌manifest及235项自动/独立导出匹配。自动ZIP SHA：`{A['ZIP_sha256']}`。

本批native完成、internal UNKNOWN、process cleanup confirmed均按原字段独立保存。额外兜底/手工finalize/人工清理0；最终研究包仅读取既有自动包并汇总证据，未替代自动流程。

[自动原结果](evidence/STARTUP_FINALIZATION.json) · [249/250独立校验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json) · [原始post双流](evidence/STARTUP_POSTEXIT.stdout.raw)
''')
report('TRA2_INTERNAL_STATE_RESULTS.md','内部状态、CLOSED与退出分轴','''
**TR-D7=UNKNOWN。** 正常关闭路径仍未生成mr_close_state，原terminal审查和自动行政字段都保持internal UNKNOWN。

|轴|实际结果|
|---|---|
|STOP_REQUEST|正常结束无此文件，未人工补写|
|CLOSED|102.107384106正常原因持久化|
|child退出|当前协调器直接waitpid，raw0/exit0|
|角色/cgroup|原stop_result0/empty；自动和独立审计均确认空|
|预算|3133/3133事务/6266行一致，读取与归档未变|
|native seal|真实COMPLETED233/234|
|行政|自动SEALED249/250|
|内部收据|缺失，保留UNKNOWN；原batch_state仍CALIBRATING，CLOSED支配后续资格|

内部缺件没有被native或行政成功覆盖。原冻结规则允许正常关闭证据完整时封存一个仍含UNKNOWN的真实快照；本批保持该适用范围，没有引入新状态收敛规则或倒填历史。

本批已关闭，claim/T0/R和全部原件保留，不继续旧窗口。新root行政/只读导出进程均结束，人工/外部停止后备0。

[实际状态/退出/停止汇总](evidence/ACTUAL_RESULTS.json) · [原始journal](evidence/JOURNAL_MESSAGE_INDEX.json) · [终态证据](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json)
''')
report('TRA2_RESOURCE_ACCOUNTING.md','实际预算、时间与资源',f'''
**R=3133，等于冻结正常完成计费，低于阶段A硬4417。TR-D8=CONDITIONAL_PASS：当前最小前缀观测符合范围，完整资源校准尚未取得。**

|指标|实际值|
|---|---|
|C00/PT/PF/TR/RA|1 / 1089 / 817 / 681 / 545|
|journal|3133 PREPARED/COMMITTED对，6266行，连续0→3133，每次amount1|
|counter/intent|BRNGv001/cap1000000/used3133，COMMITTED after3133，字节在读取/封存后相同|
|T0/deadline/stop_at|37.238567090 / 1837.238567090 / 1777.238567090|
|T0→CLOSED|{R['T0_to_CLOSED_seconds']:.9f}秒|
|T0→terminal review|{R['T0_to_terminal_review_seconds']:.9f}秒|
|T0→native manifest|{R['T0_to_native_manifest_seconds']:.9f}秒|
|active host|79.446917700秒；含客户端开销/两侧时钟观察范围|
|全部host|86.799039300秒，含自动post|
|自动post|6.610676100秒|
|Payload charged peak|{R['charged_memory_peak_observed_bytes']}字节＝{R['charged_memory_peak_MiB']:.7f}MiB；该parent代memory.peak，区别于RSS|
|Payload tasks保存观测|3，父TasksMax/pids.max4；C04第五任务测试未执行|
|C00 RLIMIT_AS|实际soft/hard均1GiB，原process值保留|
|Root/全树精确RSS/tasks峰|UNKNOWN；行政live RLIMIT数值未独立采样|

终态API是有界只读行政IO，不创建额度或debit R；四套模型测试按同一预算prepay计费。生产oracle在有效窗口内执行，退出后仅结构/SHA审查，没有checker重放。

完整硬68498≤100000、总1000000/1800、校准300、预T0120、提前1740及AS1GiB/父4tasks未放宽。当前约65秒是最小正常前缀，不能线性外推完整C/MR/S/门18链。新checker增加映射/包/文件IO，未来完整300秒时间可行性继续UNRESOLVED。

[3133事务审计](evidence/BUDGET_AUDIT.json) · [阶段A界证明](evidence/RESOURCE_ADMISSION_PROOF.json) · [每case访问/时间范围](evidence/TEST_CASE_RESULTS.json) · [真实资源](evidence/ACTUAL_RESULTS.json)
''')
timeline=load('EXECUTION_TIMELINE.json')['native_boottime'];rows='\n'.join('|'+x['event']+'|'+format(x['boottime'],'.9f')+'|'+format(x['T0_offset'],'.9f')+'|' for x in timeline)
report('TRA2_EXECUTION_TIMELINE.md','A2执行与封存时间线','''
以下为同boot CLOCK_BOOTTIME原始采样及相对T0偏移；具体fsync、flock和kernel exit瞬间缺独立打点的项保持UNKNOWN。

|事件|BOOTTIME秒|T0偏移秒|
|---|---:|---:|
'''+rows+'''

host active UTC2026-11-13 10:51:02.502176–10:52:21.947396；全部host10:51:02.243471–10:52:29.040661；自动行政封存10:52:29.022951。guest UTC与host UTC、BOOTTIME/MONOTONIC各自保存，差值不作精确跨时钟证书。

seal入口/返回和完整per-case/oracle耗时没有单独事件，实际review/manifest/auto审计提供可靠区间。每case的charged-prefix→raw sample间隔包含预算IO、排除后续persist/oracle，明细保留完整语义。

[全量时间JSON](evidence/EXECUTION_TIMELINE.json) · [journal消息](evidence/JOURNAL_MESSAGE_INDEX.json)
''')
report('TRA2_COUNTEREXAMPLES.md','本批未决边界与反例范围','''
**本批未观察到非预期关键执行失败。** 正常WORK/C00、184模型检查、终态读取、活动拒绝、native和自动行政均取得对应原件；下列边界继续单列。

|编号|实际范围/限制|
|---|---|
|A2-PROV|缺8.12新.deb独立payload再现，TCB-conditional来源结论保留；用户显式批准位不变成无条件来源证明|
|A2-IDENTITY|当前Root/Payload磁盘/自身映射相符；没有path→exec原子或阻止未来特权更新的证明|
|A2-INTERNAL|正常路径缺mr_close_state，internal UNKNOWN原件保持，未用封存成功升级|
|A2-NEGATIVE|184项为明确标记的合成模型输入；系统库、真实预算、Root state或其他单位未被破坏做OS故障|
|A2-TELEMETRY|锁/逐文件IO/完整case和import起点、行政Live RLIMIT等细粒度字段部分未发出；不从其他PID或旧批次补值|
|A2-RESOURCE|仅C00和最小前缀资源观测，未跑完整校准和完整300秒链|

pre-native review中的native_status UNRESOLVED准确反映当时尚未打包，后续Native和自动结果COMPLETED属于新时点事实；没有倒填或更写该review。旧TR-A/PFA失败及UNKNOWN全部保持。

本批源码/系统库修改、安装/重锁、测试重跑、手工seal、后备清理和免费窗口均0。下一步可准备独立MR有限验证申请及必要新身份/摘要，当前不自动启动。

[原生包完整性](evidence/NATIVE_SEAL_VERIFICATION.json) · [来源/映射回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json) · [终态比对](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json)
''')
report('TRA2_FINAL_DECISION.md','TR-A2最终动态裁决','''
**正常最小TR-A2取得CONDITIONAL_PASS：新运行时、WORK/C00、四套184项/33变异、真实CLOSED只读、活动拒绝、native与自动行政均完成；来源/内部/范围条件继续保留。**

|验收门|状态|范围|
|---|---|---|
|RA-D1 运行时身份|PASS_DYNAMIC|本批Root/Payload检查点3组件/路径/包/Build-ID/自身映射匹配|
|RA-D2 原生兼容|PASS_DYNAMIC|获批正常A2 Python/资源接口/启动及封存；非全部ABI/完整资源链|
|TR-D1 终态只读|PASS_DYNAMIC|CLOSED后VALID原window/R/journal/phase/退出；关键摘要三侧相同|
|TR-D2 安全守卫|CONDITIONAL_PASS|实际IPC_CLOSED_DOMINATES，其他破坏性真实请求未执行，模型覆盖单列|
|TR-D3 TR40|PASS_DYNAMIC|TR-SIMULATION/1：32safe＋8变异检出|
|TR-D4 PT/PF兼容|PASS_DYNAMIC|PT55/9、PF40/8；另RA24/8，均当前版本原生模型结果|
|TR-D5 native|PASS_DYNAMIC|233 manifest/234 ZIP entries，原始输入与CRC/SHA完整|
|TR-D6 自动行政|CONDITIONAL_PASS|自动249/250完整，资源先行成功控制流支持，精细原始回执缺项保留|
|TR-D7 内部终态|UNKNOWN|缺正常MR关闭收据，原UNKNOWN保持|
|TR-D8 资源|CONDITIONAL_PASS|R3133、正常约65秒、实际C00限额/观测符合，完整资格/峰/300秒未证明|

关键事实：新batch14/当前boot/一次认领/同PID有效，T0只创建一次；C00八项全部MATCH。PT64/PF48/TR40/RA32共184项接受，151safe＋33mutant，所有预期变异检出。R3133、3133事务/6266行，读取和封存不改变原账。

CLOSED后终态review读取真实37.238567090/1837.238567090/1777.238567090、R3133；原活动接口实际IPC_CLOSED_DOMINATES。Native包与行政包独立完成并逐流验证，extra fallback/manual0。角色/组空，counter/window/claim与CLOSED保留，未在当前窗口继续MR或模型。

RUNTIME_PROVENANCE_CONDITIONAL持续，缺新.deb payload及path→exec原子边界未升级。internal UNKNOWN可与真实原件封存同时存在；本批没有修改内部状态或旧native未决。旧PFA112/17与R1907、TR-A preflight失败、TerminalRead静态和所有旧锁保持。

本批具备准备下一独立MR/C09有限验证申请的正常前缀依据，仍需新批次/完整锁及fresh准入和明确许可；完整C00–C09/C09/MR64/C10–C12/S34/门18资格链未执行。当前不授予RESOURCE_GATE_PASS或F1/F4运行资格。

[实际全量结果](evidence/ACTUAL_RESULTS.json) · [未决边界](TRA2_COUNTEREXAMPLES.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('NEXT_INDEPENDENT_STAGE.md','下一独立MR有限验证准备边界','''
本文件仅记录下一研究阶段条件，未创建新身份、回执或运行窗口。

当前最小A2正常前缀已取证，后续可独立审阅最新RuntimeAdapt/TerminalRead下的C00–C09、真实C09与ManagerRecovery有限验证方案。需机械派生新namespace、完整最终摘要、准确预算/argv与新用户许可；batch14已CLOSED，当前T0/R不能继续使用。

保留来源TCB前提、身份替换窗口、内部UNKNOWN及遥测范围。新方案如需内部收敛规则或细粒度原生观测，先列最小静态修改范围；没有凭封存或组空推定完整内部成功。

完整C/MR/S/门18资源资格与300秒性能仍未取得。后续即使有限MR验证成功，完整RESOURCE_GATE_PASS与F1/F4另按新的授权与证据裁决。
''')
report('COMMAND_SUMMARY.md','实际命令和调用分类','''
WSL实际5次＝1冻结active＋1冻结自动post＋3行政（62源部署/compile、只读基础环境、退出后完整235原件/64源/journal导出）。精确argv、raw双流、SHA与耗时见[行政计划](evidence/ADMIN_COMMAND_PLAN.json)及commands/01–03.result.json。

active为/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ra01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch14；自动post为同解释器/参数的admin_postexit.py --post-exit-export。均Ubuntu-24.04/root，active/post/外层exit0。

唯一host入口及其内部实际argv见[调用原件](evidence/ACTIVE_ENTRY_INVOCATION.json)和[post计划](evidence/STARTUP_POSTEXIT_PLAN.json)。没有当前源码修复、系统库写入、依赖安装、WSL主动重启、手工seal/API/checker重放或下一批自动启动。
''')
report('EVIDENCE_INDEX.md','TR-A2证据索引','''
|主题|工件|
|---|---|
|裁决|[TRA2_FINAL_DECISION](TRA2_FINAL_DECISION.md)、[全量实际JSON](evidence/ACTUAL_RESULTS.json)|
|授权/锁|[用户原文](evidence/TASK_REQUEST.txt)、[回执](evidence/execution_authorization.json)、[绑定](evidence/AUTHORIZATION_RECEIPT_LOCK.json)、[64项准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json)|
|运行时/兼容|[实际Root/Payload身份回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json)、[C00八项](evidence/C00_READINESS_SUMMARY.json)|
|四套184项|[原input/trace/hash/oracle/预算/时间范围](evidence/TEST_CASE_RESULTS.json)|
|终态/守卫|[关键原件摘要不变与实际拒绝](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json)|
|预算|[3133事务/6266行独立审计](evidence/BUDGET_AUDIT.json)|
|Native|[233/234逐流核验](evidence/NATIVE_SEAL_VERIFICATION.json)|
|自动行政|[原计划](evidence/STARTUP_POSTEXIT_PLAN.json)、[原结果](evidence/STARTUP_FINALIZATION.json)、[249/250核验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json)|
|时间/退出|[时间线](evidence/EXECUTION_TIMELINE.json)、[journal原文](evidence/RUN_BOOT_JOURNAL.stdout.raw)、[消息索引](evidence/JOURNAL_MESSAGE_INDEX.json)、[退出后审计](evidence/POSTRUN_AUDIT.json)|
|原件和源码|[235 Native导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[64源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[源后核](evidence/SOURCE_AFTER_CHECK.json)|
|历史/交付|[旧包](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[8605基线](evidence/BASELINE_LOCK.json)、[历史保持](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

完整原件D:/毕业设计/DCL-R6-isolated-verification/batch14/native_snapshot、FROZEN_RA；最终研究ZIP对应export/native和export/frozen。自动Native/行政包保持原名及真实hash，研究包只汇总。能力nonce保留私有原件/本地包，不在报告展开。
''')
report('README.md','DCL-R6-TR-A2','''
正常最小A2已取得条件性通过：新运行时预检/实际Root与Payload映射、WORK/C00、PT64/PF48/TR40/RA32共184项及33变异，真实CLOSED只读与活动拒绝、native233/234、自动行政249/250全部取得原始证据。

R3133，角色/组空，源码修改/重跑/后备0；internal UNKNOWN、条件性来源和点位身份/完整资源性能边界保留。资源资格与模型实施门未升级，旧batch和当前CLOSED不恢复。

[最终裁决](TRA2_FINAL_DECISION.md) · [授权](TRA2_AUTHORIZATION_AND_LOCK.md) · [运行时](TRA2_RUNTIME_IDENTITY_RESULTS.md) · [兼容](TRA2_NATIVE_COMPATIBILITY_RESULTS.md) · [启动](TRA2_BOOT_AND_WORK_RESULTS.md) · [TR40](TRA2_TR40_RESULTS.md) · [PT/PF/RA](TRA2_PT_PF_COMPATIBILITY.md) · [终态](TRA2_TERMINAL_READ_RESULTS.md) · [守卫](TRA2_ACTIVE_GUARD_RESULTS.md) · [native](TRA2_NATIVE_SEAL_RESULTS.md) · [行政](TRA2_ADMIN_FINALIZER_RESULTS.md) · [内部](TRA2_INTERNAL_STATE_RESULTS.md) · [资源](TRA2_RESOURCE_ACCOUNTING.md) · [时间](TRA2_EXECUTION_TIMELINE.md) · [边界](TRA2_COUNTEREXAMPLES.md) · [证据索引](EVIDENCE_INDEX.md) · [下一独立阶段](NEXT_INDEPENDENT_STAGE.md)
''')
# Fix a count label in the native link without rewriting any source or original.
p=O/'TRA2_NATIVE_SEAL_RESULTS.md';p.write_text(p.read_text(encoding='utf-8').replace('157?原件导出锁','235项原件导出锁'),encoding='utf-8')
print(json.dumps({'required_reports':15,'markdown_files':len(list(O.glob('*.md'))),'checks':184,'mutants':33,'native':'COMPLETED','admin':'SEALED','internal':'UNKNOWN'},ensure_ascii=False))
