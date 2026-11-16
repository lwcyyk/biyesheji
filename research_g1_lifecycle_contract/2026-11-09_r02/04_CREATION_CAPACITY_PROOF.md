# 创建容量的条件性证明

## 1. 计数对象与假设

目标attempt i是一次成功持久release产生的attempt_id及其原rid/origin/v_rel。直接创建单位是该次原生处理新建的一个Token记录代次及其同次AT/RT/ID token材料束。owner/name与创建代次共同固定身份。它与B独立撤销域、原始授权根、JWT字符串和后续刷新子代分别计数。

ID token有独立jti，AT/RT生成时使用同一记录jti。单次材料束归一为一个容量单位，仅对声明的Token表创建合同使用；任意接受者的失效关系另证。[token_jwt.go:649—698；token_oauth_util.go:719—738]

| 假设 | 内容 | 证据等级 |
|---|---|---|
| A01 | 权威/密钥/批准/托管及鉴别可信，单活持久状态不回滚，身份与摘要无碰撞 | 本地源码支持；部署/密码学前提 |
| A02 | 只有固定Controller为该放行调用provider；旧perform无重发/其他角色重放 | Controller单调用支持；排他能力配置是部署前提 |
| A03 | 源模型忠实；相关helper无额外Token创建，无改变效果的自定义hook/后台写入 | 主路径/helper定点支持；全部署行为须固定合同 |
| A04 | 标准数据库一次固定PK Insert最多建立一行；提交错误保留不确定性；无额外创建触发器 | Token主键与Insert源码；数据库合同 |
| A05 | 固定RPC/NativeHTTP单open、无自动整请求重发、无重定向/代理 | 项目源码及历史stdlib片段；实际依赖/加载配置需绑定 |
| A06 | 一个完整HTTP请求至多一次AS handler执行，无中间复制/整体重入 | 直接loopback部署前提；路由本身不证明该条 |
| A07 | 创建见证按代次互异、不重复计同一行，name/JTI映射可靠 | 生成/查询源及可信来源；唯一性/代次持久性前提 |
| A08 | 全部目标后续刷新、重试、派生和在途调用入I或有封口终态；无未登记RT持有者 | 托管/源profile前提；active=false单独不足 |
| A09 | 外部创建者/管理员写入被排除或计入来源；相关配置稳定 | 受控夹具/部署前提 |
| A10 | 获准点读/枚举完整性、来源、历史见证及失效证据可靠新鲜 | 条件接口与多尝试C1—C5 |
| A11 | 指定路径/必要后代的失效持续，乙有明确独立支持/成功证据 | 源接受合同与scope前提 |
| A12 | 重试、查询、清理、RPC/计算/维护/输出完整计费，计划动作数有界 | 06纸面合同；实际模型接入待补 |

P_direct采用A01—A07；P_closed另需A08—A11；费用采用A12。假设被破坏时扩模型或返回边界，原未知责任保留。

## 2. C1：每handler直接新建至多一个单位

固定一次object.RefreshToken调用，在A03/A04下直接Token创建数≤1。

证明：创建前检查可返回，没有循环进入插入。705只生成一次新束/name，719—738构造一个newToken并调用AddToken一次；AddToken执行一次固定记录Insert，PK为(owner,name)。之后DPoP更新和父DeleteToken为更新/删除，返回不再生成/插入。标准同键插入重试也不会建立第二个不同单位。任意崩溃、提交后报错均增加0或1，不能从错误缩成0。helper/后台额外创建由A03/A04明确限制。

裁定PROVED_WITHIN_PROFILE，限固定源模型的一次handler直接创建；实际二进制/部署忠实为条件。

## 3. C2：每rid至多一个本地放行

A01下，admit固定同rid规范请求与origin，同体重放、异体冲突。release仅在QUEUED且当前检查通过时生成attempt并返回send=true；后续phase不同返回send=false。并发事务串行，崩溃后当前权威不将已放行记录还原为QUEUED。因此同rid至多一次放行，reserved/spent守恒。

这不提供provider/AS幂等：perform没有按attempt去重，AS表单不带rid。不同rid分别消耗预算。裁定PROVED_WITHIN_PROFILE。

## 4. C3：每放行直接容量1

在A01—A07下，每成功release的attempt可取直接c_i=1。令V_i为perform次数，H_i为refresh预记账机会，S_i为完整应用请求调用，A_i为端点接收请求，P_i为handler执行，C_i为直接创建数。A02及Controller链保证V_i≤1；每perform最多一次refresh调用。A05给S_i≤H_i≤V_i；A06给P_i≤A_i≤S_i；C1给C_i≤P_i。因此

\[
C_i\le P_i\le A_i\le S_i\le H_i\le V_i\le1.
\]

该链逐前缀成立，生命周期容量按全部允许后继取上界。H_i(prefix)=0不排除待执行perform未来首次发送，不能用当前0把c_i改为0。H=1且可靠观察到一个同源不同创建，才可在总容量1下令剩余创建余额0。

actual_sends来自requests表COUNT，是H_i。它不提供S/P/C的已发生下界。一次预记账后发送前崩溃为合法路径。CLOSED依赖可靠创建见证的下界与总上界饱和，计数本身不足。

裁定CONDITIONAL_ON_ASSUMPTIONS；本地代码支持部分链，传输、单dispatch、源/DB及排他托管显式保留。

## 5. 单位、根、派生与反例

Token行P被轮换删除后，子代C仍可能有效。AT/RT/ID三字符串不代表三个独立撤销域。DisableRefreshRotation=true时新行复用RT，ExpireToken会按相同RT hash批量失效，域可相关；当前profile轮换开启，但同父并发仍可创建多个新行。

**每父容量1的反例，固定代码允许。** 两个不同rid均合法放行，两个handler先读取有效P并通过检查，再各Insert u/v。第一删P，第二删P返回false,nil；调用755忽略bool，只检查err，仍可返回成功。每attempt各1成立，每父1失效。

**单H复制处理反例，放宽A06。** 同一个H槽的请求被中间层复制为两个并发handler，按上述交错创建u/v，得到H=1、C=2。它排除无A06的容量1，未声称当前loopback已发生复制。

**无限传递派生。** 子代RT持有者若能不断在到期前刷新，新RT有效期从生成时刻计算；任意d都可形成d次创建链。无限制域无统一有限传递容量。当前有限批准/方法预算只约束经登记入口的调用，未登记持有者须由A08排除。

若有可靠ρ_i个handler执行上界，可取直接c_i=ρ_i；有限派生树应把全部节点纳入I再相加。无可靠重试/派生上界时标UNKNOWN/UNBOUNDED，退出有限流子域。ID token其他用途、离线JWT、cookie及业务效果不由Token行失效自动关闭。

## 6. 最终容量裁决

| 对象 | 结论 |
|---|---|
| 单次固定源handler显式插入 | 至多1，固定源模型证明 |
| 一次持久放行直接创建 | 条件c_i=1，A01—A07 |
| 同rid本地重放 | 不增加放行；provider/AS重放另受前提限制 |
| 不同rid/两代理同父 | 各attempt分别计；每父1被反例否定 |
| 同次AT/RT/ID束 | 一项记录创建；各接受路径分别验 |
| 全部未来后代 | 有限I/封口时求和；无限制域无统一有限界 |
| 当前历史收据 | 仍为单未知/单机会/单效果及来源饱和条件实例 |
