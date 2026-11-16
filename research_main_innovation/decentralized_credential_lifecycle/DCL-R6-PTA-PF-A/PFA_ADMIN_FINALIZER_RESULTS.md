# 原生自动行政收尾结果

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**固定源入口在原生环境成功加载并自动生成ADMIN_EVIDENCE_SEALED；PF-A6整体保留CONDITIONAL_PASS，资源/导入精细时点缺少独立回执。**

实际唯一post命令为：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pf01/src/admin_postexit.py --post-exit-export
```

Root actor1130/start13146，boot6b12daf8…，实际administrative_uid0；post exit0、WSL客户端reaped=true。固定源及模块origin核验已在成功路径执行，Source manifest/执行锁/当前回执匹配。模块加载没有重现ModuleNotFoundError。实际GID、cwd、完整sys.path、导入起始时点和post所在cgroup未单列记录，保持UNKNOWN。

冻结hash-bound主入口先调用setrlimit(AS1GiB)，建立唯一30秒alarm及deadline，再做source检查和load_target；原生post成功还经过继承timer/AS条件核验。administrative_deadline实际161.496699746；减30推得主入口参考时点131.496699746，audit sample131.528678948。该差值是控制流时段线索，live RLIMIT数值与具体导入起始时点没有独立日志。Payload的实际1GiB记录另属C00，不移作行政进程回执。

host在active返回后自动触发post，实际post3.890178100秒，少于30/35秒；原生组/角色只采样一次即空，没有等待竞争。导出157项原件，host行政manifest171项、ZIP172 entries，356682字节。逐流SHA/CRC及manifest字节一致；自动快照与独立只读导出157项均匹配。

自动行政ZIP SHA-256：`e4bb3cb9e66c179027d3d8bd2313fdeef14ba8d4d2d5bc5da10817b5d1da0c6b`。原始stdout/stderr完整入包，WSL代理提示保留原始混合编码字节。额外兜底归档0；后续研究ZIP只汇总已完成的自动包、原件和分析报告，未替代或重放自动finalize。

该行政包如实记录native UNRESOLVED和internal UNKNOWN。行政成功没有升级native状态，旧batch11自动post失败也保持。

[自动结果原件](evidence/STARTUP_FINALIZATION.json) · [逐流校验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json) · [字段映射](evidence/FIELD_MAPPING_AND_UNKNOWN.json) · [post原始双流](evidence/STARTUP_POSTEXIT.stdout.raw)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
