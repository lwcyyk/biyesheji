# 本批未决边界与反例范围

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**本批未观察到非预期关键执行失败。** 正常WORK/C00、184模型检查、终态读取、活动拒绝、native和自动行政均取得对应原件；下列边界继续单列。

|编号|实际范围/限制|
|---|---|
|A2-PROV|缺8.12新.deb独立payload再现，TCB-conditional来源结论保留；用户显式批准位不变成无条件来源证明|
|A2-IDENTITY|当前Root/Payload磁盘/自身映射相符；没有path→exec原子或阻止未来特权更新的证明|
|A2-INTERNAL|正常路径缺mr_close_state，internal UNKNOWN原件保持，未用封存成功升级|
|A2-NEGATIVE|184项为明确标记的合成模型输入；系统库、真实预算、Root state或其他单位未被破坏做OS故障|
|A2-TELEMETRY|锁/逐文件IO/完整case和import起点、行政Live RLIMIT等细粒度字段部分未发出；不从其他PID或旧批次补值|
|A2-RESOURCE|仅C00和最小前缀资源观测，未跑完整校准和完整300秒链|

pre-native review中的native_status UNRESOLVED准确反映当时尚未打包，后续Native和自动结果COMPLETED属于新时点事实；没有倒填或更写该review。旧TR-A/PFA失败及UNKNOWN全部保持。

本批源码/系统库修改、安装/重锁、测试重跑、手工seal、后备清理和免费窗口均0。下一步可准备独立MR有限验证申请及必要新身份/摘要，当前不自动启动。

[原生包完整性](evidence/NATIVE_SEAL_VERIFICATION.json) · [来源/映射回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json) · [终态比对](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
