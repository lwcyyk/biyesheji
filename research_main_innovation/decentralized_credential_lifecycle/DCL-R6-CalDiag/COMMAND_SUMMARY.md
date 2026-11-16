# CalDiag实际命令与停止范围

实际执行冻结host入口一次：

```text
C:\Program Files\Python314\python.exe -X utf8 D:\毕业设计\DCL-R6-isolated-verification\cr09\host\windows_entry.py --activate
```

该入口使用锁内唯一前台WSL argv进入/var/lib/dcl-r6/cr09/src/boot_continuity.py，随后same-PID exec选择带--calibrate-only的冻结B命令。原始argv、开始/退出、双流和native事件均保存。host环境只设置PYTHONDONTWRITEBYTECODE=1，源文件字节保持。

行政WSL调用共4次：部署41份Linux文件；入口exit125后的初次导出/审计；在发现自动关闭缺口后调用原冻结guard.stop_tree/seal关闭本批；最终独立快照/角色空审计。加上唯一active入口，共5次WSL调用。当前boot绑定与动态资格来自active单会话内部fresh验证，部署/事后读取的boot只作对应阶段观察。

补充关闭只设置本批终止标记、停止本批资源并封存，原T0、deadline、stop_at和counter/journal/intent SHA保持，新增case=0、重跑=0。它没有建立新的模型/参考运行，也没有重新激活任何窗口。初始607文件快照和未关闭事实保持，最终另存612文件快照。

host分析只读取原件、时间、摘要及预算格式，目标oracle和业务语义重放0。原生已完成套件的独立原始审核均在运行时收费执行；S34/门18及完整资源审核仍未运行。原始NAT localhost代理提示作为stderr前缀保留，首个关键失败为后续UNREVIEWED_MANAGER_FAILURE。

源码、判据、权限及资源上限修复0；主动WSL重启/关闭、其他发行版/Docker、安装下载、外发、误路径执行和自动下一批均0。F1/F4未启动。各行政脚本、完整输入代码及结果见evidence/ADMIN_COMMAND_PLAN.json与对应commands原始流。
