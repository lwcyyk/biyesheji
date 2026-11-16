# batch06 独立动态执行申请（当前尚未授权）

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

申请仅绑定RootIPC-static-1/r4及下列实际hash。batch05持续CLOSED，R37,293与原窗口/错误证据保持；batch06未创建。当前RootIPC-Fix专项授权覆盖静态修复，本文件为下一动态阶段的可审阅申请材料。

|锁|SHA-256|
|---|---|
|static_manifest.json|f47f15c1bd41c037200203864199c062027ebf2f708ae9e46fd601c382400e95|
|execution_lock.json|6da1da1cc5d89ccfb9b9f5cf615dc47398784114b5f3cc6189b4714646e8a2e8|
|root_ipc_contract.json|0a26a1a3c7d6491bc85a781145ab53672946ec46174a17c445cfeacb6850fe77|
|c09_contract.json|3e51bdb78d6047f22873eb7594001d77b2b21298c53e363d9c9e3e3c2e2495a3|
|safety_contract.json|28bd92be7541e959f8048de5719cb4473196459c90f47a2f6deb421a3b340203|

请求接受：原Root父协调器/scheduler及外部停止器TCB；新增56项Root权限/停止回归；最多1个顺序降权探针子进程（当前既有UID999/GID989与nobody65534/GID65534，AS≤1GiB、无新账户）；Root私有目录及受控发布；原C00–C12、C09H34、S34、门17和全部资源门后同批自动F1→F4。外部Root管理/测试开销另列，payload条件性4GiB与4 tasks范围保持。

未来准备命令（当前执行0）：

```text
/usr/bin/install -d -m 0750 -o root -g dcl-r6 /var/lib/dcl-r6/batch06 /var/lib/dcl-r6/batch06/inputs /var/lib/dcl-r6/batch06/reports
/usr/bin/install -d -m 0700 -o dcl-r6 -g dcl-r6 /var/lib/dcl-r6/batch06/out
/usr/bin/install -d -m 0700 -o root -g root /var/lib/dcl-r6/batch06/inputs/root_private
/usr/bin/install -m 0644 -o root -g root /var/lib/dcl-r6/ri01/inputs/dclr6batch06.slice /etc/systemd/system/dclr6batch06.slice
/usr/bin/systemd-analyze verify /etc/systemd/system/dclr6batch06.slice
/usr/bin/systemctl daemon-reload
```

随后安装新授权原文为`inputs/BATCH06_AUTHORIZATION_TEXT.txt`及Root:989/0640的有效执行回执；[模板](evidence/BATCH06_AUTHORIZATION_TEMPLATE.json)尚缺明确批准与授权原文hash，无法直接启动。预检核Python3.12.3、32关键工具/1224树、当前boot、全部44文件、UID/GID/补充组、目录metadata/ACL/同设备、当前systemd/cgroup及冲突/残留。发现漂移停止，不修改锁后沿用许可。

唯一首次入口：

```text
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ri01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch06
```

仅在真实C09当前有效Root成功交接后，同窗一次恢复：

```text
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ri01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch06 --resume
```

全冻结argv与17-unit journal命令见[执行锁](evidence/execution_lock.json)。建议启动模式为完整条件链，避免C12之后重复申请同范围许可：预检→C00–C08→C09H34/Root重算→IPC56逐项及完整独立审查→真实C09持久ACK/waitpid/fresh-read/唯一分类→原窗一次恢复→C10–C12→S34/Root原始重算→17负向门→RESOURCE_GATE_PASS→F1→F4→关闭/父最终封存。缺少任何IPC/C09/C/S/门证据均阻断FORMAL。

资源保持总访问1,000,000、总窗1,800秒、T0+1,740提前停止、校准300秒/100,000、每payload进程AS1GiB、父slice4tasks。IPC完成路径505、硬限512，和原C09H共同完成上界2750≤5000；完整校准硬访问上界62034保持。新增目录屏障/进程与Root普通退出记录的实际耗时未测量；窗口不足即首次失败停止，当前没有提出扩窗。

下一运行首个关键失败立即停止后续、保存原件、关闭/清空并封存；重试、退款、重置账/deadline、放宽阈值、恢复CLOSED和自动下一批均禁止。成功与预期故障须由独立raw oracle接受；仅exit23或PASS字段无法通过。

本申请未覆盖F2/F3、Casdoor、T1–T4、真实账户/凭据、无关单位/系统权限变化、依赖安装、误副本处置或外发。D1/强G原条件保持，严格分离0、IMPLEMENTATION_GATE=CLOSED。
