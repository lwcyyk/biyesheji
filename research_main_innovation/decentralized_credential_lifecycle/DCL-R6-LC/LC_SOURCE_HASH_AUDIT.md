# LC：源码与输入哈希审查

2026-11-10。Material Passport：ADMIN_CHECK/SOURCE_HASH_MATCH；原始摘要见[LC_SOURCE_LOCK](evidence/LC_SOURCE_LOCK.json)、[静态manifest](evidence/LC_STATIC_MANIFEST.json)。

|业务文件|SHA-256（v2/v3/host LC/Linux LC一致）|
|---|---|
|f1_model.py|5669c8486d00f56085ef1a69ad7b40c3fc328bd41ae1a8424f1cd68018911d35|
|f1_check.py|1ed89b7da8a03593d49cd91c409e161eb8a118584d8e066423feefbaf6e21645|
|f4_dp.py|a07194f1dbec98efc2932186777f5bdb084012e3d8b5784d9b3c27b6ecbb50c5|
|f4_reference.py|9d1fcbc5752bfe7c6cd0308fb06a838174834dfe0b2f23a75c352418c3047e2b|
|compare.py|3848301c699b5a25a284e5747bb37d38d61ddb144cf49e0506e3ea82a5b7244f|

只修改新lc01/src的guard.py、guard_probe.py、run_batch.py。三文件各有v3→Linux完整diff、最终hash；八个Linuxpyc只属新行政编译产物，hash与.py分别登记。旧v3未接受任何“移植覆盖”。

原输入计划SHA=2245be87d589e6f5b055b7f19b67f7f757914fae6064d4c1f8a21956c5a36801。运行时树锁、关键文件、单位和最终执行锁均保存实际字节/摘要。源→编译缓存→静态manifest→执行锁→未来授权收据构成无自引用的来源链；普通payload只读前三者及Root许可。

LR全目录入场复核后冻结，四根导航旧版留存于evidence/navigation_before；P/Envelope/Repair和R6-B继续沿用各自原锁/快照。batch01原62文件、60项ZIP及v1/v2/v3/静态草稿hash继续验证。原账27次、118.7340827秒、过期关闭状态保持；原ZIP SHA=358778fff25aa3f8354874803e2cc26cbaac1d7d70478e9f0923f9c756559594。

git diff --no-index只读取三资源文件；其换行提示未执行换行改写，最终hash核对确认原件保持。哈希行政复核不计作校准或模型证明，全部真实模型实际值仍未产生。
