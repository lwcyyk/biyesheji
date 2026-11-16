# batch09 RootIPC56结果

Material Passport：DCL-R6-batch09；2026-11-12；UNRUN_STATIC_ADMISSION。

冻结56项输入及root_ipc.py/root_ipc_regression.py/root_ipc_oracle.py摘要全部匹配，包含48 safe和8 mutant，case_id无重复。完成路径静态计费为1＋56×8＋56=505，共享C09H的5,000硬限，专项上限512。

本轮UID999共享intent读取、Root私有对象DAC/ACL、原子发布、STOP_REQUEST、CLOSED拒绝、ready/RPC/waitpid有限回收及8项变异均未启动；实际结果、退出码、延迟和检出数为null。Root额外顺序探针启动数0。

动态工作由静态准入阻断，真实权限/停止修复继续待完整验收。继承TCB范围为Root父协调器、scheduler、外部停止器及最多一个顺序凭据探针，位于Payload slice外，资源单独登记。Payload父4tasks与每进程AS1GiB合同保持。

[库存](evidence/FROZEN_TEST_INVENTORY.json)；[源摘要](evidence/FROZEN_HASH_CHECK.json)；[准入](BATCH09_STATIC_ADMISSION.md)。
