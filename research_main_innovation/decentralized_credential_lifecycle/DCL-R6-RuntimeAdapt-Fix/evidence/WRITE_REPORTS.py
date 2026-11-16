"""Author conditional runtime baseline review and request; no dynamic work."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
def load(name):return json.loads((E/name).read_bytes())
R=load('STATIC_RESULT.json');P=load('PROVENANCE_AUDIT.json');A=load('ELF_ABI_AUDIT.json');D=load('RUNTIME_DISCOVERY.json');X=load('PLATFORM_EXPORT.json')
passport='Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。'
gates='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。'
def report(name,title,body):
    with(O/name).open('x',encoding='utf-8') as f:f.write('# '+title+'\n\n'+passport+'\n\n'+body.strip()+'\n\n'+gates+'\n')
report('RUNTIME_CHANGE_TIMELINE.md','运行时变化与历史阻断时间线','''
**旧TR-A的PREFLIGHT_FAILED_RUNTIME_DRIFT保持；本轮只读确认变化属于Ubuntu glibc包修订。**

|阶段|时间/主体|可复核事实|
|---|---|---|
|旧冻结8.9|旧runtime_critical/runtime_files与历史TR前缀|loader/libc/libm旧SHA固定，Python3.12.3固定|
|本机包日志|原文2026-11-13 13:26:52–53|libc6/libc-bin 2.39-0ubuntu8.9→2.39-0ubuntu8.12；安装/配置记录完整|
|旧TR-A入口|UTC2026-11-13 09:28:55.908611；Bootstrap2271/start43611|PREFLIGHT_BEGIN后loader摘要首次失配，active exit125|
|旧TR-A保全|UTC09:28:56.510318；行政Root2275|自动14清单/15ZIP，T0/R=null，正式实例未创建|
|本轮来源核验|7次只读WSL查询，各boot/time/argv单列|dpkg、签名/索引、ELF/静态依赖、旧包成员、最终文件访问核验|
|本轮重冻结|新r1/新batch14静态身份|仅3项已观察运行时pin变化；实际动态窗口0|

当前系统/etc/localtime指向Asia/Shanghai；历史包日志未带时区，原文时间与host/guest UTC分别保留，避免构造未经记录的精确跨时钟关系。各只读查询可以处于不同boot，原始boot列表保留，均不成为后续运行资格。

升级执行者和具体自动机制未被本轮证明，报告不归因到某个进程。任务期间网络下载、安装/升级/降级、库文件写入、WSL重启均0。

[原TR-A首错/包日志](../DCL-R6-TR-A/evidence/RUNTIME_DRIFT_AUDIT.json) · [本轮原生结果](evidence/PROVENANCE_AUDIT.json) · [查询boot/最终绑定](evidence/FINAL_BINDING_REVIEW.json)
''')
report('GLIBC_VERSION_AND_PACKAGE_AUDIT.md','GNU libc版本与Ubuntu包审查','''
**GNU libc上游版本仍为2.39；8.9→8.12对应Ubuntu包版本的发行版修订部分。**

实际getconf GNU_LIBC_VERSION输出glibc2.39；ldd --version输出Ubuntu GLIBC2.39-0ubuntu8.12与上游2.39。dpkg-query确认libc6:amd64、libc-bin均2.39-0ubuntu8.12，已安装状态ii，架构amd64。

三个真实/usr/lib路径均由libc6:amd64归属查询命中。dpkg -V libc6 libc-bin exit0且stdout为空；三项实际MD5与/var/lib/dpkg/info/libc6:amd64.md5sums一致。ubuntu-keyring2023.11.28.1包核验同样无差异。Root所有权/普通文件元数据及真实路径均保存。

apt-cache policy显示当前安装/候选版本来自noble-updates/main和noble-security/main。两份对应InRelease使用现有Ubuntu archive keyring经gpgv验证exit0，缓存main/amd64 Packages内容SHA256与签名Release声明的大小/摘要匹配，均含libc6和libc-bin8.12完整stanza。

当前8.12 .deb在已检查本地缓存/临时目录未找到，未下载补齐。已有8.9 libc6缓存包被只读解包，三个旧成员SHA精确匹配旧冻结pin，进一步锚定旧8.9身份。安装文件与签名仓库包之间的payload再提取证据仍缺，现结论依赖受信Root/dpkg数据库与既有keyring。

本地changelog.Debian列出的8.12补丁涉及libio、resolver、动态加载器ORIGIN/AT_SECURE、nscd及gettext等。此处仅报告本机包携带的更新说明，未联网确认各CVE细节；不能由修订号或changelog推出资源行为和全部运行语义等价。

[版本/归属/完整性原输出](evidence/RUNTIME_DISCOVERY.json) · [签名/索引/成员目录](evidence/PROVENANCE_AUDIT.json) · [旧包与changelog](evidence/OLD_NEW_ABI_AUDIT.json)
''')
rows=[]
for path,obj in A['three_components'].items():
    file=next(x for x in D['artifacts'] if x['path']==path)
    rows.append('|'+Path(path).name+'|'+str(file['bytes'])+'|'+obj['build_id']+'|'+obj['sha256']+'|')
report('ELF_THREE_COMPONENT_AUDIT.md','三个ELF组件独立身份审查','''
三项均为ELF64、小端、Machine62（x86-64/AMD64），三个主要/usr/lib路径均为普通Root文件，最终目标与路径相同。已记录的/lib64及解释器别名另有精确symlink文本和resolve目标绑定。

|artifact_id|字节数|GNU Build-ID|SHA-256|
|---|---:|---|---|
'''+ '\n'.join(rows)+'''

|对象|DT_NEEDED/符号关系|来源与裁决|
|---|---|---|
|ld-linux|无DT_NEEDED；提供GLIBC_PRIVATE等版本定义|libc6:amd64 8.12，静态匹配|
|libc|需要同名ld-linux；含GLIBC_PRIVATE与GLIBC_ABI_DT_RELR等|同一libc6包，静态匹配|
|libm|需要libc与ld-linux；最高已观察定义包含GLIBC_2.39|同一libc6包，静态匹配|

旧8.9包三个成员与旧锁SHA完全相符，新的版本定义名称集合无增加/删除。该比较仅覆盖GNU版本命名集合，不能证明函数行为、线程调度或资源占用相同。Build-ID与Native readelf及独立纯ELF-note解析3项一致；Build-ID并未替代SHA。

真实路径、别名、文件大小/uid/gid/mode、包信息、所有版本定义/需要列表、readelf -h/-n/-d/-V/-l原输出分别保留。没有对目标ELF使用ldd执行检查；ldd仅运行受信系统工具的--version。

[三组件完整字段](evidence/ELF_ABI_AUDIT.json) · [路径/别名和旧成员导出](evidence/PLATFORM_EXPORT.json) · [新旧版本集合](evidence/OLD_NEW_SYMBOL_COMPARISON.json) · [新旧pin](evidence/RUNTIME_PIN_DIFF.json)
''')
report('RUNTIME_PROVENANCE_ASSESSMENT.md','运行时来源裁决与条件','''
**分类RTA-1：正常软件包变更，结论CONDITIONAL_PASS。** 正确包归属、已安装版本、无差异dpkg校验、成员目录MD5、升级日志及签名仓库索引相互吻合，未观察到异常替换或来源矛盾。

|证据链|结论|
|---|---|
|当前Root文件→已安装libc6目录|三个MD5匹配；SHA/Build-ID/路径完整|
|已安装包→版本/架构/状态|8.12/amd64/installed，dpkg验证无差异|
|软件源→签名Release→完整Packages|两个gpgv成功、两个完整索引SHA/size匹配，含8.12包SHA256/Filename|
|旧源→8.9包身份|已有旧.deb控制字段及只读成员SHA匹配旧锁|
|新.deb payload再现|本地缺8.12缓存包，未下载；无法独立从签名包payload重提取三个现行成员|
|更新行为来源|日志可说明正常包修订，执行者/自动更新机制未证明|

采用原项目受信Root/kernel/软件包数据库与本机Ubuntu keyring的假设，可以建立受限静态基线。该假设不等于独立外部信任锚或新payload全链再现。本轮没有网络freshness/revocation查询，仓库时效与来源仍限定于现有缓存及已安装可信状态。

下一执行模板新增RuntimeAdapt_provenance_assumptions_explicitly_approved批准位，当前false。若后续执行许可不接受这些前提，应保持RUNTIME_PROVENANCE_UNRESOLVED并停止资格发放；本次没有授予无条件执行批准。补齐8.12已有可信包并独立payload核验是最小强化证据，不自动下载或安装。

[来源决定](evidence/PROVENANCE_DECISION.json) · [可复核签名/目录证据](evidence/PROVENANCE_AUDIT.json) · [保存的完整索引/ELF](evidence/PLATFORM_EXPORT.json)
''')
report('PYTHON_NATIVE_ABI_COMPATIBILITY.md','CPython与原生ABI兼容条件','''
**静态必要ABI条件满足，运行行为仍CONDITIONAL_PASS。** 当前CPython为3.12.3-1ubuntu0.17，执行文件SHA与旧e50d468e…锁完全相同，PT_INTERP=/lib64/ld-linux-x86-64.so.2，其实际目标为已审查加载器。

原1241对象中66个ELF入口进行只读解析，递归解析114个当前对象。DT_NEEDED均可解析，GNU version needs无未满足组。systemd-core所需SD_SHARED通过父systemd/systemd-analyze直接装载的唯一同SONAME共享库解析，初始未处理该link-map上下文的结果和精化证据均保留。

实际只读Python进程/proc/self/maps中的loader/libc/libm路径、device/inode与当前磁盘对象相符，未观察到deleted映射。LD_PRELOAD/LD_LIBRARY_PATH/LD_AUDIT为空，/etc/ld.so.preload不存在；配置、cache及六个文件身份均记录。它是当前查询进程的证据，不能借作未来业务服务PID的加载证明。

libc导出setrlimit/getrlimit/prlimit、clock_gettime/flock/fsync/open/pread64/pwrite64/waitpid/syscall等需要接口。系统d255.4-1ubuntu8.18、原kernel6.18.33.2-microsoft-standard-WSL2、cgroup v2及UID999/GID989保持观察值一致。RLIMIT_AS/cgroup/TasksMax行为、信号/退出、seal与资源时延仍须新C00及后续原生证据。

静态图按实际RPATH/RUNPATH/本机cache和父已加载SONAME条件解析；它未执行目标ELF或解析全部重定位/运行时dlopen行为。原Kernel/Manager信任及无并发特权运行时更新前提继续保留，全部动态兼容性及完整300秒可行性UNRESOLVED。

[ELF完整图与缺项检查](evidence/ELF_ABI_AUDIT.json) · [原始初图](evidence/ELF_ABI_AUDIT_INITIAL.json) · [当前映射与环境](evidence/RUNTIME_DISCOVERY.json) · [最终基本环境](evidence/FINAL_PLATFORM_AUDIT.json)
''')
report('RUNTIME_SECURITY_IMPACT_MATRIX.md','RT-1至RT-10安全影响矩阵','''
|性质|证据及静态适配|待动态事项/当前结论|
|---|---|---|
|RT-1 RuntimeIdentity|原严格pin守卫保留，3项显式重锁，新身份合同SHA绑定|未来fresh读取；CONDITIONAL_PASS|
|RT-2 LoaderConsistency|3项同libc6包、路径/alias/Build-ID/byte hash与当前映射一致|实际服务映射及变更窗口；CONDITIONAL_PASS|
|RT-3 PythonCompatibility|Python文件不变，66入口/114对象必要version集合满足|重定位/程序语义与全链性能；CONDITIONAL_PASS|
|RT-4 ResourceEnforcement|原AS/Task/cgroup代码/单位保持，接口符号存在，基本平台一致|实际C00/资源校准；CONDITIONAL_PASS|
|RT-5 NoSilentRelock|运行时匹配器只读、合同固定哈希，无法写回新值；source/key批准位|PASS_STATIC|
|RT-6 NoCrossBatchReuse|batch14静态新身份，batch13失败attempt和旧动态记录冻结|fresh PID/boot/T0/账；PASS_STATIC准备|
|RT-7 PreflightFailClosed|旧BC_ARTIFACT_DRIFT保持，新pkg/路径/映射不符均抛错|故障副本与实际拒绝；PASS_STATIC|
|RT-8 ExecutionTimeRecheck|预检两次、原Guard字节+映射、服务前full、服务内pkg/自身映射、seal及admin重查|非原子path→exec及后续特权修改边界；CONDITIONAL_PASS|
|RT-9 TerminalCompatibility|原TR/RootIPC/MR模块和PT/PF/TR判据保持；seal/admin只增加身份读取|真实CLOSED/native/admin联调；CONDITIONAL_PASS|
|RT-10 EvidenceProvenance|Root包目录/日志＋已验证签名索引；精确旧/新文件|新payload未重提取及既有信任锚条件；CONDITIONAL_PASS|

新代码检查点内可检测映射deleted、inode/device不符、路径或包目录变化；不能原子固定整个机器在预检与exec之间的所有文件，也无法阻止已获Root权限的更新或运行中内存修改。相同glibc身份下其他受信系统依赖和动态装载仍受原TCB边界约束，报告没有将一次扫描解释为永久保证。

没有扩大D1/D2安全结论、模型范围或原创性声明。RA身份匹配结果runtime_authority=NONE，执行/终态守卫仍由原接口支配。

[静态控制流](evidence/SYNTAX_AND_IDENTITY_CONTROL_CHECK.json) · [批准前提与剩余边界](evidence/PROVENANCE_DECISION.json)
''')
report('RUNTIME_LOCK_REFINEMENT.md','运行时身份锁精化与最小代码依赖','''
**新资源profile仍为CPY312-UBU24/1；另加精确glibc身份GLIBC-UBU24-2.39-8.12/1。** AS1GiB、父TasksMax4、总1000000/1800、校准100000/300、预T0120及提前1740均不改变。

程序变更分两类：必要的namespace/版本字面值适配将tr01/batch13改为独立ra01/batch14；功能变更限于新的runtime_identity、RA32驱动/oracle及运行时匹配/授权调用点。固定SPEC和批次检查使全程序字节保持与独立新身份无法同时实现，完整diff明确标出机械重命名。

严格pin仅显式更新已确认变化的loader/libc/libm，在runtime_files与runtime_critical中同步。stdlib runtime_tree中没有这三项路径，旧1241合并闭包的其他pin未更新。新metadata记录包身份、Build-ID、别名、dpkg目录和六项加载配置；输入摘要DAG重新生成，原Root运行时字节检查继续抛错。

新匹配器：只读固定Root文件/合同；full模式校SHA/Build-ID/路径/元数据；包模式校dpkg中精确版本/架构/安装状态和已安装目录摘要；当前进程maps校3项路径、inode/device与deleted状态。hot Guard先由原runtime_files循环查字节，再轻量查路径和映射。包/配置full检查在预检、服务前/内、seal与行政入口执行。

没有改为版本范围、缺hash放行、warning-only或自动学习新hash。新增RuntimeAdapt及来源前提批准位，当前模板false。host entry/finalizer字节保持；admin bootstrap仅在原资源界后、目标模块加载前追加只读身份检查。

13关键文件逐字节、70成员AST、完整RootIPC/MR/Terminal模块与PT/PF/TR jobs归一保持。namespace/cfg变化和新增只读检查不构成新研究机制实施，严格分离0与实施门CLOSED保持。

[3项pin差异](evidence/RUNTIME_PIN_DIFF.json) · [全部源码/输入差异](evidence/FILE_DIFF_INDEX.json) · [完整diff](evidence/FULL_DIFF.patch) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)
''')
report('RUNTIME_NEGATIVE_REGRESSION_PLAN.md','运行时负向与变异准备','''
新增RA32＝24safe＋8mutant，当前全部UNRUN；真实系统库从未被改动制造故障。输入覆盖新三摘要/同源/依赖/包、旧新混用、单项hash、symlink、包不符、Build-ID、搜索覆盖、来源缺失、读取失败、预检后变化、自动重锁、仅版本判断、跨批资格、CLOSED工作等。

八项变异missing_digest_pass、alias_change_pass、package_change_pass、build_id_pass、loader_override_pass、stale_mapping_pass、cross_batch_pass、silent_relock_pass复用对应safe输入。独立oracle只导入stdlib，按实际trace判断IDENTITY_BYPASS/SILENT_RELOCK或其他违规，再检查声明目标，原始input/binding/hash必须对应。

RA-SIMULATION/1是合成身份决策/观察测试，未替代真实映射、包目录或换库故障的OS证明。未来若需要实际故障注入只能使用独立文件副本/冻结对象，不能写系统loader/libc/libm。本轮只完成schema/源码/配对静态审查与只读平台取证；RA32和oracle没有调用。

RA每job16预付＋1审查，entry1，完成545/硬768。下一A2全量PT64/PF48/TR40/RA32共184合成job，其中33变异，另有真实C00。完成3133、阶段A硬4417；完整硬68498≤100000。真实hash/包/maps读取为5秒有界行政IO，新增子进程0，不能变成修改预算或追加窗口的权限。

[32项冻结输入](evidence/SOURCE_FINAL_R1/inputs/runtime_regression_contract.json) · [独立oracle](evidence/SOURCE_FINAL_R1/src/runtime_oracle.py) · [静态变异矩阵](evidence/RUNTIME_REGRESSION_STATIC_CHECK.json) · [资源界](evidence/RESOURCE_BOUND_RECALCULATION.json)
''')
report('STATIC_VERIFICATION_RESULTS.md','静态、只读查询与兼容检查结果','''
|检查|实际结果|
|---|---|
|业务/模型/Launcher/服务|全部0；T0/R=null|
|原生只读查询|7次WSL封装调用，版本/包/签名/ELF/缓存/日志/最终环境/文件读取条件，raw argv与双流完整|
|44程序|主机AST/3.12文法/内存compile通过；20条运行时身份控制流断言|
|ELF兼容|66冻结入口，114解析对象，剩余DT_NEEDED/版本缺项0；条件性静态解析|
|纯ELF parser探针|主机对3份保存ELF只读解析GNU Build-ID，与Native readelf相同；非业务动态测试|
|源码保护|13文件字节/70成员AST保持，完整RootIPC/MR/Terminal模块保持；host两文件字节保持；PT/PF/TR jobs保持|
|来源|两份InRelease签名与完整索引SHA/size匹配，dpkg目录/文件MD5一致；信任Root/DB/keyring前提明确|
|当前状态|三项当前组件和Python在最终只读检查仍相同；未来源/实例/slice未创建|
|执行准备|64文件/44程序/62 Linux项；精确RuntimeAdapt身份及未批准新模板齐备|

RA-1/2/3=CONDITIONAL_PASS，RA-4=PASS_STATIC。新ABI、文件/包元数据和执行时匹配提供必要条件与拒绝策略；未取得资源/服务/TerminalRead动态资格或完整时间证明。

行政分析器的初始systemd-core缺项被父已加载唯一SONAME关系解释并保留初图；冻结器按实际文件集合处理三项glibc，不假定它们在stdlib树内。它们属于分析工具修正，没有修改系统文件、旧执行锁或业务判据。

[机器结果](evidence/STATIC_RESULT.json) · [静态断言与3探针](evidence/SYNTAX_AND_IDENTITY_CONTROL_CHECK.json) · [最后摘要核验](evidence/FINAL_BINDING_REVIEW.json) · [全部只读调用](COMMAND_SUMMARY.md)
''')
report('SOURCE_AND_INPUT_LOCK.md','RuntimeAdapt最终源码、输入与运行时锁',f'''
最终RuntimeAdapt-static-1/r1；Windows工作区D:/毕业设计/DCL-R6-isolated-verification/ra01；静态副本evidence/SOURCE_FINAL_R1。规划/var/lib/dcl-r6/ra01、batch14、dclr6batch14.slice和DCL-R6-RuntimeAdapt-Fix/authorization/batch14-r1。

|对象|SHA-256|
|---|---|
|static_manifest.json|{R['manifest_sha256']}|
|execution_lock.json|{R['execution_lock_sha256']}|

64文件＝42 Linux程序＋2 host程序＋20输入，未来Linux62项。Source/输入/运行时pin→manifest；manifest/规则版本与源码/host/argv→execution_lock；未来回执绑定两锁、新glibc身份、测试合同和来源前提批准。新检查规则RA/1的文件SHA明确纳入两锁。

原TerminalRead/tr01与TR-A失败回执保持。只有原三项变化pin显式更新，其他冻结运行时字节保持。Python文件SHA仍e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f。新源码身份/目录机械适配与运行时checker功能差异均有完整diff。

当前模板TEMPLATE_UNAPPROVED、所有批准位false，真实原文SHA=null，实际control/回执/部署/运行窗口均无。只读查询boot不预填为新运行boot。来源和执行时边界是显式条件，模板不是最终执行批准。

[64项精确锁](evidence/STATIC_WORKSPACE_LOCK.json) · [运行时身份合同](evidence/SOURCE_FINAL_R1/inputs/runtime_identity_contract.json) · [pin差异](evidence/RUNTIME_PIN_DIFF.json) · [最终源](evidence/SOURCE_FINAL_R1/inputs/static_manifest.json) · [执行锁](evidence/SOURCE_FINAL_R1/inputs/execution_lock.json)
''')
report('NEXT_DYNAMIC_AUTHORIZATION.md','独立TR-A2有限动态申请',f'''
**REQUEST_ONLY，当前业务动态许可0。** 建议下一交付DCL-R6-TR-A2，唯一申请RuntimeAdapt-static-1/r1、全64项/44程序；manifest `{R['manifest_sha256']}`，execution_lock `{R['execution_lock_sha256']}`。

申请前提：明确接受现有Root/dpkg数据库/keyring信任及无并发特权运行时更新的原TCB条件，或先补齐可信8.12包payload证据。若不接受或关键来源发生变化，维持RUNTIME_PROVENANCE_UNRESOLVED并停止，不把模板当批准。

规划独立batch14-r1，scope=PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START，旧batch13不恢复。未来源部署62项Linux文件、Root元数据/source-only，不创建pyc；fresh核当前Python3.12.3、kernel/systemd、三ELF/aliases/Build-ID、精确包/目录/配置、当前maps和全部原runtime pin。

```text
python -X utf8 D:\\毕业设计\\DCL-R6-isolated-verification\\ra01\\host\\windows_entry.py --activate
```

host环境PYTHONDONTWRITEBYTECODE=1，唯一active argv：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ra01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch14
```

顺序：新运行时双侧预检/同PID sealed认领 → 一次初始化/ARMED/WORK → C00实际资源及映射 → PT64 → PF48 → TR40 → RA32 → 正常CLOSED/原回收 → terminal只读/活动守卫拒绝 → native真实结果 → 自动行政/独立校验。

匹配器5秒有界只读，原Guard继续重新核实际字节/当前映射；服务前及服务内、seal与admin重查。发现任何关键hash/path/pkg/Build-ID/预加载或映射漂移即失败。所有点仍无法提供path→exec原子保证，当前TCB条件与后续映射记录须审查，不声称历史扫描永久有效。

原资源合同保持：1000000访问/1800秒、校准100000/300秒、预T0120秒、stop_at=T0+1740、AS1GiB/父TasksMax4。新增RA545完成/768硬，正常A3133完成/4417硬，完整68498≤100000。性能全链UNRESOLVED，实际观测额外IO/文件容量必须核验，硬界不扩。

自动post精确目标保持机制：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ra01/src/admin_postexit.py --post-exit-export
```

原AS1GiB/单次30秒先于源码/目标模块装载，加入只读身份核验，host32秒wait与35秒总回收、256文件/32MiB界保持。请求必要冻结当前批次关闭后备和故障保全，真实使用时独立登记，不能冒充自动成功。

未来回执需RuntimeAdapt诊断和provenance_assumptions显式批准位true、两项新合同摘要、既有TR/PF/PreT0/RootIPC/单会话兼容位齐全，真实用户原文SHA与最终两锁绑定。Full/MR/预窗注入false。当前所有位false、实际回执未创建。

首次关键失败立即停止发放、原流程关闭/适用seal/admin保全；禁止现场修改、重跑、预算/T0重置或第二免费窗。A2结束全部关闭，不进入MR/C09/C01–C12/S34/门18/F1/F4。即使A2通过，完整资源资格仍需新的独立许可与身份。

[未批准模板](evidence/TR_A2_AUTHORIZATION_TEMPLATE.json) · [运行时身份与规则](evidence/SOURCE_FINAL_R1/inputs/runtime_identity_contract.json) · [真实执行锁](evidence/SOURCE_FINAL_R1/inputs/execution_lock.json)
''')
report('FINAL_DECISION.md','RuntimeAdapt最终静态裁决','''
**已形成带明确来源条件的新基线RuntimeAdapt-static-1/r1，业务动态验证0。GNU libc仍2.39，Ubuntu包修订8.9→8.12，三项新文件身份/归属和静态必要兼容条件可复核。**

|验收门|结果|范围与未决边界|
|---|---|---|
|RA-1 版本与来源|CONDITIONAL_PASS|正确包归属/MD5/版本/日志、两签名与完整索引匹配；依赖Root/DB/keyring，缺新.deb独立payload再现|
|RA-2 兼容性|CONDITIONAL_PASS|66 ELF入口/114对象、必要版本需求无缺项，Python和当前map符合；全部行为/资源/服务仍待原生验证|
|RA-3 安全重冻结|CONDITIONAL_PASS|旧hash拒绝保留、3项显式新pin、包/路径/mappings等重查；path→exec原子性及后续特权替换边界保留|
|RA-4 执行准备|PASS_STATIC|64文件/44程序、RA32/8变异、资源68498及独立A2模板齐备，未批准|

本轮7次原生只读查询、3项纯ELF-note主机探针和20静态控制流断言完成；13保护文件字节/70成员AST、RootIPC/MR/Terminal模块和PT/PF/TR jobs保持。原host finalizer/entry字节保持；功能变更仅运行时检查及其授权/调用点/新增回归。

本轮安装/下载/系统库写入/WSL配置修改或重启均0；Launcher/服务/资源校准/PT/PF/TR/RA套件/生产oracle/F1/F4均0，T0/R=null。源与配置仅在新ra01和本轮交付目录适配，未来Linux源、实例和实际回执未创建。

旧TR-A的exit125/PREFLIGHT_FAILED、3项失配、T0/R未初始化、全部未运行及自动14/15行政成功保留。旧PFA112/17、R1907、native UNRESOLVED/internal UNKNOWN与行政成功保持。

新静态身份不是无条件执行批准；后续若不接受显式来源信任前提，保持RUNTIME_PROVENANCE_UNRESOLVED。下一步仅审阅[独立TR-A2申请](NEXT_DYNAMIC_AUTHORIZATION.md)，不恢复旧attempt，不直接进入MR或模型。

[来源裁决](RUNTIME_PROVENANCE_ASSESSMENT.md) · [安全矩阵](RUNTIME_SECURITY_IMPACT_MATRIX.md) · [最终源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('COMMAND_SUMMARY.md','七次只读平台调用与原始输出','''
本轮WSL调用7次，全部固定Ubuntu-24.04/root、/usr/bin/python3.12 -I -S -B -c的只读行政取证，无Launcher/service或预算对象。

1. 版本、dpkg校验/归属、apt-policy、工具与缓存清单、当前Python maps及LD环境。
2. 本地gpgv两个InRelease、完整Packages哈希、目录/MD5/日志/软件源记录。
3. 66 ELF种子与114对象静态依赖/版本图、readelf -h/-n/-d/-V/-l及资源符号、ldconfig -p只读缓存。
4. 三现行ELF/两完整索引保存、缓存旧8.9包只读成员提取与1241对象重新比较。
5. 旧ELF readelf -V、相关本地changelog和ubuntu-keyring完整性校验。
6. 最终字节稳定、systemd/kernel/UID/GID/cgroup、六加载配置、未来源/实例不存在核对。
7. 匹配器将读取的九项配置/目录文件O_NOFOLLOW元数据/访问条件核对。

精确argv、起止时间、exit、原始双流与SHA见[行政计划](evidence/ADMIN_COMMAND_PLAN.json)及evidence/commands/01–07.result.json。内部工具命令另在native_queries/elf_raw/provenance/old_new_abi保留。ldd仅--version，目标ELF仅读elf数据，旧包成员不执行。

[只读结果boot列表](evidence/FINAL_BINDING_REVIEW.json) · [行政操作说明](evidence/ADMIN_OPERATIONS.json)
''')
report('EVIDENCE_INDEX.md','运行时适配证据索引','''
|主题|工件|
|---|---|
|总裁决|[FINAL_DECISION](FINAL_DECISION.md)、[机器结果](evidence/STATIC_RESULT.json)|
|授权与门|[原文](evidence/TASK_REQUEST.txt)、[SCOPE_BOUNDARY](SCOPE_BOUNDARY.md)|
|版本/归属/完整性|[DISCOVERY](evidence/RUNTIME_DISCOVERY.json)、evidence/native_queries原始双流|
|来源/签名/索引|[审计](evidence/PROVENANCE_AUDIT.json)、[来源决定](evidence/PROVENANCE_DECISION.json)、evidence/provenance原InRelease/keyring/stanza/目录/日志|
|当前ELF/旧包/索引保存|[导出锁](evidence/PLATFORM_EXPORT.json)、evidence/platform_snapshot|
|ELF/ABI|[完整图](evidence/ELF_ABI_AUDIT.json)、[初图](evidence/ELF_ABI_AUDIT_INITIAL.json)、[旧新版本](evidence/OLD_NEW_SYMBOL_COMPARISON.json)、evidence/elf_raw与old_new_abi|
|配置与fresh条件|[最终平台](evidence/FINAL_PLATFORM_AUDIT.json)、[实际文件读取条件](evidence/MATCHER_FILE_ACCESS.json)|
|pin与源码差异|[3项pin](evidence/RUNTIME_PIN_DIFF.json)、[完整diff](evidence/FULL_DIFF.patch)、[前后SHA](evidence/FILE_DIFF_INDEX.json)|
|静态与保护|[20断言/3探针](evidence/SYNTAX_AND_IDENTITY_CONTROL_CHECK.json)、[13字节/70成员保持](evidence/PROTECTED_SEMANTICS_CHECK.json)、[导入图](evidence/IMPORT_GRAPH.json)|
|RA32/资源|[静态矩阵](evidence/RUNTIME_REGRESSION_STATIC_CHECK.json)、[预算重算](evidence/RESOURCE_BOUND_RECALCULATION.json)|
|新冻结与申请|[64项锁](evidence/STATIC_WORKSPACE_LOCK.json)、[绑定核验](evidence/FINAL_BINDING_REVIEW.json)、[未批准模板](evidence/TR_A2_AUTHORIZATION_TEMPLATE.json)|
|历史/交付|[旧包核验](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[8239基线](evidence/BASELINE_LOCK.json)、[历史保持](evidence/HISTORY_PROTECTION_CHECK.json)、[最终校验](evidence/DELIVERY_CHECK.json)|

所有业务套件和新RuntimeAdapt匹配器的原生服务调用尚未执行，Root只读进程映射不借作新batch14资格。
''')
report('README.md','DCL-R6-RuntimeAdapt-Fix','''
RuntimeAdapt-static-1/r1已静态冻结。GNU libc上游2.39未变，Ubuntu修订8.9→8.12；3项文件身份/包/签名索引与静态ABI必要条件核验完成，基线依赖受信Root/dpkg/keyring条件。

64文件/44程序，原严格摘要守卫保留，新增路径/包/Build-ID/自身映射重查及RA32/8变异。当前业务动态测试0，A2模板未批准，剩余执行身份原子性和完整性能未决。

[最终裁决](FINAL_DECISION.md) · [时间线](RUNTIME_CHANGE_TIMELINE.md) · [包审查](GLIBC_VERSION_AND_PACKAGE_AUDIT.md) · [3 ELF](ELF_THREE_COMPONENT_AUDIT.md) · [来源](RUNTIME_PROVENANCE_ASSESSMENT.md) · [Python ABI](PYTHON_NATIVE_ABI_COMPATIBILITY.md) · [安全矩阵](RUNTIME_SECURITY_IMPACT_MATRIX.md) · [锁精化](RUNTIME_LOCK_REFINEMENT.md) · [负向计划](RUNTIME_NEGATIVE_REGRESSION_PLAN.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [下一申请](NEXT_DYNAMIC_AUTHORIZATION.md) · [证据索引](EVIDENCE_INDEX.md)
''')
print(json.dumps({'required_reports':12,'markdown_files':len(list(O.glob('*.md'))),'version':R['version'],'readonly_WSL_calls':7,'business_dynamic_tests':0},ensure_ascii=False))
