# 实际接口映射与应用门槛

版本：PR-SCREEN-1，2026-11-05。选择的实际计算对象为Vega MC公开接口返回的`VegaMcPrepZkSNARK`，并单列证明系统key对象。固定源码提交`c0ee259053cd12eaf43ed71b5cde375452b3ee4d`，官方源归档及摘录位于sources。源码只读；编译、真实凭据处理、证明生成与网络服务调用均为0。[SOURCE：sources/VEGA_CODE_VERSION.json]

## 1. 对象与可操作粒度

|模型节点候选|真实数据/位置|现成操作与依赖|驻留、逐出及重建依据|费用及应用结论|
|---|---|---|---|---|
|完整prepared bundle|`VegaMcPrepZkSNARK`，vega_mc_zkp.rs 1349–1365|`prep_prove`生成；`prove`消费并在成功时返回|调用方可保留/释放整个对象；Clone/Serialize/Deserialize支持副本或存储；原始材料和兼容pk可用于重新prepare|整份操作有依据；私有state驻留字节、加载及错误恢复费未报告|
|证明系统pk/vk|同文件1268–1295|`setup`返回pk/vk；均有Serialize/Deserialize；pk供prepare/prove，vk供verify|调用方可保留/释放整份key；加载与setup是不同路径，分别计费|可作为共享初始化对象；本轮固定它们及工作区后采用文件缓存profile|
|ps_step中每个元素|同文件1353、1500–1514|内部按step创建的`PrecommittedState`|高层prep字段私有；未定位到调用方可单独取出、丢弃、重建并接回bundle的接口|任意step节点调度`APPLICATION_INTERFACE_UNSUPPORTED`|
|ps_core/shared witness|同文件1354、1490–1523；r1cs.rs 292–408|内部shared生成后复制到各step，core再填precommitted段|数学共享关系明确；高层外部接口不提供任意父对象重接或按节点恢复|图存在与可调度操作分别登记|
|matvec/i64/large_positions缓存|同文件1355–1365、1526–1596|依赖step witness、形状及public values；特定形状时自动创建|字段私有；高层未暴露逐项关闭/重建方法；源码扫描见API_SCAN.json|不能免费给候选一个任意缓存管理接口|
|固定基/稀疏矩阵预处理|同文件1430–1476|setup内部`precompute_ck`及`S_step/S_core.precompute()`|位于key/shape内部；调用方管理的是外层key；具体独立失效/加载规则需进一步接口依据|共享成本存在；大小及持久化细节待测|
|证明中的临时向量/层|同文件562–588、1770–1784|底层无缓存时计算matvec；高层证明还复制缓存供NIFS使用|临时对象生命周期由内部函数掌控；调用方无法在任意内部点插入逐出/重算决策|需要预留工作区W；未获得任意节点调度合同|

[SOURCE：固定源码相应行；官方prepare/prove快照。这里“未定位”限定于该归档的51个Rust文件和本轮高层/相关底层检查，扫描结果不构成所有未来版本的接口判断。]

公开的`PrecommittedState::rerandomize_in_place`和`rerandomize_with_shared_in_place`（r1cs.rs 568–601）更新承诺盲因子、共享承诺。它们具有特定输入/类型合同。仅凭这些方法无法构造“任意丢弃一个中间witness段，再从其他节点恢复并重新装配高层prep”的现成操作。[SOURCE/DERIVED]

Serialize/Deserialize确实提供了状态的存取入口。通过重新编码私有字段来改变缓存，在工程上可能存在适配路径；本轮未获得官方保证这种任意子字段改写/重建保持依赖、版本及密码协议正确性的合同。该路线保留为未核实接口适配，private字段本身无法证明语言层面的不可实现性。应用门裁决表示当前可靠操作依据尚缺。[SOURCE/证据边界]

## 2. 兼容性与输出核验

- `setup`绑定step/core形状及步骤配置；vk存精确num_steps，verify会检查，而非只检查填充后的数量。[SOURCE：1393–1476、2126–2132]
- `prep_prove`保存shared/precommitted witness；静态内容变化需要新兼容状态。[SOURCE：1490–1523；r1cs.rs 306–408]
- 活动matvec依赖step public values，`prove`检查其与prepare时一致；普通nonce/日期若确实位于在线段，则按原接口复用。[SOURCE：1526–1541、1646–1670；前轮依赖表]
- 每次成功证明重随机化并返回prep；验证返回公开IO，应用还需比对预期语句。[SOURCE：1614–1632、2107、2111；官方scope]
- 发生兼容性错误前可能已经进行重随机化；错误Result不返回prep。备份、重新加载、重新prepare及失败前工作需进入费用。[SOURCE：1620–1670]

这些条件允许建立“合法整份bundle”兼容标签。标签建立、credential版本/配置检查、公开IO核验和安全随机性均按真实流程另计。节点不能只因预测将来会用到而被判定合法。[DERIVED]

## 3. 大小、费用与工作区的可靠程度

|字段|目前可靠依据|状态|
|---|---|---|
|整份P/O/V|Vega原论文Figure10，对应其原评估配置|作者报告；原benchmark提交与当前源码对应尚缺|
|单个step、ps_core或matvec的驻留字节|仅类型及生成路径|`NOT_REPORTED`，未实测|
|单个节点生成/重算时延|内部函数定位|`NOT_REPORTED`；整份P无法直接拆分成这些数值|
|峰值工作区W|源码会临时复制matvec/i64；论文给阶段峰值|需要配置绑定的测量；阶段峰值与常驻prep大小分别处理|
|整份序列化/加载费|类型具备serde能力|具体格式、版本、大小、I/O与初始化预处理恢复尚缺|
|外部输出请求建议|可按应用的credential/config标签定义|历史数据、训练和可用信息尚无本轮数据；不可假定准确|
|内部祖先实际使用建议|依赖内部控制流与逐出决策|真值需先修正，无法当作算法无关外部数据|

[SOURCE/UNRESOLVED]

## 4. 现有高层接口下可用的成熟归约

固定共享key、在线/构建工作区及配置，令每个合法prepared bundle为一个文件，其大小为s_f，加载或重新prepare费为c_f，外部请求为某credential/config的合法展示。成功`prove`返回同兼容类，命中后仍可复用。这样直接继承前轮Q1-F与Young模型的对应。[DERIVED；前轮FORMAL_PROBLEM_AND_REDUCTIONS.md]

当所有对象等大小、费用异质且获取PRP建议时，加权paging预测结果同样成为强基线；一般大小时先保留Young文件缓存及恰当的已有扩展。未来对key也进行驻留决策时，应使用已有共享初始化/依赖对象模型，并补齐key加载费用。仅增加这层对象划分尚不足以形成细粒度重物化的新方法差距。[DERIVED]

## 5. 转成细粒度DAG需要新增哪些能力

至少需要公开或新增：稳定的子状态句柄；父/版本/随机性依赖；可逐出的边界；从驻留父对象重建子状态的操作；执行期间的pin/峰值合同；重建结果接回高层证明状态的兼容检查；输出正确性及密码协议保证的保留论证。若用自定义代码暴露这些操作，还需记录新增内存、分析和工程成本。[DERIVED，需求清单]

这些工作属于新增工程与正确性前提。目前候选机制实现门未通过，因此本轮未编写接口扩展、调度器、测量器或生成程序。即使工程补齐，已有图调度方法也应获得完全相同的节点接口。[执行记录/DERIVED]

## 6. 与其他计算系统的关系

LRC原文说明Spark RDD具有不可变数据块、DAG lineage与缓存重算等实际对象；DTR原文也有真实tensor逐出及依赖重算机制。这些来源说明生成依赖模型具有计算系统意义。它们尚不足以把Vega的私有对象变成可调节点。[SOURCE：LRC §II、DTR §2]

本轮保持Vega为应用核验对象，未转向Spark或训练系统。若将它们用作毕业设计主应用，需要另外证明代理认证/凭据证明任务真实产生相应可调计算图、输出请求与成本瓶颈；该应用条件尚未取得。

**应用门裁决：** 整份bundle级别`REDUCIBLE_TO_KNOWN_MODEL`；任意子状态DAG级别`APPLICATION_INTERFACE_UNSUPPORTED`。当前仅补齐性能参数会改善整份缓存评价，尚无法直接开启细粒度算法研究。
