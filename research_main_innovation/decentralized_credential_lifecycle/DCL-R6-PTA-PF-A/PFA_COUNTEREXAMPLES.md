# 新缺口、首个失败验收项与证据边界

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**运行与模型检查全部完成；首个未满足的验收项是正常CLOSED之后的native seal。** 实际最早明确分类原件为131.332716174的pt_seal_disposition=UNRESOLVED。完整A裁决独立于active exit0。

|登记|实际证据与结论|
|---|---|
|PFA-SEAL-1|CLOSED先建立；终态只读phase guard仍经G.state读取期限，触发其stopped拒绝；适用性层捕获后native UNRESOLVED，底层原生包未创建|
|PFA-OBS-2|冻结版本没有逐次锁acquire/release、竞争计数和各次读判定；最终版本/工作成功保留，锁故障覆盖保持条件性|
|PFA-OBS-3|Root行政post原生成功并有UID/PID/deadline，精确导入时刻、Live RLIMIT、完整sys.path/cwd/cgroup字段缺失，未用Payload或其他PID补值|
|PFA-CLOSE-4|正常路径没有mr_close_state，内部UNKNOWN保持；CLOSED/组空不能推导全部持久状态成功|

PFA-SEAL-1是冻结新辅助路径的活动态/终态前提混用。相关BATCH_STOPPED异常被源码catch，没有独立记录该异常的traceback，报告保留这一来源差异。没有重现旧的PT_RUNTIME_PHASE_DRIFT或ModuleNotFoundError。

本批不现场修复、重跑、手工seal或追加免费预算窗口。自动行政证据完整保存，原生包UNRESOLVED、内部UNKNOWN分别保持。旧batch11的漂移精确值UNKNOWN及native成功、旧MRA失败、CalDiag真实C09与旧账都保持。

[原生封存缺口](evidence/NATIVE_SEAL_GAP.json) · [观测字段映射](evidence/FIELD_MAPPING_AND_UNKNOWN.json) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
