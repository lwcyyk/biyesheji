"""Build declarative B1 review material from verified frozen inputs.

Outputs describe proposed semantics and approval questions. No executable
patch, quota allocator, runtime test or execution authorization is generated.
"""
import ast
import json
import re
from pathlib import Path
from AUDIT_INPUTS import ROOT, PREVIOUS, OUT, EVIDENCE, RUNTIME, read_json, digest, file_record, save

assert read_json(EVIDENCE / 'INITIAL_INTEGRITY.json')['runtime_objects'] == 64
future_review_root = ROOT / 'DCL-R6-B1-Maintenance-Review-PROPOSED'
assert not future_review_root.exists()

function_index = {}
for folder in ('src', 'host'):
    for path in sorted((RUNTIME / folder).glob('*.py')):
        source = path.read_text(encoding='utf-8-sig')
        tree = ast.parse(source)
        functions = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({'function': node.name, 'line': node.lineno, 'end_line': node.end_lineno})
            if isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        functions.append({'function': node.name + '.' + method.name,
                                          'line': method.lineno, 'end_line': method.end_lineno})
        function_index[path.relative_to(RUNTIME).as_posix()] = functions
save('FUNCTION_SOURCE_INDEX.json', function_index)

test_cases = [
    ('BQ01', '固定profile和字段边界', '原生三调用点的JSON键、ASCII、数值类型、LF和1322/948/1028槽满足来源profile'),
    ('BQ02', '256次与第257次', '第256条完整facts持久后吸收额度耗尽，第257次classify/event调用数增量均0'),
    ('BQ03', '两请求争最后额度', '同一稳定H锁内fresh read和持久预扣只产生一个新token'),
    ('BQ04', '七类别去重', '六stage与ACK各最多一次，重复token获得0写资格'),
    ('BQ05', '终态cleanup间隙', 'VERIFIED终态锁存先于解锁回收，分类重入被拒，后续两个合法stage仍按类别位处理'),
    ('BQ06', '预付部分失败', '256次scalar中途失败烧掉已付前缀，旧T0/R/intent与所有原字节留存'),
    ('BQ07', '预扣完成分界', 'cursor INFLIGHT、append前后和completion前后崩溃的余额单调，恢复转停止审查'),
    ('BQ08', '短写和fsync错误', 'raw部分尾部与staging保留，失败槽单次消费，结果UNKNOWN'),
    ('BQ09', '终态与过期', 'STOP/CLOSED/过期入口新观察数增量0，空余成功stage仅按适用终态定义使用'),
    ('BQ10', '外来或损坏cursor', 'binding/boot/handoff/hash/owner/size/type或残留staging异常触发拒绝和既有关闭入口'),
    ('BQ11', '调用者耗尽消费', 'guard调用者实际结束观察循环，外层abort层数符合冻结调用包络'),
    ('BQ12', '锁序', '进入M.abort和stop_tree前释放H生命周期锁，异常finalization责任可追溯'),
    ('BQ13', '共享标记写失败', 'EIO/ENOSPC时各角色取消可见性、实际退出与必要证据分别裁决'),
    ('BQ14', '资源与资格隔离', '新增检查全量记入delta，原资源资格和F1/F4条件独立核验'),
    ('BQ15', '独立原件oracle', '从原log/cursor/预付/绑定原件重算slot、行数、字节和部分尾部，缺件/换件/重复/跨版本拒绝')]
save('B1_TEST_OBLIGATIONS.json', {
    'artifact_type': 'DECLARATIVE_TEST_LIST_ONLY', 'tests_executed': 0,
    'future_test_manifest_relative': 'review_only/B1_TEST_CASES.json',
    'future_oracle_relative': 'review_only/b1_quota_oracle.py',
    'future_harness_relative': 'review_only/b1_quota_checks.py',
    'proposed_files_exist_now': False,
    'cases': [{'id': key, 'subject': subject, 'expected_evidence': evidence}
              for key, subject, evidence in test_cases],
    'oracle_contract': 'Separate source review and raw parser, no target logger/persistence imports, compare declared limits and raw evidence, classify partial/UNKNOWN honestly',
    'permission': 'Future explicit code and test authorization required after implementation gate prerequisites'})

clauses = []
def clause(number, title, group, value, proof, sites, domain, closed, dependencies, files, tests, effectiveness):
    clauses.append({'id': f'B-C{number}', 'title': title, 'class': group, 'parameter': value,
                    'existing_proof': proof, 'source_basis': sites, 'input_scope': domain,
                    'closure_status': closed, 'dependencies': dependencies, 'proposed_files': files,
                    'negative_tests': tests, 'applicability': 'Single newly approved bound source and handoff identity',
                    'effectiveness': effectiveness, 'approval_decision': None,
                    'approved': False, 'user_approved': False, 'effective': False, 'runtime_enabled': False})
clause(1, 'C09观察尝试上限', 'A', 256,
       '显式有限工程政策可独立选择，接受延迟witness可能导致额度耗尽关闭的活性代价',
       ['src/c09_handoff.py:252-279', 'src/guard.py:799-808'], '所有已准入尝试，包含预检和I/O失败的烧额路径',
       'POLICY_REVIEW_READY', ['B-C4', 'B-C5', 'B-C6耗尽关闭子合同'],
       ['src/c09_handoff.py', 'src/guard.py', 'inputs/c09_quota_contract.json'], ['BQ02', 'BQ06', 'BQ11'],
       '逻辑审批完成后仍须符合本轮B1实施门和独立源码/测试授权')
clause(2, '主日志记录数', 'B', 263,
       '256分类槽加六stage加ACK1，所有主日志生产者共享持久类别和预扣不变量',
       ['src/c09_handoff.py:75-89', 'src/c09_handoff.py:187,196,226,232,262,277,286,343'],
       '封闭原生调用域、单handoff、全路径含部分尾部写入尝试', 'CONDITIONAL_PROVED',
       ['B-C1', 'B-C4', '稳定H锁inode', '存储持久性和可信Root'], ['src/c09_handoff.py'],
       ['BQ03', 'BQ04', 'BQ05', 'BQ07'], '逐调用token注入证明、实现复核和已授权检查全部完成')
clause(3, '主日志字节预留', 'B', 345148,
       '256×1322＋6×948＋1028，compact sorted JSON与LF及现行字段profile',
       ['src/c09_handoff.py:15', 'src/c09_handoff.py:54-60', 'src/c09_handoff.py:75-84'],
       '现行main行与window键集、ASCII身份和约定数值ABI', 'CONDITIONAL_PROVED',
       ['B-C2', 'B-C4', '编码前字段验证', 'batch和mode长度profile'],
       ['src/c09_handoff.py', 'inputs/c09_quota_contract.json'], ['BQ01', 'BQ08', 'BQ15'],
       '源码/输入/授权摘要准确绑定，main schema变化触发重新计量')
clause(4, '预付、持久预扣和关闭空间责任', 'B',
       {'prepay_visits': 256, 'main_reserved_bytes': 345148, 'physical_close_space': None},
       '旧v2给出预付→local预扣→主行fsync→completion及终态锁存逻辑，完整空间充分性仍未决',
       ['src/guard.py:629-691', 'src/guard.py:1095-1096', 'src/boot_continuity.py:78-109', 'src/manager_recovery.py:453-467'],
       'C09H/IPC/BC完成后、launch_one(C09)前的受信Root阶段及随后原生日志', 'PARTIAL_ORDER_PROVED_SPACE_OPEN',
       ['有效C00 ticket和旧deadline', '单次预付绑定', 'B-C6', '跨角色失败可见性'],
       ['src/c09_handoff.py', 'src/guard.py', 'inputs/c09_quota_contract.json'],
       ['BQ06', 'BQ07', 'BQ08', 'BQ10', 'BQ12', 'BQ13'],
       '关闭必要空间、持久/异常模型和B1调用图接线均需具体验证')
clause(5, '超额观察前置拒绝', 'B', {'rejected_attempt': 257, 'new_classifications': 0, 'new_main_rows': 0},
       '拒绝置于事实构造/classify/event之前，调用者消费耗尽并结束观察循环',
       ['src/c09_handoff.py:252-279', 'src/guard.py:799-818'],
       '已耗尽或相同token重放、STOP/CLOSED后入口', 'SEMANTIC_OBLIGATION_READY',
       ['B-C1', 'B-C4', 'B-C6', 'outer abort责任有限'], ['src/c09_handoff.py', 'src/guard.py'],
       ['BQ02', 'BQ09', 'BQ11', 'BQ12'], '完整caller/sink/关闭调用链静态和授权负向检查通过')
null_specs = [
    (6, '完整关闭保留量', 'B_close与必要停止来源的剩余空间/隔离', ['src/manager_recovery.py:317-400', 'src/guard.py:749-769', 'src/root_ipc.py:91-129'], ['BQ08','BQ12','BQ13']),
    (7, '行政证据最大数量', '选定的新export数量和实施/测试集合差', ['src/startup_lifecycle.py:495-510', 'host/startup_finalize.py:96-118'], ['BQ14','BQ15']),
    (8, 'Native ZIP最大成员数', '选定的新member cap和全量原件集合', ['src/guard.py:1019-1027', 'src/terminal_evidence.py:158'], ['BQ14','BQ15']),
    (9, '完整总字节', 'B_other、raw、native、admin各层字节和嵌套复制', ['src/guard.py:1019-1027', 'src/startup_lifecycle.py:493-519'], ['BQ14','BQ15']),
    (10, '单文件最大大小', 'TCB诊断、kernel字段、模型/终态/host原始流profile', ['src/guard.py:96-97,718-721', 'src/terminal_evidence.py:259-263', 'host/windows_entry.py:50-60'], ['BQ01','BQ08','BQ15']),
    (11, '内存、FD、IO与syscall', '全路径峰值和最大操作/读取/写入量', ['src/guard.py:96,718', 'src/startup_lifecycle.py:386-410,461', 'host/startup_finalize.py:118'], ['BQ13','BQ14']),
    (12, 'native与行政封存资源', 'builder/readers、manifest、压缩膨胀、raw完整性和资源匹配', ['src/guard.py:993-1027', 'src/terminal_evidence.py:143-186', 'host/startup_finalize.py:52-121'], ['BQ14','BQ15']),
    (13, '墙钟与外部TCB假设', '定量调度、fsync、manager、host完成时延', ['src/terminal_evidence.py:196', 'src/admin_postexit.py:46-65', 'host/windows_entry.py:42'], ['BQ13','BQ14'])]
for number, title, reason, sites, tests in null_specs:
    clause(number, title, 'C', None, reason, sites, '完整新版本scope及其必要输入/错误模型', 'NULL_BLOCKS_EFFECTIVENESS',
           ['ResidualBounds最终未决责任', '确切源码/输入/测试差异和审批'],
           ['DEPENDENCY_SCOPE_REQUIRES_SEPARATE_REQUEST'], tests,
           '数值、来源证明、完整性/超限语义和版本隔离条件齐备后才能独立审批生效')
assert len(clauses) == 13
save('CAPACITY_CLAUSE_MATRIX.json', {'classes': {'A':'逻辑政策可独立审议', 'B':'条件证明需显式TCB和接线义务', 'C':'null阻断完整容量生效'},
                                     'clauses': clauses, 'all_actual_approvals': None})

plans = []
def file_plan(relative, category, functions, issue, delta, invariant, tests, dependency, rollback):
    path = RUNTIME / relative
    info = {'file': str(path), 'relative': relative, 'current_hash': digest(path), 'bytes': path.stat().st_size,
            'category': category, 'affected_function': functions, 'issue': issue, 'proposed_delta': delta,
            'invariant': invariant, 'regression': tests, 'dependency': dependency, 'rollback': rollback,
            'current_changes': 0}
    plans.append(info)
file_plan('src/c09_handoff.py', 'FUTURE_MINIMUM_BEHAVIORAL_CANDIDATE',
          ['lifecycle_lock:40','event:75','publish:85','sender_prepare:168','Receiver.poll:205','Receiver.observe_exit:252','resume_admission:323'],
          'PENDING反复append，全部三event调用与六stage必须共用额度不变量',
          '独立cursor绑定/七类别位/持久预扣与completion/终态锁存/封闭schema，额外policy和ordinal放cursor，耗尽消费沿现有异常关闭链请求',
          '当前main/window编码、ACK/commit/witness、安全谓词classify、原预算快照与一次resume语义作为保持式',
          ['BQ01','BQ02','BQ03','BQ04','BQ05','BQ07','BQ08','BQ09','BQ10','BQ15'],
          ['guard调用者与预付','BC.Store私有JSON','c09_contract和新quota输入','B-C6关闭子合同'],
          '将来隔离候选可整体弃用，授权前源摘要可复核，已消费预算/已有终态保留为原件')
file_plan('src/guard.py', 'FUTURE_MINIMUM_BEHAVIORAL_CANDIDATE',
          ['authorization:232','c09_contract:334','_external_stop_impl:771','external_stop:813','_launcher_work:1028'],
          '原caller只消费VERIFIED/CLOSED，新的耗尽返回值会落回循环，scalar预付依赖正确ticket和时点',
          '在1095后与1096前绑定有效C00票据并256次scalar预付，恢复_TICKET，加载并核验新quota契约，明确耗尽异常从H锁释放后到808/817既有abort责任',
          '630-691预算核心、真实CLOSED含义、counter固定后R稳定、资格门和所有既有期限作为保持式',
          ['BQ02','BQ06','BQ09','BQ11','BQ12','BQ13','BQ14'],
          ['c09_handoff','current C00 ticket','source/input/authorization锁','M.abort接口'],
          '隔离候选source/输入/锁按同一版本撤回，现行运行目录和已关闭实例保持审计来源')
file_plan('src/manager_recovery.py', 'INTERFACE_REVIEW_REQUIRED_CHANGE_NOT_SELECTED',
          ['abort:317','_stop_other_roots:291','permit_external_seal:405','seal:414','prepay:453'],
          '耗尽经两层abort并生产首错、STOP/CLOSED、attempt/state等独立证据，必要关闭空间未证明',
          '本次文件级计划仅核对接口、双层调用次数、错误/UNKNOWN和锁序，改变MR关闭责任须追加明确文件和合同审批',
          '首错语义、原预算/期限、真实pidfd/组空、单sealer和跨实例规则作为依赖保持式',
          ['BQ11','BQ12','BQ13','BQ15'], ['B-C6','guard异常链','RootIPC','BC.Store'],
          '待审申请未选定MR行为修改，后续独立diff需要独立回退版本')
file_plan('src/boot_continuity.py', 'EXISTING_HELPER_READ_DEPENDENCY',
          ['Store.read:78','Store.put:86','entry:415'], '私有JSON发布可复用，但输入quota控制与残留staging消费由调用者承担',
          '使用现有私有.json路径语义审查cursor和首错存储，完整大小验证和单次失败责任在拟B1调用层说明',
          'Root权限、metadata、file/directory fsync、单次activation/resume保持式',
          ['BQ07','BQ08','BQ10'], ['RootIPC目录链','quota schema'], '只读依赖版本锁')
file_plan('src/root_ipc.py', 'EXISTING_HELPER_READ_DEPENDENCY',
          ['policy:21','publish:91','checkpoint:143'], '关闭marker使用新增staging且共享storage，可信来源与空间保证需分别核验',
          '核对现行STOP/CLOSED目标与取消支配性，选择BC.Store私有域后无需新增RootIPC目标',
          '可信权限/无链接发布/取消支配/跨目录fsync作为保持式', ['BQ08','BQ09','BQ13'], ['B-C6'], '只读依赖版本锁')
file_plan('src/c09_regression.py', 'EXISTING_SYNTHETIC_REFERENCE', ['Subject.step:10','run_suite:52'],
          'H34合成classify轨迹缺原生日志quota I/O覆盖', '用于回归语义基线，新增quota检查另列review_only计划',
          'H1-H8原定义和已冻结34 jobs', ['BQ14','BQ15'], ['c09_oracle.py'], '原合成基线持续作为读取输入')
file_plan('src/c09_oracle.py', 'EXISTING_SYNTHETIC_REFERENCE', ['check_job:41','check_suite:79'],
          '既有oracle验证合成truth和收费，主log/cursor新原件需独立计划', '原函数作为保持式，新quota oracle在独立review_only路径提出',
          '独立H1-H8判断和原始事件集合/计费检查', ['BQ15'], ['new oracle plan'], '原oracle版本锁')
for relative, reason, delta in [
    ('inputs/c09_contract.json','需绑定quota profile与测试范围','仅提出新版本quota引用/作用域/字节profile字段'),
    ('inputs/static_manifest.json','源码和输入内容摘要改变时需绑定','source_hashes/bound_inputs与新quota输入摘要的独立重冻结'),
    ('inputs/execution_lock.json','manifest与quota契约需要精确绑定','未来只在静态review lock固定新manifest/契约摘要，运行身份和授权另行审批')]:
    file_plan(relative, 'FUTURE_INPUT_BINDING_CANDIDATE', ['JSON bound fields'], reason, delta,
              '版本完整性与授权来源', ['BQ01','BQ10','BQ14','BQ15'], ['source_manifest','quota_contract'],
              '候选输入与对应source/lock整组弃用，历史原件保持')
for relative, reason in [
    ('inputs/manager_contract.json','当前MR接口读取依赖，MR行为差异尚未选定'),
    ('inputs/batch_identity.json','当前旧namespace读取依赖，新运行身份须后续明确授权'),
    ('inputs/runtime_tree_lock.json','绑定Python标准库树，B1同运行时假设下作为只读TCB依赖'),
    ('src/terminal_evidence.py','终态/归档读取门的后层依赖'),
    ('src/startup_lifecycle.py','行政导出与原256守卫后层依赖'),
    ('host/startup_finalize.py','host封存/原始流后层依赖')]:
    file_plan(relative, 'READ_ONLY_BOUNDARY_DEPENDENCY', ['frozen file'], reason,
              '仅核对绑定及当前责任', '原始证据/资格/权限和范围保持式', ['BQ14','BQ15'], ['full capacity'], '只读依赖版本锁')
save('B1_FILE_PLAN.json', {'files': plans, 'future_review_root': str(future_review_root), 'future_root_status':'PROPOSED_ABSENT',
                         'future_root_choice':'Assistant planning suggestion for a separate review-only sibling directory, subject to user adoption',
                         'behavioral_candidates': ['src/c09_handoff.py','src/guard.py'],
                         'manager_recovery_role': 'INTERFACE_REVIEW_REQUIRED_CHANGE_NOT_SELECTED',
                         'implementation_admission': 'B1_BLOCKED_BY_CLOSE_RESERVE'})
proposed = [
    {'relative':'inputs/c09_quota_contract.json','role':'quota固定schema、上限、绑定、失败/终态及生效前提'},
    {'relative':'review_only/B1_TEST_CASES.json','role':'15项negative/边界义务的纯数据清单'},
    {'relative':'review_only/b1_quota_checks.py','role':'未来经批准的独立静态/隔离harness'},
    {'relative':'review_only/b1_quota_oracle.py','role':'未来经批准的独立raw重算oracle'},
    {'relative':'review_only/B1_STATIC_REVIEW_LOCK.json','role':'未来候选源码、输入、测试清单和独立oracle的准确摘要锁'}]
for item in proposed:
    item.update(file=str(future_review_root/item['relative']),current_hash=None,
                affected_function='Future contract/data or oracle/harness entry defined by explicit authorization',
                issue='现有冻结文件集合没有该新quota原件/评审对象',proposed_delta=item['role'],
                invariant='原始记录与绑定可独立重算，权限与生效状态显式核验',
                regression=['BQ01','BQ10','BQ14','BQ15'],
                dependency=['B1关闭子合同','独立代码/检查授权','确切source/input绑定'],
                status='PROPOSED_ABSENT', created_now=False,
                container='future separately approved review root', rollback='候选目录整体撤回且保留已生成研究证据')
save('FUTURE_FILE_SLOTS.json', {'future_review_root':str(future_review_root),'files':proposed,'runnable_patch_generated':False})

steps = [
    ('SD01','绑定与版本','static_manifest/execution_lock/authorization及quota输入全部精确绑定，profile字段有唯一schema标识','guard.py:232-278'),
    ('SD02','预付位置','C09H、RootIPC和BC资格结束后，在launch_one(C09)前完成256次scalar预付，依赖有效C00 ticket及原calibration deadline','guard.py:1095-1096,629-691'),
    ('SD03','初始化与handoff绑定','预付cursor初始化独占一次，已有/foreign/残留/模糊记录进入拒绝，handoff_id确定后同H锁绑定一次','c09_handoff.py:168-187'),
    ('SD04','全部主行sink','event、六publish与ACK共享类别/slot/字节预扣，新增policy/ordinal放cursor以维持原main schema','c09_handoff.py:75-89,196,277'),
    ('SD05','观察准入','停止、身份和现有终态门后，在check_base/facts/classify/event前消费一个新观察资格，失败烧额','c09_handoff.py:252-277'),
    ('SD06','持久完成','预扣cursor持久后进行一次raw append/fsync，再发布完成cursor，成功终态先锁存后解锁cleanup','c09_handoff.py:277-287'),
    ('SD07','额度耗尽','256th PENDING原始facts完整保留，发布耗尽吸收状态。候选采用现有AdmissionBlocked及固定quota耗尽代码衔接，H上下文退出后由外层异常路径消费，257分类/主行增量0','guard.py:799-818'),
    ('SD08','既有异常关闭','固定异常经过H上下文释放后交付808和817两层现有M.abort，实际退出及所有必要收据计量，耗尽异常终止原观察循环','guard.py:806-823;manager_recovery.py:317-400'),
    ('SD09','重放与恢复','相同binding/handoff/kind/ordinal再次提交为已消耗，模糊持久化恢复进入停止/UNKNOWN，T0和账保留原来源','c09_handoff.py:323-347'),
    ('SD10','封存和oracle','新raw/cursor/首错/staging按唯一路径计入未来Δ，独立oracle重算，原封存和资格接口接受完整原件','guard.py:993-1027')]
save('SEMANTIC_DIFF_STEPS.json', {'artifact_type':'NATURAL_LANGUAGE_SEMANTIC_PLAN',
                                 'steps':[{'id': key,'subject': subject,'required_semantics': text,'source': source}
                                          for key,subject,text,source in steps],
                                 'patch_or_implementation':False})

requirements = [
    {'id':'ID-1','user_requirement':'耗尽维护现有关闭路径','status':'CONDITIONAL_PASS',
     'evidence':'guard808/817和M.abort提供现有接口，拟语义需释放H锁及结束循环', 'remaining':'具体接线/重复关闭责任尚待证明'},
    {'id':'ID-2','user_requirement':'必要停止信息有受信保留来源','status':'UNRESOLVED',
     'evidence':'RootIPC权限和fsync来源明确，BC.Store私有对象存在', 'remaining':'主log/cursor后剩余空间、独立保留量与隔离未证明'},
    {'id':'ID-3','user_requirement':'超额观察日志增长有界','status':'CONDITIONAL_PASS',
     'evidence':'主quota可规定257前置0分类0主行', 'remaining':'caller必须消费耗尽并一次性退出，MR其他日志沿已证调用图计量'},
    {'id':'ID-4','user_requirement':'预算和CLOSED语义','status':'CONDITIONAL_PASS',
     'evidence':'原scalar核心、check_base.counter和stopped为明确保持式', 'remaining':'预付时点、有效_TICKET、缺cursor/闭后请求及恢复差异验证'},
    {'id':'ID-5','user_requirement':'资源资格来源','status':'PASS_STATIC',
     'evidence':'本轮逻辑草案及B1计划的权限状态为未批准，当前formal gate依赖仍为实际资源资格', 'remaining':'后续diff必须复核资格调用保持式'}]
save('B1_INDEPENDENCE_GATE.json', {
    'status':'B1_BLOCKED_BY_CLOSE_RESERVE', 'BG-2':'BLOCKED',
    'authority':'Current request section六 explicitly requires sufficient trusted retention and safe exhaustion before independent B1 implementation',
    'requirements':requirements,
    'minimal_obligations':['B1耗尽/模糊持久化需要共享停止和原有关闭原件',
                           '主log/cursor与STOP/CLOSED的staging使用实际存储，可信写入权限只建立来源',
                           '必要关闭子集的剩余空间/隔离及失败责任暂无可核验充分性证据'],
    'counterexample':'候选组合前缀将最后主行和完成cursor成功保存，随后STOP/CLOSED staging创建返回ENOSPC。实际回收可继续尝试，必要持久停止证据保持UNKNOWN。',
    'counterexample_type':'PROPOSED_COMPOSITION_REASONING_ONLY',
    'full_capacity_relation':'A sufficiently proven restricted close sub-contract could address the direct B1 gate. Existing full admin/native nulls remain later fullchain gates. Current evidence provides neither a complete close bound nor that restricted proof.',
    'current_B_close':None,'current_B_other':None,'implementation_permission':None,
    'unlock_evidence_required':['精确B1耗尽/持久化失败所需对象、写者和原件集合',
                                '这些对象的记录数/encoded bytes/失败staging及资源上界',
                                '相对main、cursor和新预付journal的可用空间与隔离或等价保留证明',
                                '可信持久顺序、跨角色失败可见性和H锁释放后的关闭责任',
                                'I/O故障下实际回收、外部证据与UNKNOWN的有限语义'],
    'pending_revision_after_gate':'Any added closing allocator, storage contract, shared failure responsibility or MR change requires a separately bounded request'})

nodes = ['logical_clauses','minimum_semantic_scope','exhaustion_close_subcontract','B1_admission',
         'native_source_authorization','isolated_candidate','candidate_validation_and_delta',
         'full_close_contract','archive_resource_proof','full_capacity_contract','archive_and_oracle_contract',
         'MR_principle_approval','MR_native_evidence_pair_use','fullchain_dynamic_authorization',
         'new_identity_lock_preflight','current_calibration','RESOURCE_GATE_PASS','F1_F4']
edges = [('logical_clauses','B1_admission'),('minimum_semantic_scope','B1_admission'),('exhaustion_close_subcontract','B1_admission'),
         ('B1_admission','native_source_authorization'),('native_source_authorization','isolated_candidate'),
         ('isolated_candidate','candidate_validation_and_delta'),('candidate_validation_and_delta','full_capacity_contract'),
         ('candidate_validation_and_delta','archive_resource_proof'),('archive_resource_proof','full_capacity_contract'),
         ('full_close_contract','full_capacity_contract'),('full_capacity_contract','archive_and_oracle_contract'),
         ('archive_and_oracle_contract','fullchain_dynamic_authorization'),('MR_principle_approval','MR_native_evidence_pair_use'),
         ('MR_native_evidence_pair_use','fullchain_dynamic_authorization'),('candidate_validation_and_delta','fullchain_dynamic_authorization'),
         ('fullchain_dynamic_authorization','new_identity_lock_preflight'),('new_identity_lock_preflight','current_calibration'),
         ('current_calibration','RESOURCE_GATE_PASS'),('RESOURCE_GATE_PASS','F1_F4')]
save('DEPENDENCY_GRAPH.json', {'nodes':nodes, 'edges':edges,
                              'direct_B1_blocker':'exhaustion_close_subcontract',
                              'formal_model_gate':'Current RESOURCE_GATE_PASS is produced inside an authorized qualification run before F1/F4',
                              'MR_scope':'Intended strengthened fullchain uses separately approved finite cross-instance evidence rule with actual pair/certificate/use',
                              'reviewed_only':True})

runtime_tree = read_json(RUNTIME / 'inputs/runtime_tree_lock.json')
keys = list(runtime_tree['files'])
save('BINDING_SCOPE_REFINEMENTS.json', {
    'runtime_tree_lock': {'source':file_record(RUNTIME / 'inputs/runtime_tree_lock.json'),
                         'entries':len(keys),'sample_paths':keys[:3],
                         'application_source_entries':[key for key in keys if key.endswith(('/c09_handoff.py','/guard.py','/manager_recovery.py'))],
                         'B1_status':'READ_ONLY_TCB_DEPENDENCY_UNLESS_RUNTIME_CHANGED'},
    'main_schema': 'extra quota/ordinal/policy fields belong in cursor. Changes to main row or h.window require re-deriving1322/948/1028 and345148.',
    'prepay_ticket': 'Existing C00 ticket retains calibration ceiling T0+300 from guard931. Future prepay must fresh-read/check it and restore _TICKET in every path.',
    'prior_quota_schema_issue':read_json(EVIDENCE / 'DRAFT_HASH_AND_STATUS_CHECK.json')['quota_v2_format_note'],
    'idempotence_scope':'observe_exit() keeps its zero-argument interface. Distinct observations with unchanged facts consume new ordinals. Replay identity refers to an already reserved internal token, lifecycle category or ACK.',
    'staging_ownership_obligation':'BC.Store uses generic random .bc.<pid>.<nonce> names. Future B1 must establish binding/current-writer and residue ownership under H lock without confusing unrelated live updates. Any required helper API change expands the request explicitly.',
    'prepay_after_vs_handoff_counter':'Existing C09 controller charges one Budget.visit before its ready marker. The prepay end prefix and final handoff.counter are separate snapshots with the intervening legal charge accounted.',
    'contract_raw_availability':'New quota source JSON is a required frozen input to the future independent oracle. Static review package and lock retain it. Runtime/native/admin collector availability and path-set delta require explicit later accounting.',
    'documentation_only':True})

prepay_sizes = {}
intent_sizes = {}
for status in ('PREPARED','COMMITTED'):
    record = {'protocol':'EXACT-RANGE/1','status':status,'before':0,'after':0,'amount':1,'cap':1000000,
              'request':None,'boottime':0,'utc_ns':0,'boot_id':'b'*36}
    width_delta = 2*(7-1)+(25-1)+(20-1)
    prepay_sizes[status] = len((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())+width_delta
    intent_sizes[status] = len(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2).encode())+width_delta
assert prepay_sizes == {'PREPARED':238,'COMMITTED':239}
assert intent_sizes == {'PREPARED':278,'COMMITTED':279}
save('RESOURCE_IMPACT_MODEL.json',{
    'artifact_type':'STATIC_CODEC_AND_CALL_COUNT_ARITHMETIC',
    'prepay':{'global_visit_increment_healthy':256,'completed_transactions':256,'journal_rows':512,
              'journal_line_bounds':prepay_sizes,'journal_byte_increment_upper':256*sum(prepay_sizes.values()),
              'intent_write_bounds':intent_sizes,'intent_write_bytes_upper':256*sum(intent_sizes.values()),
              'counter_write_bytes':256*8,'data_write_attempts':256*5,
              'total_data_write_bytes_upper':256*(sum(prepay_sizes.values())+sum(intent_sizes.values())+8),
              'fsync_calls_healthy_root':256*9,
              'fsync_basis':'Each Root scalar reservation has two RootIPC intent writes at3 sync calls each, two journal fsync calls and one counter fsync call',
              'source':'guard.py:597,624-691; root_ipc.py:91-129',
              'conditions':'fixed scalar request=None, old positive decimal<=7, bootUUID36, binary64<=25, utc_ns<=20, successful Root publication'},
    'local_v2_proposed_only':{'cursor_bytes':1198,'cursor_updates':522,'retained_subset_bytes':350166,
                              'data_write_bytes':971216,'durability_attempts':1316,
                              'status':'historical draft component model, requires current-writer/residue/single-poison and exact codec obligations'},
    'count_deltas':{'new_stable_quota_objects_proposed':2,'failed_quota_staging_proposed_max':3,
                    'source_input_review_oracle_test_lock_paths':'See future file slots, each scope/layer requires its own delta',
                    'full_runtime_raw_delta':None,'new_export_member_cap':None},
    'visits':{'prior_scope_bound':68498,'plus_quota_prepay':68754,'additional_checks_delta':None,
              'effective_phase_limits':'Existing per-phase/global/calibration caps and valid ticket deadlines still apply'},
    'full_memory_FD_IO_syscalls':None,'whole_close_bytes':None,'whole_native_admin_bytes':None,
    'WALL_TIME_BOUND':'UNRESOLVED','new_execution_window_created':False})

bindings = read_json(PREVIOUS / 'evidence/DECISION_BINDINGS.json')
mr = read_json(bindings['MR_rule']['path'])
mrtext = ROOT / 'DCL-R6-C09-BoundClosure/MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md'
numbers = re.findall(r'^(\d+)\. ', mrtext.read_text(encoding='utf-8'), re.MULTILINE)
assert numbers == [str(index) for index in range(1,15)]
save('MR_APPROVAL_RECHECK.json', {'rule':file_record(Path(bindings['MR_rule']['path'])), 'text':file_record(mrtext),
                                 'rules':14, 'user_approved':mr['user_approved'], 'runtime_enabled':mr['runtime_enabled'],
                                 'evidence_usable_now':mr['evidence_usable_now'], 'status':'PROPOSED_NOT_EFFECTIVE',
                                 'user_decision_received':False})

OUT.joinpath('proposals').mkdir(exist_ok=True)
flags = {'approved':False,'user_approved':False,'effective':False,'runtime_enabled':False,'user_decision':None}
approval = {'schema':'DCL-B1-CAPACITY-LOGICAL-APPROVAL/1-DRAFT', 'version':'B1-ApprovalGate/review-1', **flags,
            'clauses':clauses, 'review_ready':['B-C1','B-C2','B-C3','B-C4 logical order only','B-C5 local rejection requirement'],
            'full_capacity':'CAPACITY_CONTRACT_NOT_READY','B1_implementation_admission':'B1_BLOCKED_BY_CLOSE_RESERVE',
            'source_implementation_authority':None,'dynamic_authority':None}
request = {'schema':'DCL-B1-MINIMUM-MAINTENANCE-REQUEST/1-DRAFT','version':'B1-ApprovalGate/review-1',**flags,
           'status':'B1_BLOCKED_BY_CLOSE_RESERVE','admission_approval_eligible_now':False,
           'future_review_root':str(future_review_root),'future_review_root_status':'PROPOSED_ABSENT','files':plans,'new_file_slots':proposed,
           'test_obligations':[item[0] for item in test_cases],
           'unlock_obligations':read_json(EVIDENCE/'B1_INDEPENDENCE_GATE.json')['minimal_obligations'],
           'current_allowed_artifact':'natural language semantic plan and pending approval material',
           'rollback':'Future unexecuted isolated candidate may be retired as a whole with its evidence kept. Any executed identity would remain permanently closed with its budget and original evidence retained.',
           'new_execution_lock_created':False,'runtime_patch_created':False}
permissions = {'schema':'DCL-B1-FOUR-PERMISSION-REVIEW/1-DRAFT','version':'B1-ApprovalGate/review-1',**flags,
    'CAPACITY_CONTRACT_APPROVAL':{'logical_status':'CONDITIONAL_PASS','total_effectiveness':'BLOCKED_NULLS','user_decision':None},
    'MR_CROSS_INSTANCE_APPROVAL':{'status':'PROPOSED_NOT_EFFECTIVE','rule_sha256':bindings['MR_rule']['sha256'],'user_decision':None},
    'NATIVE_IMPLEMENTATION_AUTHORIZATION':{'status':'B1_BLOCKED_BY_CLOSE_RESERVE','scope_prepared':True,'user_decision':None,'executable_permission':False},
    'FULLCHAIN_DYNAMIC_AUTHORIZATION':{'status':'BLOCKED','user_decision':None,'executable_permission':False},
    'independent_permissions':True,
    'decision_forms':{
       'CAPACITY_CONTRACT_APPROVAL':{'eligible_now':'finite logical policy and conditional-bound review',
          'choices':['APPROVE_LISTED_LOGICAL_CLAUSES_WITH_CONDITIONS','RETURN_FOR_REVISION','REJECT_LISTED_CLAUSES'],
          'selected':None,'activation_requires':'individual clause dependencies and full-capacity nulls handled explicitly'},
       'MR_CROSS_INSTANCE_APPROVAL':{'eligible_now':'exact original14-rule principle decision',
          'choices':['APPROVE_EXACT_LIMITED_RULE_PRINCIPLE','REJECT_OR_RETURN_EXACT_RULE'],
          'selected':None,'rule_sha256':bindings['MR_rule']['sha256']},
       'NATIVE_IMPLEMENTATION_AUTHORIZATION':{'eligible_now':'scope acceptance, revision or defer decision',
          'choices':['ACCEPT_SCOPE_DEFER_IMPLEMENTATION_ADMISSION','RETURN_SCOPE_FOR_REVISION','REJECT_CURRENT_REQUEST'],
          'selected':None,'source_mutation_permission':False,'admission_blocker':'B1_BLOCKED_BY_CLOSE_RESERVE'},
       'FULLCHAIN_DYNAMIC_AUTHORIZATION':{'eligible_now':'defer or reject current dynamic request',
          'choices':['DEFER_UNTIL_REQUIRED_EVIDENCE_AND_AUTHORIZATION','REJECT_CURRENT_DYNAMIC_REQUEST'],
          'selected':None,'execution_identity':None,'argv':None,'T0':None,'budget_account':None,'run_permission':False}}}
for name, data in [('CAPACITY_LOGICAL_CLAUSES_DRAFT.json',approval),('B1_MAINTENANCE_REQUEST_DRAFT.json',request),('FOUR_PERMISSION_REVIEW_DRAFT.json',permissions)]:
    path = OUT / 'proposals' / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
save('APPROVAL_OBJECT_BINDINGS.json', {'files':[file_record(path) for path in sorted((OUT/'proposals').glob('*.json'))],
                                       'MR_original_rule':bindings['MR_rule'], 'approval_received':False})
save('GENERAL_G_COMPARISON.json', {'input_family':'同一handoff的n次缺witness观察、并发token重放和持久化失败',
                                   'metrics':['原始记录/字节','持久写次数','至多一次额度','关闭证据完整性'],
                                   'strong_G':'标准有界追加日志、原子计数、持久预付、幂等token、独立关闭预留和版本化manifest',
                                   'candidates':['有界追加日志','原子额度','预付持久化','幂等task_id/token','固定reason token','独立关闭保留','标准manifest','版本化容量'],
                                   'status':'COVERED_BY_G','predicted_strict_gap':0,'necessary_higher_cost_instance_for_G':None,
                                   'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'})
print(json.dumps({'clauses':len(clauses),'file_rows':len(plans),'future_slots':len(proposed),
                  'tests_planned':len(test_cases),'B1_admission':'B1_BLOCKED_BY_CLOSE_RESERVE'}))
