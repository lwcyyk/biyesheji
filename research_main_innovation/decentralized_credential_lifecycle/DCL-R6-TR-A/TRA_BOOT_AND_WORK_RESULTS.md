# 原生启动、预检与WORK结果

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

**入口实际运行，正式启动停于PREFLIGHT_BEGIN；WORK/C00=UNRUN_PREFLIGHT_FAILED。**

实际Bootstrap为PID2271/start43611，boot ef808858-4c80-4fd8-ac74-25a41b5b99ef，PREFLIGHT_BEGIN sample436.167570765。boot_continuity.artifact_check检查当前文件时抛Rejected('BC_ARTIFACT_DRIFT:/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2')，active退出125。

原始stdout仅有PREFLIGHT_BEGIN，没有PREFLIGHT_QUALIFIED、ACTIVATION_REQUESTED_ONLY或ENTRY_VERIFIED。运行目录、service/slice安装、cgroup、claim、memfd激活能力、scheduler/stopper、T0、counter均未创建；主机授权文件和Linux源部署是已获批的前置行政准备。

基础只读环境核验只证明Python/kernel/systemd/身份等当时字段匹配，完整Native资格还需要全部运行时字节匹配。加载器失配先于准备命令与运行窗口，因此未进入C00八项资源检查。

[首错/抛出位置](evidence/FIRST_FAILURE.json) · [真实stderr](evidence/windows_entry.stderr.raw) · [真实stdout](evidence/windows_entry.stdout.raw)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
