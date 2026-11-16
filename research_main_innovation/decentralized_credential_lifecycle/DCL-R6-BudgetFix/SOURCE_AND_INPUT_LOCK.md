# 源码、输入与执行锁
Material Passport：BF-static-1 / FROZEN_STATIC；冻结后新增代码变更须新版本、新hash。当前执行资格：UNAUTHORIZED。

## 唯一可信工作区
host：D:\毕业设计\DCL-R6-isolated-verification\lc03
Linux：/var/lib/dcl-r6/lc03，SOURCE=/var/lib/dcl-r6/lc03/src。
起点：D:\毕业设计\DCL-R6-isolated-verification\batch02\FROZEN_LC\src。
研究交付：D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle\DCL-R6-BudgetFix。

evidence/STATIC_WORKSPACE_LOCK.json记录24项实际文件（8源、8缓存、7输入和1拟用slice副本），含路径、字节数、SHA与Linux对应。evidence/SOURCE_DIFF_INDEX.json记录八源新旧hash与完整diff位置。inputs/static_manifest.json以16项source/cache、31关键runtime、完整树锁和原计划、子合同、拟用slice摘要构成静态锁；inputs/execution_lock.json绑定manifest与全部未来argv。工作区锁摘要在OUTPUT_MANIFEST中另锁，避免自引用。

## 实际摘要
|项目|SHA-256|
|---|---|
|guard.py|752c92f6114ce7c2ec9d45d39e4d46256b778ee91ce3a59ec55f37b6a27e4a02|
|guard_probe.py|32ed91e5135e09454d6634bf369193c7ccf4e8ae669e523b1dd781ed96109de3|
|run_batch.py（保持）|c88fc3b07e6feddf5d2aa96adf3b3b63fc3f6f9897d585f42d6882a5279a63e7|
|static_manifest.json|7c320d6183dff88bb032abd33ed2ff882301a7d06a8bac53e9c19bd327e7f41f|
|execution_lock.json|5090e398d32295513b51249ac9942d9ce9c97fc37bc5d2f11242dd11347a3260|
|原business_plan_original.json|2245be87d589e6f5b055b7f19b67f7f757914fae6064d4c1f8a21956c5a36801|
|完整runtime_tree_lock.json（继承）|0768bfe15ccb71c903cd350e444997a0371a179f3def35a7566f9ec1d8fadaf7|
|拟用dclr6batch03.slice（原LC模板同字节）|e4bdea70e3e13ad7a3a431652ba8634bfa527e1aba0a0037a1bbb7e6698b89c2|
|既有LC service模板（历史参照）|edd9b151f1875e62f6d96372219d93295b0218049f56df411656ced07895ec4b|

五业务hash在SOURCE_DIFF_INDEX逐项列出，compare/f1_check/f1_model/f4_dp/f4_reference全部changed=false。源码行内的参数和fixtures生成逻辑是实际输入；原business_plan作为来源意图归档，run_batch没有从该JSON加载参数，执行锁因此同时绑定run_batch源码及各业务模块。child_contracts.json实际hash见manifest和工作区锁，N为32896/4096/1。

## 运行时与权限
Python3.12.3（包3.12.3-1ubuntu0.17）/usr/bin/python3.12，e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f。Kernel=6.18.33.2-microsoft-standard-WSL2/x86_64；systemd=255.4-1ubuntu8.18；dcl-r6 UID999/GID989。版本/平台声明继承已有合同，31关键文件本轮重新核hash。未来boot/T0只有批准后生成，当前锁不编造运行身份。

stat观察：lc03/src、inputs及lc03目录root:root 0755；guard、manifest、execution_lock、child_contracts为root:root 0644。三个既有LC/批02单位root:root 0644。当前仅静态准备目录；batch03 root、单位、授权receipt、out与预算账均未创建。拟用slice只保存准备副本，没有安装或daemon-reload。

## 历史保护与后续
batch02原预算32191、原失败与两个ZIP保持；外层ZIP=c4399b337cb1f46827c85d82e6e316f6180ac9bf6a37ef8616a4725bb6cde0c7，native ZIP=910af1ca01bf8e2258a18f95d1a12187eb2b7efd23f44fbe11146c66c5d97c84。误路径47项只读对照，原blocked by policy事件保持；本轮迁移、删除、替代权限操作0次。

系统配置检查范围为31个关键文件、3个既有单位及源/输入摘要；完整系统无变化证明需要外部审计，当前记录所发动作与锁定路径。运行前必须按实际授权重核完整runtime树、source/cache、目录权限、unit属性、实际boot与不冲突目录；差异直接停止，不生成可运行receipt。详见[B03申请](BATCH03_EXECUTION_REQUEST.md)。
