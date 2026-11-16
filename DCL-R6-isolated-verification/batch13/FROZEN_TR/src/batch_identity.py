"""Fixed B09 namespace. Configuration is checked against an exact reviewed identity."""
import json
from pathlib import Path

SPEC = {
    'schema':'DCL-BATCH-IDENTITY/1','revision':'TerminalRead-static-1/r1',
    'batch_id':'batch13','source_root':'/var/lib/dcl-r6/tr01',
    'runtime_root':'/var/lib/dcl-r6/batch13','slice':'dclr6batch13.slice',
    'service_prefix':'dclr6batch13-',
    'host_package':'D:/毕业设计/DCL-R6-isolated-verification/tr01',
    'host_control':'D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-TerminalRead-Fix/authorization/batch13-r1',
    'linux_control':'/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-TerminalRead-Fix/authorization/batch13-r1',
    'authorization_filename':'execution_authorization.json',
    'authorization_text_filename':'BATCH13_AUTHORIZATION_TEXT.txt',
    'operator_text_filename':'TASK_REQUEST.txt',
    'cases':['C%02d'%i for i in range(13)]+['C09H','RANGE','FORMAL','STOP'],
}

def load(package):
    package=Path(package)
    config=json.loads((package/'inputs/batch_identity.json').read_bytes())
    if config != SPEC:raise ValueError('MR_IDENTITY_CONFIGURATION_MISMATCH')
    legal={SPEC['source_root'],SPEC['host_package']}
    if package.resolve().as_posix() not in legal:raise ValueError('MR_SOURCE_PACKAGE_MISMATCH')
    return config

def unit(config,case):
    if config != SPEC or case not in SPEC['cases']:raise ValueError('MR_UNREGISTERED_UNIT')
    return config['service_prefix']+case.lower()+'.service'
