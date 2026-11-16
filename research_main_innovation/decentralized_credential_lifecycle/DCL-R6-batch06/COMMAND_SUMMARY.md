# batch06 实际命令与双流索引

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

19条native命令按调用前登记精确argv，之后保存真实UTC区间/退出/原始双流与SHA。所有native exit0；最终业务准入结果由same_boot谓词单独判为PREFLIGHT_FAILED，管理包装进程exit0无法替代资源门结果。

|编号/精确argv|分类|exit|宿主墙钟ms|用途|
|---|---|---|---|---|
|[01](<evidence/commands/01.result.json>)|PREFLIGHT_READ_ONLY|0|2632.105|Verify1326 unique Linux frozen/runtime/historical hashes before initialization|
|[02](<evidence/commands/02.result.json>)|PREFLIGHT_READ_ONLY|0|254.801|Read current runtime, identity, files/ACL, historical closed ledgers and process absence|
|[03](<evidence/commands/03.result.json>)|PREFLIGHT_READ_ONLY|0|262.298|Read live systemd Version|
|[04](<evidence/commands/04.result.json>)|PREFLIGHT_READ_ONLY|0|310.876|Read batch06 unit conflicts before preparation|
|[05](<evidence/commands/05.result.json>)|PREFLIGHT_READ_ONLY|0|322.766|Read failed units against frozen launcher allowed set mnt-e.mount|
|[06](<evidence/commands/06.result.json>)|B06_FROZEN_PREPARATION|0|6036.426|Frozen batch06 preparation1: exact execution_lock argv|
|[07](<evidence/commands/07.result.json>)|B06_FROZEN_PREPARATION|0|258.470|Frozen batch06 preparation2: exact execution_lock argv|
|[08](<evidence/commands/08.result.json>)|B06_FROZEN_PREPARATION|0|229.379|Frozen batch06 preparation3: exact execution_lock argv|
|[09](<evidence/commands/09.result.json>)|B06_FROZEN_PREPARATION|0|256.481|Frozen batch06 preparation4: exact execution_lock argv|
|[10](<evidence/commands/10.result.json>)|B06_FROZEN_PREPARATION|0|278.361|Frozen batch06 preparation5: exact execution_lock argv|
|[11](<evidence/commands/11.result.json>)|B06_FROZEN_PREPARATION|0|343.294|Frozen batch06 preparation6: exact execution_lock argv|
|[12](<evidence/commands/12.result.json>)|B06_AUTHORIZATION_INSTALL|0|257.475|Install current explicit batch06 BATCH06_AUTHORIZATION_TEXT.txt|
|[13](<evidence/commands/13.result.json>)|B06_AUTHORIZATION_INSTALL|0|250.753|Install current explicit batch06 execution_authorization.json|
|[14](<evidence/commands/14.result.json>)|PREFLIGHT_READ_ONLY|0|228.094|Read installed frozen parent limits; require inactive before T0|
|[15](<evidence/commands/15.result.json>)|PREFLIGHT_READ_ONLY|0|210.013|Final boot, metadata/ACL, authorization and no-window/no-counter checks|
|[16](<evidence/commands/16.result.json>)|POSTFAIL_READ_EXPORT_ONLY|0|6879.044|After preflight failure: read-only Linux metadata/process audit and byte export to approved host workspace|
|[17](<evidence/commands/17.result.json>)|POSTFAIL_READ_ONLY|0|240.385|Postfailure parent unit state; no stop/start action|
|[18](<evidence/commands/18.result.json>)|POSTFAIL_READ_ONLY|0|227.439|Postfailure exact batch06 unit listing|
|[19](<evidence/commands/19.result.json>)|POSTFAIL_READ_ONLY|0|232.250|Frozen exact17-unit current-boot journal after preflight stop; no runtime case started|

命令1–5为基础预检，6–11为冻结准备，12–13安装授权，14–15为最终预检；失败后16–19仅审计/导出。所有目标Launcher、resume、controller、watchdog、external-stop和模型角色调用0。WSL localhost代理提示按原stderr保留；未观测的交接/模型输出没有补写。
