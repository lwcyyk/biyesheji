# 实际Staging契约与字段映射

机器契约见`B1_STAGING_SCHEMA.json`，40字段/18接口逐项实际状态见`FIELD_MAPPING_ACTUALS.json`。Schema沿R11冻结名称，无新生产协议改名。

## 输入与信任

`read_dsat_authority_snapshot(reader, scope, trusted_read_context, limits)`接受已初始化reader协议。scope明确账户、audience、task、caller、generation；请求范围必须是宿主授权范围的子集。普通dict中的actor/read_ok/source_confirmed无法替代上下文。

TrustedReadContext由已授权宿主在序列化请求之外构造，并绑定具体reader对象。该工厂提供本进程策略载体，实际宿主认证/授权仍是前提；它没有实现远程身份服务或新认证凭据。当前验证使用SYNTHETIC_ONLY来源。

先检查scope和读取额度，再持有reader.lock调用read_state一次。源内核验原请求规范结构、保存的digest、grant/handle/六元origin与原请求之间的等式。输出operation/source_rid来自通过核验的原请求，外部AI请求无法提供替代origin来收窄来源。

## 输出

公开对象由字段白名单逐项新建，根及嵌套Schema均关闭未知属性。输出包含a、source locator/producer/principal、已过滤的grant/request、opaque result_ref、处置点观察、窗口历史摘要、原请求校验记录、legacy义务、保守风险视图、开放前沿、来源标签、兼容缺口及成本。

源端校验只输出既存完整request_digest与校验出处；不输出原请求正文、handle或独立handle摘要。result_ref由source locator和请求tuple等元数据构造，未采用Token原值或原生材料内容作公开标识。它属于本地元数据引用，尚非Native出生代次身份证据。

`source.authority_instance`、`source.sql_schema_version`和`obligation_revision`为null。缺失typed O/o始终明确，输入中伪造同名新字段不会升级legacy合同。固定六类来源标签覆盖DIRECT_FIELD、DERIVED_WITH_TRUSTED_BINDING、LEGACY_PROJECTION、SYNTHETIC_ONLY、UNAVAILABLE、UNVERIFIED；标签/内容摘要自身不提供外部真实性。

## 映射完成度

40项全部登记：16项有本地Staging实现或部分映射，1项敏感handle明确扣留，23项本次未导出或延期。该统计不表示40项生产能力均已实现。

已验证字段主要为：a、完整保存tuple、origin、phase、原请求operation、获准的source_rid、grant操作/预算、opaque结果/处置、旧窗口与receipt摘要、源内原请求校验、局部候选attempt和读取时钟。缺父或父跨scope时source_rid置null并保留SOURCE_REFERENCE_UNAVAILABLE，避免暴露其他作用域的标识或伪造唯一来源。

新proposal/ledger、base/proof/after O、packet、实际checker/evidence/frame、稳定instance/o、完整c/U/出生历史/E/D_P均未由本接口提供。partial_math只保存本地候选，c_known为空、未知容量明确列出，U/E/D_P为null。math_input为null，完整有限数学域保持未准入。

18接口中N01内部适配器已实现；A01/A03及scoped legacy view有相应代码。Provider各接口、真实S3事务及证书读写均未接入；S1/S2/S3-A仅作获准的纯数据负向兼容检查，原模块保持。

失败返回固定错误码、null数据及风险缺口，不返回部分前缀充当完整结果。snapshot_digest绑定本次净化快照、scope、a、来源和读取元数据；它不等同生产S3 source_snapshot_digest或认证签名。
