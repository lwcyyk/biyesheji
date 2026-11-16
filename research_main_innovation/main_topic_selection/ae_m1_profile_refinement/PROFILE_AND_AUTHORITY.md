# 冻结Casdoor profile、权威与观察范围

版本 MR-1，2026-11-07（Asia/Shanghai）。AUTO-RESEARCH-M1-007。本轮为知情模型辅助只读证据审查；新增原生调用、账户、重放、实验和机制代码均为0。

## 1. 唯一原生依据

本轮固定 **CD425-M203-ORIGINAL**：`mainline_native_casdoor_v1/raw/batch01/M2-03`、其批次ENVIRONMENT_LOCK/SOURCE_LOCK及`source_snapshot`。只用这个case的初态、故障、最终观察和收尾作原生事实。其他调查/校准与CI归档仅用于解释合同边界，不拼接为当前轨迹。

|身份项|冻结依据|能说明的范围|
|---|---|---|
|服务|Casdoor4.25.0，单个owned-account、同一客户端/应用，本文记账户U0、客户端C0、应用App0|同一case的A/B共享账户和客户端，分别有批准与初始发行|
|运行二进制|环境锁记录SHA256 `ddbab07cbe0a913e3bf3b3fbb09b0a1fa3b4abc5127c6b3156930aa77a37ad5c`，与发行ZIP内exe相同|当时的发行物/运行路径绑定；本轮未查询正在运行的服务|
|发行包|锁定preflight代码核对ZIP SHA256 `24457f4383e33639d851514ddbb49fcaac85fca630f4736901c14d13a1114b32`|既有版本记录，未重新下载|
|提供方源码参照|commit `528a0213f01caf70b9f41009cbf7b2f67bdd67ec`|本轮只读Git对象/文件hash一致；源码到二进制可复现构建仍UNPROVED|
|运行层源码|原批次16个Python/SQL/脚本文件均与source_snapshot逐一SHA256匹配|使用当时实现解释行为；不把final未来运行器替代旧样本|
|配置|password/refresh_token、JWT、AT/RT各1h、刷新轮换开启|具体App0配置；其他应用、关闭轮换、授权码/SSO均不继承|
|故障子配置|M2-03的durable_inbox=false，控制器在after_effect退出后恢复|由锁定run_native/run_case和实际事件共同定位；不借M2-02的持久收件箱能力补结果|
|资源观察|fresh、cookie-free的UserInfo，HTTP200且sub匹配U0；另测内省/指定RT|没有其他RP或业务提交终结保证|

原评分SAFETY_FAILURE只因`real_controller_restart`固定次数规则，离线修正为PASS，原始数据与原评分均保留。这个修正没有消除A1的运行态UNKNOWN。当前审查不重跑评分器；读取原文件及既有修正记录。

## 2. 四层实现身份

|层|实际内容|本轮处理|
|---|---|---|
|B有限模型|固定路径目录、批准/费用，停止菜单revoke/close/gate|读现有MODEL/engine；没有重绑转换|
|known-contract-single-path/v1|用于原生校准的名义数学绑定：单registered世界、空probes、query_needed_profile=false|不等同完整部分观测A/AB验证，也不是另一个独立原生实现；没有用于执行M2-03的M₁迁移|
|ONLINE_TRUSTED_STATE_V1|控制器、SQLite权威、固定Casdoor适配器，任务句柄/来源/pending和本地截止|本轮原生事实来自其锁定M2-03轨迹|
|Casdoor AS|发行/刷新/接受/撤销及原生token记录|只按版本限定观察和源码参照解释，不赋予它本地任务批准代次协议|

同一个Casdoor版本名不足以拼接不同客户端、授权流程、托管条件和Cookie观察。

planning.py在online模式写入的all_material是该名义模型的输入声明；它没有替M2-03建立完整世系围栏。该声明不能因提供方版本相同而覆盖本case动态/未决状态。

## 3. 名词与真实效果单位

用T_A/T_B表示逻辑任务，P_A/P_B表示本地批准实例，A0/B0表示初始结果句柄，A1表示A0派生的刷新尝试/结果。U_A0/U_B0/U_A1表示评分通过材料摘要与AS记录映射的单位。它们是本文抽象ID，不包含原生凭据。

- 本地`grant_id`属于批准权威，不是Casdoor签发的世系ID；本地g0/g1是批准代次。
- AT/RT是材料，初始一对AT/RT映到一个已观察原生记录，不按字符串数计独立根。
- B_use沿用B0材料，产生新请求记录，原生根数不因此增加。
- A1保留P_A的任务/批准来源，原生记录却可更换；本case初始/最终记录并集为3个，不是固定预建根库存3。
- account/client相同不等于同一原生根，也不提供完整批准世系截止。JWT标识须与原生效果映射，不能自行当作根证明。

提供方参照源码`object/token_oauth_util.go`的ExpireToken/RevokeToken按给定材料查找记录、处理到期状态；非空RefreshTokenHash还有组策略分支。RefreshToken生成新记录并按轮换配置处理旧记录。这里没有把所有配置写成“只影响一行”，也没有从代码得到按本地P_A选择的持久世系围栏。具体后效以本case观察为准；源码—二进制精确构建仍有前提。

原生记录行在所有配置中也未必等于最小撤销等价类。本case的G_trace保留原评分定义；将它提升为M₁独立根库存仍需效果保持证明。

## 4. 控制权与材料托管

|主体|可取得/执行|限制|
|---|---|---|
|任务代理agentA/agentB|自己的能力身份、批准句柄、rid/状态/来源投影；登记call/status|正常投影不含AT/RT/ID token、密码或client secret；不能任意更换caller/task/account/audience/generation|
|批准操作者user|grant/revoke/recover/deliver/status及本profile已开放dispose|可信实验夹具，不等于已验证的真实用户批准UI；创建新批准要另付并遵守绑定，不自带原子迁移|
|R控制器|向权威admit/release/record、已知材料处置、结果补收|旧来源不可重标成另一个批准；lookup只用运行收件箱，不读评分私有数据|
|权威|原子事务保存批准、预算、派发、结果和处置|单个事务原子性是本地性质；没有与AS状态合为一项跨系统原子move|
|原生适配器|持材料、密钥、固定方法/端点；issue/refresh/UserInfo及已知单元revoke/introspect|method通道不开放账户管理或任意URL；M2-03无持久结果收件箱|
|测量/评分者|原批次加密HTTP结果、额外原生接受观察、限定AS记录|可见运行者未知A1；这些值不回流R。当前审查没有解密HTTP或打开secret材料文件|
|环境/清理夹具|建户、配置核验、最终处置/删户，独立CookieJar|权限和预算与方法分开，收尾不得替代B保留期间的选择性完成|

各测试进程共享可信OS用户。角色能力和材料投影有有限检查，恶意OS用户/任意文件读取的隔离尚未验收。本轮没有假设代理实际持原始token；CI归档中的raw-RT对手属于别的合同。

受保护HTTP响应日志由适配器传输层持久写入，物理数据和解密能力仍在可信实验侧。当前lookup只查运行收件箱，方法合同不允许借评分/取证通道补结果；这种分层不是全平台信息不可恢复性定理。若把既有日志改成运行接口，需要完整来源/attempt关联、故障持久性、保留及授权合同，并向G同等开放，不能当作候选独享的新增原生能力。

## 5. Local与Native观察函数

定义O_L(t,s)：该任务按当前批准/调用者/代次通过R新放行并由R提供服务的能力。批准失效或权威不可恢复时，REJECTED/UNKNOWN不构成成功交付。

定义O_N(m,s)：持指定材料m的独立观察者向本profile资源提交后是否被AS接受；fresh UserInfo的200及sub匹配才是这一路径的接受见证。内省是C0调用者范围下的另一观察，指定RT拒绝又是独立事实。

两类观察都保留UNKNOWN。未知表示未有足够判断，不等于底层能力已不存在。Native正接受由测量者持有材料得到，也不表示原代理已经取得该材料或绕过R。

强M₁的完整旧支持退役还需要对归属任务的全部材料/后继和允许未来派生路径量化。单个O_N为false没有给出世系全称结论，O_L旧批准截止也没有自动改变O_N。

原生revoke的200只表示响应；RPC服务自身也可用HTTP200返回JSON中的REJECTED/UNKNOWN。它们与UserInfo接受的200有不同语义。当前ID token、浏览器Cookie/SSO、离线JWT及其他RP没有被资源观察函数覆盖。

## 6. 事实、真值和前提的边界

原始公开轨迹表明：P_A在本地版本11撤回，A_after_ack被拒；A0处置收据只声明named_native_material_response_only；A1仍DISPATCHED_UNKNOWN。独立最终观察A1仍接受、B0继续接受，A0拒绝。详见第二稿的准确定位。

这些是历史原生观察及运行状态，本轮没有新增实测。AS内部精确线性化点未观测；客户端屏障、提交版本和发送序号给出偏序。逐点B成功不升级为故障全过程/全部交错的持续可用性证明。

完整支持闭包、所有已交付副本、绝对派生截止、生产批准真实性和原子任务迁移均未从此profile获得。CI01合同/截止审计涉及不同raw-token能力和其他应用/配置，只保留其已归档范围，不重开缺陷，也不向本case导入那些能力。
