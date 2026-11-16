# 原生证据与五个最小接口差距

## 1. 源码实际支持

| 来源 | 可用事实 | 需要的实例前提/缺口 |
|---|---|---|
| Inbox：C03:19—52,114—149 | 接收/验签后保存五元与material；lookup可回放Issue/Refresh结果 | 原请求operation/source_rid连接；无结果不排除创建；重启按attempt覆盖，缺冲突全集导出 |
| Journal：C03:116—121,C11 | Issue/Refresh成功响应后的jti/账户/client/native_sequence与五元 | 日志无operation/source_rid；非AS事务日志；缺项不能作无效果；birth/不同创建去重 |
| get-token：G01/C03/C04 | 精确行与账户/app/状态、材料元数据 | 当前helper为refresh-only且写死旧scope；过期token_bundle可能阻断历史元数据读取；须分历史标识与当前使用资格 |
| introspect/UserInfo：G01,G11,G12,C13 | 指定材料/时点/路径的active或accepted | RT inactive、实际Refresh拒绝、AT拒绝、全部后代关闭分型；通用只读typed入口未齐 |
| get-tokens：G01,C04,C05 | 获准组织内一次Find正向行 | count独立；分页不自动一致；旧2/20/唯一未知不足覆盖gV；来源全集要另证 |

只读证据获取仍消费机会/权限/日志；deliver随后会写本地权威。评分端隐藏真值、原生数据库私读、原始密钥/Token导出均不能补缺字段。

birth可以由已有PK/JTI、数据库实例及可靠freshness/no-ABA合同共同确定，无须默认要求AS新增birth API。单Find内不同PK在这些前提下可证明互异；跨快照同PK且缺代次/无重用依据时继续保留别名不确定性。

## 2. 可信D_P包的责任

最小P可限定固定Casdoor cookie-free AT UserInfo和RT Refresh接受路径。持续失活可来自可靠命名处置/原生行状态加源分支与frame证明：同birth/账户/client绑定，实际操作/结果语义正确，记录expires_in≤0或删除对这些路径有效，freshness/no-ABA、无恢复写入，已通过检查的后代单独计入I。

Revoke成功响应有不存在/其他client/已失活等分支；HTTP200本身不完成上述证明。已有dispose的RT revoke＋AT UserInfo拒绝＋AT内省false只提供命名收据基础，必须结合源分支/材料和部署前提。RT内省可补点时观察，仍不封已检查请求。任意离线JWT/RP/cookie或已接纳业务效果超本P，继续缺证。

本轮没有实例化新的D_P原生包，也未证明源到二进制可复现。来源合同被明确列为当前现场关闭的阻塞项，数学校核不能把它填成true。

## 3. 五接口最小规格

**GAP1 可信请求快照。** 当前C01公开六字段缺operation/source_rid，grant视图还缺operations。新增受控只读typed导出或原正文规范摘要核验：保留五元、完整origin、操作/源、phase、spent、result/disposal refs及创建门/剩余额度。只读导出不增authority version、不回显material/handle/secret。

**GAP2 完整证据导出。** Provider内部扫描相关已认证Inbox条目和journal，输出条目引用、重复/冲突、解析/尾行/缺口、时间/生产者域和读取范围；保留旧results用于旧操作，不用其最后值视图作完整证据。没有历史检查点时承认未检测删行可能，不制造完备性标志。

**GAP3 纯投影。** 使用R04 readonly-lifecycle-projection/1，输出互异U、全部E、隐式F状态、c/R/H、D_P和开放前沿、O提案与成本。无网络/数据库写；所有未满足字段保UNKNOWN。标准流输入与native影响域分开。

**GAP4 版本化提交。** 在AuthorityStore事务内重核authority/O revision、当前批准、证据/profile/frame依赖，保存O转换/历史/费用/证书引用。版本一致不证明AS无新写入；frame无法证实时不提交native-close。旧native-attempt-closure/1和单目标window守卫原义保留。

**GAP5 独立证明检查。** 从原输入重建网络，检查流/势或不足割；独立核对输入摘要及source/scope/currentness依赖。数学层成功与现场关闭准入输出不同状态。

## 4. 当前代码与实施阻塞

C15旧独立检查器可复用其“packet绑定＋条件前提明确”的设计，但它只验证原单未知谓词/固定模型，未包含多尝试流和新O。不能直接放宽single_unknown_creator变成支持本域。

本轮当前代码需要GAP1—5的成熟接线；尚有D_P、来源全集、排他持有者、运行实现对应和当前权限的部署证明责任。离线S1/S2可以先实现标准输入/证书边界并输出条件结果，真实关闭提交和原生测试必须等待相应证据/授权。
