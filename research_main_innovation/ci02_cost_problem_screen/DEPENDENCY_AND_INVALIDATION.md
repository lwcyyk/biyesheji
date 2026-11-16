# Q1：依赖、合法复用与失效边界

版本：COST-SCREEN-1，2026-11-05。对象为合法证明操作的性能管理。证据标记：`SOURCE`原文/接口事实，`DERIVED`本轮纸面推导，`MODEL`明确增加的建模条件，`NOT_REPORTED`已读来源未给数值，`UNRESOLVED`尚缺接口或实例映射。本轮沿用academic-research-suite的来源核验流程，全部分析在当前会话内完成。

## 1. 版本和结论范围

接口事实绑定微软官方Vega仓库提交`c0ee259053cd12eaf43ed71b5cde375452b3ee4d`。来源为官方main归档，其ZIP注释给出该提交；归档SHA256见[sources/VEGA_CODE_VERSION.json](sources/VEGA_CODE_VERSION.json)。代码采用只读检查，编译、证明生成及性能采样次数均为0。下文行号指该提交。[SOURCE：V-CODE，详细定位见sources/READING_LOG.md]

性能数字继续绑定19页Vega作者PDF的SHA256 `2893026c8c8dc4db4da724869873119b3c4834406913c33f8200a210ae3ba8a4`。论文实验提交与本轮源码提交之间的对应关系尚未取得。因此，接口边界与论文数字分别使用；把数字代入接口实例时会附同成本配置假设。[SOURCE/UNRESOLVED：V-PAPER §8、V-CODE；sources/READING_LOG.md]

核心结论：成功的`prove`重随机化并返回prepared state，支持同一兼容类中的重复展示。高层MC接口会检查step数量及活动matvec缓存所依赖的step public values。静态见证变化时，现有高层恢复路径是为新输入执行`prep_prove`；当前已读高层类型未暴露清空单个缓存或局部重建的调用方法。内部无缓存计算路径与调用方可选择的接口分别登记。[SOURCE：V-CODE 1352–1365、1482–1607、1614–1670、1770–1784、2107；V-PREP]

## 2. 实际调用及对象层次

1. `setup(step_circuit, core_circuit, num_steps) -> (pk,vk)`：生成形状、commitment key、固定基预处理及稀疏矩阵预处理；`num_steps>=2`。步骤数内部向二次幂填充，但`vk.num_steps`保留精确数量。[SOURCE：V-CODE 1393–1476]
2. `prep_prove(pk, step_circuits, core_circuit, is_small) -> prep`：从首个step构造shared witness，为每个step及core填充precommitted witness，并在适用时计算matvec缓存。[SOURCE：V-CODE 1482–1607]
3. `prove(pk, step_circuits, core_circuit, prep, is_small) -> Result<(proof,prep),error>`：按值接收prep；重随机化后校验兼容性并继续证明；成功返回prep供下一次使用。[SOURCE：V-CODE 1614–1670、2107]
4. `verify(vk,num_instances)`返回公开IO；应用还需将返回值与预期语句比较。完整输出核验的费用记入成本。[SOURCE：V-CODE 2111–2132；V-SCOPE “Verifier acceptance”]

`VegaMcPrepZkSNARK`包含`ps_step`、`ps_core`、`cached_step_matvec`、`cached_step_i64`、`large_positions`、`cached_step_public_values`，字段均为私有。它支持Clone及序列化/反序列化；这说明对象可以存储，具体文件格式、加载费用及失败恢复流程仍需调用方明确。[SOURCE：V-CODE 1349–1365]

## 3. 输入—对象—恢复依赖表

|变化|继续有效的对象|需要更新或失效的对象|现有合法处理|全部重建是否有依据|证据|
|---|---|---|---|---|---|
|同一凭据、相同形状/配置，仅改变明确划在在线段的nonce、设备签名、当前日期|兼容pk/vk；shared/precommitted状态；step public values保持相同时的matvec|当次在线见证、盲因子、proof|将上次成功返回的prep交给`prove`|论文明确支持复用；动态段按次生成|V-PAPER §1.2、§8.1；V-CODE 1623–1632；R1CS 411–467|
|凭据内容、issuer签名或版本变化，并使shared/precommitted值变化|形状及精确step配置兼容时可复用pk/vk及其共享预处理|相应shared/precommitted witness及其承诺；依赖它们的缓存|为新输入调用`prep_prove`；旧版本如仍合法可另存|高层API支持整份prep重建；“每个内部对象必须全重算”的最小性尚无证明|V-PAPER §8.1；V-CODE 1490–1523；R1CS 306–408|
|step public values变化，且活动matvec缓存包含旧值|形状/step数相同时的pk/vk；静态见证若未变，其数学值仍可相同|旧matvec与相关i64、large_positions及兼容记录|当前高层路径为重新`prep_prove`后证明|高层恢复会重建整份；内部数学依赖只要求更新受影响对象，局部调用口尚缺|V-CODE 1526–1541、1646–1670|
|step public values变化，matvec缓存未启用|兼容pk/vk、未变化的shared/precommitted状态|当次公开IO及在线计算|按具体电路的合法输入域调用`prove`|此时源码未运行活动缓存的public-value相等检查；仍须满足电路关系|V-CODE 1591–1596、1649；R1CS 411–467|
|step数量变化|凭据原始材料可继续使用；部分底层数学结构可能相同|prep一一对应关系、vk精确step绑定|使用精确配置兼容的setup/key及新prep|仅“填充后数量相同”不足以复用原vk|V-CODE 1434–1457、1635–1643、2126–2132|
|电路形状、witness划分、参数/engine/协议版本变化|仅由新配置明确声明兼容的对象|受影响形状、pk/vk、fixed-base/sparse预处理、prep|建立新配置对象；依新配置重建|当前接口未提供跨任意形状迁移合同|V-CODE 1410–1476；V-SCOPE|
|披露选择或谓词变化|由具体应用电路决定|若仅影响在线段则当次更新；若影响precommitted查找位置、step public values或形状则相应失效|先检查实际划分，再选上一行对应路径|“每次披露变化都重建”及“所有披露变化均可复用”均未取得统一依据|V-PAPER §8.1把lookup positions计入静态段；V-TRAIT 19–52|
|issuer/device公共密钥变化|需区分凭据关系的公钥与证明系统pk/vk|公钥进入shared/precommitted时其依赖状态变化；进入在线段时当次更新；形状硬编码时配置变化|按具体电路的公钥位置处理|相同字段名不足以确定setup必须重做|V-PAPER §1.1、§8.1；V-TRAIT；应用映射UNRESOLVED|
|仅发生成功证明中的重随机化|相同兼容类、相同长度的witness及缓存|承诺、盲因子和proof字节更新|继续使用返回prep|已有重随机化直接保留预计算收益|V-CODE 1623–1632、1770–1784、2107；R1CS 568–601|
|序列化存储/重新加载同一兼容prep|逻辑兼容类可以保持|驻留位置、反序列化和验证费用|使用已有Serialize/Deserialize能力，并登记版本/配置匹配|加载I/O、内存峰值和错误处理NOT_REPORTED|V-CODE 1350–1351；V-PREP|

“继续有效”表示在列明的其余前提下可合法复用，范围涵盖正确输入。源码检查项目的存在只证明对应检查，尚不足以证明所有其他输入变化均有自动检测。[DERIVED]

## 4. 可选缓存的准确含义

活动条件为`pk.S_step.num_challenges == 0 && pk.S_step.num_rest_unpadded == 0`。此时完整step向量在prep时已知，其中包括public values。条件不成立时，构造函数自动保存`None`缓存及空public-values列表。`is_small`为witness算术提示，公开签名未将它定义为关闭matvec缓存的开关。[SOURCE：V-CODE 1486、1526–1596]

底层NIFS把已缓存项加入层数组，并对其余项执行`S.multiply_vec(z)`；因此源码包含无matvec时重算的路径。高层prep字段为私有，本轮在已取得源归档中未定位到公开的单缓存清空/重建方法。通过改写序列化字节、修改私有字段或改变电路以强迫关闭缓存，会引入额外工程和正确性义务，均未作为本轮现成调用能力。[SOURCE：V-CODE 562–588、1349–1365；源码扫描记录sources/API_SCAN.json]

`prove`为保留可复用缓存，还会在内部复制matvec/i64向量。在线工作内存因此需单独预算；它与prepared state常驻字节数有区别。[SOURCE：V-CODE 1770–1784]

## 5. 错误、失效和最小重建的证据边界

- 兼容性校验位于重随机化之后。一次stale调用可能已经发生部分工作；错误返回类型未携带prep，调用者若希望重试需预先保留合法备份或重新prepare。相关复制、I/O与失败费用均记作符号。[SOURCE：V-CODE 1620–1670]
- 成功路径允许直接复用。预先比较可信的凭据/配置版本与已知public values，可避免可预测的stale调用；依赖元数据的建立、比较和存储费用仍需计入。[DERIVED；实现未开始]
- 全量`prep_prove`是一条已存在的恢复上界。它提供的成本上界与“全量重建在计算上必要”属于不同命题。当前接口事实尚无局部最优性下界。[DERIVED]
- 源码注释“~66MB”缺少输入配置和测量条件；论文约100 MB预计算/562 MB在线峰值也对应阶段峰值。三者均未用作私有cache大小。`s_f`、加载时间、峰值工作区及失败恢复费用保持`NOT_REPORTED`。[SOURCE：V-CODE 1611；V-PAPER p15 Peak memory]

## 6. 本轮选题及下一步

选择**固定配置、固定共享key和工作区预留条件下，多份有效整份prepared state的驻留**作为Q1的精确性能问题。输入变化先经上述兼容性划分，真正的新版本成为新的缓存对象。该子问题具备公开API支持，且有成熟缓存模型的精确对应，见[归约](FORMAL_PROBLEM_AND_REDUCTIONS.md)。

跨形状迁移、任意内部子状态局部重建及配置可选缓存的收益保持独立待核实项。需要继续测量的最小集合为：各配置prep驻留大小、预留在线工作区、整份加载/重建费用；这些数据决定部署收益。当前材料尚未提供新的严格代价差距。
