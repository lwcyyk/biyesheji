"""Create reports from observed administrative extractions; no target execution."""
from pathlib import Path
import json

E=Path(__file__).resolve().parent;O=E.parent
def load(name):return json.loads((E/name).read_bytes())
def report(name,body):(O/name).write_text(body.strip()+'\n',encoding='utf-8')
P='Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。\n\n'
account=load('RESOURCE_ACCOUNTING.json');identity=load('BOOT_IDENTITY_AND_FAILURE.json');cases=load('CASE_DURATIONS.json');audits=load('COMPLETED_NATIVE_AUDITS.json');handoff=load('C09_ACTUAL_HANDOFF.json');c00=load('C00_ACTUAL_FIELDS_AND_TIMING.json');receipt=load('AUTHORIZATION_RECEIPT_LOCK.json');native=load('NATIVE_ZIP_CHECK.json')
boot=account['T0'];runboot=identity['run_boot_id']
report('CALDIAG_AUTHORIZATION_AND_LOCK.md','# CalDiag授权与执行锁\n\n'+P+f'''本次用户原文明确批准方案B=CALIBRATE_S1S9_ONLY，使用申请中尚未建立运行窗的batch09-r1身份。原batch09旧记录是静态准备失败，本次建立新的动态实例；旧工件和旧锁保持。实际控制路径为DCL-R6-B09-Supplement/authorization/batch09-r1，报告与当前新增证据保存在本目录。

|对象|实际绑定|
|---|---|
|manifest|c7bed9528ea4a6ada08882d02be23dd37c62e8ee79fbb70a9445ddcc361ea127|
|execution_lock|fcc70f0d78aefc1ccc1fcc96489a3984417c6b4b7f203c78162c910b64746b81|
|授权原文SHA|{receipt['request_sha256']}|
|实际回执SHA|{receipt['receipt_sha256']}|
|boot_id|{runboot}|
|Root owner|PID4259/start135655，跨exec及内部恢复尝试保持|
|Linux源/活账|/var/lib/dcl-r6/cr09 / /var/lib/dcl-r6/batch09|
|T0/deadline/stop_at|{account['T0']:.9f} / {account['deadline']:.9f} / {account['stop_at']:.9f}|
|scope|CALIBRATE_S1S9_ONLY；Calibrate_only=true，Full=false|

42份冻结文件及28程序在host核验通过，41份Linux文件逐项部署/摘要/Root元数据及原生语法核验通过。当前CPython3.12.3、工具/stdlib树、systemd、kernel、UID999/GID989、cgroup和单位资源由冻结单会话预检fresh核验；原始命令和双流完整保存。host入口只设置PYTHONDONTWRITEBYTECODE=1保护冻结工作区，原生argv保持-I -S -B。

预检PREFLIGHT_PASS，同boot同PID exec及一次认领通过，C00取得实际PASS。实际入口调用1、允许的同父内部恢复尝试1、成功恢复准入0。F1/F4批准位false，模型执行0。首次关键失败后保留原T0/账，追加冻结关闭和封存函数调用属于本次停止授权，运行case新增0。

[授权原文](evidence/TASK_REQUEST.txt) · [实际回执](evidence/execution_authorization.json) · [入口计划](evidence/ACTIVE_ENTRY_INVOCATION.json) · [源/范围准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [原生部署](evidence/DEPLOYMENT_RESULT.json)。
''')

report('CALDIAG_EXECUTION_TIMELINE.md','# CalDiag实际执行时间线\n\n'+P+f'''时间主线采用本批CLOCK_BOOTTIME，T0={account['T0']:.9f}。journal服务跨度单列MONOTONIC，各自同boot内作差。Windows UTC/perf_counter只作host调用证据。

|事件|BOOTTIME或相对T0|实际证据|
|---|---|---|
|预检开始/通过|1356.587195913 / 1357.428358928|预检观测跨度0.841163015秒|
|same-PID exec后entry验证|1357.707236031|owner4259/start135655|
|T0建立|1357.752228527|原窗口1次|
|C00实际服务确认|1358.123037115|PID4322/start135795、同boot|
|READY64收据采样|1367.333902934|47 PASS＋17 MUTATION_DETECTED|
|RootIPC56收据采样|1395.408516584|48 PASS＋8 MUTATION_DETECTED|
|BC40收据采样|1405.657504726|30 PASS＋10 MUTATION_DETECTED|
|Launcher原生waitpid|1406.135674940|PID4314，raw5888/exit23|
|C09退出见证发布采样|1406.287321124|持久ACK/Receiver/Root见证绑定|
|真实C09 PASS|T0+{account['C09_completed_from_T0']:.9f}|HANDOFF_VERIFIED/classification_count=1|
|同父恢复entry验证|1406.427000870|同owner；新scheduler PID4804|
|恢复健康检查失败|T0+{account['failure_from_T0_interval'][0]:.9f}至+{account['failure_from_T0_interval'][1]:.9f}|UNREVIEWED_MANAGER_FAILURE，精确raise时刻未打点|
|原入口返回|host累计50.3556852秒，exit125|时钟域为Windows perf_counter|
|初次事后快照|AWAIT_EXPECTED_RESUME、无CLOSED/原生seal|Payload为空，external-stop4318仍在|
|追加冻结关闭|T0+{account['CLOSED_marker_from_T0']:.9f}|CLOSED=CALDIAG_ABORT_AFTER_RESUME_MANAGER_FAILURE|
|清理确认/冻结seal完成|T0+{account['frozen_cleanup_finish_from_T0']:.9f}|角色全空，R不变|

失败位于恢复前言，早于launcher.lock及清理try块，后继C10尚未启动。Receiver在等待恢复时清空coordinator_identity；父协调器对普通wait返回的125直接退出，未进入异常清理。因此初始CLOSED和seal均缺失，Root停止器继续等待。本轮保存607份初始文件后，经授权调用原冻结stop_tree/seal完成关闭；保留612份最终快照及两次独立manifest。

关闭后state文档仍保留AWAIT_EXPECTED_RESUME作为原始状态；CLOSED文件为吸收标记，准入函数优先据此拒绝后续工作。本轮没有改写该状态字段来伪造恢复成功或关闭时间。

[启动/失败区间](evidence/BOOT_IDENTITY_AND_FAILURE.json) · [初次审计](evidence/POSTRUN_AUDIT.json) · [冻结补充清理](evidence/FROZEN_FAILURE_CLEANUP.json) · [最终审计](evidence/FINAL_POSTRUN_AUDIT.json)。
''')

rows=[]
for r in cases['cases']:
    def f(x):return 'UNRUN/UNMEASURED' if x is None else f'{x:.6f}'
    rows.append('|'+ '|'.join([r['case_id'],r['status'],f(r['service_startup_span']),f(r['service_envelope_span']),f(r['child_span']),str(r['fsync_count']),f(r['fsync_total_seconds'])])+'|')
suite_rows=[]
for r in audits['native_independent_audits']:
    suite_rows.append(f"|{r['receipt']}|{r['visits']}|{r['charged_work_observed_span']:.6f}|{r['time_scope']}|")
report('CALDIAG_CASE_DURATION_REPORT.md','# Case实际耗时及测量边界\n\n'+P+'''|case|结果|服务启动秒|服务包络秒|child秒|已记录fsync数|fsync累计秒|
|---|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

服务启动=journal Starting→Started；包络=Starting→terminal，均为journal MONOTONIC。child采用原BOOTTIME spawn_request→wait_return。C06/C07/C09的系统级失败退出为指定故障，其Root校准裁决是PASS。

fsync仅统计原程序已落盘的instrumented聚合；C06/C07/C09的0表示聚合文件缺失或未写出，实际持久化时间保持UNMEASURED。线程/阶段可能重叠，fsync累计值可超过对应服务墙钟，无法直接作为完整时间分区。纯程序、监督等待、清理和写证缺独立起止打点时保持PARTIAL/UNMEASURED。

|Root/合成阶段收据|访问增量|实际观测跨度秒|边界|
|---|---:|---:|---|
'''+ '\n'.join(suite_rows)+'''

上述Root阶段从第一笔持久PREP采样起算；READY/IPC/BC到Root收据sample，H34到最后COMMITTED采样。函数前言与最终收据发布处于边界外，实际阶段总时间还包含这些开销。嵌套子case不与所属阶段重复相加。

已测Root跨度最长为IPC56 11.392948秒，其次BC40 10.200091、READY64 8.899268、H34至少7.649303。payload服务包络最长为C09H 7.135260，其次C02 2.788151和C06 2.160464。C09H落盘fsync累计6.364018秒提示已观测持久化开销突出，当前资料仍不足以推出剩余S34/门18的完整耗时。

[逐case机器结果](evidence/CASE_DURATIONS.json) · [测量覆盖](evidence/MEASUREMENT_COVERAGE.json) · [journal原件](evidence/FINAL_RUN_BOOT_JOURNAL.stdout.raw)。
''')

crows=[];visits={'C00':1,'C01':1,'C02':32897,'C03':4097,'C04':2,'C05':19,'C06':1,'C07':1,'C08':1,'C09':1}
for n in range(13):
    c='C%02d'%n;crows.append(f"|{c}|{'PASS' if n<10 else 'UNRUN_AFTER_RESUME_FAILURE'}|{visits.get(c,'0（未启动）')}|")
fieldrows=[]
for r in c00['samples'][-1]['checks']:
    fieldrows.append('|'+r['check_id']+'|'+str(r['expected'])+'|'+str(r['observed'])+'|'+r['result']+'|')
report('CALDIAG_RESOURCE_CALIBRATION.md','# C00–C12实际校准结果\n\n'+P+'''|case|本轮结果|实际访问|
|---|---|---:|
'''+ '\n'.join(crows)+'''

C02按N=32,896一次持久范围后由child扣减，实际内存探针PASS；C03共享页和C04第5任务拒绝PASS；C05并发局部17成功/1拒绝；C06时间停止、C07控制器exit23、C08 watchdog故障均按预期PASS。真实C09取得PASS。恢复前言失败使C10–C12保持UNRUN。

C00最终八项双侧实际值：

|字段ID|期望|实际双侧|结果|
|---|---|---|---|
'''+ '\n'.join(fieldrows)+f'''

当前C00先观察到STARTING/STARTING，随后两轮READY/READY；前五凭据在STARTING按合同defer为NOT_READY，最终全部MATCH。屏障返回区间为{c00['wait_return_interval'][0]:.9f}–{c00['wait_return_interval'][1]:.9f}秒，重复验证结束为请求后{c00['second_validation_end_from_request']:.9f}秒。独立pidfd时刻/后侧原始stat/精确返回点继续缺打点，诊断完整性FIELD_EVIDENCE_PARTIAL保留。

BC40已完成：30 PASS＋10 MUTATION_DETECTED；它是冻结模拟启动回归。真实前缀另有单会话、同PID、sealed认领及服务内复核证据，真实交接后的C10连续性资格仍未取得。

[八字段与原始来源](evidence/C00_ACTUAL_FIELDS_AND_TIMING.json) · [原生检查摘要](evidence/COMPLETED_NATIVE_AUDITS.json) · [实际环境绑定](evidence/RUNTIME_EXPECTED_AND_OBSERVED_BINDING.json)。
''')

report('CALDIAG_ROOTIPC_AND_C09_RESULTS.md','# RootIPC与C09真实结果\n\n'+P+f'''RootIPC56全部获原生独立oracle接受：48 PASS＋8 MUTATION_DETECTED，访问505。UID999读取共享对象、Root私有对象保护、原子发布、停止/等待夹具和8项变异已按冻结范围验证。该套件通过与后续完整生命周期出现的新失败分别保留。

C09H34全部获原生独立oracle接受：28 PASS＋6 MUTATION_DETECTED；含Root原始复核共访问273。

真实C09成功链已取得：当前意图、Receiver4318确认、持久ACK、Launcher4314实际exit23、Root4259直接waitpid raw5888、当前状态fresh-read、HANDOFF_VERIFIED及classification_count=1。ACK/见证/结果的窗口、锁、授权SHA、boot、T0和R=38,729一致，原件摘要吻合。

|实际时间书签（BOOTTIME）|值|
|---|---|
|ACK确认|{json.dumps(handoff['acknowledged_at'],ensure_ascii=False)}|
|退出见证采样|{handoff['exit_witness_sample']['boottime']:.9f}|
|C09 PASS|{handoff['C09_result_sample']['boottime']:.9f}，T0+48.592009253秒|
|同父内部恢复|entry已验证；准入在manager检查处失败，resume_count=0|

交接成功收据证明真实C09这一阶段；完整恢复及后续C10资格仍未取得。失败后发现等待态coordinator身份被清空、普通非零退出缺关闭收敛；本轮通过冻结stop_tree/seal补充关闭，原R及T0保持。

独立原始复核的完成范围是READY64/RootIPC56/BC40/C09H34；host仅核对Root结果、原件摘要及账格式，没有在关闭后重跑目标oracle。S34/门18与完整资源门原始复核保持UNRUN。

[真实交接证据](evidence/C09_ACTUAL_HANDOFF.json) · [完成套件原始摘要](evidence/COMPLETED_NATIVE_AUDITS.json) · [失败与收敛缺口](evidence/FIRST_FAILURE_AND_CLOSURE_GAP.json)。
''')

report('CALDIAG_S1_S9_RESULTS.md','# S1–S9真实执行状态\n\n'+P+'''S1–S9全部34项统一UNRUN_AFTER_RESUME_FAILURE。RANGE service启动数0，冻结17个safe及17个mutant的原始S轨迹均尚待生成。本轮fault_triggered、detected、逐job费用与退出状态为null。

首次关键错误发生在C09之后、C10之前。当前全局账健康及其他套件通过不授予S1–S9通过结论。原S34源码/夹具与其N=4/cap=8/全局20,000等上限保持冻结，本轮没有删减测试、额外执行或生成固定PASS结果。

后续先修复恢复健康检查与失败关闭路径，再申请新的独立校准窗口，S34及原始预算故障检查继续是完整资源资格的必需项目。

[最终机器裁决](evidence/CALDIAG_RESULT.json) · [case时间表](evidence/CASE_DURATIONS.json)。
''')

report('CALDIAG_GATE18_RESULTS.md','# 18项负向资格门实际状态\n\n'+P+'''顶层18项统一UNRUN_AFTER_RESUME_FAILURE。原17项没有进入执行；新增GATE-LEDGER-ANOMALY的健康控制、13异常和4个mutant也均UNRUN，实际拒绝原因/故障触发/变异检出数为null。GATE_NEGATIVE_AUDIT与GATE_LEDGER_QUALIFICATION的当前批资格文件均未生成。

实际回执、冻结输入和执行清单均绑定18项；调度在更早的恢复manager检查失败后停止，新增用例保持原件待运行状态。当前全局账的行政格式核对通过仅说明已产生账的一致性，新增异常门的动态检出责任继续未完成。

RESOURCE_GATE_PASS=NOT_OBTAINED。F1/F4维持UNRUN_RESOURCE_GATE，本次scope即使全门通过也只允许诊断关闭。后续正式批次需要重新取得当批资格。

[机器状态](evidence/CALDIAG_RESULT.json) · [原始账行政核验](evidence/JOURNAL_ACCOUNTING.json) · [冻结42项](evidence/SOURCE_AND_SCOPE_ADMISSION.json)。
''')

report('CALDIAG_RESOURCE_ACCOUNTING.md','# CalDiag资源、持久账与关闭核算\n\n'+P+f'''最终R=38,729/1,000,000；1,739组PREPARED/COMMITTED完整配对、3,478行journal。counter、最终intent及全部顺序范围一致；3个精确范围信用替代逐次事务，未用信用保守占用。

|实际计费阶段|访问|
|---|---:|
|C00–C08|37,020|
|READY64|449|
|C09H34＋Root原始重算|273|
|RootIPC56|505|
|BC40|481|
|真实C09|1|
|合计|38,729|

原全批1,800/校准300/提前1,740秒，校准100,000访问，单进程AS1GiB及Payload父4tasks保持。C02 child按合同降至96MiB，C04实际第5任务拒绝，观测最大任务数4。跨case/父组快照所见charged memory peak最大128,413,696B=122.46484375MiB；该值是已采到的内核计费峰值，精确RSS树峰值及Root RSS峰值仍UNMEASURED。Root/外部可信编排器和清理行政进程单列，清理进程设置AS1GiB。

T0={account['T0']:.9f}；deadline={account['deadline']:.9f}；stop_at={account['stop_at']:.9f}。最后完成C09在T0+48.592009253；失败区间T0+48.699583118–48.738270904。停止器因关闭缺口继续等待，初次快照记录Payload为空、Root停止器仍在。追加冻结关闭于T0+299.567904452发布CLOSED，T0+299.993796083完成seal并确认角色全空。该生命周期保留实际诊断/导出/清理时间，校准本身尚未完整完成。

初始607常规文件与最终612常规文件分别保留；冻结源导出42项。CLOSED权威标记存在，state原AWAIT_EXPECTED_RESUME字段保持原件，后续准入优先读取CLOSED。清理前后counter/journal/intent的SHA完全一致，退款/重置/新增测试访问0。

冻结seal包含610行文件manifest、611个ZIP条目，{native['bytes']}B，SHA `{native['sha256']}`；逐流检查差异0。控制socket等非regular对象只记录元数据。最终Payload及Root角色为空，父cgroup不存在。旧历史账及原失败保持。

[账格式与配对](evidence/JOURNAL_ACCOUNTING.json) · [资源书签](evidence/RESOURCE_ACCOUNTING.json) · [冻结清理](evidence/FROZEN_FAILURE_CLEANUP.json) · [原生seal核验](evidence/NATIVE_ZIP_CHECK.json)。
''')

report('CALDIAG_TIME_FEASIBILITY.md','# 300秒时间可行性裁决\n\n'+P+'''**TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。总体RESOURCE_GATE_FAILED，首次错误属于验证基础设施恢复/收敛问题。**

完整校准实际总耗时=null，因为执行在恢复前言中止。最后完整case为C09，T0后48.592009253秒PASS；失败发生在48.699583118–48.738270904秒区间。首个尚未启动case为C10，其后的C11/C12/S34/门18/总资源资格均未运行。

300秒软截止没有构成本次首次失败原因。补充关闭在T0+299.567904452发布标记，T0+299.993796083确认清理/seal完成；这些接近300秒的生命周期观察包含失败后Root停止器等待与人工诊断/导出，保留在总账，同时与正常校准前缀分别呈现。

已完成Root收费阶段观测跨度：IPC56 11.392948、BC40 10.200091、READY64 8.899268、H34至少7.649303秒。service包络最长C09H 7.135260秒。C02 child本次2.362582833秒。这些是当前部署、当前r1和当前范围的实测证据，尚未覆盖完整RANGE和新预算异常门的主要未知成本。

因此本轮既未授TIME_FEASIBILITY_OBSERVED_PASS，也未把首次失败归为INCONCLUSIVE_LIMIT。下一阶段优先静态修复manager健康检查对预期故障单位的处理，以及等待恢复/非零退出的关闭收敛；重新冻结后申请新的独立方案B测量，维持原300秒及访问/AS/任务硬限。当前技术条件仍不足以直接申请正式F1/F4运行。

[逐case耗时](CALDIAG_CASE_DURATION_REPORT.md) · [测量缺口](evidence/MEASUREMENT_COVERAGE.json) · [首次失败](CALDIAG_COUNTEREXAMPLES.md)。
''')

report('CALDIAG_COUNTEREXAMPLES.md','# CalDiag首次失败与基础设施反例\n\n'+P+'''|登记|真实见证|性质与边界|
|---|---|---|
|CD-1 恢复manager拒绝|same-PID resume entry已验证；scheduler4804在guard.py:976抛UNREVIEWED_MANAGER_FAILURE、exit125|新恢复准入/执行编排缺陷；实际C06/C07/C09预期故障单位处于failed，Root结果均PASS|
|CD-2 关闭收敛缺口|原父调用返回125后无CLOSED/无seal，状态AWAIT_EXPECTED_RESUME，coordinator和launcher身份均null，external-stop4318仍在|完整控制流未保证非零退出后关闭；本轮观察并保存等待态，随后经授权冻结关闭|

CD-1：原systemd健康检查只接受mnt-e.mount。C06时间停止、C07预设exit23、真实C09停止controller都产生本批failed单位，它们对应当前锁和Root实际PASS。恢复时同一全局谓词将这些状态当作未审阅失败；本轮事后失败列表明确包含c06/c07/c09。精确抛错调用的stdout未落盘，故当时循环最先遇到哪个单位保留UNRECORDED，不用事后顺序填值。

CD-2：健康检查位于_launcher_body清理try之前；父launcher普通wait路径直接返回子进程125，异常清理和“已有CLOSED才seal”的finally均未触发。c09_handoff.observe_exit在HANDOFF_VERIFIED后清空coordinator_identity，external_stop只有该身份存在时才检查Root丢失。两处组合形成已观察的等待空窗。Payload已空、预算保持，资源资格仍关闭，未产生模型业务执行。

本轮按停止授权调用原冻结stop_tree/seal，未修改源、判据、权限或上限，没有重跑、再次激活或新建预算窗。保留初始607与最终612文件及完整命令/时间/账。Native C09真实交接PASS与后续恢复失败分别裁决。

下一静态修复应限制于：按当批受保护结果/原件识别预期故障单位，其他未审阅失败继续拒绝；把恢复前言及普通非零退出纳入关闭收敛；在等待恢复期间保留可监控的Root责任与校准截止。历史失败单位的后续管理也应形成明确、可审阅策略。本轮仅记录这些具体需求，代码保持冻结。

D1/D2正式协议反例0；本轮新增的是验证基础设施的真实控制流反例。batch07具体C00失配仍UNRESOLVED，原条件/强G/严格分离0保持。

[首错原件](evidence/windows_entry.stderr.raw) · [结构化失败证据](evidence/FIRST_FAILURE_AND_CLOSURE_GAP.json) · [初始审计](evidence/POSTRUN_AUDIT.json) · [冻结关闭命令](evidence/CLOSE_FAILED_BATCH.py)。
''')

answers=[
('1 新执行身份','PASS：batch09-r1/当前boot/源/输入/单位/账/回执/argv完整绑定'),
('2 预检及C00','PREFLIGHT_PASS / SAME_BOOT_CONFIRMED / C00_PASS；八字段双侧MATCH'),
('3 BootContinuity40','30 PASS＋10 MUTATION_DETECTED；完整恢复连续性仍未完成'),
('4 C00–C12','C00–C09全部PASS；C10–C12 UNRUN_AFTER_RESUME_FAILURE'),
('5 RootIPC56','48 PASS＋8 MUTATION_DETECTED'),
('6 C09H及真实C09','28 PASS＋6 MUTATION_DETECTED；真实HANDOFF_VERIFIED/ACK/waitpid PASS，恢复准入失败'),
('7 S1–S9','34项UNRUN_AFTER_RESUME_FAILURE'),
('8 门18','原17和新聚合全部UNRUN；健康/13异常/4mutant实际结果null'),
('9 原始重算','完成套件的原生独立审核有效，原件SHA一致；全链重算未完成'),
('10 全校准耗时','null；C09前缀48.592009253秒，首次失败区间48.699583118–48.738270904秒'),
('11 300秒条件','TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE；未取得完整完成实测'),
('12 最长观测项','Root套件IPC56 11.392948秒；payload service C09H 7.135260秒，范围及重叠单列'),
('13 资源资格','RESOURCE_GATE_PASS=NOT_OBTAINED'),
('14 资源/退出','R38,729、1,739事务/3,478行；charged peak观测122.46484375MiB、最大tasks4；补充冻结关闭后角色全空'),
('15 新缺陷','恢复manager对预期故障单位拒绝；等待恢复/非零退出未自动关闭，已保存反例'),
('16 F1/F4技术条件','尚缺C10–C12/S34/门18/全链资格与时间证据；模型启动0'),
('17 下一阶段','先最小静态修复具体恢复/收敛缺陷，再以新身份/锁申请独立校准诊断')]
report('CALDIAG_FINAL_DECISION.md','# CalDiag最终裁决\n\n'+P+'''**RESOURCE_GATE_FAILED；首次关键错误为恢复入口UNREVIEWED_MANAGER_FAILURE。TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。真实C09及四套前序检查已取得实际证据，完整资源资格仍关闭。**

|最终问题|真实回答|
|---|---|
'''+ '\n'.join('|'+a+'|'+v+'|' for a,v in answers)+'''

本次入口1次、允许的同父内部恢复尝试1次（成功0）、测试重跑0、源码/判据/权限/上限现场修复0、T0/预算重置0、自动下一批0。初始未关闭的等待态和停止器已取证；随后按本次停止授权调用冻结stop_tree/seal，CLOSED标记在T0+299.567904452发布，清理确认在+299.993796083完成。counter/journal/intent字节保持，最终Payload/Root角色为空、父cgroup不存在。

C00–C09及READY64/IPC56/BC40/H34的通过只归本次实际范围。194项合成/混合回归的原生检查结果为153 PASS＋41 MUTATION_DETECTED；新ledger聚合与S34尚未运行。当前boot、Root4259/start135655、Sender4314/Receiver4318及新scheduler4804的角色时序均保存。额外pidfd精细打点缺口保留FIELD_EVIDENCE_PARTIAL。

F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]，D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持。后续正式模型批次需新明确授权和新当批动态资格，当前已CLOSED窗口保持关闭。

[首次失败及最小修复方向](CALDIAG_COUNTEREXAMPLES.md) · [真实时间裁决](CALDIAG_TIME_FEASIBILITY.md) · [资源核算](CALDIAG_RESOURCE_ACCOUNTING.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('README.md','''# DCL-R6-CalDiag

真实方案B诊断，batch09-r1。RESOURCE_GATE_FAILED / TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。

C00–C09及READY64、H34、RootIPC56、BC40实际完成；真实C09交接PASS。恢复manager健康检查失败，后继C10–C12/S34/门18保持UNRUN。R38,729，追加冻结关闭后CLOSED、角色全空、预算不变，F1/F4未启动。

[最终裁决](CALDIAG_FINAL_DECISION.md) → [失败与修复方向](CALDIAG_COUNTEREXAMPLES.md) → [时间表](CALDIAG_CASE_DURATION_REPORT.md) → [证据索引](EVIDENCE_INDEX.md)。
''')
print(json.dumps({'reports_created':12,'RESOURCE_GATE_PASS':'NOT_OBTAINED','status':'RESOURCE_GATE_FAILED','time':'TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE','target_replays':0},ensure_ascii=False))
