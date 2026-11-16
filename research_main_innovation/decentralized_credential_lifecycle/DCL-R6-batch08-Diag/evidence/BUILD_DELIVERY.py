"""Offline minimal-diagnostic reports and private evidence sealing; no target replay."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib
import json
import os
import re
import struct
import zipfile

E=Path(__file__).resolve().parent
P=E.parent
ROOT=P.parent
C=ROOT/'DCL-R6-batch08'
WORK=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
W=WORK/'cr01'
N=WORK/'batch08/native_snapshot'
F=WORK/'batch08/FROZEN_C00READY'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def link(p,label=None):return '['+(label or Path(p).name)+'](<'+os.path.relpath(p,P).replace('\\','/')+'>)'
def table(headers,rows):
    def c(v):return str(v).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(c,r))+'|' for r in rows])
def report(name,title,text):
    (P/name).write_text('# '+title+'\n\nMaterial Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。\n\n'+text.strip()+'\n',encoding='utf-8')

base=load(E/'BASELINE_LOCK.json');fields=load(E/'C00_FIELD_ACTUAL.json');times=load(E/'READINESS_TIMELINE.json')
account=load(E/'RESOURCE_ACCOUNTING.json');result=load(E/'ACTUAL_RESULTS.json');post=load(E/'POSTRUN_AUDIT.json')
native=load(E/'NATIVE_EXPORT_LOCK.json');frozen=load(E/'FROZEN_SOURCE_EXPORT_LOCK.json');nz=load(E/'NATIVE_ZIP_CHECK.json')
cfg=load(E/'readiness_contract.json');lock=load(E/'execution_lock.json');refs=load(E/'REGRESSION_REFERENCE_CHECK.json')
state=load(N/'inputs/batch_state.json');closed=load(N/'inputs/CLOSED.json');boot=state['boot_id'];t0=state['T0']
c00=load(N/'inputs/result_C00.json');qual=load(N/'inputs/C00_READY_QUALIFICATION.json');startup=load(N/'out/C00.startup.json')
assert state['execution_mode']=='C00_DIAGNOSTIC_ONLY' and account['R']==450 and qual['accepted']
assert len(native['files'])==101 and len(frozen['files'])==36 and refs['counts']=={'PASS':47,'MUTATION_DETECTED':17}
assert not post['payload_processes'] and not post['root_role_processes'] and not post['parent_cgroup_exists']
history=[]
def verify(name,rows,path,key='sha256'):
    errors=[]
    for row in rows:
        p=path(row)
        if not p.is_file() or sha(p)!=row[key] or ('bytes'in row and p.stat().st_size!=row['bytes']):errors.append(str(p))
    history.append({'name':name,'count':len(rows),'mismatches':errors,'status':'PASS_ADMIN_ONLY' if not errors else 'FAIL'})
    assert not errors,(name,errors)
verify('All historical R6 research files',base['history'],lambda r:ROOT/r['relative'])
verify('Canonical cr01 final36',base['source_files'],lambda r:W/r['relative'])
verify('Native101 actual bytes',native['files'],lambda r:Path(r['host']))
verify('Frozen35 Linux files plus Windows entry',frozen['files'],lambda r:Path(r['host']))
assert {r['relative']:r['sha256'] for r in base['source_files']}=={r['relative']:r['sha256'] for r in frozen['files']}
for folder in ['DCL-R6-batch07','DCL-R6-batch06','DCL-R6-batch05','DCL-R6-batch04']:
    for name in ['NATIVE_EXPORT_LOCK.json','FROZEN_SOURCE_EXPORT_LOCK.json']:
        x=load(ROOT/folder/'evidence'/name);verify(folder+'/'+name,x['files'],lambda r:Path(r['host']))
for folder in ['DCL-R6-BootContinuity-Fix','DCL-R6-RootIPC-Fix','DCL-R6-C09Fix','DCL-R6-GapClosure','DCL-R6-BudgetFix']:
    x=load(ROOT/folder/'evidence/STATIC_WORKSPACE_LOCK.json');d=Path(x.get('host',str(WORK/'c09f01')))
    if folder=='DCL-R6-C09Fix':d=WORK/'c09f01'
    verify(folder+' old workspace',x['files'],lambda r,d=d:d/r['relative'])
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/BASELINE_LOCK.json');verify('batch02 original51',x['immutable_B02_external'],lambda r:Path(r['path']))
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');verify('Mispath47 read/hash only',x['files'],lambda r:Path(x['path'])/r['relative'],'duplicate_sha256')
for row in base['navigation']:assert sha(row['snapshot'])==row['sha256']
old_R={}
for batch,want in [('batch07',0),('batch05',37293),('batch04',37021),('batch02',32191)]:
    p=WORK/batch/'native_snapshot/out/visits.bin'
    if not p.exists():
        xs=list((WORK/batch).rglob('visits.bin'));assert len(xs)==1;p=xs[0]
    assert struct.unpack('<QQ',p.read_bytes()[8:])==(want,1000000);old_R[batch]=want
archives=[]
for folder,name in [('DCL-R6-C00Ready-Fix','C00READY_STATIC_REVIEW.zip'),('DCL-R6-batch07','BATCH07_EVIDENCE.zip'),('DCL-R6-batch06','BATCH06_EVIDENCE.zip')]:
    p=ROOT/folder/name
    with zipfile.ZipFile(p) as z:
        m=json.loads(z.read('OUTPUT_MANIFEST.json'))
        for row in m['files']:
            b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
        archives.append({'path':str(p),'sha256':sha(p),'entries':len(z.namelist()),'stream_errors':[]})
for name in ['TASK_REQUEST.txt','execution_authorization.json','WINDOWS_ENTRY_PLAN.json','WINDOWS_ENTRY_EXIT.json','windows_entry.stdout.raw','windows_entry.stderr.raw']:
    assert sha(C/'evidence'/name)==sha(E/name),name
dump(E/'HISTORY_PROTECTION_CHECK.json',{'schema':'D08-history/1','checks':history,'archives':archives,'old_budgets':old_R,
 'modified_history_files':0,'mispath_actions':'read/hash only','prior_policy_rejection':'blocked by policy retained',
 'control_and_diag_log_bytes_equal':True})

events=[json.loads(s) for s in (E/'windows_entry.stdout.raw').read_text(encoding='utf-8').splitlines() if s.strip()]
entries=[x for x in events if x['event'] in ('ACTIVATION_REQUESTED_ONLY','ENTRY_VERIFIED')]
assert len(entries)==2 and entries[0]['identity']==entries[1]['identity']==state['coordinator_identity']
self_identity=c00['actual']['probe']['actual']['facts']['process']['identity']
assert self_identity==fields['process_identity'] and self_identity['boot_id']==boot
cap=load(N/'inputs/root_private/boot/capability.json');entry=load(N/'inputs/root_private/boot/entry_initial.json')
assert cap['sha256']==entry['ticket_sha256'] and cap['seals']==15
err=(E/'windows_entry.stderr.raw').read_bytes()
dump(E/'STDERR_DECODE.json',{'schema':'D08-stderr/1','raw_sha256':sha(E/'windows_entry.stderr.raw'),
 'encoding':'utf-16-le' if b'\x00'in err else 'utf-8','text':err.decode('utf-16-le' if b'\x00'in err else 'utf-8',errors='replace'),
 'scope':'Client warning only if present; native entry exited0; raw bytes unchanged'})
inner=[];innerdir=E/'internal_commands';innerdir.mkdir(exist_ok=True)
for event in events:
    if event['event']!='PREFLIGHT_COMMAND':continue
    i=len(inner)+1;r={'order':i,'argv':event['argv'],'start':event['start'],'after':event['sample'],'exit_code':event['exit_code'],'identity':event['identity']}
    for stream in ['stdout','stderr']:
        raw=bytes.fromhex(event[stream+'_hex']);p=innerdir/f'{i:02}.{stream}.raw';p.write_bytes(raw)
        r[stream+'_file']=p.relative_to(P).as_posix();r[stream+'_sha256']=hashlib.sha256(raw).hexdigest()
    inner.append(r)
assert all(r['exit_code']==0 for r in inner)
dump(E/'INTERNAL_COMMANDS.json',{'schema':'D08-inner-commands/1','commands':inner,'reconstructed_from_original_hex':True})
dump(E/'BOOT_IDENTITY_ACTUAL.json',{'schema':'D08-boot/1','run_boot':boot,'owner_before_exec':entries[0]['identity'],
 'owner_after_exec':entries[1]['identity'],'service_self_identity':self_identity,'same_boot':True,'same_PID_exec':True,
 'capability_sha256':cap['sha256'],'seals':15,'postrun_observation_boot':post['observation_boot_id'],
 'postrun_boot_not_reused_for_activation':True,'duplicate_claim_test':'Not independently replayed; frozen one-shot checks and one actual entry',
 'fine_pidfd_evidence':'Successful frozen checks inferred, separate per-check timestamps not emitted'})

hashrows=[[name,sha(E/name)] for name in ['static_manifest.json','execution_lock.json','readiness_contract.json','boot_contract.json','root_ipc_contract.json','c09_contract.json','safety_contract.json','TASK_REQUEST.txt']]
report('BATCH08_DIAG_AUTHORIZATION_AND_LOCK.md','batch08最小诊断授权与版本锁',f'''
实际scope为 **C00_DIAGNOSTIC_ONLY**，Full_conditional_chain=false、RootIPC_helpers=false、SameProcess_C09_resume=false；C00_diagnostic=true和单会话exec明确批准。原文/回执见[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[execution_authorization](evidence/execution_authorization.json)。

{table(['对象','SHA-256'],hashrows)}

本轮第7节要求按最小申请具体清单执行。冻结申请第一目标明确列出“原C00 probe、64正反夹具/17mutant及独立raw重算”；据此64项属于已批准最小范围。其余BC40、RootIPC56、C09H34、C01–C12、真实C09、S34、17完整门和F1/F4均未授权/未执行。范围与449/512、静态最小R上界513的核对见[SCOPE_AND_RESOURCE_ADMISSION](evidence/SCOPE_AND_RESOURCE_ADMISSION.json)。

36项host文件和24份程序身份匹配，35项Linux源码/输入部署为Root0:0/0644、目录0755、ACL空且无pyc。该部署观察不构成运行boot期望常量；冻结Windows入口的一次WSL调用重新取得当前动态身份。

```text
{' '.join(lock['windows_single_call'])}
```

实际冻结控制目录为`DCL-R6-batch08/evidence`，目标入口从该路径读取授权并写活动双流；报告位于`DCL-R6-batch08-Diag`。两处对应原文、回执及入口日志字节相同，source与argv未改。仅调用1次入口，无重试/补窗/代码或阈值现场修复。

[主机入口调用](evidence/FROZEN_ENTRY_INVOCATION.json)、[实际Windows plan](evidence/WINDOWS_ENTRY_PLAN.json)、[退出记录](evidence/WINDOWS_ENTRY_EXIT.json)、[部署结果](evidence/DEPLOYMENT_RESULT.json)、[命令索引](COMMAND_SUMMARY.md)。
''')

journal=load(E/'JOURNAL_SUMMARY.json')
report('BATCH08_DIAG_RUNTIME.md','运行时、资源边界与关闭',f'''
原生CPython3.12.3 `/usr/bin/python3.12`、SHA e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f；native artifact_check及内存语法编译完成，冻结kernel/systemd/架构/来源断言通过，systemd输出255.4-1ubuntu8.18、page4096。没有安装依赖或修改WSL全局配置。

Root协调器438/start4792，scheduler796/start4949，C00实际进程811/start4978；boot均{boot}。C00 startup中的RLIMIT_AS soft/hard均1073741824，实际kernel/proc和manager值已取证。after-watchdog组观测pids.current={startup['after_watchdog_group']['values']['pids.current']}，父pids.max4/memory.max4GiB；观察charged peak={account['observed_charged_peak_bytes']}B（{account['observed_charged_peak_bytes']/1048576:.8f}MiB），精确树RSS及Root峰值未认证。

{table(['run-boot journal单位','MONOTONIC µs','原始消息'],[[r['unit'],r['mono_us'],r['message']] for r in journal['records']])}

批次按C00_DIAGNOSTIC_COMPLETE正常关闭，T0+{account['close_elapsed']:.9f}，首次组空T0+{account['first_empty_elapsed']:.9f}；普通父waitpid raw0/exit0，Windows WSL子进程exit0。事后UID999/Root角色为空、父cgroup不存在。事后boot={post['observation_boot_id']}的not-found/default单位属性仅作清理观察，不拼入旧运行资格。

14秒屏障只接受获准暂态，300秒/1800秒窗口及原AS4-PAYLOAD/1解释保持。C00与模拟安全检查通过仍缺其余C/S/H/完整门，资源总资格未取得。
''')

report('BATCH08_DIAG_BOOT_IDENTITY.md','启动连续性与稳定身份核验',f'''
**SAME_BOOT_CONFIRMED（本次有效最小启动范围）**。单会话预检、same-PID exec前后Root、scheduler和C00服务自查均绑定{boot}。exec前后Owner均438/start4792；C00自己的kernel_admission报告811/start4978和相同boot。

sealed能力实际生成并由Guard核验，seals15；摘要`{cap['sha256']}`。原始能力材料保留Root私有路径和授权私有审阅包，普通日志/报告只展示摘要。实际初始认领消费一次，未发起独立重复认领或恢复测试。

3份原生readiness记录的目标身份均为811/start4978/该boot，双侧/proc中Pid与UID/GID等值对应当前目标。READY返回意味着冻结pidfd_open、G.identity前后比较及select存活检查路径已成功；但记录未独立保存每次pidfd检查时间/后侧starttime原始stat，成功属于控制流见证。精细pidfd事件覆盖与八项原始值完整性分别报告。

D08-4总体取 **FIELD_EVIDENCE_PARTIAL**：八字段值、双次原文、来源时刻/版本完整；单独pidfd时刻和wait函数精确返回点缺少打点，不能补造成实测值。D08-3 C00_PASS独立保留，不因记录粒度而改写安全判断。

[boot摘要](evidence/BOOT_IDENTITY_ACTUAL.json)、[原生字段重算](evidence/C00_FIELD_ACTUAL.json)、[原始readiness目录](<../../../DCL-R6-isolated-verification/batch08/native_snapshot/inputs/root_private/boot>)。
''')

field_rows=[]
for r in fields['fields']:
    field_rows.append([r['check_id'],r['field_name'],r['expected'],r['initial_observed'],r['initial_result'],r['final_observed'],r['final_result']])
report('BATCH08_C00_FIELD_RESULTS.md','C00八项真实字段结果与历史定位边界',f'''
**C00_PASS**：原生C00 readiness通过并取得Root机器result_C00 PASS；所有最终8项在两轮READY检查中均MATCH。无稳定失配、读取错误或身份变化。

{table(['check_id/编号','字段','expected','首次observed','首次结果','最终双侧observed','最终结果'],field_rows)}

CR-01 Uid、CR-02 Gid、CR-03 Groups来自实际/proc/811/status集合；CR-04 CapEff十六进制转整型0，CR-05 NoNewPrivs为1。CR-06/07来自systemd硬/软AS属性字符串，CR-08来自manager ControlGroup路径；独立辅助门还核对实际/proc/limits soft/hard1GiB、实际/proc/cgroup及parent4tasks/4GiB。

首次manager为STARTING且MainPID811已存在，CR-01…05按冻结合同defer，observed=null/NOT_READY；CR-06…08当时已MATCH。这里没有把未读值当错误或通过，STARTING期间Root票据未发放，controller尚未开始计费probe。随后READY两轮才实际读取五项凭据并得到匹配。

双次读原文与诊断JSON的observed由离线独立parser逐项重算一致，未调用目标collector或修改判据。每项read_time/来源、PID/starttime/boot和证据SHA见[C00_FIELD_ACTUAL](evidence/C00_FIELD_ACTUAL.json)及3份原始ready_C00记录。

**旧batch07具体失败字段仍C00_FAILED_FIELD_UNRESOLVED。** 本轮证实非零MainPID可与合法STARTING并存，并支持加入exec-ready屏障；batch07没有保存同刻UID/GID等值，本轮早期也有意不读最终凭据，因此无法倒推它当时是哪项失配。当前全部MATCH不能重写旧聚合拒绝或认定旧配置错误。
''')

time_rows=[[r['file'],r['phase'],f"{r['begin']:.9f}",f"{r['end']:.9f}",r['result']] for r in times['samples']]
report('BATCH08_C00_READINESS_TIMELINE.md','C00就绪时间线、双取样和14秒上界',f'''
时间使用同一run-boot CLOCK_BOOTTIME。源合同until=min(start+14,T0+300,stop_at,deadline)；实际until={times['readiness_until']:.9f}，其他边界更晚，因此由until−14可恢复原start请求时刻={times['activation_started']:.9f}。该推导按冻结控制流，保持与独立时钟域分开。

{table(['原始文件','manager双侧阶段','采样开始','采样完成','裁决'],time_rows)}

首次完整READY决策采样在{times['first_READY_decision_time']:.9f}；Native wait返回发生于该采样完成与后续confirm开始之间。相对start请求的可核验区间为 **{times['native_wait_return_lower_seconds']:.9f}–{times['native_wait_return_upper_seconds']:.9f}秒**。函数返回点没有独立打点，区间代替伪造的精确值。

再次完整验证结束于相对{times['second_validation_end_seconds']:.9f}秒，ACTUAL_SERVICE_CONFIRMED事件为相对{times['service_confirmed_event_seconds']:.9f}秒；两者均远早于14秒上界。C00 probe机器结果为T0+{times['C00_result_T0']:.9f}秒。

第一轮读取跨度{times['samples'][0]['end']-times['samples'][0]['begin']:.9f}秒，第二轮{times['samples'][1]['end']-times['samples'][1]['begin']:.9f}秒，确认轮{times['samples'][2]['end']-times['samples'][2]['begin']:.9f}秒。READY两轮的unit版本、InvocationID、字段值、目标身份和kernel辅助门一致；pidfd成功仅由冻结路径与无错误结果见证，其单独检查时间未记录。

没有STOP_REQUEST、FAILED或屏障超时事件；正常关闭使用C00_DIAGNOSTIC_COMPLETE，退出时刻见[资源核算](BATCH08_RESOURCE_ACCOUNTING.md)。journal MONOTONIC与Host perf_counter只在各自域计时，不与BOOTTIME混算。
''')

refrows=[]
for job,r in zip(cfg['jobs'],qual['results']):refrows.append([job['case_id'],job['variant'],r['status'],','.join(r['violations']) or '∅',r['accepted']])
report('BATCH08_C00_REGRESSION_RESULTS.md','获准64项回归与17项变异的实际结果',f'''
冻结最小申请的64项全部执行并接受：**47 PASS、17 MUTATION_DETECTED**。每项私有raw、输入摘要、实际frame facts、subject shadow/decision、全局访问前后及Root独立结果均保存；没有以expected代填actual。

{table(['case','variant','actual status','Root oracle实测违规','accepted'],refrows)}

17项错误行为均在声明的合成subject触发，并由冻结独立oracle接受其违规见证；它们覆盖逐项忽略8字段、读错视为匹配、陈旧快照、部分字段、错误PID/boot、稳定错误降级、超时续等、缺锁和跨版本拼接。其真实性范围为SIMULATION_ONLY/1，未主动改变真实UID/资源/WSL，也未运行BC40或原RootIPC等其他套件。

原始64文件SHA与Root资格结果逐一一致；当前host额外只读reference按实际observed/错误/身份/boot/版本和decision检查重新验证安全样本及每个mutant见证，错误0，未import或重放目标程序。[独立reference](evidence/REGRESSION_REFERENCE_CHECK.json)。

该阶段global_before=1/global_after=450，449次包含entry1＋每job预付6＋Root重算1；未用部分保守占用，硬限512。更广的故障调度及物理接口覆盖保持冻结声明，不把合成通过扩大成完整资源门。
''')

report('BATCH08_RESOURCE_ACCOUNTING.md','batch08最小阶段持久预算与退出核算',f'''
最终 **R=450/1000000**；450组PREPARED/COMMITTED完整配对，900行journal与counter/intent after450一致。原C00 probe访问1＋获准64阶段449=450。独立行政parser逐笔核before/after/amount/status，差异0；退款/重置/resume均0。

run boot={boot}；T0={t0:.9f}、deadline={state['deadline']:.9f}、stop_at={state['stop_at']:.9f}，差值1800/1740，初始化1次。关闭={closed['boottime']:.9f}，T0+{account['close_elapsed']:.9f}；首次组空T0+{account['first_empty_elapsed']:.9f}，close→empty {account['closed_to_empty']:.9f}秒；普通父waitpid exit0/raw0。

Host单次活动调用{account['host_active_seconds']:.9f}秒，包含预检、执行与回传，独立perf_counter口径。实际readiness wait返回区间约0.150–0.155秒，后续64账/写证成本都计入同一T0/300秒校准窗。未放宽14、300或1800秒。

原生自动seal实际完成：{nz['manifest_rows']}行manifest、{nz['entries']}个ZIP条目、{nz['bytes']}B，SHA `{nz['sha256']}`；101个native常规文件与36个冻结程序/输入导出完成，逐流差异0。旧socket仅保存类型/mode/身份，byte hash不适用。

全局cap及原CPY312/AS4条件不变；本轮额外Root探针进程0。观察charged peak43937792B、C00 startup观测3 tasks/父max4；精确RSS树峰值与Root峰值未采样。旧batch07 R0、batch05 R37293、batch04 R37021、batch02 R32191与原失败均保留。

最小阶段结束不授RESOURCE_GATE_PASS：BC40/RootIPC56/C09H34/真实C09/C01–C12/S34/门17/F1/F4全部未执行且未授权。本批CLOSED，无法改回执后沿旧窗进入Full。

[账核算JSON](evidence/RESOURCE_ACCOUNTING.json)、[原生seal检查](evidence/NATIVE_ZIP_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。
''')

report('BATCH08_DIAG_COUNTEREXAMPLES.md','诊断结论、旧字段未决与观测缺口',f'''
本轮没有新的C00稳定身份/资源失配、读取错误或不安全READY见证。真实路径为STARTING→READY→再次READY→原C00 probe PASS→47安全/17变异接受→C00_DIAGNOSTIC_COMPLETE关闭。17个合成错误见证是预期检测成功，不能视为生产代码被观察到相同失误。

旧batch07失败原因继续未决。当前首次STARTING只实际观察manager AS/CG匹配，最终凭据被有意defer，历史中缺失的Uid/Gid/Groups/CapEff/NoNewPrivs值无法补齐。结构性“MainPID存在且exec尚未确认”在本轮真实出现，支持原就绪竞态假设；无法唯一定位旧8路OR的真实触发项。

新增/保留观测缺口：READY包含pidfd与前后身份检查成功的控制流证据，但独立pidfd检查时间、后侧starttime原始stat和wait_native精确返回时刻未打点。八字段与双源读取原件完整，D08-4总体保守记FIELD_EVIDENCE_PARTIAL。将来需要细粒度时序证明时，可独立静态增强这些打点；当前禁止为补记录修改源或重跑本批。

当前没有凭空修复某个UID/AS字段的依据。后续可以准备完整条件链的独立版本/执行准入，同时保留测时责任；已经CLOSED的batch08不能恢复或自动转换Full。源含固定batch08命名，新独立批次需要匹配命名/摘要/锁及明确Full批准，当前没有创建batch09，也没有自动进入任何后续项目。

总体结论只涉及已运行的C00和获准64，未新增F1/F4模型安全结论。[字段实值](evidence/C00_FIELD_ACTUAL.json)、[时序区间](evidence/READINESS_TIMELINE.json)、[独立检查](evidence/REGRESSION_REFERENCE_CHECK.json)。
''')

answerrows=[
 ['1 新批次','成功建立并按最小范围正常关闭'],['2 同boot/身份','Same boot，Root438/start4792跨exec；C00自查811/start4978'],
 ['3 原八字段','Uid/Gid/Groups/CapEff/NoNewPrivs/LimitAS/LimitASSoft/ControlGroup'],
 ['4 实值','最终双侧[999]/[989]/[989]/0/1/1073741824/1073741824/规定服务CG，全部MATCH'],
 ['5 首次STARTING','CR-01…05 defer为NOT_READY；CR-06…08已MATCH'],['6 稳定失配','本轮0'],
 ['7 双样本','两次READY字段/版本/身份和kernel辅助值一致；原始状态、时间均存'],
 ['8 pidfd','冻结检查路径成功，无身份变化；独立每次时间/后侧stat未记录'],
 ['9 等待','wait返回区间0.149840881–0.155141782秒；再次验证结束0.185783023秒'],
 ['10 C00','原生Root机器PASS'],['11 最早失败','本轮无失败字段；旧batch07失配项仍UNRESOLVED'],
 ['12 资源','R450、450事务、T0后10.267560352秒正常关闭、charged peak43937792B'],
 ['13 新缺陷','未见稳定字段/接口拒绝；精细pidfd/返回点可观测性缺口保留'],
 ['14 下一步','准备新的独立完整链准入；不恢复CLOSED batch08，不猜测修正某个字段']]
report('BATCH08_DIAG_FINAL_DECISION.md','batch08-Diag最终裁决',f'''
**最小诊断成功完成并正常关闭；C00_PASS。RESOURCE_GATE_PASS仍NOT_OBTAINED，F1/F4均UNRUN_RESOURCE_GATE。**

{table(['裁决轴','结果','边界'],[
 ['D08-1 预检','PREFLIGHT_PASS','原生3.12/源/锁/当前身份及单会话预检通过'],
 ['D08-2 连续性','SAME_BOOT_CONFIRMED','预检/exec/Root/scheduler/C00服务自查同boot'],
 ['D08-3 八项资格','C00_PASS','真实STARTING后READY，最终8项全部MATCH，原probe PASS'],
 ['D08-4 诊断完整性','FIELD_EVIDENCE_PARTIAL','8项与双源原件完整；pidfd独立时刻/后侧stat及精确wait返回点缺打点'],
 ['D08-5 模型资格','NOT_OBTAINED','最小权限范围；其余资格链和模型未启动']])}

{table(['用户最终问题','实际回答'],answerrows)}

获准64项全部有效：47 PASS＋17 MUTATION_DETECTED，Root独立oracle与host只读reference一致，未命中/额外错误0。实际单会话入口1、重试0、源码/判据/权限现场修复0、主动WSL shutdown0。Full批准位false，BC40/RootIPC56/C09H34/C09/C01–C12/S34/门17及F1/F4均UNRUN_UNAUTHORIZED，保持本次边界。

本批boot {boot}，T0={t0:.9f}，R450，CLOSED reason=C00_DIAGNOSTIC_COMPLETE。101 native文件、36最终文件、原生100条目包及run-boot journal已保存；受控进程为空、父cgroup不存在。原batch07聚合拒绝不改，旧字段仍C00_FAILED_FIELD_UNRESOLVED；本轮没有倒填历史observed。

当前代码/输入/全部历史工件与原包hash保持；47误路径副本只读/hash，blocked by policy保持。完整条件链仍需独立批准与匹配新批次版本/锁，当前batch08不可复用，也未创建后续批次。

PASS_BOUNDED授予0；D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离实例0与IMPLEMENTATION_GATE=CLOSED保持。原生诊断成功和完整资源/协议性质分别裁决。

[字段证据](BATCH08_C00_FIELD_RESULTS.md)、[时序](BATCH08_C00_READINESS_TIMELINE.md)、[回归](BATCH08_C00_REGRESSION_RESULTS.md)、[账](BATCH08_RESOURCE_ACCOUNTING.md)、[观测边界](BATCH08_DIAG_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
''')

admin=[load(q) for q in sorted((E/'commands').glob('*.result.json'))]
report('COMMAND_SUMMARY.md','实际命令、控制路径和时钟索引',f'''
单次活动调用由冻结windows_entry.py完成，控制路径{link(C/'evidence/WINDOWS_ENTRY_PLAN.json')}与{link(C/'evidence/WINDOWS_ENTRY_EXIT.json')}保留实际argv、Windows PID和UTC/perf_counter区间。报告内同名副本逐字节相同。

{table(['内部序号','实际argv','BOOTTIME开始','BOOTTIME结束','exit'],[[r['order'],' '.join(r['argv']),r['start']['boottime'],r['after']['boottime'],r['exit_code']] for r in inner])}

内部命令双流由原始事件hex无损解码，见[INTERNAL_COMMANDS](evidence/INTERNAL_COMMANDS.json)。Guard/C00后续被冻结控制流执行，native票据/结果、startup及journal进一步见证；本表没有补造独立execve审计。

{table(['行政编号','用途','exit'],[[link(E/f"commands/{i:02}.result.json",str(i)),r['purpose'],r['exit_code']] for i,r in enumerate(admin,1)])}

行政1为静态部署，2–3在正常关闭后只读导出/清理核查。所有source与测试判据不改，无失败case重跑。run-boot journal使用同一UUID的32-hex表示限定17个既定unit；未运行unit无对应日志，不构造启动记录。
''')

required=['BATCH08_DIAG_AUTHORIZATION_AND_LOCK.md','BATCH08_DIAG_RUNTIME.md','BATCH08_DIAG_BOOT_IDENTITY.md',
 'BATCH08_C00_FIELD_RESULTS.md','BATCH08_C00_READINESS_TIMELINE.md','BATCH08_C00_REGRESSION_RESULTS.md',
 'BATCH08_RESOURCE_ACCOUNTING.md','BATCH08_DIAG_COUNTEREXAMPLES.md','BATCH08_DIAG_FINAL_DECISION.md']
dump(P/'SOURCE_INDEX.json',{'schema':'D08-source-index/1','source_version':'C00Ready-static-1/r2','scope':'C00_DIAGNOSTIC_ONLY',
 'host_source':str(W),'actual_Linux_source':'/var/lib/dcl-r6/cr01','actual_Linux_batch':'/var/lib/dcl-r6/batch08',
 'host_native':str(N),'host_frozen':str(F),'control_directory':str(C),'report_directory':str(P),
 'native_files':native['files'],'source_files':frozen['files'],'nonregular':native['nonregular'],
 'run_boot':boot,'observation_boot':post['observation_boot_id'],'source_changes':0,'full_chain':False,
 'private_scope':'Native Root-private material retained under private paths; ordinary outputs digest-only'})
report('EVIDENCE_INDEX.md','batch08-Diag证据索引',f'''
{table(['交付材料','范围'],[[link(P/name),name[:-3]] for name in required])}

[字段独立重算](evidence/C00_FIELD_ACTUAL.json)、[时序](evidence/READINESS_TIMELINE.json)、[boot身份](evidence/BOOT_IDENTITY_ACTUAL.json)、[64原始参考检查](evidence/REGRESSION_REFERENCE_CHECK.json)、[账核算](evidence/RESOURCE_ACCOUNTING.json)、[实际状态](evidence/ACTUAL_RESULTS.json)。

[入口原始stdout](evidence/windows_entry.stdout.raw)、[原始stderr](evidence/windows_entry.stderr.raw)、[stderr解码](evidence/STDERR_DECODE.json)、[实际命令](COMMAND_SUMMARY.md)、[run journal](evidence/JOURNAL_SUMMARY.json)、[原始journal字节](evidence/RUN_BOOT_JOURNAL.stdout.raw)。当前数据来源于真实当前接口及标记清楚的合成套件，未从expected回填observed。

[101 native锁](evidence/NATIVE_EXPORT_LOCK.json)、[36最终源码/输入锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[路径映射](SOURCE_INDEX.json)、[原生100条目seal](evidence/NATIVE_ZIP_CHECK.json)、[关闭后核查](evidence/POSTRUN_AUDIT.json)、[历史原件保护](evidence/HISTORY_PROTECTION_CHECK.json)。当前sealed秘密原件只保留Root私有相对路径；Linux原权限/ACL/inode在导出锁，host副本证明字节。

[BATCH08_DIAG_EVIDENCE.zip](BATCH08_DIAG_EVIDENCE.zip)是授权私有审阅包，含研究、native101、最终36、原冻结控制文件与四导航。[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)列路径/字节/sha/archive_path，[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)另记manifest/ZIP摘要，排除自引用。行政PASS只证明字节和索引，不升级本轮为完整资源门或模型结论。

旧batch07所有字段缺口/失败和原包保留，未来完整链需要独立新批次准入；本轮没有创建batch09。
''')
report('README.md','DCL-R6-batch08-Diag','''
最小C00诊断成功：真实STARTING→READY→再验证，八项全部MATCH、原C00 probe PASS；64合成检查47 PASS/17 MUTATION_DETECTED。R450，正常关闭并原生seal；Full链和模型均未授权/未运行。

[最终裁决](BATCH08_DIAG_FINAL_DECISION.md) · [字段证据](BATCH08_C00_FIELD_RESULTS.md) · [时间线](BATCH08_C00_READINESS_TIMELINE.md) · [证据索引](EVIDENCE_INDEX.md) · [私有审阅包](BATCH08_DIAG_EVIDENCE.zip)

旧batch07具体字段仍未决；精细pidfd/函数返回点记录为PARTIAL，八字段原始值完整。RESOURCE_GATE_PASS=NOT_OBTAINED；IMPLEMENTATION_GATE=CLOSED。
''')

intro='''# DCL-R6-batch08-Diag 最新最小诊断裁决（2026-11-12）

PREFLIGHT_PASS / SAME_BOOT_CONFIRMED / C00_PASS：C00Ready-static-1/r2实际单会话启动，Root438/start4792跨exec；C00自查811/start4978同boot0cc7ff50…。真实1轮STARTING后2轮READY，首次凭据CR01–05 defer为NOT_READY，最终8项双侧全MATCH。wait返回区间0.149840881–0.155141782秒；精确pidfd/返回点未单独打点，D08-4总体FIELD_EVIDENCE_PARTIAL。

64项获准合成检查全部接受：47 PASS＋17 MUTATION_DETECTED，独立reference无差异。R450/450持久事务/900行配对；T0后10.267560352秒按C00_DIAGNOSTIC_COMPLETE正常关闭，进程/父组为空，原生100条目seal保存。源码/权限修复、重跑/恢复0，batch09创建0。

Full批准false，其余BC40/RootIPC56/C09H34/C01–C12/C09/S34/门17及F1/F4均未授权/未运行，RESOURCE_GATE_PASS仍NOT_OBTAINED。旧batch07具体失败字段保持UNRESOLVED；下一步可准备匹配新批次版本/锁的独立完整链，不恢复已CLOSED的batch08。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-batch08-Diag/BATCH08_DIAG_FINAL_DECISION.md) · [字段证据](DCL-R6-batch08-Diag/BATCH08_C00_FIELD_RESULTS.md) · [证据索引](DCL-R6-batch08-Diag/EVIDENCE_INDEX.md)

以下完整保存本轮前历史导航，旧阶段许可/下一步/未创建文字按相应时点理解。

---

'''
for row in base['navigation']:(ROOT/row['original']).write_bytes(intro.encode()+Path(row['snapshot']).read_bytes())
planned={P/'OUTPUT_MANIFEST.json',P/'BATCH08_DIAG_EVIDENCE.zip',E/'DELIVERY_CHECK.json'}
count=0;errors=[]
for path,text in [(q,q.read_text(encoding='utf-8')) for q in P.glob('*.md')]+[(ROOT/'README.md',intro)]:
    assert '不是' not in text
    for dest in re.findall(r'\]\(([^)]+)\)',text):
        dest=dest.strip('<>')
        if '://'in dest or dest.startswith('#'):continue
        count+=1;q=(path.parent/dest.split('#')[0]).resolve()
        if not q.exists() and q not in planned:errors.append({'file':str(path),'target':dest})
assert not errors,errors
for name in required:assert (P/name).is_file()
nonce=load(N/'inputs/root_private/boot/activation.json')['ticket']['nonce'].encode()
ordinary=[*P.glob('*.md'),E/'windows_entry.stdout.raw',E/'windows_entry.stderr.raw',E/'C00_FIELD_ACTUAL.json',E/'ACTUAL_RESULTS.json']
assert all(nonce not in q.read_bytes() for q in ordinary)
dump(E/'NONCE_DISCLOSURE_CHECK.json',{'schema':'D08-nonce-scope/1','ordinary_files':len(ordinary),'raw_nonce_matches':0,
 'protected_raw_scope':'native_snapshot/inputs/root_private and authorized private review archive','raw_nonce_in_this_file':False})
parsed=0
for d in [P,C,N,F]:
    for q in d.rglob('*.json'):
        if q.name not in ['OUTPUT_MANIFEST.json','DELIVERY_CHECK.json']:load(q);parsed+=1
dump(E/'REPORTING_RECEIPT.json',{'schema':'D08-reporting/1','script':str(Path(__file__).resolve()),'new_links_checked':count,'link_errors':errors,
 'JSON_parsed':parsed,'target_imports_or_replay':0,'scope':'Offline parsing/reference/byte and archive integrity; scope not expanded'})
exclude={P/'OUTPUT_MANIFEST.json',P/'BATCH08_DIAG_EVIDENCE.zip',E/'DELIVERY_CHECK.json'}
rows=[]
for directory,prefix in [(P,'research'),(N,'native'),(F,'FROZEN_C00READY'),(C,'control')]:
    for q in sorted(directory.rglob('*')):
        if q.is_file() and q not in exclude:rows.append({'host':str(q),'scope':prefix,'archive_path':prefix+'/'+q.relative_to(directory).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)})
for row in base['navigation']:
    q=ROOT/row['original'];rows.append({'host':str(q),'scope':'navigation','archive_path':'navigation/'+q.name,'bytes':q.stat().st_size,'sha256':sha(q)})
manifest={'schema':'D08-output-manifest/1','files':rows,'scope_counts':dict(Counter(r['scope'] for r in rows)),
 'exclusions':['OUTPUT_MANIFEST.json','BATCH08_DIAG_EVIDENCE.zip','evidence/DELIVERY_CHECK.json'],'nonregular':native['nonregular'],
 'artifact_scope':'Authorized private review; Root-private originals retained; ordinary summaries digest-only',
 'scope':'C00_DIAGNOSTIC_ONLY','RESOURCE_GATE_PASS':'NOT_OBTAINED'}
dump(P/'OUTPUT_MANIFEST.json',manifest);archive=P/'BATCH08_DIAG_EVIDENCE.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(P/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
    assert len(set(z.namelist()))==len(rows)+1
    for row in rows:
        b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'] and sha(row['host'])==row['sha256']
    assert z.read('OUTPUT_MANIFEST.json')==(P/'OUTPUT_MANIFEST.json').read_bytes()
delivery={'schema':'D08-delivery/1','status':'PASS_ADMIN_ONLY','D08-1':'PREFLIGHT_PASS','D08-2':'SAME_BOOT_CONFIRMED','D08-3':'C00_PASS','D08-4':'FIELD_EVIDENCE_PARTIAL',
 'eight_field_values_complete':True,'pidfd_separate_event_times':'UNRECORDED','required_reports':9,
 'regressions':64,'PASS':47,'MUTATION_DETECTED':17,'reference_errors':[],'R':450,'transactions':450,'journal_records':900,
 'normal_close':'C00_DIAGNOSTIC_COMPLETE','controlled_processes_empty':True,'active_entry_calls':1,'retries':0,'source_or_permission_repairs':0,
 'native_files':101,'frozen_files':36,'native_zip_entries':100,'native_auto_seal':True,
 'manifest_rows':len(rows),'ZIP_entries':len(rows)+1,'ZIP_stream_errors':[],'manifest_sha256':sha(P/'OUTPUT_MANIFEST.json'),'ZIP_sha256':sha(archive),'ZIP_bytes':archive.stat().st_size,
 'history_mismatches':0,'history_research_files':len(base['history']),'links_checked':count,'link_errors':[],'JSON_parsed':parsed,
 'old_batch07_field':'C00_FAILED_FIELD_UNRESOLVED','RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'new_batch09':False,'IMPLEMENTATION_GATE':'CLOSED','strict_separation_instances':0,'sealed_utc':datetime.now(timezone.utc).isoformat(),
 'self_excluded_from_manifest_and_zip':True,'scope':'C00_DIAGNOSTIC_ONLY; admin integrity separate from actual diagnostic and unrun full resource qualification'}
dump(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps(delivery,ensure_ascii=False,indent=2))
