# M5 复核、复现和清理

正式 batch01 只执行一次，十二项均通过。下列重新执行命令使用新目录和新批次编号；新结果单独计数。源码和脚本保存在 source_frozen，当前仓库也保留同一新增实现。运行依赖 Windows、现有 Python 3.12 及 cryptography 50.0.2；本机支持无提升权限的 CreateRestrictedToken/CreateProcessAsUserW。

## 无新采样的复核

```powershell
$report = 'D:\毕业设计\mainline_agent_isolation_v1'
$py = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH = "$report\source_frozen\src"
$env:PYTHONDONTWRITEBYTECODE = '1'
& $py -B -X utf8 "$report\source_frozen\scripts\score_agent_isolation.py" --root "$report\batch01"
& $py -B -X utf8 "$report\source_frozen\scripts\verify_agent_isolation.py" --root "$report\batch01"
```

评分写入独立最终结果；ACL 核验只读并打印实际 SDDL。源散列可按 SOURCE_LOCK.json 核对，运行库散列按 batch01/RUNTIME_MANIFEST.json 核对。

## 从新目录建立全部环境并运行

```powershell
$batch = 'D:\毕业设计\mainline_agent_isolation_v1\reproduction_NEW_ID'
& "$report\source_frozen\scripts\Start-M5Isolation.ps1" -BatchRoot $batch -AuthorizationId 'M5-LOCAL-REPRODUCTION-NEW-ID' -PythonExe $py
& $py -B -X utf8 "$report\source_frozen\scripts\score_agent_isolation.py" --root $batch
& $py -B -X utf8 "$report\source_frozen\scripts\verify_agent_isolation.py" --root $batch
```

BatchRoot 须不存在。入口创建本批三项 loopback TLS 服务、两个代理权限域和可信 R 服务令牌，生成全套合成值与新证书；无 SAM 建户，无原生 AS/RP 调用。能力配置、密钥及权威数据在 cache 回滚范围之外。初始化失败记录 BLOCKED_ENVIRONMENT 或 ABORTED，保留实际操作名与错误码。

加入 -Development 参数只运行开发探测，不执行正式十二场景。全部环境由当前可信配置用户创建；原始 Python 安装和已有目录 ACL 保持原状态。

## 开发回归

在 D:\毕业设计\auth-lifecycle 下运行 unittest discover -s tests -v。将 ONLINE_STATE_TEST_ROOT、NATIVE_TEST_ROOT、RECONCILIATION_TEST_ROOT、UNIDENTIFIED_TEST_ROOT、M5_TEST_ROOT、AUTH_L0_RESULT_DIR、TEMP、TMP 指向本轮新建开发目录；AUTH_L0_RESULT_DIR 与 TEMP 先建立。PYTHONPATH 指向仓库 src，PYTHONDONTWRITEBYTECODE=1。全仓结果见 FULL_REGRESSION.log，M5 专测见 DEV_TEST_01.log。历史 native 单元测试采用合成响应和 mock。

## 限域清理

```powershell
& $py -B -X utf8 "$report\source_frozen\scripts\cleanup_agent_isolation.py" --root $batch
# 可选择清除本批复制的运行库，保留源码、状态与审计：
& $py -B -X utf8 "$report\source_frozen\scripts\cleanup_agent_isolation.py" --root $batch --remove-runtime
```

正常入口和异常退出均尝试按持有的真实进程句柄终止并等待。额外清理脚本逐项核对 OWNED_PROCESSES 中 PID、创建时间和精确映像路径；复用 PID 会跳过。删除前解析绝对路径，目标只允许本批 assets/python。文件和证据目录保留其受保护 DACL。无机器级权限、账户或系统服务需要还原。
