"""Offline evidence review, Chinese reports and byte-sealed RootIPC review package."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import ast
import hashlib
import json
import os
import re
import struct
import zipfile

E=Path(__file__).resolve().parent
P=E.parent
ROOT=P.parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ri01')
OLD=Path(r'D:\毕业设计\DCL-R6-isolated-verification\c09f01')
B05=ROOT/'DCL-R6-batch05'
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch05\native_snapshot')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def dump(path,x):Path(path).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def link(path,label=None):return '['+(label or Path(path).name)+'](<'+os.path.relpath(path,P).replace('\\','/')+'>)'
def tab(headers,rows):
    def c(x):return str(x).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(c,row))+'|' for row in rows])
def report(name,title,text):
    (P/name).write_text('# '+title+'\n\nMaterial Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。\n\n'+text.strip()+'\n',encoding='utf-8')
def point(name,func):
    tree=ast.parse((W/'src'/name).read_text())
    node=next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==func)
    return link(W/'src'/name,name+':'+str(node.lineno)+' '+func)


baseline=load(E/'BASELINE_LOCK.json');frozen=load(E/'STATIC_WORKSPACE_LOCK.json')
m=load(W/'inputs/static_manifest.json');lock=load(W/'inputs/execution_lock.json');cfg=load(W/'inputs/root_ipc_contract.json')
checks=load(E/'AST_AND_INVARIANT_CHECK.json')
assert frozen['freeze_revision']=='r4'
history=[]
def verify(name,rows,path,key='sha256'):
    errors=[]
    for row in rows:
        q=path(row)
        if not q.is_file() or sha(q)!=row[key] or ('bytes'in row and q.stat().st_size!=row['bytes']):errors.append(str(q))
    history.append({'name':name,'count':len(rows),'mismatches':errors,'status':'PASS_ADMIN_ONLY' if not errors else 'FAIL'})
    assert not errors,(name,errors)
verify('505 historical research originals',baseline['history'],lambda r:ROOT/r['relative'])
verify('c09f01 original37',baseline['source'],lambda r:OLD/r['relative'])
verify('new static ri01 final44',frozen['files'],lambda r:W/r['relative'])
for folder in ['DCL-R6-GapClosure','DCL-R6-BudgetFix']:
    x=load(ROOT/folder/'evidence/STATIC_WORKSPACE_LOCK.json');verify(folder,x['files'],lambda r,x=x:Path(x['host'])/r['relative'])
for folder in ['DCL-R6-batch04','DCL-R6-batch05']:
    for fn in ['NATIVE_EXPORT_LOCK.json','FROZEN_SOURCE_EXPORT_LOCK.json']:
        x=load(ROOT/folder/'evidence'/fn);verify(folder+'/'+fn,x['files'],lambda r:Path(r['host']))
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/BASELINE_LOCK.json');verify('batch02 original51',x['immutable_B02_external'],lambda r:Path(r['path']))
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');verify('mispath47 read/hash only',x['files'],lambda r:Path(x['path'])/r['relative'],'duplicate_sha256')
for r in baseline['navigation']:assert sha(r['snapshot'])==r['sha256']
assert struct.unpack('<QQ',(N/'out/visits.bin').read_bytes()[8:])==(37293,1000000)
journal=[json.loads(s) for s in (N/'out/visits.bin.journal.jsonl').read_text().splitlines()]
assert Counter(x['status'] for x in journal)=={'PREPARED':303,'COMMITTED':303}
native_manifest=load(N/'out/EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(N/'out/EVIDENCE.zip') as z:
    assert len(z.namelist())==346
    for rel,row in native_manifest['files'].items():assert hashlib.sha256(z.read(rel)).hexdigest()==row['sha256']
with zipfile.ZipFile(B05/'BATCH05_EVIDENCE.zip') as z:
    old_package=json.loads(z.read('OUTPUT_MANIFEST.json'))
    for row in old_package['files']:assert hashlib.sha256(z.read(row['archive_path'])).hexdigest()==row['sha256']
    old_entries=len(z.namelist())
old_command=load(B05/'evidence/commands/24.result.json')
old_journal=load(B05/'evidence/commands/31.result.json')
messages=[json.loads(s) for s in old_journal['stdout'].splitlines() if s.strip()]
focus=[{'MESSAGE':r.get('MESSAGE'),'_SYSTEMD_UNIT':r.get('_SYSTEMD_UNIT'),'__MONOTONIC_TIMESTAMP':r.get('__MONOTONIC_TIMESTAMP')}
       for r in messages if any(k in str(r.get('MESSAGE','')) for k in ['Permission denied','visits.bin.intent','C09_NOT_READY','BUDGET_HALTED'])]
dump(E/'HISTORICAL_RAW_REVIEW.json',{
 'schema':'RI-batch05-raw-review/1','batch05_zip_sha256':sha(B05/'BATCH05_EVIDENCE.zip'),
 'batch05_zip_entries':old_entries,'batch05_zip_stream_errors':[],
 'native_zip_sha256':sha(N/'out/EVIDENCE.zip'),'native_zip_entries':346,'native_zip_stream_errors':[],
 'counter':37293,'journal_prepared':303,'journal_committed':303,'original_intent':load(N/'out/visits.bin.intent.json'),
 'original_permissions':load(B05/'evidence/commands/26.result.json')['stdout'],
 'root_launcher_stderr':old_command['stderr'],'outer_exit':old_command['exit_code'],
 'journal_record_count':len(messages),'matching_error_messages':focus,
 'live_handoff_files':[],'handoff_verdict':'NOT_EXERCISED','new_runtime_or_tests':0})
dump(E/'HISTORY_PROTECTION_CHECK.json',{'schema':'RI-history/1','checks':history,'modified_history_files':0,
 'batch05_R':37293,'batch04_R':37021,'batch02_R':32191,'mispath_actions':'read/hash only',
 'prior_policy_rejection':'blocked by policy retained','historical_package_navigation':'Sealed-time snapshots remain in each original archive'})

native_commands=[load(p) for p in sorted((E/'commands').glob('*.result.json'))]
assert len(native_commands)==13 and all(c['exit_code']==0 for c in native_commands)
deployed=json.loads(native_commands[11]['stdout']);final_native=json.loads(native_commands[12]['stdout'])
assert final_native['files_checked']==44 and final_native['hash_errors']==[] and not final_native['batch06_exists']
assert {r['relative']:r['sha256'] for r in deployed['files']}=={r['relative']:r['sha256'] for r in frozen['files']}
compile_final=json.loads(native_commands[10]['stdout']);assert len(compile_final['modules'])==17
environment=[json.loads(s) for s in native_commands[4]['stdout'].splitlines()]
dump(E/'STATIC_NATIVE_SUMMARY.json',{'schema':'RI-native-static-summary/1','commands':13,'all_exit_zero':True,
 'final_syntax_command':11,'final_syntax_modules':17,'final_static_copy_command':12,'final_hash_command':13,
 'final_Linux_files':44,'runtime_critical_files_checked':32,'runtime_tree_files_checked':1224,
 'current_read_environment':environment,'batch06_exists':False,'T0':None,'counter':None,
 'dynamic_tests_executed':0,'target_role_bodies_executed':0,'systemd_mutations':0,
 'new_UID_or_GID':0,'dependencies_installed':0,'state':'STATIC_ONLY'})

matrix=[
['batch06根 / inputs','/var/lib/dcl-r6/batch06[/inputs]','Root','Root','Root；989遍历/读','Root父目录','0:989/0750','目录创建与未来发布目录屏障'],
['out','…/out','Root准备','999；Root TCB','999/Root','999拥有其内容；Root可管理','999:989/0700','同一ext4设备'],
['共享counter','out/visits.bin','Root初始化后chown','999及Root审查；同一flock','999/Root','out的999/Root','999:989/0600','原24B counter与fsync算法保持'],
['共享预算intent','out/visits.bin.intent.json','Root初始化；双方发布','999及Root审查','999/Root','out的999/Root','999:989/0600','PREPARED/COMMITTED原协议；Root发布前设置元数据'],
['共享journal','out/visits.bin.journal.jsonl','首个payload事务','999及Root append','999/Root','out的999/Root','999:989/0600','原append与fsync保持'],
['C09 ready引用','out/C09.ready.json','999','冻结C09 payload','Root核ticket/身份/账；999','out的999/Root','999:989/0600','原marker；仅作为待核引用'],
['Root私有目录','inputs/root_private','Root准备','Root','Root','Root','0:0/0700','无POSIX ACL；独立暂存与原始审查记录'],
['Root暂存对象','inputs/root_private/.publish.<pid>.<nonce>','Root','Root持有fd','Root；目录阻断payload','Root','按目标fchown/fchmod；外层0700','内容+元数据fsync→rename→双目录fsync→stat'],
['Root私有日志/普通退出记录','inputs/root_private/c09_events.jsonl；waitpid_*.json；ipc_case_*.json','Root','Root','Root','Root','0:0/0600','日志fsync；记录Root受控发布；原始waitpid保留'],
['Payload可读Root资格','inputs/C09H_QUALIFICATION.json；ROOT_IPC_QUALIFICATION.json；RANGE/GATE/RESOURCE等','Root','Root','Root/989','Root输入目录','0:989/0640','Root完整审查后发布；payload仅读保护收据'],
['持久commit / ACK证据','inputs/c09_commit.json；c09_handoff.json；c09_exit_witness.json','Root sender/receiver/parent各职责','Root且生命周期锁','Root/989用于FORMAL/恢复核验','Root输入目录','0:989/0640','原持久ACK、waitpid、revision与摘要合同保持'],
['Root控制socket / 生命周期锁','inputs/c09_control.sock；c09_lifecycle.lock','Root','Root认证调用方','Root','Root输入目录','0:0/0600','SO_PEERCRED＋稳定身份；锁串行闭合/分类']]
report('ROOT_INTENT_FILE_LIFECYCLE.md','共享 intent 的真实权限生命周期',f'''
RI-1：PASS_STATIC，依据batch05冻结源码与真实元数据/日志。原预算intent与C09持久交接对象分别追踪；本次真实故障发生在预算intent。

1. 原guard.py:470–481由Root初始化counter，写初始COMMITTED intent，再chown为999:989；初始mode0600。out目录由冻结准备命令设为999:989/0700，输入/批根为Root:989/0750。
2. payload每次访问在`_counter_lock`取得线程锁与counter flock后读取intent（原509行）。Root需要独立重算并把审查访问纳入同一全局预算，因此C09H审查调用34次`reserve_counter`；后续S与17门审查走同一预算入口。Root具备读取原账权限，也确实需要按照原计费合同推进共享账。
3. 原`atomic`在out创建0600临时文件，`root_record=False`分支保留当前writer身份；Root euid0调用后临时文件为0:0。写入/文件fsync后`os.replace`将新inode置于共享intent名字，原payload owner随旧inode离开路径。原`atomic`此分支没有发布前fchown/fchmod。
4. batch05 Root审查最后COMMITTED intent时间3898.266588342，before37292/after47293；下一C09 uid999读取在3898.529937533前触发EACCES，STOP_REQUEST明确指向该路径。命令26确认intent0:0/0600、counter/journal999:989/0600。
5. STOP_REQUEST=T0+20.861903589，CLOSED=+20.909951317，payload组空=+20.927591657；Root最终清理=+300.043546214。303组事务内容配对完整，入口读取发生于新事务之前。

根因轴：文件路径为冻结正确路径；内容/额度配对健康；Root替换导致owner改变，0600使uid999缺少读取权限。目录本身允许uid999遍历/读写；原子rename保留临时inode的metadata。mode创建受umask影响，常规umask只会收紧所请求位；实际观察0600。历史临时文件本体/umask值和已被替换的旧inode未单独捕获，源码链与最终stat支持上述解释。旧代码的resolve/O_NOFOLLOW只覆盖部分步骤，历史源码缺少完整目录fd抗替换；当前记录没有实际符号链接攻击证据。

{tab(['对象','实际/未来路径','创建者','写入者','读取者','删除/替换权','owner:group/mode','持久化合同'],matrix)}

删除能力由父目录w+x控制；out中的uid999可替换自己的共享账对象。Root私有与保护收据位于Root拥有的输入层。当前原文件/错误日志/完整ZIP逐流核对见[原始审查](evidence/HISTORICAL_RAW_REVIEW.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、{link(B05/'BATCH05_COUNTEREXAMPLES.md','batch05首次失败')}。
''')

report('ROOT_PAYLOAD_PERMISSION_CONTRACT.md','Root/Payload 最小权限与职责合同',f'''
采用固定路径的三类发布策略，复用通用私有暂存及目录fd方法。对最强通用基线预测差距0；[研究分离门](SEPARATION_AND_SCOPE.md)保持关闭。

A类共享对象：预算intent由999与可信Root审查共同推进，目标999:989/0600，双方仍使用原counter flock。C09 ready由payload产生，Root按ticket/身份/原账核验；C09 sender为Root scheduler，payload无需获得控制socket写权限。

B类Root私有对象：内部事件、普通waitpid记录及IPC原始审查置于root_private/0700，文件0:0/0600。Root原始记录只由独立检查器读取；合成fixture无法写入真实counter/CLOSED等路径。

C类Root保护且payload必读的收据：C09状态、commit/退出见证、C09H/IPC/RANGE/GATE/RESOURCE资格为0:989/0640，输入目录0:989/0750。payload可核验原资格与摘要，写入/删除由Root输入目录边界阻断。活receiver的RPC确认仍是持久commit之外的必要条件。

实现位于{point('root_ipc.py','policy')}、{point('root_ipc.py','directories')}及{point('root_ipc.py','publish')}。Root目标采用精确名单；仅IPC合成固定文件名放行故障钩子；真实全局账故障注入继续拒绝。每级目录逐项O_DIRECTORY/O_NOFOLLOW打开，校验owner/mode、设备及无POSIX ACL。发布前fd上fchown→fchmod→metadata/ACL校验，避免umask或继承ACL改变预期授权。

审查结果：payload缺少Root私有目录访问权及保护收据写权；socket仍0:0/0600，SO_PEERCRED、稳定PID/boot、窗口与锁摘要保持；Root发布路径无需接收任意用户指定路径；迟到ACK受CLOSED吸收及fresh-read约束。原预算审查对payload可写内容的信任继续依赖冻结payload/原健康账验证，任意恶意同UID程序和Root/内核失陷超出现有边界。

更强威胁实例：恶意同UID写者可在原预算读取前替换intent路径，旧`read`仍是普通路径读取；同时也可篡改其拥有的counter。本轮Root发布不会跟随该链接写到外部目标，原预算读取核心保持。对任意恶意同UID的完整读路径/账真实性保证仍为UNRESOLVED；扩大该模型需要单独批准预算I/O重构。本轮没有作出这一扩展保证。

RI-2=CONDITIONAL_PASS：源码权限边界已实现；实际DAC、ACL拒绝、原子替换失败行为和跨身份回归全部UNRUN。未来batch06预检及内置目录检查拒绝未审查ACL/目录元数据变化。当前只读审核的源目录和/var/lib/dcl-r6前缀无POSIX ACL，运行目录尚未创建。
''')

report('ROOT_SHARED_FILE_ATOMICITY.md','Root 共享文件原子发布与失败语义',f'''
{point('root_ipc.py','publish')}采取以下顺序：固定相对目标策略 → 逐级固定目录fd/metadata/ACL → 同设备检查 → Root私有暂存O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC → fd上fchown/fchmod/验证 → 完整write → 文件fsync → dirfd相对replace → 目标目录fsync → 私有暂存目录fsync → 目标lstat与暂存fd的device/inode、owner/group/mode/nlink复核 → 返回。Root输入层和out均被Root父目录固定；目标名字在rename中按目录fd解释。

成功replace的命名原子性、相对目录描述符、不同文件系统可能失败的语义来自[Python3.12 os.replace](https://docs.python.org/3.12/library/os.html#os.replace)与[Linux rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html)。目录项的持久化需要单独目录fsync，依据[fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html)。代码同时同步两个参与rename的目录；完整持久性仍依赖文件系统、存储和可信内核条件。

[open(2)](https://man7.org/linux/man-pages/man2/open.2.html)说明O_NOFOLLOW作用于末分量，因此源码逐级打开目录；新建mode受umask/默认ACL影响，发布前显式设置并拒绝ACL。按fd变更owner遵守[fchown(2)](https://man7.org/linux/man-pages/man2/chown.2.html)语义。Python网页为当前3.12分支文档；实际3.12.3的replace签名/dir_fd接口另由静态命令1/5读取。

{tab(['失败阶段','可见状态','后续处理'],[
['创建/元数据/写入/文件fsync失败','原目标保留；私有暂存可能留下','异常上抛；共享预算失败触发原HALTED；保留暂存证据'],
['rename失败','通常保留原目标；以原始错误为准','失败关闭；无执行信用交付'],
['rename成功后目录fsync/stat失败','新目标可能已可见；持久性/身份未完成确认','返回失败；沿原预算保守占用并停止；禁止退款/回滚伪装'],
['目录或目标symlink/hardlink异常','策略/类型/目录检查拒绝；dirfd固定发布目标','不把resolve当作权限依据；动态对抗调度仍待验证'],
['重复发布','由现有counter/lifecycle锁串行；字节可相同，inode可变化','幂等信用由原EXACT-RANGE/1提供，publisher自身不制造新信用']])}

当前/var/lib/dcl-r6位于ext4 `/dev/sdd`，挂载含data=ordered，见[静态环境](evidence/STATIC_NATIVE_SUMMARY.json)。本轮执行原子发布/故障注入0；上述顺序是源码事实，掉电、介质回滚、恶意Root及严格实时行为保留条件。跨目录Root发布比旧路径增加一次目录fsync，开销必须在同一300秒校准中实测。
''')

report('ROOT_STOP_WAIT_ANALYSIS.md','Root 等待缺口与取消处理审查',f'''
batch05缺口定位于旧guard.py:834–835：ready不存在时只看时间，忽略已发布CLOSED/STOP_REQUEST。payload约21秒已退出，scheduler直到共享T0+300才以C09_NOT_READY结束。当前真实证据保持原结论。

{tab(['等待/处理点','修复后行为','期限/清理范围'],[
['C09 ready','每轮checkpoint fresh读标记及状态；检查payload与receiver活性；ready可见后再检查','50ms轮询参数；原min(T0+300,stop_at)期限保持'],
['一般case PID/退出等待','每轮checkpoint；原C07/08异常退出判据保持','原PID/单case期限保持'],
['Root父子握手','wait_fd有限select与取消复查','原5秒握手期限'],
['socket connect/send/recv','非阻塞/有限阻塞片段，每轮取消检查；保留原交接观察期','client至原12秒上限；receiver读/发送各原有0.5秒层级内'],
['父waitpid','每轮fresh标记；首次停止后有限30秒协作grace，仍受原deadline；到期pidfd kill','异常路径kill后最多5秒非阻塞回收；无法确认回收则明确失败'],
['RPC ACK并发闭合','lifecycle锁内重新检查；sender ACK后与exit23前再检查','已CLOSED不再准入；在途I/O按失败或清理处理'],
['finally seal','scheduler将封存交给父；父先回收子、保存普通raw_wait_status，再等待外部停止器退出封存','原20秒seal等待/manager清理条件；不形成新执行窗']])}

源码：{point('root_ipc.py','checkpoint')}、{point('root_ipc.py','wait_ready')}、{point('root_ipc.py','receive')}、{point('root_ipc.py','connect')}、{point('root_ipc.py','send_packet')}、{point('guard.py','launcher')}。状态优先级与工程延迟参数见[状态机](ROOT_STOP_STATE_MACHINE.md)。

终止通知采用“首个CLOSED记录＋幂等重复清理”：CLOSED原件保留，后续stop_event/stop_result记录复核。多可信管理进程可以重复请求systemctl stop；该行为不产生重复交接成功分类。停止后只允许必要的回收、持久化和封存。ticket/局部PASS文件本身无法授予运行资格，controller、恢复与FORMAL仍fresh核对停止状态。

RI-3=CONDITIONAL_PASS：缺失的取消读取和有限回收路径已实现。50ms、30秒和5秒是配置参数；实际调度、fsync、systemd阻塞及停止总延迟仍UNMEASURED，尚未证明新硬界。
''')

report('ROOT_STOP_STATE_MACHINE.md','停止状态优先级与交接并发规则',f'''
状态优先级：CLOSED吸收 → STOP_REQUEST/必要监督丢失/失败 → boot或绝对期限失效 → 当前正常准备/ACK/验证。终止判据优先于ready、exit23及迟到ACK。每次wait不长期复用之前的成功状态。

{tab(['状态','允许动作','转移与线性化'],[
['RUNNING/CALIBRATING','原case、C09H及RootIPC前置检查','每轮checkpoint核boot/stop_at/deadline/终止标记'],
['STOP_REQUEST_SEEN','停止新资格，进入stop_tree','请求是取消事实；Root在生命周期锁下发布CLOSED'],
['CLOSED','组停止、子回收、原始证据写入与seal','吸收态；后续收据/ACK不恢复'],
['HANDOFF_PREPARING/READY/COMMITTED','原身份/账/窗口核对及持久ACK','receiver commit屏障后才答复；答复前同锁重新检查停止'],
['EXIT_OBSERVED/PENDING','父waitpid见证、fresh-read、期限内等待','缺ACK/receiver或超时失败关闭'],
['HANDOFF_VERIFIED/RESUMED','一次受控恢复、原窗口继续','原classification_count=1、摘要/receiver/once bit全检；CLOSED先拒绝'],
['CLEANUP/SEALED','重复停止确认、普通退出记录、父最终seal','无需重置账或T0；无法回收明确失败']])}

STOP_REQUEST可由payload异步发布，其到达与已经开始的I/O可能重叠。Root每次观察后阻断后续资格；CLOSED发布和handoff状态变更由同一flock串行。若ACK在锁内检查后才遇到请求，sender/parent/receiver后续fresh检查仍会拒绝恢复；CLOSED后ACK不能生成合法新资格。当前不声称中断已进入内核的fsync/systemctl调用。

父协调器保留直接waitpid及稳定身份；普通退出记录写入root_private，成功交接见证仍另由原handoff合同生成。新的父最终seal顺序保证普通退出记录在本批最终封存之前产生。新顺序与正常、异常、强制终止下的行为均待动态核验。

[安全性质](ROOT_IPC_SAFETY_PROPERTIES.md)、[专项夹具](ROOT_IPC_REGRESSION_PLAN.md)、[原交接状态机](../DCL-R6-C09Fix/C09_HANDOFF_STATE_MACHINE.md)。
''')

properties=[
['IPC-1 AuthorizedRead','shared intent999:989/0600；payload只读收据0:989/0640',point('root_ipc.py','policy'),'P.read/replace/receipt_read/unauthorized；M.root600/permissions'],
['IPC-2 RootIntegrity','输入目录Root拥有；Root私有0700/0600；保护收据group只读',point('root_ipc.py','directories'),'P.private_write/private_read/receipt_write；真实C09来源核验'],
['IPC-3 AtomicPublication','发布前metadata/ACL、完整write、文件和双目录屏障、发布后stat',point('root_ipc.py','publish'),'P.fault_*；P.umask/repeat；故障后无grant'],
['IPC-4 NoPathSubstitution','Root发布固定名单、逐级NOFOLLOW/dirfd、目标type/nlink/identity',point('root_ipc.py','directories'),'P.outside/symlink/hardlink；未来调度攻击待验证'],
['IPC-5 IdentityBinding','Root共享收据和handoff窗口绑定batch/boot/源/执行锁/身份',point('c09_handoff.py','check_base'),'P.bad_batch/boot/lock/digest；M.batch；真实C09'],
['IPC-6 NoFalseHandoff','原持久ACK＋活receiver＋waitpid23＋fresh-read判据保持',point('c09_handoff.py','sender_prepare'),'M.exit23；C09H34；真实C09'],
['IPC-7 StopDominance','每轮checkpoint，ready之后/ACK之前复查；缺监督立即拒绝',point('root_ipc.py','checkpoint'),'T.stop_before/after_ready/closed_wait/fd_cancel/socket_cancel；M.stop/closed'],
['IPC-8 NoReactivation','CLOSED吸收；锁内发布与恢复复查；迟到ACK不重开',point('c09_handoff.py','resume_admission'),'T.late_ack/ack_stop；M.reactivate/closed；真实恢复'],
['IPC-9 SingleClassification','原revision/id/classification_count=0→1与直接父见证',point('c09_handoff.py','coordinator_witness'),'M.duplicate；C09H及真实一次恢复'],
['IPC-10 BudgetPreservation','24预算/资格函数AST与range_core文件保持；Root新访问原账记入',point('guard.py','_reserve'),'原C02/C05/C11、S34/门17；IPC前后原账比对；无退款/新窗']]
report('ROOT_IPC_SAFETY_PROPERTIES.md','IPC-1 至 IPC-10 静态性质与验证责任',f'''
以下为源码检查点和未来证据映射，动态结果统一UNRUN。权限和有界等待属于通用基础设施修复，原创性严格分离实例保持0。

{tab(['性质','检查谓词','最终源码检查点','未来证据'],properties)}

共同前提：冻结payload/Root代码，可信内核/systemd/Root，原CPY312-UBU24/1和AS4-PAYLOAD/1条件；目录无未审查ACL且同一ext4设备；文件系统和调度语义支持实际屏障与终止。任意恶意同UID写者的完整账真实性、Root失陷、介质回滚、宿主断电及严格实时性未获得扩展认证。

Root发布路径的抗替换与旧预算读路径的额外强威胁分别登记，见[权限合同](ROOT_PAYLOAD_PERMISSION_CONTRACT.md)。本轮通过静态检查的谓词仍需专项56、C09H34、真实C09和完整C/S/门链产生实际接受及拒绝见证。
''')

report('ROOT_IPC_FIX_IMPLEMENTATION.md','最小依赖修复与完整源码差异',f'''
最终RootIPC-static-1/r4位于`D:\\毕业设计\\DCL-R6-isolated-verification\\ri01`和`/var/lib/dcl-r6/ri01`。修改原guard.py、c09_handoff.py两份，新增root_ipc.py、root_ipc_regression.py、root_ipc_oracle.py三份；其余12份程序原字节保持。

guard：Root atomic分支委托新发布器；payload atomic分支保持；Root等待加入checkpoint、C09双进程活性检查、父有限回收；C09H独立重算后执行IPC56，并在真实C09/恢复/FORMAL前核Root IPC资格；普通waitpid记录与最终seal移至父协调器。原预算数值/事务算法、探针和业务导入门保留。

handoff：Root内部事件日志移入私有目录；RPC连接/发送/接收可取消且保留原期限；ACK发送前生命周期锁内fresh检查；原classify、window/counter、resume及completed_handoff函数AST保持。c09_oracle/c09_regression原字节保持。

root_ipc：固定策略、私有暂存、目录fd与ACL/type/metadata校验、有界wait/checkpoint及资格重核。root_ipc_regression：Root受限fixture驱动、一次至多一个独立降权探针子进程、原账计费、逐job即时独立oracle，首次意外失败即停止。root_ipc_oracle：独立原始文件/元数据/实际probe/事件真值检查；导入仅标准库。

新增子探针位于外部Root测试TCB，顺序执行、最多1个，saved/real/effective UID/GID一致、补充组受限、CapEff=0、AS≤1GiB、2秒alarm、父3秒等待/3秒清理。该新增运行范围需要下一动态授权明确接受；当前fork执行0，实际系统UID/GID配置变更0。

[原源码37项](evidence/original)、[完整source diff](evidence/SOURCE_COMPLETE.diff)、[完整input diff](evidence/INPUT_COMPLETE.diff)、[变更索引](evidence/SOURCE_DIFF_INDEX.json)、[24函数及原文件不变检查](evidence/AST_AND_INVARIANT_CHECK.json)。输入仅必要路径/版本/哈希/未来批名与新合同发生变化；S34的N/事件/断言、C09H34、门17值保持。

r1/r2/r3候选各44项及当时检查保存在evidence/freeze_candidate_r1、freeze_candidate_r2、freeze_candidate_r3。r4保留原12秒交接期内可取消I/O并加入ACL与探针权限核查；中间候选未获动态执行资格。
''')

regrows=[[j['case_id'],j['kind'],j['scenario'],j['variant'],','.join(j['allowed_violation_set']) or '∅','UNRUN'] for j in cfg['jobs']]
report('ROOT_IPC_REGRESSION_PLAN.md','新增56项权限与停止夹具冻结计划',f'''
冻结56项：48个safe（含8个变异对照）、8个mutant；实际执行0。原C09H34、S34、负向门17均作为独立原测试保留。新增Root套件只在未来授权Root scheduler内、C09H通过且真实C09之前调用，无新增systemd单位或standalone入口。

文件层fixture实际调用新publisher、读取真实lstat及一次降权UID999/65534的open结果和原始waitpid；历史root600、replace与合成路径/故障仅影响`ipc_fixture_*`。私有/保护收据分别测试Root私有拒绝及group-read/禁止写入。文件fsync故障属于受限EIO注入，物理介质失败与掉电保持额外责任。

停止层在Root私有合成命名空间建立真实ready/STOP/CLOSED文件，调用生产wait_ready/wait_fd/receive检查。payload/receiver失效为liveness观察回调的投影；ACK/退出/重复分类使用冻结合成subject。真正socket端到端确认、实际receiver进程失效、父waitpid/pidfd交错仍由真实C09及原C07–C12链取得；本套件不会把这些投影称为真实交接成功。

{tab(['case','层','scenario','variant','允许违规集','实际'],regrows)}

每job保存绑定、输入摘要、Root稳定身份、时钟、全局访问前后值，以及metadata/probe errno/真实子退出或合成事件原件。独立oracle拒绝错误UID/GID/saved身份/CapEff、原件缺失/非Root写入/错mode/超限/错误绑定、未触发历史故障和未命中或额外未声明违规。逐job即时审查失败即停止；整套完成后再独立重算并发布Root保护资格。

计费为entry1＋每job保守预付8＋Root整套审查1：1+56×9=505（未用占用保留），硬限512。原C09H完成路径上界2245，合计2750≤5000；二者共用原C09H ticket的5000上限。完整校准硬上界62034≤100000保持，全部共享T0+300软窗。新增进程、磁盘屏障及实际耗时待测；任何窗口不足即停止，现有预算/期限保持。

[冻结合同](evidence/root_ipc_contract.json)、{point('root_ipc_regression.py','run_suite')}、{point('root_ipc_oracle.py','check_job')}、[batch06申请](BATCH06_EXECUTION_REQUEST.md)。
''')

impact=[
['C07 Controller崩溃','探针/原退出23判据保持；Root等待先查全批终止状态','本版本UNRUN'],
['C08 Watchdog崩溃','monitor_failure/拒绝grant的原谓词保持；局部watchdog故障不等同全批STOP','本版本UNRUN'],
['真实C09','前置新增IPC资格；保留ACK/receiver/waitpid/fresh-read/revision；I/O可取消','本版本NOT_EXERCISED'],
['C09H34','原subject/oracle字节保持；输入只改batch命名；合并计费限5000','本版本UNRUN'],
['C10子进程封闭','原探针/AS/能力/网络/cgroup规则保持','UNRUN'],
['C11持久化故障','原local payload预算fault钩子及事务函数保持；Root新故障仅fixture','UNRUN'],
['C12 CLOSED/恢复拒绝','原state谓词AST保持；真实恢复加IPC Root资格','UNRUN'],
['S7持久化/S8身份关闭','原range_core、fixtures、evidence字节保持，S34 N/断言值保持','UNRUN'],
['门17','原17输入及verify_sealed/negative/exercise函数AST保持；Root共享intent修复覆盖其记账','UNRUN']]
report('STATIC_VERIFICATION_RESULTS.md','最终静态检查与回归影响',f'''
最终r4：17份源码均由实际CPython3.12.3 `py_compile`通过（命令11），CHECKED_HASH缓存17份；目标模块正文执行0。命令12复制最终44项到独立Linux静态目录；命令13对全部44项hash与目录ACL/metadata核对通过。源码/缓存/输入哈希均绑定最终r4；先前候选编译记录保留各自时点。

12份原源码字节保持：{', '.join(checks['unchanged_source_files'])}。guard中24个预算/资格函数AST保持，涵盖init_counter、_counter_lock、_reserve、Budget、Root S/gate/C09H审查及FORMAL导入门；实际共享发布helper按当前专项范围修复。预算核心文件和事务算法保持，Root写入元数据与停止监督属于本轮授权的修改位置。

原C09H34、S34及门17输入语义核对通过，只有batch05→batch06命名绑定差异；业务计划、child合同、runtime_critical、runtime_tree四份输入原字节保持。源diff与输入diff全部封存。

{tab(['范围','静态影响审查','动态状态'],impact)}

当前runtime只读核验：Python3.12.3/e50d…150f、kernel6.18.33.2、UID999/GID989和nobody65534；32关键文件、1224运行时树hash全部相符。ext4和源目录无POSIX ACL；未来运行目录未创建，其owner/mode/ACL仍需启动前核验。systemd资源参数模板仅批次命名变化，实际单位和全局配置修改0。

本轮13条native命令均exit0：环境读2、语法编译5、静态复制4、最终只读核对2。当前最晚语法对应命令11，复制12，hash13。字段UNRUN与PASS_STATIC保持独立；没有任何本批机器行为PASS、RESOURCE_GATE_PASS或PASS_BOUNDED。

[静态结构检查](evidence/AST_AND_INVARIANT_CHECK.json)、[native摘要](evidence/STATIC_NATIVE_SUMMARY.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[命令目录](evidence/commands)。
''')

hashrows=[[name,sha(W/'inputs'/name)] for name in ['static_manifest.json','execution_lock.json','root_ipc_contract.json','c09_contract.json','safety_contract.json']]
source_rows=[[r['relative'],r['sha256']] for r in frozen['files']]
report('SOURCE_AND_INPUT_LOCK.md','RootIPC-static-1/r4 最终源码、输入与命令锁',f'''
唯一host静态目录`D:\\毕业设计\\DCL-R6-isolated-verification\\ri01`；唯一Linux静态目录`/var/lib/dcl-r6/ri01`；拟申请运行根`/var/lib/dcl-r6/batch06`及host同名导出路径。当前batch06运行实体、账、T0、单位均未创建。

{tab(['核心锁','SHA-256'],hashrows)}

17源码＋17缓存＋10输入=44项；Linux复制与最终逐项hash/owner/mode核对通过。全量列表如下，权威机器锁见[STATIC_WORKSPACE_LOCK](evidence/STATIC_WORKSPACE_LOCK.json)。静态目录源/输入/缓存0:0/0644、目录0:0/0755；运行目录权限由未来6条准备命令另行建立。

{tab(['相对路径','SHA-256'],source_rows)}

精确argv、16组payload命令、34个原S worker模板、Root internal IPC56调用与顺序helper、原停止及一次恢复命令、17-unit journal命令均在[execution_lock](evidence/execution_lock.json)。新增Root IPC无独立unit；原AS4/CPY312、总额度/窗口/TasksMax不变。当前授权仅允许静态工作，execution_lock保留DYNAMIC_UNAUTHORIZED。

源码进一步改变需要新冻结修订及新hash；r1/r2候选仅作过程记录，当前动态申请绑定r4。runtime树/关键工具摘要已实际只读复核，未来启动仍需全量fresh预检与当前boot；当前boot读取记录不替代下一运行boot绑定。
''')

template={
 'schema':'BATCH06_AUTHORIZATION_TEMPLATE_STATIC_ONLY','batch_id':'batch06','scope':'CALIBRATE_S1S9_THEN_F1_F4',
 'profile':'CPY312-UBU24/1','limits':[1000000,1800,1740,1073741824,4],
 'source_version':'RootIPC-static-1','freeze_revision':'r4',
 'static_manifest_sha256':sha(W/'inputs/static_manifest.json'),'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),
 'root_ipc_contract_sha256':sha(W/'inputs/root_ipc_contract.json'),'root_ipc_profile':'ROOT-IPC/1',
 'c09_contract_sha256':sha(W/'inputs/c09_contract.json'),'safety_contract_sha256':sha(W/'inputs/safety_contract.json'),
 'handoff_profile':'C09-DURABLE-RPC/1','test_mode':'RANGE_ONLY/1',
 'special_mapping_scope':'ORDINARY_AS_ACCOUNTED;KERNEL_SPECIALS_SEPARATELY_REVIEWED',
 'authorization_text_sha256':None,'Root_coordinator_explicitly_approved':None,'RootIPC_helpers_explicitly_approved':None,
 'authorization_status':'NOT_GRANTED; template only'}
dump(E/'BATCH06_AUTHORIZATION_TEMPLATE.json',template)
prep='\n'.join(' '.join(x) for x in lock['preparation_commands'])
report('BATCH06_EXECUTION_REQUEST.md','batch06 独立动态执行申请（当前尚未授权）',f'''
申请仅绑定RootIPC-static-1/r4及下列实际hash。batch05持续CLOSED，R37,293与原窗口/错误证据保持；batch06未创建。当前RootIPC-Fix专项授权覆盖静态修复，本文件为下一动态阶段的可审阅申请材料。

{tab(['锁','SHA-256'],hashrows)}

请求接受：原Root父协调器/scheduler及外部停止器TCB；新增56项Root权限/停止回归；最多1个顺序降权探针子进程（当前既有UID999/GID989与nobody65534/GID65534，AS≤1GiB、无新账户）；Root私有目录及受控发布；原C00–C12、C09H34、S34、门17和全部资源门后同批自动F1→F4。外部Root管理/测试开销另列，payload条件性4GiB与4 tasks范围保持。

未来准备命令（当前执行0）：

```text
{prep}
```

随后安装新授权原文为`inputs/BATCH06_AUTHORIZATION_TEXT.txt`及Root:989/0640的有效执行回执；[模板](evidence/BATCH06_AUTHORIZATION_TEMPLATE.json)尚缺明确批准与授权原文hash，无法直接启动。预检核Python3.12.3、32关键工具/1224树、当前boot、全部44文件、UID/GID/补充组、目录metadata/ACL/同设备、当前systemd/cgroup及冲突/残留。发现漂移停止，不修改锁后沿用许可。

唯一首次入口：

```text
{' '.join(lock['launch_command'])}
```

仅在真实C09当前有效Root成功交接后，同窗一次恢复：

```text
{' '.join(lock['expected_C09_resume_command'])}
```

全冻结argv与17-unit journal命令见[执行锁](evidence/execution_lock.json)。建议启动模式为完整条件链，避免C12之后重复申请同范围许可：预检→C00–C08→C09H34/Root重算→IPC56逐项及完整独立审查→真实C09持久ACK/waitpid/fresh-read/唯一分类→原窗一次恢复→C10–C12→S34/Root原始重算→17负向门→RESOURCE_GATE_PASS→F1→F4→关闭/父最终封存。缺少任何IPC/C09/C/S/门证据均阻断FORMAL。

资源保持总访问1,000,000、总窗1,800秒、T0+1,740提前停止、校准300秒/100,000、每payload进程AS1GiB、父slice4tasks。IPC完成路径505、硬限512，和原C09H共同完成上界2750≤5000；完整校准硬访问上界62034保持。新增目录屏障/进程与Root普通退出记录的实际耗时未测量；窗口不足即首次失败停止，当前没有提出扩窗。

下一运行首个关键失败立即停止后续、保存原件、关闭/清空并封存；重试、退款、重置账/deadline、放宽阈值、恢复CLOSED和自动下一批均禁止。成功与预期故障须由独立raw oracle接受；仅exit23或PASS字段无法通过。

本申请未覆盖F2/F3、Casdoor、T1–T4、真实账户/凭据、无关单位/系统权限变化、依赖安装、误副本处置或外发。D1/强G原条件保持，严格分离0、IMPLEMENTATION_GATE=CLOSED。
''')

report('FINAL_DECISION.md','RootIPC-Fix 最终静态裁决',f'''
**RootIPC-static-1/r4 已完成有限静态修复与冻结；batch06动态执行仍待独立授权。** 本轮未运行C00–C12、C09H、新56、S34、门17或F1/F4；batch06无运行目录/T0/账/单位。

{tab(['验收门','裁决','依据及剩余责任'],[
['RI-1 权限根因','PASS_STATIC','batch05源码、真实stat/EACCES、303事务、双流与ZIP互证；原结论保持'],
['RI-2 权限修复','CONDITIONAL_PASS','固定Root策略、私有暂存、发布前owner/mode、目录fd/ACL/双目录屏障已实现；真实DAC/失败路径及调度待测'],
['RI-3 停止修复','CONDITIONAL_PASS','ready/RPC/父waitpid加入fresh取消，有限回收，ACK/闭合优先级保持；实际总延迟与清理收敛待测'],
['RI-4 回归版本','PASS_STATIC','56项/8变异、原测试语义不变、17最终语法、44项host/Linuxhash、完整diff/历史保护与batch06申请已冻结']])}

原guard.py、c09_handoff.py两份修改，新增3份关联模块；12份程序字节保持，guard中24个预算/资格函数AST保持。原五业务、D2-DP/TRACE-REF、range核心、探针、S34与门17判据保持；输入仅未来命名与锁适配。最终44文件包括17源码、17实际CPython3.12.3缓存、10输入。

56项夹具当前动态0；计费完成路径505，和C09H合计2750≤共同5000硬限，校准硬上界62034≤100000保持。Root额外顺序探针TCB最多1个，下一授权明确接受；实际AS、内存、停止响应及300秒整套可完成性尚未测量。

batch05继续RESOURCE_GATE_FAILED：C00–C08九项PASS、C09H34接受，真实交接NOT_EXERCISED，R37,293、303配对事务、20.928秒payload清空与300.044秒Root结束保留。其531-entry行政包和346-entry原生包逐流核对无差异；历史505研究文件、原source37、各旧工作区/原件和误副本47只读/hash通过，blocked by policy保留。

本轮native13条只含环境读取、语法编译、独立静态目录复制及hash/ACL核对，全部exit0；目标角色正文0、动态故障注入0、systemd/全局资源/实际UID配置修改0、依赖安装0。最终只读检查确认batch06不存在。r1/r2/r3中间静态候选及旧hash保留。

更强的任意恶意同UID预算读路径/账真实性保证仍为UNRESOLVED，当前保持冻结payload与可信Root/内核/存储/调度假设；未修改预算读取核心或扩大安全宣称。新权限/停止行为、真实ACK/waitpid及最终父seal仍需匹配r4的动态证据。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED授予0。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离实例0和IMPLEMENTATION_GATE=CLOSED保持。下一步材料见[batch06申请](BATCH06_EXECUTION_REQUEST.md)。

[权限合同](ROOT_PAYLOAD_PERMISSION_CONTRACT.md)、[停止分析](ROOT_STOP_WAIT_ANALYSIS.md)、[56项计划](ROOT_IPC_REGRESSION_PLAN.md)、[静态检查](STATIC_VERIFICATION_RESULTS.md)、[最终锁](SOURCE_AND_INPUT_LOCK.md)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
''')

required=['ROOT_INTENT_FILE_LIFECYCLE.md','ROOT_PAYLOAD_PERMISSION_CONTRACT.md','ROOT_SHARED_FILE_ATOMICITY.md',
 'ROOT_STOP_WAIT_ANALYSIS.md','ROOT_STOP_STATE_MACHINE.md','ROOT_IPC_SAFETY_PROPERTIES.md',
 'ROOT_IPC_FIX_IMPLEMENTATION.md','ROOT_IPC_REGRESSION_PLAN.md','STATIC_VERIFICATION_RESULTS.md',
 'SOURCE_AND_INPUT_LOCK.md','BATCH06_EXECUTION_REQUEST.md','FINAL_DECISION.md']
report('EVIDENCE_INDEX.md','RootIPC-Fix 研究证据索引',f'''
{tab(['交付材料','范围'],[[link(P/name),name[:-3]] for name in required])}

[SOURCE_INDEX](SOURCE_INDEX.json)、[静态全量锁](evidence/STATIC_WORKSPACE_LOCK.json)、[source完整diff](evidence/SOURCE_COMPLETE.diff)、[input完整diff](evidence/INPUT_COMPLETE.diff)、[原源码](evidence/original)、[24函数AST与12源文件保持](evidence/AST_AND_INVARIANT_CHECK.json)。

[batch05原始证据审查](evidence/HISTORICAL_RAW_REVIEW.json)、[历史hash保护](evidence/HISTORY_PROTECTION_CHECK.json)、[native静态摘要](evidence/STATIC_NATIVE_SUMMARY.json)、[13条精确argv/双流](evidence/commands)、[原始请求](evidence/TASK_REQUEST.txt)、[研究实现门](SEPARATION_AND_SCOPE.md)、[公开接口来源摘录](evidence/PRIMARY_API_SOURCES.json)。

静态候选r1/r2/r3保留源44项与当时锁/检查；最终r4位于独立ri01。当前Linux只部署静态源，batch06运行实体尚未创建。归档含本轮研究材料、final44静态文件、四导航现状和batch05原审阅ZIP，旧源码/ZIP均不改写。

[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)、[ROOTIPC_STATIC_REVIEW.zip](ROOTIPC_STATIC_REVIEW.zip)、[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)分列字节与SHA。manifest排除自身、最终ZIP和delivery避免循环；交付核对记录manifest与ZIP摘要，逐流校验仅授予PASS_ADMIN_ONLY。原batch05包内导航保留该封存时点，本轮新导航前保留完整旧字节快照。
''')
report('README.md','DCL-R6-RootIPC-Fix','''
最终RootIPC-static-1/r4：Root共享文件发布和停止等待已完成有限静态修复；56项专项夹具、17份源码语法、44项源码/缓存/输入及完整diff已冻结。动态执行0，batch06未创建。

[最终裁决](FINAL_DECISION.md) · [batch06执行申请](BATCH06_EXECUTION_REQUEST.md) · [源与输入锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [审阅包](ROOTIPC_STATIC_REVIEW.zip)

IMPLEMENTATION_GATE=CLOSED；严格分离实例0；RESOURCE_GATE_PASS尚未取得。
''')

index={'schema':'RI-source-index/1','version':'RootIPC-static-1','freeze_revision':'r4','workspace':str(W),
 'Linux':'/var/lib/dcl-r6/ri01','files':frozen['files'],'source_changes':checks,
 'old_batch05_package':{'path':str(B05/'BATCH05_EVIDENCE.zip'),'sha256':sha(B05/'BATCH05_EVIDENCE.zip')},
 'root_future':'/var/lib/dcl-r6/batch06','future_created':False,'all_dynamic_status':'UNRUN',
 'gates':{'RI-1':'PASS_STATIC','RI-2':'CONDITIONAL_PASS','RI-3':'CONDITIONAL_PASS','RI-4':'PASS_STATIC'},
 'root_tcb_extra_probe_children':1,'execution_lock_sha256':sha(W/'inputs/execution_lock.json')}
dump(P/'SOURCE_INDEX.json',index)

intro='''# DCL-R6-RootIPC-Fix 最新静态裁决（2026-11-11）

RootIPC-static-1/r4完成有限静态修复：Root共享intent发布前固定999:989/0600，Root私有与payload可读收据分离；ready/RPC/父waitpid加入停止fresh-read及有限回收。修改原2份源码、新增3份；原12程序及24预算/资格函数保持，56专项夹具/8变异与最终44项文件冻结。

RI-1/RI-4=PASS_STATIC；RI-2/RI-3=CONDITIONAL_PASS。17份最终源码语法与44项host/Linuxhash通过；动态执行0，batch06未创建。下一动态申请绑定r4真实hash，并明确新增最多1个顺序降权探针TCB、完整C/C09H/IPC56/S/17门及资格后自动F1→F4。实际停止延迟和300秒可完成性仍待测量。

batch05原RESOURCE_GATE_FAILED、R37,293、303事务、真实C09 NOT_EXERCISED与全部失败证据保持。D1-PBFT-SEAL/1.1、强G原条件、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-RootIPC-Fix/FINAL_DECISION.md) · [batch06申请](DCL-R6-RootIPC-Fix/BATCH06_EXECUTION_REQUEST.md) · [证据索引](DCL-R6-RootIPC-Fix/EVIDENCE_INDEX.md)

以下完整保留本轮开始前的历史导航；各旧阶段“下一步/许可/未创建”文字按对应时点理解。

---

'''
for row in baseline['navigation']:(ROOT/row['original']).write_bytes(intro.encode() + Path(row['snapshot']).read_bytes())

planned={P/'OUTPUT_MANIFEST.json',P/'ROOTIPC_STATIC_REVIEW.zip',E/'DELIVERY_CHECK.json'}
links_checked=0;broken=[]
for file,content in [(q,q.read_text(encoding='utf-8')) for q in P.glob('*.md')]+[(ROOT/'README.md',intro)]:
    assert '不是' not in content
    for dest in re.findall(r'\]\(([^)]+)\)',content):
        dest=dest.strip('<>')
        if '://' in dest or dest.startswith('#'):continue
        links_checked+=1;p=(file.parent/dest.split('#')[0]).resolve()
        if not p.exists() and p not in planned:broken.append({'file':str(file),'target':dest})
assert not broken,broken
for name in required:assert (P/name).is_file()
json_count=0
for base in [P,W]:
    for q in base.rglob('*.json'):
        if q.name not in ['OUTPUT_MANIFEST.json','DELIVERY_CHECK.json']:load(q);json_count+=1
dump(E/'REPORTING_RECEIPT.json',{'schema':'RI-offline-reporting/1','script':str(Path(__file__).resolve()),
 'new_local_links_checked':links_checked,'link_errors':broken,'JSON_parsed':json_count,
 'historical_dynamic_replay':0,'new_target_modules_executed':0,'statistical_inference':'N/A deterministic evidence',
 'research_candidate_implementation':0,'infrastructure_repair':'explicit current task authorization'})

excluded={P/'OUTPUT_MANIFEST.json',P/'ROOTIPC_STATIC_REVIEW.zip',E/'DELIVERY_CHECK.json'}
rows=[]
for base,prefix in [(P,'research'),(W,'FROZEN_ROOTIPC')]:
    for q in sorted(base.rglob('*')):
        if q.is_file() and q not in excluded:
            rows.append({'host':str(q),'scope':prefix,'archive_path':prefix+'/'+q.relative_to(base).as_posix(),
                         'bytes':q.stat().st_size,'sha256':sha(q)})
for row in baseline['navigation']:
    q=ROOT/row['original'];rows.append({'host':str(q),'scope':'navigation','archive_path':'navigation/'+q.name,'bytes':q.stat().st_size,'sha256':sha(q)})
q=B05/'BATCH05_EVIDENCE.zip';rows.append({'host':str(q),'scope':'historical','archive_path':'historical/batch05/BATCH05_EVIDENCE.zip','bytes':q.stat().st_size,'sha256':sha(q)})
combined={'schema':'RI-output-manifest/1','version':'RootIPC-static-1/r4','files':rows,
          'scope_counts':dict(Counter(r['scope'] for r in rows)),
          'exclusions':['OUTPUT_MANIFEST.json','ROOTIPC_STATIC_REVIEW.zip','evidence/DELIVERY_CHECK.json']}
dump(P/'OUTPUT_MANIFEST.json',combined)
archive=P/'ROOTIPC_STATIC_REVIEW.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(P/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
    assert len(set(z.namelist()))==len(rows)+1
    for row in rows:
        raw=z.read(row['archive_path']);assert hashlib.sha256(raw).hexdigest()==row['sha256'] and len(raw)==row['bytes']
        assert sha(row['host'])==row['sha256']
    assert z.read('OUTPUT_MANIFEST.json')==(P/'OUTPUT_MANIFEST.json').read_bytes()
delivery={'schema':'RI-delivery/1','status':'PASS_ADMIN_ONLY','version':'RootIPC-static-1/r4',
 'required_reports':len(required),'final_syntax_modules':17,'static_source_files':44,
 'budget_core_AST_preserved':24,'original_source_bytes_preserved':12,'IPC_jobs':56,'IPC_mutants':8,
 'dynamic_tests':0,'target_role_bodies':0,'batch06_created':False,'T0':None,'counter':None,
 'history_mismatches':0,'links_checked':links_checked,'local_link_errors':[],'JSON_parsed':json_count,
 'manifest_rows':len(rows),'ZIP_entries':len(rows)+1,'ZIP_stream_mismatches':[],
 'manifest_sha256':sha(P/'OUTPUT_MANIFEST.json'),'ZIP_sha256':sha(archive),'ZIP_bytes':archive.stat().st_size,
 'source_manifest_sha256':sha(W/'inputs/static_manifest.json'),'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),
 'root_ipc_contract_sha256':sha(W/'inputs/root_ipc_contract.json'),
 'gates':index['gates'],'resource_gate':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE',
 'IMPLEMENTATION_GATE':'CLOSED','strict_separation_instances':0,
 'administrative_scope':'All listed bytes/ZIP streams/schema/new Markdown links; no dynamic correctness certification',
 'link_scope':'New RootIPC Markdown and navigation prefix; historical bodies preserved',
 'seal_time_utc':datetime.now(timezone.utc).isoformat(),'self_excluded_from_ZIP_and_manifest':True}
dump(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps(delivery,ensure_ascii=False,indent=2))
