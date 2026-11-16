"""Write authorized research/approval artifacts, with no mechanism changes."""
from pathlib import Path
import ast,hashlib,json
O=Path(__file__).resolve().parent.parent;P=O.parent;E=O/'evidence'
def j(n):return json.loads((O/n).read_bytes())
def save(n,x):
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def text(n,s):
 with(O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s.strip()+'\n')
q=j('proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json');q['fsync_attempts_upper']=798
(O/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
w=j('evidence/WORK_MEMORY_FD_MODEL.json');w['steps'][1]['complexity']='O(263*Lmax+266*Lcursor); <=798 durability attempts including2 failure-record fsyncs and1 initial log-directory fsync; stop/native seal work separately accounted'
(E/'WORK_MEMORY_FD_MODEL.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
hist=j('evidence/HISTORICAL_NATIVE_LOG_ACCOUNTING.json');L=j('evidence/NATIVE_RECORD_BYTE_ALGEBRA.json')['record_upper_bytes'];gj=j('evidence/GLOBAL_JOURNAL_BYTE_MODEL.json');z=j('evidence/ZIP_BOUND_ALGEBRA.json')
gates=j('evidence/BC_GATE_DECISIONS.json');summary=j('evidence/ANALYSIS_SUMMARY.json')
S=E/'FROZEN_RA_ORIGINALS';cfg=json.loads((S/'inputs/c09_contract.json').read_bytes())
save('evidence/C09H34_FROZEN_INVENTORY.json',{'jobs':[{'case_id':r['case_id'],'events':r['events'],'event_count':len(r['events']),'mutant':r.get('mutant')} for r in cfg['jobs']],
 'jobs_count':34,'total_event_rows':204,'actual_max_events':8,'contract_max_events':64,'mutants':6,'native_Root_log_quota_applies':False,
 'observation':'Synthetic H1-H8 finite traces; old observed28 PASS+6 mutants retained; no fixture/native test executed this turn'})
separation=[
 {'candidate':'PENDING quota','input_family':'X_n: one handoff, n repeated valid missing-witness observations','metric':'Persisted bytes, observation work, durable write count',
 'G':'Bounded append log + pre-debited event/byte quota + fail-closed cursor','prediction':'Same chosenQ and schema bounds: O(Q*L), no strict difference','gap':0,'instance':'For n=17 or n=257 the generic quota can make exactly the same accept/stop decision and preserve the same original prefix','status':'COVERED_BY_G'},
 {'candidate':'Versioned capacity','input_family':'Y_m: m original files with explicit path/byte/hash manifest','metric':'Metadata bytes, total read/write/hash work',
 'G':'Versioned verification contract + standard ZIP manifest and explicit file/byte caps','prediction':'Same O(m+B) verification and same original set','gap':0,'instance':'The1082-path witness is accepted/rejected identically under the same chosencount/byte policy','status':'COVERED_BY_G'},
 {'candidate':'Segmented archive','input_family':'Z_{m,s}: m originals partitioned into s standard segments','metric':'Complete-set validation work and lossless retained bytes',
 'G':'Standard archives + content-addressed/versioned root and per-segment manifests','prediction':'Same full-set/hash checks; generic method can use identical segmentation','gap':0,'instance':'Two standard segments bound by one root manifest incur the same required full-object reads','status':'COVERED_BY_G'},
 {'candidate':'MR cross-instance evidence','input_family':'A native scenario certificate applicable to one explicitly bound B instance','metric':'Native fault-test count and verifier/current-state check work',
 'G':'Version-bound software qualification evidence + exact target/current-state revalidation','prediction':'Same limited evidence class and same current B obligations','gap':0,'instance':'One A result and one B can be checked by the same generic source/TCB/identity/hash predicates','status':'COVERED_BY_G'}]
save('evidence/GENERAL_G_COMPARISON.json',{'comparisons':separation,'strict_separation_instances':0,'candidate_implementation_code':0,
 'scope':'Applicable mature engineering constructions; no global algorithmic optimality claim','protocol_G_context':'Original BASELINE_G and SEPARATION_GATE retain their broader D1/D2 metrics and prior rejected separation claims'})
producer_context=[
 {'category':'Native formal handoff','source':'c09_handoff.py:event/publish/sender_prepare/Receiver.observe_exit','rows':'6 stage +1ACK+Ncheck; only EXIT_CLASSIFICATION_CHECK can repeat indefinitely in contract model','native_log':True,'fsync':True},
 {'category':'C09H34 synthetic traces','source':'c09_regression.py:52-75','rows':'204 frozen event JSON files +34 oracle files; per-step c09h charge; no Root handoff log append','native_log':False,'fsync':'G.write metadata file/directory barriers'},
 {'category':'Independent C09 oracle','source':'c09_oracle.py:read/truth/check_job','rows':'Reads raw fixture rows, returns result; no native append','native_log':False,'fsync':False},
 {'category':'RootIPC synthetic wait/fault tests','source':'root_ipc_regression.py:permission_case/wait_case/semantic_case/run_suite','rows':'56 raw case rows plus bounded scenario files; PENDING-like labels are synthetic cases','native_log':False,'fsync':'Publication/fixture-specific'},
 {'category':'Root recovery/MR','source':'manager_recovery.py:event/health/resume/abort','rows':'mr_events.jsonl (per row<=32768), first-failure/close/credit/role records; no c09_events append','native_log':False,'fsync':True},
 {'category':'waitpid coordinator','source':'guard.py:1222-1234; c09_handoff.py:297-321','rows':'One protected scheduler waitpid file plus one C09 witness; waiting reads stage, no direct event append','native_log':False,'fsync':'Root publication'},
 {'category':'STOP/CLOSED','source':'guard.py:request_stop/stop_tree; manager_recovery.abort','rows':'Fixed STOP/CLOSED and bounded wrapper stop results/errors; no recursive native PENDING producer','native_log':False,'fsync':True},
 {'category':'native seal/errors','source':'guard.py:993-1027/finally; terminal_evidence.py','rows':'Read-only pre-review, native manifest/ZIP, SEAL_ERROR and stderr; no c09_events append','native_log':False,'fsync':'Mixed existing guarantees, errors stay real'},
 {'category':'Administrative finalizer','source':'startup_lifecycle.post_exit_export; host/startup_finalize.py','rows':'Separate control/snapshot/audit/admin manifest/ZIP/final receipt; current ROOT originals read-only','native_log':False,'fsync':'Existing administrative record/export rules'}]
save('evidence/PRODUCER_CONTEXT_MATRIX.json',{'contexts':producer_context,'all_current_source_sink_calls':3,'new_logging_code':0})

passport='Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。'
tail='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。'
def doc(n,title,s):text(n,f'# {title}\n\n{passport}\n\n{s}\n\n{tail}')
doc('C09_PENDING_PRODUCER_AUDIT.md','C09 PENDING生产与消费全路径审计','''
基线RuntimeAdapt-static-1/r1的64份源码/输入逐件匹配冻结锁；上轮8份审查对象和合同锁保持。c09_handoff.py SHA-256为0441874d3eec62720b920a48077bc52f4f3db9c64e3c21f3aa3aa97cd43e109f，与历史CalDiag部署副本完全相同。

|原生生产点|进程/阶段|触发与重复性|可变字段/持久化/约束|
|---|---|---|---|
|c09_handoff.py:75–84 event sink|实际调用者的Root身份|向inputs/root_private/c09_events.jsonl追加一行|compact JSON＋UTF-8＋LF，O_APPEND/O_NOFOLLOW，Root0600，逐条fsync；sink自身无行长/总量/终态守卫|
|publish:85–89；调用187/226/232/262/286/343|初始scheduler、Receiver、恢复scheduler|6种进度stage；单handoff下各最多一次|base identity/window/time/hash/revision；不把publish.extra或resources整图展开到event|
|sender_prepare:196|初始scheduler/COMMITTED后|SENDER_ACK_OBSERVED，冻结调用一次|仅追加commit_sha256；peer、fresh commit和live sender核验；RPC连接等待没有重发PREPARE业务循环|
|Receiver.observe_exit:277|独立external-stop Receiver/退出观察阶段|EXIT_CLASSIFICATION_CHECK；witness缺失时PENDING可重复|固定16项facts＋verdict；check_base默认允许sender已退出；每次append/fsync，缺记录/字节额度|

进度创建路径PREPARING→READY→COMMITTED→EXIT_OBSERVED→VERIFIED→RESUMED依次受旧state存在、当前PID/boot/window/counter、持久ACK和一次性分类/恢复约束。HANDOFF_FAILED仅在STAGES声明中，当前原生代码没有对应publish调用。原生日志没有task_id字段；重复对象为同一handoff_id。

waitpid生产者为guard.py:1225及coordinator_witness:309。父协调者未运行/见证持久发布尚未完成时，Receiver看到witness=None；就绪pidfd在PENDING返回后保留，select可立即再次返回。其余消费者读取commit/witness/result/原始H34资格，不把日志PENDING数量当作已受限条件。

C09H34实际204个事件、34个oracle文件，最大单job8事件，合同上限64。它们由UID999受控服务产生合成H1–H8轨迹，每事件收费；当前原生忙等自环没有从这些费用中取得隐含配额。RootIPC56和MR64的REVIEW_PENDING等合成标签与原生日志分别登记。

STOP_REQUEST可以在一次已入锁观察检查之后出现，因此当前代码允许一条在途记录晚于STOP；不能声称“终态标记后绝无日志写”。CLOSED在可信生命周期锁下阻止后续入口，VERIFIED早返回，resume仅记录RESUMED。stop/abort/native seal/admin没有递归调用本原生event sink，错误记录转入mr/SEAL_ERROR/stderr等各自对象。

[3个原生event调用及6个stage位置](evidence/C09_NATIVE_PRODUCERS.json) · [全部上下文矩阵](evidence/PRODUCER_CONTEXT_MATRIX.json) · [逐行源码](evidence/SOURCE_EXCERPTS.json) · [C09H34原输入](evidence/C09H34_FROZEN_INVENTORY.json)。''')
doc('C09_PENDING_RECORD_BOUND.md','记录数上界与可达自环','''
结论：**C09_PENDING_RECORD_BOUND_UNPROVABLE_UNDER_CURRENT_CONTRACT**。单handoff的合法状态转换数量有限；同一状态的PENDING观察次数缺少数值上界。

初态为已PREPARE/COMMIT/持久ACK、Receiver已在sender活着时取得pidfd、sender随后os._exit(23)，父协调者仍存活但尚未发布waitpid见证。当前boot/身份、票据/ready、counter/ACK/window匹配，STOP/CLOSED均缺，handoff.observe_until仍有正余量。

第一次observe_exit把stage从HANDOFF_COMMITTED发布为LAUNCHER_EXIT_OBSERVED，revision从3变4。check_base(require_sender_live=False)允许已退出sender，self.durable核验ACK，witness=None；classify得到PENDING，277行追加/fsync后278行返回。

guard._external_stop_impl的799–805行仅在VERIFIED关闭/清空pidfd，CLOSED触发停止；PENDING分支保留就绪fd，也不进入else的sleep。下一轮Receiver.poll无socket请求可立即返回，M.supervision只核当前责任和deadline，然后重走相同路径。stage/revision4/classification_count0/resume_count0与R都可保持。

对任意有限n，选择正余量tau小于剩余12秒/校准/stop截止，在tau内延迟父协调者，安排n次Receiver路径，其余监督保持健康。当前合同没有给这条立即返回/编码/append/fsync路径可靠的最短耗时；故无法从tau推得固定n上界。该结论针对源码与合同调度模型，未声称固定物理机器无限吞吐，也没有执行新的调度/故障实验。

完整成功日志总记录可写作N_pending＋8：6个stage＋1ACK＋1终态分类；首次失败前缀不超过对应进度类别，但N_pending项仍无界。classification_count约束成功交接只分类一次，未对此前反复判断计数。当前无自动创建第二handoff/第二恢复/新预算窗口。

历史CalDiag的同字节C09源码实际产生17 PENDING＋1 VERIFIED；无RESUMED，故总24=17＋7。17条都处于revision4、同一handoff_id，原全局journal在该PENDING区间追加0条。历史支持该自环可达，不能给出其最坏最大次数。

[可复核状态与调度族](evidence/COUNTEREXAMPLE_FAMILY.json) · [状态/记录公式](evidence/NATIVE_STATE_RECORD_PROOF.json) · [历史原件统计](evidence/HISTORICAL_NATIVE_LOG_ACCOUNTING.json)。''')
doc('C09_PENDING_BYTE_BOUND.md','单条编码、总量与配额合同',f'''
现行event没有显式单行字节检查。对固定原生调用点，字段为封闭schema，pid/ticks/clock/boot取受信ABI值；原生PENDING行不含task_id、自由错误文本、traceback、raw systemd返回或resources大对象。

|参数|宽度假设|来源/证明边界|
|---|---:|---|
|batch_id、mode|7、27字节|固定ASCII身份及C09可达scope；新身份超长须重算|
|boot UUID、各hash|36、64字节|kernel UUID与SHA-256 hex|
|revision|1字符|冻结进度最多6；PENDING保持4|
|PID、start_ticks、utc_ns|10、20、20字符|pid_t32、proc计数u64、CPython时钟i64的明确ABI假设|
|JSON binary64数值|25字符|17位有效数值与符号/小数/指数的保守编码界|
|witness退出值|11字符|保守带符号整数退出值；PENDING固定null|

compact sorted JSON默认ensure_ascii=True，当前字符串均白名单ASCII，不产生额外转义；每行计入1 LF。通用Unicode扩展若获准，应另计BMP/非BMP转义（每code point最多12个ASCII字节），当前1322界不自动覆盖。

序列化骨架加上述数值宽度得到：PENDING≤1298、任意分类行≤1322、stage≤948、ACK≤1028字节。该结果为**CONDITIONAL_PROVED**，条件为固定调用者/schema/命名及ABI宽度；源码没有逐字段range/digit/byte validator，任意外加Root调用或未知ABI不属于该证明。

现行总量B_pending=ΣL_i，N_pending缺上界，故总量仍UNRESOLVED。27144字节/最大实测行1211只属于历史，未用平均值或历史峰值推最坏界。

独立待批配额草案：256次分类尝试，最多255条PENDING，最后1槽仅供终态分类；再计6个stage＋1ACK，原生主日志最多263行。256来自已使用的native-review块尺度，作为新的独立政策额度；它既非状态机隐含上界，也不挪用旧MR的256额度。

记录实际类型上界：255×1298＋1×1322＋6×948＋1028=339028字节。为分类前预扣最坏槽位，合同按256×1322＋6×948＋1028=345148字节预留，不退还未用字节；sidecar≤956、固定失败摘要≤333，保留对象合计≤346437。cursor中的reserved/debited字段不冒充实际写入数量。

额度共享单一batch/boot/handoff绑定；Receiver独占分类额度，Sender/恢复stage与ACK类别各有固定次数；全部原生生产者共用总字节界。预付应在C09控制器/ready marker/counter冻结之前完成，之后只更新独立Root保护cursor，全球R/ACK counter保持。

追加前先校验字段类型/长度与身份/截止/终态，持久预扣一次完整槽位，再写原始行/fsync；模糊持久化立即停止并保留原件，余额不退、缺/错配cursor不重建。第256次仍PENDING时只保存固定错误码摘要并请求关闭，不追加第256条PENDING。耗尽表示资源/观察限额，不构成协议反例或交接PASS。

任何有限次数可能在父协调者获CPU前被合法快速轮询耗尽，故该政策有明确活性代价，历史17条只提供一个可行观测。cursor/锁序/首错/崩溃恢复和新字段校验的最小实施仍需新授权与静态接线审查。

[单行代数与骨架](evidence/NATIVE_RECORD_BYTE_ALGEBRA.json) · [具体待批配额](proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json)。''')
doc('C09_PENDING_COUNTEREXAMPLES.md','最小反例族与阻止条件','''
反例只需一个合法handoff和一个缺waitpid见证的窗口；任务数、批次数、模型访问额均无需增长。输入族X_n变化的是调度次序：同一sender已退出、相同durable ACK、相同Receiver和Root owner，让父协调者的见证发布推迟到n次Receiver观察之后。

轨迹骨架：COMMITTED/revision3 → EXIT_OBSERVED/revision4 → [witness=None；R=R0；PENDING；append+fsync]^n → 父waitpid/见证 → VERIFIED一次。每次自环仅新增原生记录，不推进classification_count/恢复次数，不消费Budget.visit或c09h_charge。日志增长至少n行及其正字节长度。

|具体阻止条件|实际后果|与族X_n的关系|
|---|---|---|
|pidfd尚未取得而sender已消失|G.identity(target)可能先拒绝|族要求sender活着时已装好fd|
|ACK/binding/ticket/counter不匹配|check_base/分类拒绝|族固定这些原件有效且不变|
|wrong witness退出码|FAILED，首次异常关闭|族在重复区间witness缺失，之后只允许真实23|
|CLOSED已存在|入口返回CLOSED，追加前终止|族在截止前无终态标记|
|handoff截止先到|check_base先拒绝；分类中跨界最多一条FAILED|族只取有正余量的有限前缀|
|HANDOFF_VERIFIED已持久化|observe_exit早返回，不再追加CHECK|族自环发生于成功分类之前|

原合同不能阻止X_n的原因：新handoff/成功分类/恢复唯一性没有给PENDING观察计数；持久fsync没有带入可靠最短耗时合同；就绪pidfd不会因一次PENDING返回而变为未就绪。

历史原件显示同源码17次PENDING自环，全部revision4、一个handoff id、该区间全局journal增量0。其日志SHA为db70519e1b47cdb42d1a852d5ad7db19096a616886450b3714a57ff231ac6675。完整原始字节和相关commit/witness/预算均仅复制到本轮研究目录用于复核，历史不改写。

本轮没有运行反例重放程序、替换Root调度、创建state/账/服务或修改日志。可重放描述由源码行、初始前提、分支序列、保持式和参数n组成；未来真实实验需独立动态授权，有限实例的实测也不能证明无限统一上界。

[完整反例规范](evidence/COUNTEREXAMPLE_FAMILY.json) · [原日志副本](evidence/HISTORICAL_RAW/CALDIAG_c09_events.jsonl) · [保持式统计](evidence/HISTORICAL_NATIVE_LOG_ACCOUNTING.json)。''')
doc('EVIDENCE_TOTAL_BYTE_BOUND.md','完整证据字节闭包审查',f'''
当前B_total不能闭合；**CAPACITY_CONTRACT_NOT_READY**。给C09一份未生效的有限草案，不会给现行生产者或其他文件自动带来总量限制。

|类别|已经具备的界|界的性质/剩余责任|
|---|---|---|
|C09 native|条件行1298/1322；当前次数无上界|生成总量缺口已构造可达反例；草案预留345148仍未生效|
|C00–C12固定二进制|counter24、C03共享16MiB|源码固定布局/ftruncate，可证明；C05/C11局部journal需独立计量|
|全局预算journal|健康完成全域最多2,000,000行；条件line-none/请求界见机器表|生成器没有对应总字节检查；range oracle只接受≤200000行/16KiB行，terminal另要求总32MiB/32KiB行|
|预算journal条件精算|旧完整校准≤{gj['full_calibration_journal_bound']:,}字节；全1m窗口≤{gj['full_1m_journal_conditional_bound']:,}字节|固定请求/ABI条件，三次批预付节省36990事务；该有限粗界仍可超过32MiB接受界，不证明实际模型会耗尽预算|
|Boot/RootIPC/MR/PT/PF/TR/RA|Root JSON读取4MiB、BC读取128KiB；MR事件写32KiB|读取接受cap与生成界分开；事件/元数据/异常链及聚合仍需逐schema证明|
|readiness原生诊断|602×131072=78905344字节|写前单条cap与sample300＋confirm1；组合cap高于32MiB，未证明该极端同时可达|
|C09H34|204事件＋34oracle；事件reader上限64KiB|writer/reader义务不同，按接受cap估计事件部分13369344；独立oracle输出另计|
|S1–S9|48个实际actor×256事件×4096=50331648；原子metadata16KiB|可证明写cap乘积，尚非紧上界；registry/journal/snapshot/临时件/派生结果另计|
|门18及ledger聚合|固定18门、ledger18子例及两轮重查|有限数量，内容/派生证明/日志的完整字节界仍需绑定|
|stdout/stderr/系统查询/退出错误|部分MR查询8192/2048；first_error部分字段截2048|G._run PIPE未设统一输出字节界；traceback/SEAL_ERROR repr/外部journal导出未被这些局部界覆盖|
|F1/F4输入/状态/策略/反例|196个固定输入/输出/摘要槽位|未得出各状态/树/trace/report编码上界，文件数量和访问上限不足以代替字节证明|
|native/admin/manifest|各接受32MiB、manifest4MiB|接受集合有限；native构建前G.digest整文件读、admin嵌套ZIP/host原始流仍要生成/聚合证明|

分层公式：U_native=R_raw＋M_native；Z_native=ΣD(s_i)＋H_native；行政导出=R_raw＋M_native＋Z_native；行政归档未压缩量再加host流、4份source lock和M_admin。ZIP本身的文件字节及包内原件都需计入行政总量，不能因包内包而忽略复制成本。

现有32MiB是拒绝/失败边界。源码没有因此在生成时为每个必要对象分配总量；超限可能使封存无法完成，真实裁决应保留FAIL/UNKNOWN和首次失败，不能删除原始记录或缩短反例以制造成功。

[全对象分类表](evidence/TOTAL_BYTE_FAMILY_AUDIT.json) · [journal条件推导](evidence/GLOBAL_JOURNAL_BYTE_MODEL.json) · [ZIP代数](evidence/ZIP_BOUND_ALGEBRA.json)。''')
workrows='\n'.join(f"|{r['step']}|{r['input']}|{r['read']}|{r['write']}|{r['memory']}|{r['FD']}|{r['status']}|" for r in w['steps'])
doc('ARCHIVE_WORK_COMPLEXITY.md','处理工作量、压缩、内存和FD边界',f'''
|步骤|输入规模|最坏读取|最坏写入|工作内存|FD|裁决|
|---|---|---|---|---|---|---|
{workrows}

拟议日志组件在严格schema/额度生效条件下可记**WORK_BOUND_PROVED**：主日志预留345148字节、cursor956、失败333，最多266次cursor写，总写入≤599777字节；包含文件/目录的持久化尝试≤798。它只覆盖日志编码/追加/cursor，不覆盖完整check_base/systemctl响应/stop/seal。当前原生循环的整个工作量仍UNRESOLVED。

现有native构建器hash为整文件read_bytes，ZipFile按N个条目构建索引，sorted(rglob)还需O(N log N)路径排序。独立终态checker使用64KiB块，但ZipFile/JSON对象占用O(N＋manifest)；其他host/native helper会用z.read一次物化成员。AS1GiB是硬拒绝边界，缺少完整对象分配常数/输入字节证明时，不能据此宣称工作内存足够且封存会完成。

ZIP不能假设压缩后更小。对固定ZIP32、空extra/comment、保守16字节descriptor及命名profile（最多6个路径分量、每分量255字节），F≤1535。H≤22＋N(92＋2F)，N=4451得H≤14074084字节。该粗界来自字段/源层级，不作为新容量许可；未来scope和ZIP64/扩展字段须重新审查。

若另证实际pinned默认zlib满足compressBound式D(s)≤s＋(s>>12)＋(s>>14)＋(s>>25)＋13，则U=32MiB下压缩数据和元数据条件上界47696620字节；ZIP_STORED条件界47628516。两者都高于现行压缩包32MiB，展示该双上限缺少“所有合法raw都能被容纳”的保证。此处是保守上界超出接受界，未声称实际输入必定达到该界。

文件描述符与TasksMax分别计量。终态reader路径可列13个增量源描述符（目录/boot/counter/phase/ZIP open+dup），再加进程已有基线；当前没有获批的新NOFILE上限。目录/库/子进程辅助资源仍需结合实际scope审查。

即使获得有限操作/读写量，存储fsync、调度、systemd和终止时延仍缺严格最坏完成时间；保持**WALL_TIME_BOUND_UNRESOLVED**。完整300秒、终态5秒、行政30秒均未通过新的原生实测或严格时延证明。

[ZIP参数/压缩假设](evidence/ZIP_BOUND_ALGEBRA.json) · [工作量全表](evidence/WORK_MEMORY_FD_MODEL.json)。''')
doc('RESOURCE_BOUND_COMPATIBILITY.md','访问合同、数量前提与资源兼容性','''
旧冻结校准访问硬界68498仍只属于旧程序/测试范围。本轮R/T0/deadline未建立，模型访问消耗0。

日志草案若另行批准并集成独立256预付，分开计的保守估计为68754，再加新负向/原件验证等收费项。若明确把该256放入原H/IPC/BC共同5000封套且保持精确合法收费上下文，则旧联合保守3269＋256=3525，存在1475余量；这需要版本化合同明确承认，当前没有自动吸收或重复计费。新完整实现尚未冻结，因此完整新访问硬界继续UNRESOLVED。

预付时点必须在C09 controller启动/ready marker及handoff.counter固定之前。固定后不得逐次修改全局R；新cursor只能消耗先付额度。预算核心、持久ACK、RootIPC权限及deadline语义当前保持原字节。

数量前提复核发现上一轮表漏列manager_recovery.event实际创建的mr_events.lock（历史native manifest已有该零字节原件）。对本轮明确的CALIBRATE_S1S9_THEN_F1_F4 scope，pt_expected_abort.json只由PT_STARTUP_DIAGNOSTIC_ONLY分支产生，因而不可达。修复固定族的一对一覆盖后，raw4450/native4451/admin原件4452仍可作为该完整scope的保守包络；旧报告不改写。该修正不把旧表视为无遗漏，也不向其他诊断scope无条件外推。

新配额sidecar/失败摘要/可能staging、新测试及未来MR use证据会带来ΔE和ΔV。其未实现生成规则不能直接套用4450，后续应按同一源级族方法重算。当前旧256/257守卫保持，未建立新执行锁/身份/nonce。

总访问1,000,000、校准软访问100,000、总墙钟1800、软校准300、pre-T0 TCB120、提前1740、单进程AS1GiB、父slice TasksMax4继续冻结。历史TR-A2 WORK/C00与CalDiag前缀的实际资源/退出证据保留其原批次边界；当前新批资格和完整封存成功没有动态证据。

[覆盖修正与历史lock原件hash](evidence/COUNT_COVERAGE_FINDING.json) · [完整scope固定族复核](evidence/COUNT_SCOPE_COVERAGE_REVIEW.json)。''')
doc('EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.md','容量合同与日志配额审批草案','''
**CAPACITY_CONTRACT_NOT_READY。** 本文件不给256/257替代值以生效权限，不是扩容批准回执。现行64份运行源、日志/构建/预算/资格门及数量守卫全部保持。

可独立审阅的日志配额条款：256个独立分类额度，PENDING255、终态保留1、主日志263行；逐行1322字节及按类型预扣主日志345148，cursor956、单次失败摘要333。所有当前原件保持，持久预扣→append/fsync，模糊状态fail-closed，无退款/重建/免费窗口。计数/字节/identity先验证，失效只登记真实资源停止。完整参数见附件。

256为新政策，使用既有review块尺度并单独收费；当前没有性能/活性保证。批准该政策仍需后续最小维护实现和边界/崩溃/原件校验审查，不能自动授权源码修改或动态运行。

完整容量合同必须在批准前填实：最大文件/成员N、单文件与所有raw总字节、native压缩/解压与admin嵌套总量、manifest上限、文件类型/权限、相对路径规范、duplicate/missing/extra拒绝、source/boot/instance绑定、完整原件重放、编码/CRC/hash/集合逐项检查、所有生成/异常staging闭包、读写/内存/FD/访问成本和失败/UNKNOWN语义。

当前精确缺口为：当前C09额度未生效；ABI字段上界未转为明确输入校验；readiness/S34等局部cap未推出聚合32MiB；stdout/stderr/command/traceback与模型输出缺单项/总量证明；journal可生成体量超过后验接受界；native构建整文件读取缺前置总量；ZIP元数据/压缩膨胀/admin嵌套和新测试/证据ΔE、ΔV未闭合。

现行接受cap可供草案继承，但无法同时声称“所有必需原件都可完整生成、打包并通过”。超限应停止并如实封存适用原件，缺失/部分包保持FAIL/UNKNOWN，原始记录不得静默截断、丢弃或并入不受逐件检查的容器。

容量批准项保持BLOCKED；日志政策与MR规则分别可审阅。当前JSON全部user_approved/effective/runtime_enabled=false。

[日志具体合同](proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json) · [容量缺口/字段合同](proposals/EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.json)。''')
mr_path=O/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json';mr_sha=hashlib.sha256(mr_path.read_bytes()).hexdigest()
doc('MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md','MR限定跨实例承认最终待批文本',f'''
**MR_CROSS_INSTANCE_ADMISSION = PROPOSED_NOT_EFFECTIVE。** 建议仅对下列原则合同作APPROVE_RECOMMENDED；当前无用户批准回执、已批准artifact pair、有效A证书或B动态身份。本文件与容量批准互相独立。

批准对象：MR-CROSS-INSTANCE-ADMISSION-FINAL-TEXT/1-DRAFT，版本C09-BoundClosure/review-1；附件SHA-256 `{mr_sha}`。批准/拒绝均应引用这一版本及摘要。

1. 唯一承认类别：独立A在指定原生受控服务故障下，真实触发未审查failed-unit事件后，主A自动STOP/CLOSED、真实进程退出和组空的已观察实现能力。它仅证明明确场景及轨迹，不推出主B已经关闭或任意未来故障必定安全。
2. 身份：A/B各有唯一batch/boot/锁/单位/InvocationID/PID/一次性使用记录，保持不同窗口和不同账；A已CLOSED永久保持，当前A_identity/B_identity均未签发。
3. 源与TCB：精确A/B source/input/execution locks和相关程序保持相同受审安全核心；仅允许按AST坐标逐项批准的namespace字面量映射。禁止盲目替换、忽略所有字符串或仅比较版本标签。审批pair表填实前拒绝使用。
4. 限定同boot，kernel/systemd/Python/loader/libc/libm/关键TCB指纹、有效UID/GID/资源sandbox符合明确等价条件，B必须fresh-read。既有受信Root/kernel/存储、dpkg/keyring和无并发特权更新前提保留；新.deb payload独立再现缺口保持条件性。
5. 原生故障实际触发以Raw query/journal、当前单位和InvocationID/PID、故障码/时间、未审查拒绝及责任关系证明；MR-SIMULATION/1或主机native-shaped夹具不能替代。
6. 自动停止、STOP/CLOSED、真实角色退出/组空、原预算/窗口保持及独立oracle均需原始字节复核。主自动路径失败、只靠手动/兜底成功、退出未确认或必需UNKNOWN时，拒绝该能力类别，分别保留fallback/UNKNOWN结果。
7. native seal与行政归档分别完成并逐件校验，原始ACK/commit/witness/日志/预算/关闭/退出证据及checker程序/结果完整可取。后层证书在A两包封存后生成于其hash前像外；缺/换/额外/重复/跨版本成员均拒绝。
8. 新B授权使用独立use_spec，固定certificate/rule/源码pair/B身份/boot/执行锁和fresh nonce；授权收据绑定use_spec，实际use记录随后绑定授权hash，避免互相自hash。A预算/额度/期限不合并到B。
9. B始终重做当前boot、锁、单位、UID/GID、binary/maps、budget/T0/deadline、WORK/C00、真实C09、正常ManagerRecovery/当前监督与停止前提以及全部C/S/负向门/独立原件/资源强制条件。A证书不能直接授予RESOURCE_GATE_PASS。
10. 规则仅替换强化合同中那一项“异常场景能力观察”的证据来源。D1/D2语义、F1/F4有限域/PASS_BOUNDED标准、native seal活动/终态安全义务和原创性门保持。
11. 版本、boot、源/TCB、fault scope、目标/use nonce、批准状态有任何变化或撤销即失效；当前B直接授权须固定材料hash。缺新鲜授权、未知撤销状态、旧证书重放或跨版本冒用均拒绝，未声称已实现通用防回滚注册表。
12. checker/被测程序可能共享parser等TCB错误，需披露并独立审阅规则和原件。既有15个主机变异的成功不能作为未来跨实例gate的充分验证。
13. 缺任一必需原生事件/身份/自动关闭/预算保持/退出/封存/oracle/源码pair/B当前检查/use绑定即拒绝；A遗留failed单位只能按精确A关闭原件只读分类，禁止reset-failed或批量白名单。
14. 用户批准本文仅采纳有限承认条款，不自动授权实现、容量/日志变更、实际A注入、新B校准或F1/F4。后续具体源/输入/资源/argv锁、原生证据和实现适配须独立申请；容量当前NOT_READY不会因MR原则获批而解除。

可直接使用的决定文字：

> 批准：我批准上述MR限定跨实例承认原则合同及其SHA-256，保留全部先决条件和主批次独立检查。该决定仅用于后续具体适配/执行申请，当前不授权代码变更、真实故障、扩容或F1/F4，也不使现有证书自动有效。

> 拒绝：我拒绝上述MR跨实例承认条款；现行同实例要求保持。后续可单独申请MR专项关闭验收，完整链的生命周期冲突继续阻断。

当前记录仍为**PROPOSED_NOT_EFFECTIVE / user_approved=false**，未代用户选择任何决定。

[独立规则附件](proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json)。''')
sep_table='\n'.join(f"|{r['candidate']}|{r['input_family']}|{r['metric']}|{r['G']}|{r['prediction']}|COVERED_BY_G|" for r in separation)
doc('GENERAL_BASELINE_AND_SEPARATION.md','强通用基线与实现门',f'''
|候选方向|具体输入族|度量|适用强G|预测差距|裁决|
|---|---|---|---|---|---|
{sep_table}

每个方向都有可构造的同费用覆盖实例：n=17或257的PENDING前缀、1082路径清单、两标准分段、一个A证书与一个B目标。成熟有界日志/预付配额、标准ZIP与内容寻址/版本化manifest、目标绑定的软件资格证据都能采用相同检查和同样的停止决策。当前没有证明G在这些实例中必须付更高代价。

C09自环反例揭示的是验证基础设施资源合同缺口；它没有构成D1/D2架构的严格分离实例。以上预测严格差距均为0，未形成满足实现门的候选。全局所有算法的最优性也未由本地比较声称。

原BASELINE_G/SEPARATION_GATE的同能力/共同费用及既有D1/D2覆盖裁决继续有效。日志限额等属于通用工程合同维护方向，任何未来最小维护代码仍需明确授权；当前候选机制、日志/预算/封装/资格门实现修改均0。

[具体比较与输入实例](evidence/GENERAL_G_COMPARISON.json)。''')
doc('CONTRACT_APPROVAL_CHECKLIST.md','独立审批状态与缺项清单','''
|对象|可作何种决定|当前状态|批准后仍需完成|
|---|---|---|---|
|C09日志配额政策|审阅/批准或修改独立256额度与字段/字节/fail-closed条款|PROPOSED_NOT_EFFECTIVE|精确源/ABI/字段/持久cursor/锁序/失败路径/负向测试及计费静态审查，再另行动态申请|
|完整容量合同|当前应保留待批，不签发扩容许可|CAPACITY_CONTRACT_NOT_READY|所有raw/单文件/aggregate/压缩/嵌套/工作量/新证据ΔE和ΔV闭合|
|MR限定承认原则|可独立批准或拒绝最终文本|PROPOSED_NOT_EFFECTIVE|实际A证据、source pair、TCB与B身份锁、独立实现/攻击审查；所有动态行为另批|

日志配额审批必须确认：256是新独立额度而非旧MR额度转移；255 PENDING与最后终态槽；1322行宽和345148主日志预留；956 cursor/333失败摘要；预付在counter冻结前；先持久预扣再append；模糊失败不退款/不重建；耗尽安全关闭；原始字节不删除；活性/正常完成尚无保证。

容量审批必须填实：文件/成员数及scope、逐文件/总raw/未压缩/压缩/行政嵌套字节、manifest/path/type/权限与完整集合、压缩膨胀和重复/缺失/多余拒绝、目录/原件source绑定、内存/FD/IO/访问界、墙钟不确定性、失败/UNKNOWN和版本隔离。目前任一未证字节项足以保持NOT_READY。

MR审批必须明确唯一能力类、同boot单B/精确source pair、原生故障与主自动停止、预算/封存/oracle/原件、有效范围/撤销、B当批监督/C09/账/资源独立资格，以及缺项拒绝。批准原则与授予实际RESOURCE_GATE保持分别判断。

本轮所有批准回执均未生成。报告/清单/JSON字段更新不构成用户批准，旧256/257继续生效。''')
doc('NEXT_ACTION.md','下一阶段最小授权建议','''
当前可以提交两个独立原则合同决定：C09日志配额政策，以及最终MR限定跨实例承认文本。完整证据容量保持NOT_READY，暂不申请扩容或完整动态执行。

若用户批准日志政策，可另行申请范围明确的静态维护实施：只为原生观察增加字段/次数/字节验证和独立预付cursor/首错关闭；保持预算预留核心、ACK/receiver/waitpid及CLOSED义务；审查合法收费时点、持久化/崩溃恢复、锁序和原始字节保全。未审批前保持源码冻结。

并行必要静态研究：对readiness/RootIPC/MR/标准输出/错误/模型报告建立逐schema和聚合字节界；对native构建输入预检查、ZIP压缩/元数据/admin嵌套工作量形成完整版本合同。需要新代码、配额或保留规则改变时再提交最小具体授权，避免用后验32MiB拒绝界冒充生成保证。

MR原则若获批，先完成source pair与具体适配/证据验证计划，再申请独立A真实故障关闭；A完成后另建B当前实例资格。A窗口/预算和旧CLOSED实例不复活、不合并。

当前顺序保持：合同审阅→最小静态接线/证明/锁→专门动态授权；RESOURCE_GATE实际全部成立后才可能申请/执行F1→F4。本轮没有启动下一批次。''')
answers=[
 ('全部真实PENDING生产位置','唯一原生PENDING写点c09_handoff.py:277，经75–84 sink；另两event调用是stage与ACK，合成/关闭/行政各自分离。'),
 ('单次最多多少PENDING','当前合同无可证统一数值上界；新待批政策拟255，尚未生效。'),
 ('是否有未受限重复','有；ready pidfd、witness=None、stage/revision4/counter不变的可达自环。'),
 ('单条最大字节能否证明','固定原生调用和ABI宽度下PENDING1298、全部原生行1322；源码无显式行长/range检查，结论CONDITIONAL_PROVED。'),
 ('总PENDING字节能否证明','当前不能；n可任意有限增长。待批主日志预留345148，独立metadata/失败另计。'),
 ('最小反例','一个handoff，父协调者暂延waitpid，Receiver重复PENDING；R不变、每轮追加/fsync。历史同源码已观测17次。'),
 ('是否需配额合同','需要；次数/行宽/总字节/预扣持久cursor/耗尽关闭/原件保全已给具体草案。'),
 ('完整归档字节上界','UNRESOLVED；C09现行无配额且其他raw/aggregate/输出/模型/压缩/嵌套义务未闭合。'),
 ('独立校验工作量','已接受有界输入为O(N+B)；拟日志组件有限工作可条件证明；全native构建/观察/host总工作仍未闭合。'),
 ('已有有效资源证据','旧AS/TasksMax/预算/期限配置及TR-A2/CalDiag实际有限范围证据保留；本轮无新实例资格。'),
 ('墙钟哪些未决','完整300秒、终态5秒、行政30秒和底层I/O/调度/终止最坏时延仍未决；1800/1740等硬停止合同保持。'),
 ('4450等前提是否保持','程序/输入/单次/封闭域保持；发现mr_events.lock遗漏，以完整scope不可达pt_expected_abort槽修复覆盖后数值仍保守；新实现/测试须再加ΔE。'),
 ('新容量具备审批条件吗','CAPACITY_CONTRACT_NOT_READY；旧256/257不变。'),
 ('MR条款具备审批条件吗','最终有限原则文本可独立批准/拒绝；实际承认仍PROPOSED_NOT_EFFECTIVE，A/B材料和实现未就绪。'),
 ('哪些被G覆盖','PENDING配额、版本化容量、标准分段/manifest、限定cross-instance资格证据四类均COVERED_BY_G。'),
 ('满足分离门的候选','0；严格分离实例0，研究实现门CLOSED。'),
 ('能否申请修订/最小实施','可申请精确日志政策/最小静态维护及MR原则决定；当前无实施授权，容量扩容/完整动态/F1F4继续阻断。')]
table='\n'.join(f'|{i}|{q}|{a}|' for i,(q,a) in enumerate(answers,1));gate_table='\n'.join(f"|{k}|{v['status']}|{v['finding']}|" for k,v in gates.items())
doc('FINAL_DECISION.md','C09-BoundClosure最终裁决',f'''
**C09原生重复追加反例已明确；具体日志配额待批准；CAPACITY_CONTRACT_NOT_READY；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。**

冻结同字节源码与历史原件共同确认：PENDING可以在同一handoff/revision4/账不变时反复append/fsync；历史已观察17次。现行状态唯一性无法给其记录数统一上界。ABI/固定schema条件下单行1322可计算，但当前总量无界；拟256观察、255 PENDING、263总行、345148主日志预留仍未生效。

|验收门|结果|范围|
|---|---|---|
{gate_table}

|序号|必须回答|答复|
|---:|---|---|
{table}

本轮仅读取冻结材料、核对历史字节并生成数学/合同审查工件；64份运行源码/输入、8份原审查对象和上轮合同锁保持，历史工件不改。日志/预算/构建器/native seal/gate/256/257/跨实例实现修改0；WSL/新动态/真实故障/F1/F4均0；T0/deadline/R=null。没有把反例模型或历史结果登记成新原生PASS。

已形成13份要求报告、源生产者/字段代数/原件统计/反例族/完整字节分类/工作量/覆盖修正和两类独立原则审批材料。容量条款因具体缺口继续BLOCKED，下一步可先审阅日志政策和MR原则，再申请必要的静态维护；当前没有自动推进实现或下一批次。

[研究索引](EVIDENCE_INDEX.md) · [机器裁决](evidence/FINAL_ANALYSIS_DECISION.json) · [交付核验](evidence/DELIVERY_CHECK.json)。''')
reports=sorted(p.name for p in O.glob('*.md'));assert len(reports)==13
text('EVIDENCE_INDEX.md','# C09-BoundClosure证据索引\n\n'+passport+'\n\n'+ '\n'.join(f'- [{n}]({n})' for n in reports)+'''

- [原授权](evidence/TASK_REQUEST.txt)
- [冻结源码及前序审查锁](evidence/SOURCE_AND_PRIOR_LOCK_CHECK.json)
- [原生生产者](evidence/C09_NATIVE_PRODUCERS.json)
- [所有日志上下文](evidence/PRODUCER_CONTEXT_MATRIX.json)
- [C09H34原输入](evidence/C09H34_FROZEN_INVENTORY.json)
- [源行证据](evidence/SOURCE_EXCERPTS.json)
- [可复核反例族](evidence/COUNTEREXAMPLE_FAMILY.json)
- [历史原生24条/17PENDING统计](evidence/HISTORICAL_NATIVE_LOG_ACCOUNTING.json)
- [原始日志副本](evidence/HISTORICAL_RAW/CALDIAG_c09_events.jsonl)
- [单行编码代数](evidence/NATIVE_RECORD_BYTE_ALGEBRA.json)
- [具体配额合同](proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json)
- [容量未就绪合同](proposals/EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.json)
- [MR最终待批规则](proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json)
- [字节对象分类](evidence/TOTAL_BYTE_FAMILY_AUDIT.json)
- [ZIP代数](evidence/ZIP_BOUND_ALGEBRA.json)
- [完整工作量表](evidence/WORK_MEMORY_FD_MODEL.json)
- [源覆盖修正](evidence/COUNT_COVERAGE_FINDING.json)
- [通用G比较](evidence/GENERAL_G_COMPARISON.json)
- [最终机器裁决](evidence/FINAL_ANALYSIS_DECISION.json)
- [历史前态](evidence/HISTORY_BASELINE.json)
- [历史后态](evidence/HISTORY_AFTER_CHECK.json)
- [交付核验](evidence/DELIVERY_CHECK.json)
- [研究manifest](C09BOUND_MANIFEST.json)
- [研究ZIP](C09BOUND_EVIDENCE.zip)
- [ZIP SHA-256](C09BOUND_EVIDENCE.zip.sha256)

研究ZIP与native/admin运行封存分别裁决。当前所有合同保持待批，交付收据自排除以避免自摘要循环；前序草案保留，最终配额以proposals目录为准。
''')
prefix=('## DCL-R6-C09-BoundClosure 源码/合同审查增量（2026-11-15）\n\n'
 '**原生PENDING自环反例成立，日志政策待批，容量NOT_READY。** 同字节C09历史有17条PENDING/24条原生记录，source loop保留ready pidfd且R不变；当前缺记录/总量上界。固定schema与ABI条件下单行1322；具体拟256观察/255 PENDING/263总行/345148主日志预留，未生效。完整raw/ZIP/admin字节与工作量仍有具体缺口。MR最终有限原则文本可独立决定，状态PROPOSED_NOT_EFFECTIVE。\n\n'
 '4450表复核补入mr_events.lock并排除完整scope不可达pt_expected_abort，数值保守包络保持；新实施/测试需ΔE。64运行文件、8审查对象、旧256/257与全部历史保持；WSL/动态/故障/实现/F1F4修改0，T0/R=null。RESOURCE_GATE_PASS=NOT_OBTAINED；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 '[最终裁决](DCL-R6-C09-BoundClosure/FINAL_DECISION.md) · [记录反例](DCL-R6-C09-BoundClosure/C09_PENDING_RECORD_BOUND.md) · [配额与字节](DCL-R6-C09-BoundClosure/C09_PENDING_BYTE_BOUND.md) · [MR待批文本](DCL-R6-C09-BoundClosure/MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md) · [索引](DCL-R6-C09-BoundClosure/EVIDENCE_INDEX.md)\n\n'
 '以下逐字节保留先前记录。\n\n---\n\n').encode()
for n in ['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']:
 original=(E/'NAV_ORIGINALS'/n).read_bytes();assert (P/n).read_bytes()==original;(P/n).write_bytes(prefix+original)
print(json.dumps({'reports':13,'final_questions':17,'quota_log_reservation':345148,'quota_cursor':956,'quota_retained_max':346437,'MR_rule_sha256':mr_sha,'runtime_changes':0}))
