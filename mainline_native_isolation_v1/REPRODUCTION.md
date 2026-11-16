# M6 复核与受控复现

本批两条轨迹已各执行一次；下列原生重新运行属于新采样，须另登记批次与授权。离线复核和零原生测试可使用现有受保护证据。

## 离线复核

```powershell
$r = 'D:\毕业设计\mainline_native_isolation_v1'
$py = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH = "$r\source_frozen\src"
$env:PYTHONDONTWRITEBYTECODE = '1'
& $py -B -X utf8 "$r\source_frozen\scripts\score_native_isolation.py" --case "$r\batch01\M6-01"
& $py -B -X utf8 "$r\source_frozen\scripts\score_native_isolation.py" --case "$r\batch01\M6-02"
& $py -B -X utf8 "$r\check_storage_and_audit.py" --root "$r\batch01"
```

前两项使用冻结独立评分规则，后项仅做存储/审计检查；均无原生请求。RSA私钥与权威密钥仅在当前可信评分用户下读取，输出为布尔、标识与摘要。完整秘密仍保留在保护路径。

## 零原生接线预检

```powershell
& $py -B -X utf8 "$r\launch_sanitized.py" --out "$r\preflight_NEW_ID" --authorization-id 'M6-ZERO-NATIVE-NEW-ID' --preflight
```

目标目录须不存在。合成签名材料、真实本地TLS/事务与受限进程被使用；所有AS请求在子进程中由固定FixtureOpener处理，网络原生请求0。既有 .runtime/l1 的管理凭据和数据库必须继续保持已授权收紧的ACL，原路径按只读访问核对。实际前后ACL备份随交付保留，不在复现时自动改动。

开发回归从auth-lifecycle目录运行unittest discover -s tests -v，令ONLINE_STATE_TEST_ROOT、NATIVE_TEST_ROOT、RECONCILIATION_TEST_ROOT、UNIDENTIFIED_TEST_ROOT、M5_TEST_ROOT、M6_TEST_ROOT、AUTH_L0_RESULT_DIR、TEMP和TMP指向新建测试目录，PYTHONPATH指向src。已有回归最终148/148，全部原生传输mock或合成。

## 新授权原生批次的命令模板

```powershell
& $py -B -X utf8 "$r\launch_sanitized.py" --out "$r\batch_NEW_ID" --authorization-id 'NEW-EXPLICIT-AUTHORIZATION' --preflight-evidence "$r\preflight_NEW_ID"
```

入口要求成功预检且源码与该预检一致。先持久生成220次预算与清理预留，再核验AS、创建专用组织/应用/两账户。环境差异或安全失败停止后续采样，关闭R/权威/适配器/代理并处理本批原生对象。普通入口、预算及profile位于auth-lifecycle的native_isolation模块和脚本中。

## 本地进程清理复核

```powershell
& $py -B -X utf8 "$r\source_frozen\scripts\cleanup_agent_isolation.py" --root "$r\batch01\M6-01"
& $py -B -X utf8 "$r\source_frozen\scripts\cleanup_agent_isolation.py" --root "$r\batch01\M6-02"
```

清理器只操作OWNED_PROCESSES登记且PID、创建时间与精确映像均匹配的进程；复用PID跳过。--remove-runtime仅删除该条轨迹assets/python副本，审计/源码/状态保留。本批原生账户、应用和组织已回读确认删除，后续离线命令不会再次发送清理HTTP。新的原生收尾应使用新批预算和其自己的登记对象。

封存证据及合成/真实材料密钥按可复核需要保留，目录DACL留在保护状态。源散列、规则、启动环境和授权分别为SOURCE_LOCK、M6_PREREGISTRATION、SANITIZED_NATIVE_LAUNCH和AUTHORIZATION_ADDENDUM。
