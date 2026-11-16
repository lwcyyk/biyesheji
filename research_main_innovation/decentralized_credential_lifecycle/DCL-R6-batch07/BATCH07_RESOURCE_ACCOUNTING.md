# batch07持久预算与时间核算

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

本批已初始化持久账：**R=0/1000000**，24字节BRNGv001 counter、COMMITTED/after0/cap1000000 intent对应。无实际reserve事务，journal尚未创建，记录数/事务数0；这一缺件符合首次语义访问之前的状态。独立行政parser没有导入预算核心。

运行boot=060a08fc-fceb-48ff-a264-50c34312f97a，T0=73.768774900，deadline=1873.768774900，stop_at=1813.768774900；差值分别1800和1740，原窗口只初始化一次。没有模型/测试语义访问、退款、重置或resume。

|时间/资源|实际|
|---|---|
|闭合boottime|74.078122459 / T0+0.309347559|
|首次组空|T0+0.327163166；close→empty 0.017815607s|
|父waitpid|T0+0.345387720；raw32000/exit125|
|父seal前|T0+0.354242602|
|Windows活动调用|1.803443600s，包含预检/回传；独立时钟域|
|charged peak/pids|782336B；观测1/max4；精确RSS与Root峰值N/A|
|冻结访问/时间|总1000000/1800；cal100000/300；共同5000；BC481/512；完整cal62034|
|实际测试与模型|语义访问0，搜索0，原判据未放宽|

23个native普通文件、32个最终程序/输入副本已保存。原生自动seal实际完成：21行manifest、22个ZIP条目，SHA `84c174da72c3f826941fe479a5cd3e637208ab54f97e017f94dc941133856abf`，逐流/逐文件差异0。socket仅保留类型/身份/mode元数据，不复制成普通字节文件。

账内容初始配对核验为PASS_INITIALIZED_ZERO_ACCOUNTING_ONLY；关闭后的账无法重新授权。历史batch05/04/02的R37293/37021/32191原件保持，47误副本及blocked by policy继续只读保留。

[核算JSON](evidence/RESOURCE_ACCOUNTING.json)、[native seal核对](evidence/NATIVE_ZIP_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。
