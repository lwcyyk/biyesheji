"""Host-only batch05 reporting and byte verification. Executes no research payload."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import struct
import sys
import zipfile
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
ROOT = BATCH.parent
WORK = Path(r'D:\毕业设计\DCL-R6-isolated-verification')
NATIVE = WORK / 'batch05/native_snapshot'
SOURCE = WORK / 'batch05/FROZEN_C09'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def dump(name, value):
    path = HERE / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def md(name, title, body):
    (BATCH / name).write_text(
        '# ' + title + '\n\n'
        'Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；'
        '2026-11-11；复跑 0。\n\n' + body.strip() + '\n', encoding='utf-8')


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', '<br>')
    return '\n'.join(['|' + '|'.join(headers) + '|', '|' + '|'.join(['---'] * len(headers)) + '|'] +
                     ['|' + '|'.join(map(cell, row)) + '|' for row in rows])


def link(path, label=None):
    from os.path import relpath
    rel = relpath(path, BATCH).replace('\\', '/')
    return '[' + (label or Path(path).name) + '](<' + rel + '>)'


baseline = read(HERE / 'BASELINE_LOCK.json')
timeline = read(HERE / 'RUNTIME_TIMELINE.json')
failure = read(HERE / 'FIRST_FAILURE.json')
budget = read(HERE / 'BUDGET_AUDIT.json')
c02 = read(HERE / 'C02_ACTUAL.json')
reg = read(HERE / 'C09_REGRESSION_ACTUAL.json')
cfg = read(HERE / 'c09_contract.json')
safety = read(HERE / 'safety_contract.json')
lock = read(HERE / 'execution_lock.json')
manifest = read(HERE / 'static_manifest.json')
native_lock = read(HERE / 'NATIVE_EXPORT_LOCK.json')
source_lock = read(HERE / 'FROZEN_SOURCE_EXPORT_LOCK.json')
commands = [read(HERE / f'commands/{i:02}.result.json') for i in range(1, 32)]
t0 = timeline['T0']
boot = timeline['boot']

# Recheck original bytes on the host; these operations launch no Linux process.
history_checks = []


def check_rows(name, rows, resolve, hash_key='sha256'):
    errors = []
    for row in rows:
        p = resolve(row)
        if not p.is_file():
            errors.append({'path': str(p), 'error': 'MISSING'})
        elif sha(p) != row[hash_key] or ('bytes' in row and p.stat().st_size != row['bytes']):
            errors.append({'path': str(p), 'error': 'BYTE_OR_HASH_MISMATCH'})
    result = {'name': name, 'count': len(rows), 'mismatches': errors,
              'status': 'PASS_ADMIN_ONLY' if not errors else 'FAIL'}
    history_checks.append(result)
    return result


check_rows('C09Fix/batch04/GapClosure research baseline', baseline['history'], lambda r: ROOT / r['relative'])
check_rows('Canonical c09f01 source/cache/inputs', baseline['source_files'],
           lambda r: Path(baseline['source_workspace']) / r['relative'])
check_rows('Pre-batch05 navigation snapshots', baseline['root_navigation'], lambda r: ROOT / r['snapshot'])
for folder in ['DCL-R6-GapClosure', 'DCL-R6-BudgetFix']:
    old = read(ROOT / folder / 'evidence/STATIC_WORKSPACE_LOCK.json')
    check_rows(folder + ' original workspace', old['files'], lambda r, old=old: Path(old['host']) / r['relative'])
for fn in ['NATIVE_EXPORT_LOCK.json', 'FROZEN_SOURCE_EXPORT_LOCK.json']:
    old = read(ROOT / 'DCL-R6-batch04/evidence' / fn)
    check_rows('batch04 ' + fn, old['files'], lambda r: Path(r['host']))
old = read(ROOT / 'DCL-R6-batch02-Perf/evidence/BASELINE_LOCK.json')
check_rows('batch02 original raw exports', old['immutable_B02_external'], lambda r: Path(r['path']))
duplicates = read(ROOT / 'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
dup_check = check_rows('Mispath duplicates: read/hash only', duplicates['files'],
                       lambda r: Path(duplicates['path']) / r['relative'], 'duplicate_sha256')
dup_check.update(cleanup_attempts=0, prior_policy_rejection='blocked by policy retained')
check_rows('batch05 exported native regular files', native_lock['files'], lambda r: Path(r['host']))
check_rows('batch05 exported frozen source', source_lock['files'], lambda r: Path(r['host']))
for batch_name, expected in [('batch04', 37021), ('batch02', 32191)]:
    f = WORK / batch_name / 'native_snapshot/out/visits.bin'
    if not f.exists():
        matches = list((WORK / batch_name).rglob('visits.bin'))
        assert len(matches) == 1, matches
        f = matches[0]
    raw = f.read_bytes()
    assert len(raw) == 24 and struct.unpack('<QQ', raw[8:]) == (expected, 1000000), str(f)
assert all(not row['mismatches'] for row in history_checks), history_checks
dump('HISTORY_PROTECTION_CHECK.json', {
    'schema': 'B05-history-protection/1', 'checks': history_checks,
    'historical_batch04_reserved': 37021, 'historical_batch02_reserved': 32191,
    'modified_history_files': 0, 'new_batch06': False,
    'method': 'Host byte/hash reads only; Linux verification not repeated'})

# Independent checks over archived counter, journal and native ZIP.
raw_counter = (NATIVE / 'out/visits.bin').read_bytes()
used, cap = struct.unpack('<QQ', raw_counter[8:])
assert len(raw_counter) == 24 and (used, cap) == (37293, 1000000)
records = [json.loads(line) for line in (NATIVE / 'out/visits.bin.journal.jsonl').read_text().splitlines()]
assert len(records) == 606 and Counter(r['status'] for r in records) == {'PREPARED': 303, 'COMMITTED': 303}
assert budget['errors'] == [] and budget['reserved'] == used
native_manifest = read(NATIVE / 'out/EVIDENCE_MANIFEST.json')
native_rows = native_manifest['files']
assert len(native_rows) == 345
with zipfile.ZipFile(NATIVE / 'out/EVIDENCE.zip') as z:
    assert len(z.infolist()) == 346 and len(set(z.namelist())) == 346
    for rel, row in native_rows.items():
        assert len(z.read(rel)) == row['bytes'] and hashlib.sha256(z.read(rel)).hexdigest() == row['sha256'], rel
        assert sha(NATIVE / rel) == row['sha256'], rel
    assert z.read('out/EVIDENCE_MANIFEST.json') == (NATIVE / 'out/EVIDENCE_MANIFEST.json').read_bytes()
assert sha(NATIVE / 'out/EVIDENCE.zip') == read(HERE / 'NATIVE_ZIP_CHECK.json')['sha256']
for c in commands:
    for stream in ['stdout', 'stderr']:
        assert sha(BATCH / c[stream + '_file']) == c[stream + '_sha256']
assert [c['order'] for c in commands if c['exit_code'] not in (0, 1)] == [24]
assert all(commands[i - 1]['exit_code'] == 1 for i in [12, 27, 30])
assert commands[23]['argv'][3:] == lock['launch_command']
assert not any('--resume' in c['argv'] for c in commands)

# Collect resource observations without converting charged memory to RSS.
stop_files = sorted((NATIVE / 'inputs').glob('stop_result_*.json'))
stop_results = [read(p) for p in stop_files]
first_cleanup = min(stop_results, key=lambda x: x['sample']['boottime'])
peak_values = first_cleanup['before_stop_charged_snapshot']['values']
observed_peak = int(peak_values['memory.peak'])
assert observed_peak == 125554688 and all(x['empty'] for x in stop_results)
dump('RESOURCE_OBSERVATIONS.json', {
    'schema': 'B05-observed-resource/1', 'observed_charged_peak_bytes': observed_peak,
    'observed_charged_peak_MiB': observed_peak / 1048576, 'exact_tree_RSS_peak': None,
    'C02_child_RSS_snapshot_bytes': c02['RSS_snapshot'], 'C02_child_VM_snapshot_bytes': c02['VM_snapshot'],
    'payload_tasks_max': 4, 'C04_fifth_task': 'EAGAIN',
    'root_coordinator_CPU_RSS': 'UNMEASURED; external TCB',
    'source_stop_results': [str(p) for p in stop_files],
    'payload_empty_elapsed': first_cleanup['sample']['boottime'] - t0,
    'root_cleanup_elapsed': timeline['root_final_cleanup_elapsed'],
    'outer_process_elapsed_ms': commands[23]['elapsed_ms']})

hash_rows = [[name, sha(HERE / name)] for name in [
    'static_manifest.json', 'execution_lock.json', 'c09_contract.json', 'safety_contract.json', 'TASK_REQUEST.txt']]
md('BATCH05_AUTHORIZATION_AND_LOCK.md', 'batch05 授权、冻结锁与启动前核验', f'''
本批获准执行独立 batch05，Root 协调器、C09H 34 项及完整资源门均在授权范围内；F1/F4 依赖同批 RESOURCE_GATE_PASS。授权原文与安装回执分别见 [TASK_REQUEST](evidence/TASK_REQUEST.txt)、[execution_authorization](evidence/execution_authorization.json)。冻结执行锁原有 `DYNAMIC_UNAUTHORIZED` 字段保留其静态历史语义，当前专项授权由新回执绑定，锁字节保持。

{table(['对象', 'SHA-256'], hash_rows)}

唯一源为 `/var/lib/dcl-r6/c09f01`，host 为 `D:\\毕业设计\\DCL-R6-isolated-verification\\c09f01`；14 源码、14 缓存、9 输入共 37 项与冻结锁一致。原 10 份程序字节保持。14 份源码语法检查属于 C09Fix 静态阶段记录，本批通过最终文件摘要绑定该记录；本批新增语法执行 0。

启动前 native sha256sum 对 1,282 个唯一 Linux 文件核验通过，范围见 [HASH_SCOPE](evidence/HASH_SCOPE.json)。Ubuntu 24.04.5、kernel `6.18.33.2-microsoft-standard-WSL2/x86_64`、systemd `255.4-1ubuntu8.18`、cgroup2fs、页大小 4096；Python `/usr/bin/python3.12` 3.12.3，SHA-256 `e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f`。payload UID/GID=999/989，补充组仅 989。唯一已知历史 manager 失败为 mnt-e.mount。启动前专用 UID、batch05 单位、旧账及窗口均为空。

5 条冻结准备命令安装本批目录/slice、verify、daemon-reload；verify exit 0。授权文件 root:989/0640，out 999:989/0700；父 slice inactive，TasksMax=4、MemoryMax=4 GiB。最终启动前核验 [PREFLIGHT_FINAL](evidence/PREFLIGHT_FINAL.json) 全部成立，随后仅初始化一次窗口与预算。

唯一启动为命令 24：

```text
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/c09f01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch05
```

boot `{boot}`；T0={t0:.9f}，deadline={timeline['deadline']:.9f}，stop_at={timeline['stop_at']:.9f}。资源合同 CPY312-UBU24/1、AS4-PAYLOAD/1；总访问 1,000,000、总窗 1,800 秒、提前停止 T0+1,740、校准软窗 300 秒/100,000、每 payload 进程 AS 1 GiB、payload 父 slice 4 tasks、C09H 硬限 5,000。

执行锁含 16 组 payload argv、34 个原 S worker 模板及 17-unit journal 导出。实际命令完整记录见 [COMMAND_SUMMARY](COMMAND_SUMMARY.md)。31 条 native 调用仅命令 24 启动测试链；resume 调用 0。首次失败后仅查询和封存。PowerShell 辅助函数别名冲突在准备前修正，未导致 native/payload 调用，见 [ADMIN_EVENT](evidence/ADMIN_EVENT.json)。

[源码/输入索引](SOURCE_INDEX.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[实际结果](evidence/ACTUAL_RESULTS.json)。
''')

md('BATCH05_ROOT_COORDINATOR_RESULTS.md', 'batch05 Root 协调器边界与实际生命周期', f'''
Root 协调器确实启动并参与本批监督。稳定身份来自 `batch_state.json`：父 PID 3834/start_ticks 387752，scheduler 子 Launcher PID 3835/start_ticks 387762；boot 均为 `{boot}`。独立 external-stop PID 3839/start_ticks 387769，STOP_ARMED 绑定原 stop_at 与控制 socket。

{table(['职责', '实际证据及范围'], [
['身份与启动', '直接 fork、子身份握手及 pidfd 控制流见冻结 guard.py:963–1006；状态文件保存父子稳定身份'],
['C09H 独立重算', 'root_verify_c09h 实际接受 34 项；额外 34 次全局访问'],
['真实持久交接', 'C09 ready 前失败；commit/ACK/交接状态/专用退出见证均缺失'],
['waitpid', '源码普通退出分支调用 waitpid；外层退出 125 与该路径一致。原始 raw_wait_status 独立收据缺失，成功交接退出23见证未取得'],
['停止', 'STOP_REQUEST 后 external-stop 发布 CLOSED、stop_exit=0、payload 组为空'],
['Root 结束', 'scheduler 等待至 T0+300 后 C09_NOT_READY，finally 清理和 native seal；父透传 exit125；命令30查询两个 Root PID 均为空'],
['权限与行为缺陷', '特权审查替换 intent 导致 uid999 读取失败；C09 等待循环延迟观察闭合']])}

首次 STOP_REQUEST=T0+{timeline['first_failure_elapsed']:.9f} 秒；CLOSED=T0+{timeline['close_elapsed']:.9f}；payload 组空=T0+20.927591657。scheduler 的后续 LAUNCHER_ERROR=T0+300.029941411，最终组空复核=T0+{timeline['root_final_cleanup_elapsed']:.9f}；外层命令墙钟 {commands[23]['elapsed_ms']/1000:.7f} 秒。两段停止延迟分别报告，Root 管理组件未实现迅速随 CLOSED 退出。

guard.py:834–835 仅检查 `C09.ready` 与时间；闭合后继续等待至共享校准 T0+300。真实 handoff 状态尚未发布，父协调器没有生成该状态专用的退出见证；普通错误退出与交接成功分类分别保留。

Root 父、Root scheduler 和外部停止器属于 payload slice 外的 TCB；4 tasks 与条件性 4 GiB 仅对应已批准 payload 边界。新增 Root CPU/RSS 峰值为 UNMEASURED，外层生命期与 34 次审查访问已记录。AS4 的普通映射、内核特殊映射与可信内核/Root/fsync/调度假设保持。本批观察范围内未见预算/输入变更、无关单位操作或额外任务。

命令 28：stop service exit124、C09 SIGKILL、父 slice inactive；命令 27 专用 UID 空，命令 29 父组不存在，命令 30 父子 Root PID 空。事后默认/GC 属性仅作清理观察。原始证据见 {link(NATIVE/'inputs/batch_state.json')}、{link(NATIVE/'inputs/STOP_ARMED.json')}、[时间线](evidence/RUNTIME_TIMELINE.json)、[命令24](evidence/commands/24.result.json)、[命令30](evidence/commands/30.result.json)。
''')

requirements = ['当前 batch 交接意图', 'receiver 取得有效交接状态', '同一活 receiver 的持久 ACK',
                'receiver 确认完成', 'Root waitpid exit23 见证', '退出匹配稳定 Launcher 身份',
                'pidfd 后读取当前交接状态', 'fresh-read 版本有效', '闭合/发布共锁的真实交错',
                '一次有效分类', '恢复保持预算和 deadline', '独立停止源覆盖交接/恢复']
md('BATCH05_C09_HANDOFF_RESULTS.md', 'batch05 真实 C09 交接结果', f'''
真实 C09 入口结果为 **FAIL_ENTRY_PERMISSION**；交接协议结果为 **NOT_EXERCISED**。C09H 完成并通过 Root 重算后，C09 payload 在首次全局记账读取 `visits.bin.intent.json` 时发生 EACCES，随后请求停止。`C09.startup.json` 已保存；`C09.ready.json` 尚未生成。

{table(['成功条件', '本批真实链证据'], [[x, 'NOT_EXERCISED；成功证据待取得'] for x in requirements])}

交接状态、prepare/commit、持久 ACK、receiver 完成确认及 `c09_exit_witness` 均缺失。Root fork、pidfd 初始化与 external-stop socket 已发生；这些启动事实只支持组件就绪范围。Launcher 最终 exit125，预定交接 exit23 尚未发生，恢复次数为 0。

原 T0/deadline/stop_at 与最终账保持；独立停止源实际处理了 STOP_REQUEST。H3 的该次权限故障停止路径有原始观察，完整 H1–H8 实际交接性质仍保留待验证。28 PASS+6 MUTATION_DETECTED 来自合成 C09H，见 [回归结果](BATCH05_C09_REGRESSION_RESULTS.md)。

B05-A：`NOT_EXERCISED / C09_ENTRY_FAILED`。C09Fix 对 batch04 真实持久 ACK、退出见证、fresh-read 及一次分类的修复效果尚待运行证据。首次失败见 [FIRST_FAILURE](evidence/FIRST_FAILURE.json) 与 [反例分析](BATCH05_COUNTEREXAMPLES.md)。
''')

regrows = []
for job, result in zip(cfg['jobs'], reg['results']):
    assert job['case_id'] == result['case_id'] and result['accepted']
    regrows.append([link(NATIVE/'out/c09_tests'/job['case_id'], job['case_id']),
                    ' → '.join(job['events']), job['variant'], job['expected_terminal'],
                    result['final_state'], result['status'], ','.join(result['violations']) or '∅'])
md('BATCH05_C09_REGRESSION_RESULTS.md', 'batch05 C09H 34 项合成回归', f'''
34 项全部执行、完成并获得冻结 Root 独立 oracle 接受：**28 PASS，6 MUTATION_DETECTED**。逐项原始摘要离线核对错误 0；checker SHA-256 `{reg['checker_sha256']}`。driver 的 root 结果文件记录在 T0+{reg['driver_root_PASS_time']-t0:.9f} 秒；其后执行 Root 34 次记账与独立重算，产生 `C09H_QUALIFICATION.json`（accepted=true）。该时间仅表示 driver 结果，独立 Root 资格文件未单列完成时刻。

合成初态及每步 facts、ACK/receiver/witness、事件偏序、分类次数、binding 和原始摘要见各 case 目录的 event 文件及 result。`write_interrupted`、`fsync_failed`、receiver 故障等注入在合成事实层执行。真实 socket ACK、实际接收进程崩溃、物理 fsync 故障与交接 waitpid/pidfd 顺序覆盖仍由真实 C09 另取证。表中空违规集代表相应 oracle 接受。

{table(['case/原始目录', '冻结事件顺序', 'variant', '期望终态', '实际终态', '结果', 'H 违规'], regrows)}

6 个 mutant 分别命中：stale/H2；version/H1,H8；exit_only/H1；closed/H1,H4；duplicate/H6；unknown/H1。预期异常的安全拒绝归为 PASS；变异终态为 VERIFIED 时，违规见证仍明确记为 MUTATION_DETECTED。Root 使用独立 c09_oracle 从冻结事件重建事实，无候选 subject 导入。

该阶段开始 R=37,020，driver 消耗 239、Root 审查消耗 34，共 273；273≤静态完成路径上界2,245≤硬限5,000。原校准共享 T0 与总访问额度保持。Root 审查最后一次 intent 由 euid0 替换，随后触发真实 C09 权限失败，详见 [预算](BATCH05_RESOURCE_ACCOUNTING.md)。

[逐项机器汇总](evidence/C09_REGRESSION_ACTUAL.json)、{link(NATIVE/'inputs/C09H_QUALIFICATION.json', 'Root资格原件')}、[冻结合同](evidence/c09_contract.json)。
''')

descriptions = {
    'C00': '入口 kernel/身份/AS/cgroup 与冻结映射谓词',
    'C01': '正常执行与监督器握手',
    'C02': '批量预留、真实内存 child、局部 AS 与 MemoryError 判据',
    'C03': '16 MiB 共享映射、4096 预留与可见操作',
    'C04': '父组 4 tasks；第五 task EAGAIN；pids.events max 0→2',
    'C05': '普通全局/局部并发计数',
    'C06': '预期 timeout/Watchdog 停止',
    'C07': 'Controller 预期 exit23',
    'C08': 'Watchdog 故障后的冻结拒绝/退出'}
calrows = []
for case, desc in descriptions.items():
    result = read(NATIVE / f'inputs/result_{case}.json')
    assert result['status'] == 'PASS'
    calrows.append([link(NATIVE/f'inputs/result_{case}.json', case), 'PASS',
                    f"{result['sample']['boottime']-t0:.9f}", desc])
calrows.extend([['C09H', '34 accepted', 'driver结果19.586482022', '合成回归+后续Root独立审查'],
                ['C09', 'FAIL_ENTRY_PERMISSION', '20.861903589首次请求停止', '交接NOT_EXERCISED'],
                ['C10–C12', 'UNRUN_RESOURCE_GATE', '—', '首次关键失败后停止']])
md('BATCH05_RESOURCE_CALIBRATION.md', 'batch05 资源校准实际结果', f'''
预检通过；C00–C08 共 9 个冻结 root 机器结果 PASS。真实 C09 入口失败，C10–C12 保持 UNRUN_RESOURCE_GATE；完整校准资格尚待取得。

{table(['case', '结果', 'T0后秒', '实际范围'], calrows)}

C02：N={c02['N']}，预留核心 {c02['core_reserve_ms']:.6f} ms；child 生命周期跨度 {c02['child_span_seconds']:.9f} 秒；root 结果在 T0+{c02['result_T0']:.9f}。实际操作 {c02['operations']}，未用 {c02['unused']} 信用保守占用。child 的局部 AS soft/hard 均 {c02['child_AS'][0]} B（96 MiB），VM 快照 {c02['VM_snapshot']} B，RSS 快照 {c02['RSS_snapshot']} B；这两个值分别为该 child 快照。

payload 父组本 generation 观察到 charged memory peak={observed_peak} B（{observed_peak/1048576:.6f} MiB），memory.events oom/oom_kill=0；精确 RSS 树峰值未认证。C04 实际 pids.current/max=4/4，拒绝第五 task。原父 AS4 条件仅覆盖授权 payload 边界，Root 管理进程另列外部 TCB。

STOP_REQUEST T0+20.861903589、CLOSED +20.909951317、payload 清空 +20.927591657；Root 管理层等待至约 +300 才退出，final cleanup +300.043546214。完整校准在 300 秒内完成的证据仍缺失；既有较短的 C02 结果仅证明该局部路径。完整校准静态访问上界 62,034≤100,000，当前已运行前缀占用 37,293；后缀运行成本尚未测量。

[C02实际数据](evidence/C02_ACTUAL.json)、[资源观察](evidence/RESOURCE_OBSERVATIONS.json)、[Root生命周期](BATCH05_ROOT_COORDINATOR_RESULTS.md)、[时间线](evidence/RUNTIME_TIMELINE.json)。
''')

srows = [[job['case_id'], job['property'], job['variant'], job.get('fault_point', '—'),
          'UNRUN_RESOURCE_GATE'] for job in safety['jobs']]
md('BATCH05_S1_S9_RESULTS.md', 'batch05 S1–S9 资格测试结果', f'''
计划 34 项；实际尝试 0、完成 0、通过 0、变异检出 0。C09 入口首次关键失败使 RANGE 前置条件缺失，S1–S9 结果全部为 UNRUN_RESOURCE_GATE。此前静态夹具完整性与 batch04 结果均保留各自范围。

{table(['冻结 job', '性质', 'variant', '故障点', '实际结果'], srows)}

S1–S9 的独立 Root 原始重算与 RANGE_QUALIFICATION 均未执行/生成。主账内容审计仅针对已发生的 303 笔事务，尚未形成这些崩溃、幂等、并发、持久化故障、关闭与 N+1 路径的动态资格。后续审查应覆盖全部特权全局记账路径，因为 C09H 的 intent 所有权缺陷可能同样影响 Root S/gate 审查。

[冻结 S 合同](evidence/safety_contract.json)、[实际状态](evidence/ACTUAL_RESULTS.json)、[首次失败](BATCH05_COUNTEREXAMPLES.md)。
''')

grows = [[job['case_id'], job['recipe'], job['expected_prefix'], 'UNRUN_RESOURCE_GATE']
         for job in safety['gate_negative_cases']]
md('BATCH05_GATE_NEGATIVE_RESULTS.md', 'batch05 17 项资格门负向检查', f'''
计划 17 项，实际执行 0，实际拒绝见证 0。当前批次因 C09 首次失败停止；17 项检查的有效拒绝能力仍待动态证据。源码拒绝规则和本批未调用的字段保持原锁。

{table(['case', '冻结构造', '期望拒绝前缀', '实际结果'], grows)}

RESOURCE_GATE_PASS=NOT_OBTAINED。C09 入口 FAIL、真实交接 NOT_EXERCISED、C10–C12/S34/门17 UNRUN 均阻断资格。Root 全局账内容配对完整与行政封存核对通过分别保留其窄范围，无法补足测试链。

[合同](evidence/safety_contract.json)、[校准](BATCH05_RESOURCE_CALIBRATION.md)、[最终裁决](BATCH05_FINAL_DECISION.md)。
''')

md('BATCH05_RESOURCE_ACCOUNTING.md', 'batch05 持久预算与停止资源核算', f'''
最终 R=**37,293/1,000,000**。原始 24 字节 counter、606 行 journal、COMMITTED intent 内容一致。303 笔事务为 303 PREPARED+303 COMMITTED：300 笔单信用、3 笔 exact range；独立行政 parser 导入目标模块 0，错误 0。

{table(['task', 'before', 'amount', 'after'], [[r['task'], r['before'], r['amount'], r['after']] for r in budget['range']])}

总量等式：300+32,896+4,096+1=37,293。C02 实际使用17,991/32,896，剩余14,905保持占用；退款0、预算重置0、resume0、新窗口1。C09H 基线37,020，driver239+Root34=273，最终37,293。真实 C09 在分配其入口信用前 EACCES，因此没有后续事务。最终 intent before=37,292/after=37,293/status=COMMITTED，boottime=3898.266588342。

原始内容一致性与访问权限分别裁决：counter及journal为999:989/0600；共享intent为0:0/0600。euid0审查能写入该intent，下一uid999读入失败。该缺陷导致全局预算运行健康准入失败；`PASS_RAW_ACCOUNTING`仅表示本次停止前账内容核对。

boot `{boot}`，原T0/deadline/stop_at保持。首次请求停止+20.861903589，闭合+20.909951317，payload组空+20.927591657；Root最终清理+300.043546214，外层300.5839319秒。父组观察charged峰值125,554,688 B、pids上限4；树RSS峰值与Root CPU/RSS为未测量。

历史batch04 R=37,021、batch02 R=32,191已从host原始counter再次读取；历史、源及47误副本字节核对见[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。先前 `blocked by policy` 保留；误副本仅只读/hash。

{link(NATIVE/'out/visits.bin', 'counter原件')}、{link(NATIVE/'out/visits.bin.intent.json', 'intent原件')}、{link(NATIVE/'out/visits.bin.journal.jsonl', 'journal原件')}、[独立核算](evidence/BUDGET_AUDIT.json)、[原始权限](evidence/commands/26.result.json)。
''')

for model, items, boundary in [
    ('F1', ['SMOKE', 'BRANCH', 'CHAIN', 'KEY', '规定 mutants', '反例重放', 'INV1–INV8'],
     '旧钥、历史责任、预算、ReadyState/ReadyUse 与迟到 IO 的冻结边界保持。'),
    ('F4', ['COST1', 'CE5/其他冻结夹具', 'D2-DP', 'TRACE-REF', '压缩开关对照', 'G64', '规定 mutants', '反例重放'],
     '独立参考与候选后继/终态判定隔离的原要求保持；本批尚无动态对照数据。')]:
    md(f'BATCH05_{model}_RESULTS.md', f'batch05 {model} 有界检查结果', f'''
实际状态：**UNRUN_RESOURCE_GATE**。RESOURCE_GATE_PASS 尚未取得；FORMAL unit/模型搜索均未启动。实际搜索0、语义状态访问0；无本批有限域完整性、覆盖或反例搜索结果。

{table(['冻结范围', '本批实际'], [[x, 'UNRUN_RESOURCE_GATE'] for x in items])}

PASS_BOUNDED 授予0；模型反例数量为“未搜索”，通过率及状态空间规模保持待测量。{boundary} 原模型和输入摘要均在启动前冻结范围内；本批修改0。

本批故障属于资源监督/权限实现，模型级性质裁决继续保留历史条件。D1-PBFT-SEAL/1.1、强G覆盖、严格分离实例0和IMPLEMENTATION_GATE=CLOSED保持。

[冻结执行锁](evidence/execution_lock.json)、[实际结果](evidence/ACTUAL_RESULTS.json)、[阻断原因](BATCH05_COUNTEREXAMPLES.md)。
''')

md('BATCH05_COUNTEREXAMPLES.md', 'batch05 首次失败、权限反例与生命周期缺陷', f'''
## CE-B05-01：特权审查替换共享 intent，payload 后续读取失败

可复核输入轨迹：新batch05/uid999账 → C00–C08通过 → C09H34完成 → Root独立审查用euid0执行34次全局 `reserve_counter` → 共享intent被替换 → C09 uid999入口读取intent → EACCES → BUDGET_HALTED/STOP_REQUEST → CLOSED/组空。

原始STOP_REQUEST（boottime3898.529937533）：

```text
BUDGET_HALTED:[Errno 13] Permission denied: '/var/lib/dcl-r6/batch05/out/visits.bin.intent.json'
```

源码对应：guard.py:285–307 `root_verify_c09h` 逐job通过 `c09h_charge()` 调用全局账；guard.py:119–135 `atomic(...,root_record=False)` 以当前writer创建0600临时文件，replace后保留writer所有权；共享intent路径使用该默认分支。guard.py:491–512 `_counter_lock` 在新事务前读取intent。native stat命令26确认intent=0:0/0600，counter/journal=999:989/0600。

上述控制流、最后34笔特权审查与实际owner/mode/错误路径相互吻合，支持主根因为 **ROOT_AUDIT_REPLACED_SHARED_INTENT_WITH_ROOT_0600**。内容配对错误0，入口拒绝发生于新事务之前。该反例针对监督器跨身份可用性和权限保持，尚未形成F1/F4协议模型反例或原创性分离实例。

## CE-B05-02：C09 ready 等待延迟观察 CLOSED

guard.py:834–835 等待条件只有ready是否存在与case limit。payload在T0+20.927591657已清空；Root scheduler仍等到T0+300，抛出 `C09_NOT_READY`，最终清理在+300.043546214，外层exit125。源码与命令24/stop_event/stop_result一致。停止协议及时终止了payload；Root管理组件的终止响应存在约279秒延迟。

## 修复候选与后续静态验收范围

仅提出审查目标，本轮实现修改0、权限修复0、重试0：明确全局持久账唯一writer身份，或在临时文件对外发布前保持所需owner/mode与持久化顺序；检查全部Root全局记账调用（C09H、S独立检查、门审查）；加入Root→payload与payload→Root身份切换、读写/replace故障、闭合竞态的权限回归。C09等待需统一观察CLOSED/STOP_REQUEST及受控进程退出，并保留绝对期限与已收集首次失败。修复应在独立静态版本冻结后再申请匹配动态范围；本轮batch05持续CLOSED，batch06未创建。

任何新的研究候选机制仍先完成“具体输入族＋度量＋最强通用方法＋预测差距”的可证伪分离声明及严格实例，再考虑实现。当前严格分离0，IMPLEMENTATION_GATE=CLOSED。

[因果汇总](evidence/ROOT_CAUSE.json)、[首次失败](evidence/FIRST_FAILURE.json)、[冻结源码摘录](evidence/FAILURE_SOURCE_EXCERPTS.txt)、[原始权限](evidence/commands/26.result.json)、[实际双流/退出](evidence/commands/24.result.json)。全部首次失败原件保持。
''')

md('BATCH05_FINAL_DECISION.md', 'batch05 最终裁决', f'''
**RESOURCE_GATE_FAILED；真实 C09 交接 NOT_EXERCISED；F1/F4 均 UNRUN_RESOURCE_GATE。** 本轮预检通过并实际运行冻结C09Fix-static-1/r1；首个关键失败发生在Root完成C09H审查之后的C09入口。

{table(['裁决轴', '本批结论'], [
['B05-A C09修复', 'C09入口FAIL_ENTRY_PERMISSION；真实持久ACK、waitpid退出23见证、fresh-read与一次交接分类尚待验证'],
['B05-B 资源资格', 'C00–C08九项PASS；C09H34 accepted（28 PASS+6 MUTATION_DETECTED）；C09失败；C10–C12/S34/门17未运行；RESOURCE_GATE_PASS未取得'],
['B05-C F1/F4', '模型搜索0；均UNRUN_RESOURCE_GATE；PASS_BOUNDED授予0'],
['B05-D 证据完整性', '37项源/缓存/输入及1282唯一Linux摘要启动前通过；全部原始双流/账/合成轨迹/权限与清理证据封存；交接缺件如实登记；行政完整性另见DELIVERY_CHECK']])}

主根因：Root独立审查以euid0替换全局共享intent为root:root/0600，下一uid999 payload读取失败并正确请求停止。次要缺陷：C09 ready等待忽略已发布CLOSED/STOP_REQUEST，Root scheduler延迟至共享T0+300才退出。实际handoff尚未进入；34项合成回归仅支持其自身事件/判据范围。

最终预算37,293/1,000,000；303组PREPARED/COMMITTED事务完整配对。T0+20.861903589请求停止、+20.909951317闭合、+20.927591657确认payload组空。Root最终清理+300.043546214，命令24外层exit125；其后专用UID、父slice及Root父子PID均为空。预算/deadline重置0、resume0、失败重试0、源码及权限修复0、batch06创建0。

C02局部路径通过：N32,896，核心预留43.751137ms，child跨度2.720971054秒，实际操作17,991，未用14,905保持占用。payload observed charged peak125,554,688B，pids上限4；精确树RSS与Root资源峰值未认证。完整校准300秒可完成性仍待验证。

程序在最终异常清理中实际完成native自动seal：345 manifest rows、346 ZIP entries、ZIP SHA-256 `0c548146e1c750da4d2cb0f26cf2bfae39c833caebf47e8f33a65a6261f8ebf0`；host保存347个native常规文件和37个冻结源/输入/缓存。socket只保存类型/身份/权限，字节复制不适用。该结果与历史batch04的封存情况分别保留。

360项本轮历史研究基线、37项canonical源、GC30/BF24、batch04 native94/source30、batch02原件51、误副本47再次只读/hash核验；历史R37,021/R32,191与`blocked by policy`保留。后续仅提出静态修复目标，当前执行授权已由首次失败终止规则收束。

继续保持 D1-PBFT-SEAL/1.1 原条件结论、强G覆盖、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED。资源工程结果与协议原创性分别裁决。

[授权与锁](BATCH05_AUTHORIZATION_AND_LOCK.md)、[Root生命周期](BATCH05_ROOT_COORDINATOR_RESULTS.md)、[真实交接](BATCH05_C09_HANDOFF_RESULTS.md)、[34项回归](BATCH05_C09_REGRESSION_RESULTS.md)、[首次失败与修复目标](BATCH05_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[最终交付核对](evidence/DELIVERY_CHECK.json)。
''')

cmdrows = []
for c in commands:
    outcome = str(c['exit_code'])
    if c['order'] in (12, 27, 30):
        outcome += '（ps空，预期）'
    elif c['order'] == 24:
        outcome += '（首次失败后的最终退出）'
    cmdrows.append([link(HERE/f"commands/{c['order']:02}.result.json", f"{c['order']:02}"),
                    c['classification'], outcome, f"{c['elapsed_ms']:.3f}", c['purpose']])
md('COMMAND_SUMMARY.md', 'batch05 实际命令索引', f'''
31条native调用的精确argv、UTC起止、原始stdout/stderr及SHA见各result JSON。命令计划在启动前追加，随后保存真实结果；PowerShell封装本身exit0与内部Linux退出码分别记录。实际测试入口仅命令24一次；native resume0。

{table(['编号/argv与双流', '分类', '实际exit', '墙钟ms', '用途'], cmdrows)}

命令25保留首次停止后导出的17-unit运行boot journal，命令31保留Root退出后的最终导出；两份都保留。原始stderr中的WSL localhost代理提示属于环境信息；权限错误、C09_NOT_READY和Linux exit125按各原始记录单独裁决。

本报告构造及逐字节核对在host Python运行，属于离线归档操作；没有调用冻结payload、运行模型、发起额外Linux测试或权限修复。生成脚本见[BUILD_REPORTS.py](evidence/BUILD_REPORTS.py)。
''')

source_index = {
    'schema': 'B05-source-index/1', 'version': 'C09Fix-static-1/r1',
    'canonical_host': baseline['source_workspace'], 'canonical_linux': '/var/lib/dcl-r6/c09f01',
    'native_linux': '/var/lib/dcl-r6/batch05', 'native_host': str(NATIVE),
    'frozen_host': str(SOURCE), 'source_files': source_lock['files'],
    'native_files': native_lock['files'], 'nonregular': native_lock['nonregular'],
    'runtime_hash_scope': read(HERE/'HASH_SCOPE.json'),
    'source_input_changes': 0, 'candidate_implementation_changes': 0,
    'frozen_locks': dict(hash_rows), 'actual_commands': 'evidence/COMMAND_PLAN.json',
    'source_note': '14 sources+14 caches+9 inputs; syntax evidence inherited through final-byte lock',
    'administrative_interpreter': {'executable': sys.executable, 'version': sys.version,
                                  'scope': 'Host offline reporting/hash/ZIP only; research runtime unchanged'}}
(BATCH/'SOURCE_INDEX.json').write_text(json.dumps(source_index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md('EVIDENCE_INDEX.md', 'batch05 研究证据索引', f'''
本索引串联真实运行与本轮封存报告。资源资格=FAILED；模型状态=UNRUN_RESOURCE_GATE；行政核对与实验裁决分列。

## 报告

{table(['材料', '范围'], [[link(BATCH/f'BATCH05_{stem}.md'), scope] for stem,scope in [
('AUTHORIZATION_AND_LOCK','授权、预检、源/运行时/argv锁'),('ROOT_COORDINATOR_RESULTS','Root外部TCB与实际退出延迟'),
('C09_HANDOFF_RESULTS','真实交接NOT_EXERCISED'),('C09_REGRESSION_RESULTS','34合成回归及6变异命中'),
('RESOURCE_CALIBRATION','C00–C08/C09与C02局部数据'),('S1_S9_RESULTS','34项逐项未运行'),
('GATE_NEGATIVE_RESULTS','17项逐项未运行'),('RESOURCE_ACCOUNTING','37,293账、内存与时间范围'),
('F1_RESULTS','F1未运行'),('F4_RESULTS','F4未运行'),('COUNTEREXAMPLES','权限与闭合响应缺陷'),('FINAL_DECISION','四轴裁决')]])}

## 原始来源与独立核对

[SOURCE_INDEX](SOURCE_INDEX.json)列出全部源/输入/native字节映射；[命令摘要](COMMAND_SUMMARY.md)链接31条精确argv与原始双流；[原始执行计划](evidence/COMMAND_PLAN.json)保留每次启动前登记。

{link(NATIVE/'inputs/C09H_QUALIFICATION.json','Root C09H资格原件')}、{link(NATIVE/'out/c09_tests','34项原始事件目录')}、{link(NATIVE/'inputs/STOP_ARMED.json','停止器身份')}、{link(NATIVE/'out/STOP_REQUEST.json','首次权限错误')}、{link(NATIVE/'inputs/CLOSED.json','原闭合记录')}。

[独立预算核算](evidence/BUDGET_AUDIT.json)、[首次失败](evidence/FIRST_FAILURE.json)、[时间线](evidence/RUNTIME_TIMELINE.json)、[资源观察](evidence/RESOURCE_OBSERVATIONS.json)、[原始权限](evidence/commands/26.result.json)、[运行boot最终journal](evidence/commands/31.stdout.raw)。

原始waitpid/pidfd交接见证、ACK、commit/receiver确认在本批未生成；其缺失属于实验结果。socket保存[类型/身份锁](evidence/NATIVE_EXPORT_LOCK.json)，常规文件347份；冻结代码副本37份。最终Root异常清理确实自动seal，{link(NATIVE/'out/EVIDENCE.zip','native ZIP')}逐流核对346项，详情[NATIVE_ZIP_CHECK](evidence/NATIVE_ZIP_CHECK.json)。

[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)保留旧账、误副本及先前策略拒绝；旧batch04/GC/C09Fix的研究结果及原件字节保持。Root四导航文件在新结果前保存完整旧字节快照。封存索引[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)、审阅包[BATCH05_EVIDENCE.zip](BATCH05_EVIDENCE.zip)、[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)分开记录。

Manifest覆盖本轮研究材料、四份当前导航、347 native文件及37 frozen文件，排除manifest自身、交付检查和最终ZIP避免自引用；交付检查单独记录manifest与ZIP的SHA-256。审阅包以research/navigation/native/FROZEN_C09组织，manifest记录每个archive_path。行政核对只证明所列字节与本批导出锁一致，外部研究者实际重跑0、文件系统持久化及可信Root假设仍保持原条件。
''')
md('README.md', 'DCL-R6-batch05', '''
已执行C09Fix-static-1/r1专项验证，并在首次关键失败后关闭。C00–C08九项PASS；C09H34项accepted；真实C09入口共享intent权限失败，交接尚待验证。最终R37,293，payload已清空；Root约T0+300结束。S34、门17及F1/F4全部未运行。

[最终裁决](BATCH05_FINAL_DECISION.md)、[首次失败](BATCH05_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[源码索引](SOURCE_INDEX.json)、[审阅包](BATCH05_EVIDENCE.zip)、[交付检查](evidence/DELIVERY_CHECK.json)。

IMPLEMENTATION_GATE=CLOSED；STRICT_SEPARATION_INSTANCES=0。当前批次维持CLOSED；后续仅列静态修复目标。
''')

# Prepend the new decision to exact pre-run navigation bytes; preserve historical bodies.
nav_intro = '''# DCL-R6-batch05 最新结果（2026-11-11）

实际RESOURCE_GATE_FAILED：C00–C08九项PASS；C09H34 accepted（28 PASS+6 MUTATION_DETECTED）；Root审查后intent变为root:root/0600，真实C09 uid999入口读取失败，持久ACK/交接退出见证尚未取得。预算37,293；payload在T0+20.927591657清空，Root约T0+300退出。C10–C12、S34、门17与F1/F4全部未运行；PASS_BOUNDED授予0。

当前batch05保持CLOSED；下一研究动作仅为审查共享账跨身份owner/mode与C09闭合等待的静态修复范围，审计全部Root全局记账路径，并在独立版本冻结后处理匹配动态许可。实现修改、权限修复、重试、恢复与batch06创建均为0。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0和IMPLEMENTATION_GATE=CLOSED保持；候选机制继续先过可证伪分离声明及严格实例门。

[batch05最终裁决](DCL-R6-batch05/BATCH05_FINAL_DECISION.md) · [首次失败](DCL-R6-batch05/BATCH05_COUNTEREXAMPLES.md) · [证据索引](DCL-R6-batch05/EVIDENCE_INDEX.md)

以下为本批启动前保留的历史记录；其中旧阶段“下一步/未授权/未创建”文字按其阶段理解。

---

'''
for row in baseline['root_navigation']:
    old_bytes = (ROOT / row['snapshot']).read_bytes()
    (ROOT / row['original']).write_bytes(nav_intro.encode('utf-8') + old_bytes)

# Validate newly introduced local links. Historical navigation bodies keep their own scope.
required_names = [f'BATCH05_{stem}.md' for stem in [
    'AUTHORIZATION_AND_LOCK','ROOT_COORDINATOR_RESULTS','C09_HANDOFF_RESULTS','C09_REGRESSION_RESULTS',
    'RESOURCE_CALIBRATION','S1_S9_RESULTS','GATE_NEGATIVE_RESULTS','RESOURCE_ACCOUNTING',
    'F1_RESULTS','F4_RESULTS','COUNTEREXAMPLES','FINAL_DECISION']]
assert all((BATCH/n).is_file() for n in required_names)
planned = {BATCH/'OUTPUT_MANIFEST.json', BATCH/'BATCH05_EVIDENCE.zip', HERE/'DELIVERY_CHECK.json'}
link_errors = []
links_checked = 0
for path, content in [(p,p.read_text(encoding='utf-8')) for p in BATCH.glob('*.md')] + [(ROOT/'README.md',nav_intro)]:
    assert '不是' not in content or path.parent == ROOT
    for target in re.findall(r'\]\(([^)]+)\)', content):
        target = target.strip('<>')
        if '://' in target or target.startswith('#'):
            continue
        target = target.split('#',1)[0]
        dest = (path.parent/target).resolve()
        links_checked += 1
        if not dest.exists() and dest not in planned:
            link_errors.append({'file':str(path),'target':target})
assert not link_errors, link_errors

json_checked = 0
for directory in [BATCH,NATIVE,SOURCE]:
    for p in directory.rglob('*.json'):
        if p.name not in ['DELIVERY_CHECK.json','OUTPUT_MANIFEST.json']:
            read(p)
            json_checked += 1

dump('ADMIN_REPORTING_RECEIPT.json', {
    'schema':'B05-host-reporting/1','command':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],
    'role':'offline artifact construction and byte verification only',
    'linux_commands_added':0,'payload_or_model_runs_added':0,'permissions_changed':0,
    'host_interpreter_version':sys.version,'required_reports':required_names,
    'new_local_links_checked':links_checked,'new_local_link_errors':link_errors,
    'JSON_documents_parsed':json_checked,'statistical_inference':'N/A: deterministic execution evidence',
    'reproduction_status':'ANALYZED_ARCHIVED_BYTES; independent dynamic reproduction UNRUN'})

# Combined manifest and archive. Nonrecursive exclusion rules avoid circular hashes.
excluded = {BATCH/'OUTPUT_MANIFEST.json', BATCH/'BATCH05_EVIDENCE.zip', HERE/'DELIVERY_CHECK.json'}
rows = []
for base,prefix in [(BATCH,'research'),(NATIVE,'native'),(SOURCE,'FROZEN_C09')]:
    for path in sorted(base.rglob('*')):
        if path.is_file() and path not in excluded:
            rows.append({'scope':prefix,'host':str(path),'bytes':path.stat().st_size,'sha256':sha(path),
                         'archive_path':prefix+'/'+path.relative_to(base).as_posix()})
for nav in baseline['root_navigation']:
    path = ROOT/nav['original']
    rows.append({'scope':'navigation','host':str(path),'bytes':path.stat().st_size,'sha256':sha(path),
                 'archive_path':'navigation/'+nav['original']})
combined = {'schema':'B05-output-manifest/1','files':rows,
            'counts_by_scope':dict(Counter(row['scope'] for row in rows)),
            'exclusions':['OUTPUT_MANIFEST.json','BATCH05_EVIDENCE.zip','evidence/DELIVERY_CHECK.json'],
            'nonregular':native_lock['nonregular'], 'resource_verdict':'RESOURCE_GATE_FAILED'}
manifest_path = BATCH/'OUTPUT_MANIFEST.json'
manifest_path.write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
archive_path = BATCH/'BATCH05_EVIDENCE.zip'
with zipfile.ZipFile(archive_path,'w',zipfile.ZIP_DEFLATED) as z:
    for row in rows:
        z.write(row['host'],row['archive_path'])
    z.write(manifest_path,'OUTPUT_MANIFEST.json')
zip_errors = []
with zipfile.ZipFile(archive_path) as z:
    assert len(set(z.namelist())) == len(rows)+1
    for row in rows:
        data = z.read(row['archive_path'])
        if hashlib.sha256(data).hexdigest()!=row['sha256'] or len(data)!=row['bytes'] or sha(row['host'])!=row['sha256']:
            zip_errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json') == manifest_path.read_bytes()
assert not zip_errors
assert combined['counts_by_scope']['native']==347 and combined['counts_by_scope']['FROZEN_C09']==37
delivery = {
    'schema':'B05-delivery/1','status':'PASS_ADMIN_ONLY','resource_verdict':'RESOURCE_GATE_FAILED',
    'real_C09':'FAIL_ENTRY_PERMISSION; HANDOFF_NOT_EXERCISED','F1':'UNRUN_RESOURCE_GATE',
    'F4':'UNRUN_RESOURCE_GATE','model_searches':0,'PASS_BOUNDED':[],
    'required_reports':len(required_names),'manifest_file_rows':len(rows),
    'scope_counts':combined['counts_by_scope'],'zip_entries':len(rows)+1,'ZIP_stream_mismatches':zip_errors,
    'manifest_sha256':sha(manifest_path),'zip_sha256':sha(archive_path),'zip_bytes':archive_path.stat().st_size,
    'native_zip_entries':346,'native_zip_sha256':sha(NATIVE/'out/EVIDENCE.zip'),
    'history_mismatches':sum(len(row['mismatches']) for row in history_checks),
    'JSON_documents_parsed':json_checked,'new_local_links_checked':links_checked,'local_link_errors':[],
    'link_scope':'All newly written batch05 Markdown and new navigation prefix; historical bodies preserved',
    'payload_empty':True,'root_PIDs_query_empty':True,'budget_reserved':37293,
    'code_input_changes':0,'postfailure_permission_changes':0,'retry':0,'resume':0,'new_batch06':False,
    'IMPLEMENTATION_GATE':'CLOSED','STRICT_SEPARATION_INSTANCES':0,
    'seal_time_utc':datetime.now(timezone.utc).isoformat(),
    'self_excluded_from_manifest_and_ZIP':True,
    'administrative_scope':'Byte/hash/schema/link/ZIP verification; no dynamic reproduction or protocol proof'}
dump('DELIVERY_CHECK.json',delivery)
print(json.dumps(delivery,ensure_ascii=False,indent=2))
