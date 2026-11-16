# S1/S2/S3-A部分兼容性

## 实际可用

B1已输出带a与来源/scope的本地grant/request元数据、源内原请求校验记录、保守旧O/前沿以及明确未知字段。数据对象有固定Schema和内容摘要，可交给获得相应scope的调用者检查、展示或进入后继受控适配。

## 实际阻断

B32在本次新测试内调用了既有纯project_evidence、normalize_math、Proposal.parse和raw_obligation，原模块字节保持。这些是新增用例所需的格式检查，未运行历史测试、求解器或事务。

- S1直接接收该Staging时安全拒绝；它仍要求合成bundle/FrozenTrust及含handle的完整原请求。公开净化数据需要单独的真实信任入口或私有源内计算/新版契约。
- S2数学规范器拒绝partial_math；未知c、U、E、D_P不被补0或拼成D_fin。当前没有运行solver或签出新数学证明。
- S3-A Proposal解析器拒绝Staging冒充commit。保守风险记录能通过纯obligation形状检查，这只说明数据局部形状，不提供真实base O、实例/o、权限或事务资格。

上述负向兼容均得到实际断言。兼容报告对三者direct_input全部为false。源码ID规则的legacy80、S1的160及S3-A的128等差异仍需后继严格映射；opaque本地引用不冒充Native材料身份。

## 四种O

当前B1只能提供legacy_obligations及独立conservative_O_view。它们均无持久typed O/o；O_before typed base、真实S1 O_projection、新proof_context和O_after尚未具备生产连接。没有制造这些摘要的默认相等关系，B15仍为B2 BLOCKED。

旧CLOSED/1和native-attempt-closure/1保持历史单attempt范围。旧W_h、storage/Controller/Provider及其Schema均未修改；本轮没有旧writer隔离或生产关闭写回。

真实c_i的G1前提、全部出生代次/历史、来源关系、持续D、创建前沿、接受路径与部署忠实继续SOURCE_OR_REFINEMENT_GAP。B1代码验证不会自动升级这些前提。
