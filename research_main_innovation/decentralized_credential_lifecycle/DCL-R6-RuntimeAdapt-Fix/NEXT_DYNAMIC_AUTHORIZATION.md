# 独立TR-A2有限动态申请

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

**REQUEST_ONLY，当前业务动态许可0。** 建议下一交付DCL-R6-TR-A2，唯一申请RuntimeAdapt-static-1/r1、全64项/44程序；manifest `738eb2982953971f94019b913f6b302808f9b7a8d29e784038e8e6babb50de89`，execution_lock `691f2503f2db6906552241692db0b27ec6a982a7c738839d99f3cd93f3729da6`。

申请前提：明确接受现有Root/dpkg数据库/keyring信任及无并发特权运行时更新的原TCB条件，或先补齐可信8.12包payload证据。若不接受或关键来源发生变化，维持RUNTIME_PROVENANCE_UNRESOLVED并停止，不把模板当批准。

规划独立batch14-r1，scope=PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START，旧batch13不恢复。未来部署62项Linux文件、Root元数据/source-only，不创建pyc；fresh核当前Python3.12.3、kernel/systemd、三ELF/aliases/Build-ID、精确包/目录/配置、当前maps和全部原runtime pin。

```text
python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\ra01\host\windows_entry.py --activate
```

host环境PYTHONDONTWRITEBYTECODE=1，唯一active argv：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ra01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch14
```

顺序：新运行时双侧预检/同PID sealed认领 → 一次初始化/ARMED/WORK → C00实际资源及映射 → PT64 → PF48 → TR40 → RA32 → 正常CLOSED/原回收 → terminal只读/活动守卫拒绝 → native真实结果 → 自动行政/独立校验。

匹配器5秒有界只读，原Guard继续重新核实际字节/当前映射；服务前及服务内、seal与admin重查。发现任何关键hash/path/pkg/Build-ID/预加载或映射漂移即失败。所有点仍无法提供path→exec原子保证，当前TCB条件与后续映射记录须审查，不声称历史扫描永久有效。

原资源合同保持：1000000访问/1800秒、校准100000/300秒、预T0120秒、stop_at=T0+1740、AS1GiB/父TasksMax4。新增RA545完成/768硬，正常A3133完成/4417硬，完整68498≤100000。性能全链UNRESOLVED，实际观测额外IO/文件容量必须核验，硬界不扩。

自动post精确目标保持机制：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/ra01/src/admin_postexit.py --post-exit-export
```

原AS1GiB/单次30秒先于源码/目标模块装载，加入只读身份核验，host32秒wait与35秒总回收、256文件/32MiB界保持。请求必要冻结当前批次关闭后备和故障保全，真实使用时独立登记，不能冒充自动成功。

未来回执需RuntimeAdapt诊断和provenance_assumptions显式批准位true、两项新合同摘要、既有TR/PF/PreT0/RootIPC/单会话兼容位齐全，真实用户原文SHA与最终两锁绑定。Full/MR/预窗注入false。当前所有位false、实际回执未创建。

首次关键失败立即停止发放、原流程关闭/适用seal/admin保全；禁止现场修改、重跑、预算/T0重置或第二免费窗。A2结束全部关闭，不进入MR/C09/C01–C12/S34/门18/F1/F4。即使A2通过，完整资源资格仍需新的独立许可与身份。

[未批准模板](evidence/TR_A2_AUTHORIZATION_TEMPLATE.json) · [运行时身份与规则](evidence/SOURCE_FINAL_R1/inputs/runtime_identity_contract.json) · [真实执行锁](evidence/SOURCE_FINAL_R1/inputs/execution_lock.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
