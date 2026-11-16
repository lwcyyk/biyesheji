# B09执行锁精化

Material Passport：B09-AdmissionFix-static-1/r1；独立静态冻结；2026-11-12；部署/启动0。

新包42份文件：27 Linux程序、1 Windows入口、14输入；原36份锁及历史阻断证据保持。source-only，无pyc。原源码、修改后源码、全量diff与逐文件摘要分别存于SOURCE_BEFORE、SOURCE_AFTER、FULL_DIFF.patch、STATIC_WORKSPACE_LOCK.json。

|锁|SHA-256|
|---|---|
|static_manifest.json|c7bed9528ea4a6ada08882d02be23dd37c62e8ee79fbb70a9445ddcc361ea127|
|execution_lock.json|fcc70f0d78aefc1ccc1fcc96489a3984417c6b4b7f203c78162c910b64746b81|

新锁绑定身份、ledger输入、28程序、原生工具/stdlib树、slice和全部argv。依赖按“程序/合同→manifest→execution_lock→未来授权”冻结，manifest保持既有有向依赖规则，执行锁及自身排除循环。sealed ticket保存实际回执SHA；回执正文无需包含自身SHA，后续Guard用复制后的原字节重算核对。

两个未来scope独立选择：A=CALIBRATE_S1S9_THEN_F1_F4，B=CALIBRATE_S1S9_ONLY。二者使用同一前台WSL调用与同进程exec，bootstrap在验证回执后从冻结的launch_commands_by_scope选择精确argv；B带--calibrate-only，真实C09后仍允许同父进程内一次受验证恢复，校准完成即关闭封存。FORMAL入口继续只接受A。模板的批准位全部false，原文SHA尚空，真实运行回执尚待产生。

新公共GATE_LEDGER_QUALIFICATION由Root发布，绑定输入、subject、独立oracle、当前batch/boot/T0/源/执行锁及原件摘要；原件存Root私有目录。资格门逐项核18个case，Root重新读取原件，FORMAL核Root保护证书及其摘要。UNRUN/缺件/失败/变异未检出均使实际资格失败。

资格发布后增加原RANGE截止复核，确保RANGE与RESOURCE收据的发布成本属于原300秒资格窗口。窗口、访问、AS和任务上限保持原值。

host未来入口：

```text
python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\cr09\host\windows_entry.py --activate
```

唯一内部WSL调用：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/cr09/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch09
```

本轮以上命令执行0。完整准备、payload、worker、停止和日志argv均在[新执行锁](evidence/SOURCE_AFTER/inputs/execution_lock.json)。当前准备阶段batch09旧锁保持；新r1需要独立版本和scope授权。A/B只能选择其中一次建立新运行窗；B关闭后，其后任何完整运行须重新准备独立身份/锁及相应授权。
