"""Static JSON grammar and disjoint write-volume accounting, no DCL execution."""
import json
from READ_INPUTS import PREVIOUS, E, save, read, record

class Width:
    def __init__(self, size):
        self.size = size

class Token:
    def __init__(self, name):
        self.name = name

def combine(parts):
    constant = 0
    terms = {}
    for amount, names in parts:
        constant += amount
        for name, coefficient in names.items():
            terms[name] = terms.get(name, 0) + coefficient
    return constant, terms

def pretty_bound(value, depth=0):
    if isinstance(value, Width):
        return value.size, {}
    if isinstance(value, Token):
        return 0, {value.name: 1}
    if isinstance(value, dict):
        count = len(value)
        if count == 0:
            return 2, {}
        fixed = 2 + count - 1 + sum(len(json.dumps(key).encode()) + 2 for key in value)
        fixed += 1 + count + 2 * count * (depth + 1) + 2 * depth
        return combine([(fixed, {})] + [pretty_bound(item, depth + 1) for item in value.values()])
    if isinstance(value, list):
        count = len(value)
        if count == 0:
            return 2, {}
        fixed = 2 + count - 1 + 1 + count + 2 * count * (depth + 1) + 2 * depth
        return combine([(fixed, {})] + [pretty_bound(item, depth + 1) for item in value])
    if type(value) is bool:
        return 5, {}
    return len(json.dumps(value, ensure_ascii=False).encode()), {}

clock = {'boottime':Width(25),'utc_ns':Width(20),'boot_id':'b'*36}
identity = {'pid':Width(10),'start_ticks':Width(20),'boot_id':'b'*36}
window = {'batch_id':'batch14','boot_id':'b'*36,'T0':Width(25),'deadline':Width(25),'stop_at':Width(25),
          'execution_mode':'MR_RECOVERY_DIAGNOSTIC_ONLY','source_manifest_sha256':'a'*64,
          'execution_lock_sha256':'a'*64,'contract_sha256':'a'*64,'authorization_sha256':'a'*64}
names = ['pids.current','pids.max','pids.events','memory.current','memory.peak','memory.max','memory.swap.max',
         'memory.events','memory.oom.group','cgroup.events','cgroup.procs','cgroup.threads']
snapshot = {'path':'/sys/fs/cgroup/dclr6batch14.slice',
            'filesystem_identity':{'device':Width(20),'inode':Width(20),'ctime_ns':Width(29)},
            'values':{name:Token('V'+str(index+1)) for index,name in enumerate(names)},
            'sample':clock,'metric':'cgroup charged memory; distinct from RSS'}
cleanup = {'empty':False,'stop_exit':Width(11),'closure_persistence_error':None,'before_stop_charged_snapshot':snapshot,
           'peak_scope':'observed charge peak for this group generation; no exact RSS tree peak inferred',
           'after_stop_group_exists':False,'sample':clock}
state = {'status':'AWAIT_EXPECTED_RESUME','boot_id':'b'*36,'T0':Width(25),'stop_at':Width(25),'deadline':Width(25),
         'launcher_identity':identity,'resume_count':1,'expected_launcher_exit':None,
         'execution_mode':'MR_RECOVERY_DIAGNOSTIC_ONLY','coordinator_identity':identity,'mr_stop_required':False}
handoff = {'schema':'C09-DURABLE-RPC/1','nonce':'a'*32,'revision':6,'case':'C09',
           'sender':identity,'coordinator':identity,'receiver':identity,'window':window,
           'counter':{'used':Width(7),'cap':1000000,'device':Width(20),'inode':Width(20),'sha256':'a'*64},
           'expected_exit':23,'ticket_sha256':'a'*64,'regression_sha256':'a'*64,'ready_sha256':'a'*64,
           'classification_count':1,'observe_until':Width(25),'id':'a'*64,
           'stage':'HANDOFF_VERIFIED','updated':clock,'commit_sha256':'a'*64,
           'cleanup':cleanup,'witness_sha256':'a'*64}
result_C09 = {'case':'C09','status':'PASS','actual':{'handoff_id':'a'*64,'handoff_revision':5,
               'commit_sha256':'a'*64,'witness_sha256':'a'*64,'native_exit':23,'cleanup':cleanup},'sample':clock}
normal = {}
for name, value in [('stop_result',cleanup),('handoff_state',handoff),('result_C09',result_C09),('batch_state',state)]:
    constant, terms = pretty_bound(value)
    normal[name] = {'constant_bytes':constant,'token_coefficients':terms,'codec':'RootIPC indent2 UTF8, noLF'}
assert normal['stop_result']['constant_bytes'] == 1155
assert all(value == 1 for value in normal['stop_result']['token_coefficients'].values())
save('NORMAL_HANDOFF_BYTE_MODEL.json', {
    'scope':'existing normal VERIFIED/RESUMED writes, same closed keys and inherited ABI; kernel values remain symbolic',
    'records':normal,'new_data_publications':6,
    'publication_basis':'stop_result1, HANDOFF_VERIFIED state1, result_C09_1, AWAIT state1, RESUMED state1, resumed batchstate1',
    'stable_actual_carriers':4,'cleanup_copies_in_stable_carriers':3,'cleanup_copies_in_generated_data_writes':4,
    'main_stage_rows':'already within263/345148; no duplicate billing here',
    'other_input_objects':'commit/resources/ACK/witness/bindings already existing and must remain available; full input pool not newly allocated by this model',
    'byte_total':None,'physical_guarantee':None})

prepay = read(PREVIOUS/'evidence/RESOURCE_IMPACT_MODEL.json')['prepay']
assert prepay['journal_rows'] == 512 and prepay['journal_byte_increment_upper'] == 122112
assert prepay['total_data_write_bytes_upper'] == 266752 and prepay['fsync_calls_healthy_root'] == 2304
save('PREPAY_AND_CLOSE_PARTITION.json', {'source':record(PREVIOUS/'evidence/RESOURCE_IMPACT_MODEL.json'),
    'prepay':prepay,
    'write_volume_partition':{'journal':122112,'intent_replacement_write_sum':142592,'counter_pwrite_sum':2048,'total':266752},
    'retained_space_meaning':'journal append growth; intent142592 is replacement write sum with one final intent<=279; counter2048 is overwrite sum, counter file remains24bytes',
    'double_count_rule':'122112 and512 rows are already inside266752; count266752 once for cumulative prepay data writes. Close snapshots embed hashes/size only.',
    'main_log':{'bytes':345148,'separate_path':'inputs/root_private/c09_events.jsonl','effective':False},
    'minimal_close_bytes':None,'prepay_is_close_reserve':False,'physical_space_requires_allocation_and_metadata_proof':True})
print(json.dumps({'normal_models':4,'prepay_write_total':266752,'journal_part':122112,'normal_encoded_total':None}))
