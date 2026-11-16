# batch08最小阶段持久预算与退出核算

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

最终 **R=450/1000000**；450组PREPARED/COMMITTED完整配对，900行journal与counter/intent after450一致。原C00 probe访问1＋获准64阶段449=450。独立行政parser逐笔核before/after/amount/status，差异0；退款/重置/resume均0。

run boot=0cc7ff50-243e-41d0-bf3f-ba45b3f95695；T0=49.529730421、deadline=1849.529730421、stop_at=1789.529730421，差值1800/1740，初始化1次。关闭=59.797290773，T0+10.267560352；首次组空T0+10.275995718，close→empty 0.008435366秒；普通父waitpid exit0/raw0。

Host单次活动调用15.407242400秒，包含预检、执行与回传，独立perf_counter口径。实际readiness wait返回区间约0.150–0.155秒，后续64账/写证成本都计入同一T0/300秒校准窗。未放宽14、300或1800秒。

原生自动seal实际完成：99行manifest、100个ZIP条目、199157B，SHA `3bd464f1b3a12916daa5b1ed46507133c6b2a5ea7bf5fcb76c03f33e2e2f6fdb`；101个native常规文件与36个冻结程序/输入导出完成，逐流差异0。旧socket仅保存类型/mode/身份，byte hash不适用。

全局cap及原CPY312/AS4条件不变；本轮额外Root探针进程0。观察charged peak43937792B、C00 startup观测3 tasks/父max4；精确RSS树峰值与Root峰值未采样。旧batch07 R0、batch05 R37293、batch04 R37021、batch02 R32191与原失败均保留。

最小阶段结束不授RESOURCE_GATE_PASS：BC40/RootIPC56/C09H34/真实C09/C01–C12/S34/门17/F1/F4全部未执行且未授权。本批CLOSED，无法改回执后沿旧窗进入Full。

[账核算JSON](evidence/RESOURCE_ACCOUNTING.json)、[原生seal检查](evidence/NATIVE_ZIP_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。
