# 原生seal、自动收尾与行政封存

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**真实native ZIP已生成并通过44项逐流校验；冻结host自动行政收尾失败。本轮研究证据包另行行政封存，自动性质保留失败。**

|路径|实际裁决|
|---|---|
|原生seal|NATIVE_SEAL_COMPLETED：真实运行对象齐备，自动原生包44项manifest/45 ZIP entries，CRC/逐流SHA/当前原件均匹配|
|较早原生适用性记录|pt_seal_disposition在67.175611912记NATIVE_SEAL_UNRESOLVED/T0=UNRESOLVED，属于当时关闭仍UNKNOWN的原始分类，原件保持|
|后续native manifest|sample67.382156380；此时最终内部关闭记录67.371083714已confirmed；原生包SHA见下表|
|host自动post-exit|确实调用1次，0.222965900秒返回1，顶层import boot_continuity触发ModuleNotFoundError|
|自动行政状态|原STARTUP_FINALIZATION.json保持ADMIN_EVIDENCE_UNRESOLVED、NATIVE_SEAL_UNRESOLVED；没有startup_snapshot/自动行政manifest/ZIP|
|研究行政收尾|在只读角色空审计后导出46 native原件、51冻结文件，连同原始双流、journal、授权、报告另建PTA_EVIDENCE.zip；分类为显式行政保存|

原生ZIP SHA-256：`16d0fc022ec9cdfb293ce8d44046e7124059589699a1bd31d58eb958a69e6f72`，89,300字节。[独立文件完整性校验](evidence/NATIVE_SEAL_VERIFICATION.json)仅读取原包，生产checker/测试/oracle重跑0。native成功仅表达对应快照的产物完整性，host失败与全链验收缺口继续保留。

自动host记录active返回UTC10:19:59.307345，post触发10:19:59.327527。独立停止服务退出由guest journal在67.405716记录；guest UTC标记约10:19:59.412522。两侧时钟关系缺少专用校准，避免把它们相减作为精确退出后延迟。因果上host只等待active入口结束，停止服务为独立systemd服务；完成屏障应以实际受控角色审计及有界收敛为依据。

本次自动收尾在导入阶段失败，行政文件/manifest落盘时间均为null，收尾退出码1；未手工重放该命令或调用finalize。直接脚本使用`-I -S -B`，sys.path缺少同目录兄弟模块路径，startup_lifecycle.py:11的顶层import失败。下一静态修复须保持原隔离参数和摘要验证，并审查独立服务的退出屏障。

原MRA的NATIVE_SEAL_FAILED、退出125、内部UNKNOWN及行政归档结果完整保留；本批的completed状态只属于batch11。

[自动原始结果](evidence/STARTUP_FINALIZATION.json) · [自动stderr](evidence/STARTUP_POSTEXIT.stderr.raw) · [原生核验](evidence/NATIVE_SEAL_VERIFICATION.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
