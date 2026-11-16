# CalDiag授权与执行锁

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

本次用户原文明确批准方案B=CALIBRATE_S1S9_ONLY，使用申请中尚未建立运行窗的batch09-r1身份。原batch09旧记录是静态准备失败，本次建立新的动态实例；旧工件和旧锁保持。实际控制路径为DCL-R6-B09-Supplement/authorization/batch09-r1，报告与当前新增证据保存在本目录。

|对象|实际绑定|
|---|---|
|manifest|c7bed9528ea4a6ada08882d02be23dd37c62e8ee79fbb70a9445ddcc361ea127|
|execution_lock|fcc70f0d78aefc1ccc1fcc96489a3984417c6b4b7f203c78162c910b64746b81|
|授权原文SHA|c366f2a743ca03dc2b2dce34e35fd010592ec753a780a18ede967ba77537ed62|
|实际回执SHA|714e36476673bea9644e233f07dc588698207413187407b7ce43640ec6283a98|
|boot_id|55ac71b2-e2c9-4e7b-9c94-e49d7082d8f4|
|Root owner|PID4259/start135655，跨exec及内部恢复尝试保持|
|Linux源/活账|/var/lib/dcl-r6/cr09 / /var/lib/dcl-r6/batch09|
|T0/deadline/stop_at|1357.752228527 / 3157.752228527 / 3097.752228527|
|scope|CALIBRATE_S1S9_ONLY；Calibrate_only=true，Full=false|

42份冻结文件及28程序在host核验通过，41份Linux文件逐项部署/摘要/Root元数据及原生语法核验通过。当前CPython3.12.3、工具/stdlib树、systemd、kernel、UID999/GID989、cgroup和单位资源由冻结单会话预检fresh核验；原始命令和双流完整保存。host入口只设置PYTHONDONTWRITEBYTECODE=1保护冻结工作区，原生argv保持-I -S -B。

预检PREFLIGHT_PASS，同boot同PID exec及一次认领通过，C00取得实际PASS。实际入口调用1、允许的同父内部恢复尝试1、成功恢复准入0。F1/F4批准位false，模型执行0。首次关键失败后保留原T0/账，追加冻结关闭和封存函数调用属于本次停止授权，运行case新增0。

[授权原文](evidence/TASK_REQUEST.txt) · [实际回执](evidence/execution_authorization.json) · [入口计划](evidence/ACTIVE_ENTRY_INVOCATION.json) · [源/范围准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [原生部署](evidence/DEPLOYMENT_RESULT.json)。
