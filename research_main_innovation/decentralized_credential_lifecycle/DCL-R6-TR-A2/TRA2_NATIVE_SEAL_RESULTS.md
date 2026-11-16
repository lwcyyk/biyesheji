# native seal真实执行与独立核验

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**TR-D5=PASS_DYNAMIC，NATIVE_SEAL_COMPLETED。** 原停止器等待后，真实终态输入完整、活动拒绝证明保存，原生manifest/ZIP实际生成。

pre-native review sample102.254985296、active拒绝102.255073341；manifest sample102.273823167。sealer为当前Root协调器，直接waitpid和角色/组证据在原件中；G.seal按原格式返回ZIP摘要，active进程最终exit0。单独的精确G.seal函数入口/返回时刻未打点，实际receipt/产物/自动审计提供区间与结果。

原生manifest233项，ZIP234 entries，439089字节。CRC、全部成员bytes/SHA、内嵌manifest原字节与当前独立导出均一致。ZIP SHA-256：`bf67679ccb503a2e00929cb39097afacd18e74c5d2ca7e06e3ddbf809300e461`。

Native输入包含真实window、3133最终账及journal、CLOSED、phase/version、Source/锁/回执、直接waitpid/停止记录，以及Root私有只读review。review中的evidence_digests与归档及最终导出精确一致；没有Source/账修复或手工seal重放。

原PFA native UNRESOLVED保持，旧TR-A无窗口NOT_APPLICABLE保持。本批native完成只证明当前原件封存，不升级内部UNKNOWN、来源可信等级或资源总资格。独立行政结果另列。

[完整逐流校验](evidence/NATIVE_SEAL_VERIFICATION.json) · [终态输入比对](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json) · [235项原件导出锁](evidence/NATIVE_EXPORT_LOCK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
