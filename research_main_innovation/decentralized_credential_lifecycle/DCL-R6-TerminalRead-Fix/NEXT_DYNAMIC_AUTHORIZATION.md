# 下一独立有限动态验收申请

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

**REQUEST_ONLY；当前动态授权0。** 唯一申请目标TerminalRead-static-1/r1；59项/41程序；manifest `d2a6f4f58d7afd5a14287cea1c86da76d137e80dea2b64b35535fd2b145f7aac`，execution_lock `43f362a064209ff8359e410301017741d787cb3acd272d40c75d447820671878`。

规划batch13-r1，scope=PT_STARTUP_DIAGNOSTIC_ONLY、startup_probe_mode=NORMAL_START。预检fresh核当前Ubuntu-24.04/Python3.12.3、boot、源/工具摘要、UID/GID/Root元数据/cgroup/实例全新；原batch12保持CLOSED。未来只部署57项Linux源/输入，source-only无pyc。

```text
python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\tr01\host\windows_entry.py --activate
```

host环境PYTHONDONTWRITEBYTECODE=1。唯一active Native argv：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/tr01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch13
```

顺序：原单会话/同PID/认领 → 正常预窗/一次intent/T0/counter → ARMED/WORK → C00 → 全量PT64 → PF48 → TR40 → 正常CLOSED/原停止与waitpid → 原停止器等待 → 终态只读window/预算/phase/退出审查 → 原活动接口拒绝CLOSED并保存原异常码 → native seal/manifest/ZIP → 原自动行政入口/归档。

只读每次5秒、共享锁每次最多2秒/512尝试，原journal读取最多32MiB/32768字节行/2*原cap+1次（含EOF探测），既有native包最多257成员/解压总32MiB。均为只读行政工作，不更改R或原deadline；当前native生成仍要求同boot和原窗口尚有效。历史审查模式不发放任何生成或执行资格。

访问预算：TR681完成/960硬；正常A2588完成/3649硬；含新增测试完整硬67730≤100000。维持总1000000/1800秒、校准100000/300秒、预T0120秒、stop_at=T0+1740、单进程AS1GiB、父TasksMax4。新Reader/归档性能和原finalizer文件容量须实测；不足时停止并保留未决，原硬限不扩。

自动post命令保持机制，仅迁移固定源namespace：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/tr01/src/admin_postexit.py --post-exit-export
```

原AS1GiB/单次30秒alarm先于模块加载、host32秒wait及35秒总回收、256文件/32MiB行政上界保持。请求必要的本批冻结关闭后备与原件保存，真实调用时与自动成功分开；禁止人工seal/归档冒充自动性质通过。

未来回执绑定最终两锁、terminal合同、真实原文及TerminalRead显式批准位，既有PF/PreT0/RootIPC/单会话兼容字段按schema齐备；Full/MR/预窗77注入false。当前模板全部批准位false，实际授权文件尚无。

首次非预期关键失败停止发放、保留原件和首错、自动关闭/适用封存/行政收尾；UNKNOWN保持，必要后备单列。没有现场改码、重跑、预算重置、免费第二窗或自动下一批。即使A通过，也只关闭本批，不进入MR/C09/C01–C12/S34/门18/F1/F4。完整资源与模型仍需新独立许可。

[未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json) · [真实argv锁](evidence/SOURCE_FINAL_R1/inputs/execution_lock.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
