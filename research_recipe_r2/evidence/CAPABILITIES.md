# 原生能力与故障调查

依据 [survey04 原始观测](../../results/experiments/survey04/observations.json)：两个实现×13 个条件×2 次重复，共 52 次。每次使用新建自有测试用户，调查后处置并删除；同一条件的重复不算新的独立家族。

| 条件 | Keycloak 26.8.1 | Casdoor 4.25.0 | 来源/解释边界 |
|---|---|---|---|
| grant 局部 RT 撤销 | 目标 AT/RT 的授权方内省变为 false，兄弟 grant 保持 true | 同样观察 | 原生 revoke，fresh password grants、单客户端条件 |
| AT 撤销 | AT 变 false，RT 仍 true | 对应 AT/RT 均 false | 真实原生差异，不统一改写成一种撤销语义 |
| 共享根处置 | 管理 API 结束该用户的全部会话，两个客户端令牌失效 | 禁用该自有测试账户，使其各应用令牌失效 | 第二种会阻止再次登录；并非可互换 logout |
| 查询者受限 active | 发行客户端为 true，另一个已注册客户端为 false；签名/发行方验证仍有效 | 当前同 owner 应用下另一客户端仍为 true | 仅观察本角色配置，不推断所有角色；false 不直接等于凭据失效 |
| 内省缓存 | 授权方直接查询已 false，资源 fixture 缓存暂仍 true | 同样观察 | 缓存是自写 RP 层，不能称原生 AS 缓存；未证明 AS 一般无缓存 |
| 核验副作用 | 密码认证式核验新建原生 user session；内省未新增该类记录 | 密码认证式核验新建 OAuth token 记录；内省未新增该类记录 | 两类原生记录不同，不能把 Casdoor token 行称为浏览器会话 |
| 强停止不支持 | 账户根处置后旧 AT 的离线签名/期限检查仍有效 | 同样观察 | 限于到期前、批准的 token/account 撤销接口和离线 RP；不声称任意改服务器密钥都无效 |
| 批准撤回 | 最终发送检查前撤回 stop，未发送该停止请求 | 同样 | 实验授权层，非认证服务的原生“用户批准账本” |
| 响应丢失 | 原生发行成功后对方法隐藏响应；服务器已有凭据 | 同样 | 传输边界故障注入；请求仍计费；未知句柄不能当作不存在 |
| 迟到请求 | 撤销响应后释放旧刷新意图，观测为拒绝 | 同样观察 | 具体事件顺序的样本，不证明所有网络调度 |
| 并发竞争 | 两个真实 HTTP 请求从屏障同时放行；刷新可先成功，最终观测相关访问被撤销 | 观测到刷新被拒绝等结果 | 保留每次实际返回/后效；不能将两次样本当穷尽并发证明 |
| 可观察策略漂移 | 临时切换原生刷新重用策略，再观察同一 RT 重用；随后恢复 | 临时改变原生令牌寿命，观察 expires_in，再恢复 | 管理 API 真实变更，记录触发点；不伪装成候选已完成 H-D |
| 核验后预算不足 | 发行+内省耗尽预算，随后 stop 被阻断，凭据仍活跃 | 同样 | 共享实验预算，不能把提前拒绝记作合法完成 |

## G 的核对

在本次 fresh password-grant profile 中，Keycloak 的原生会话与客户端共同构成检查单位；Casdoor 使用其原生 OAuth token 记录的标识，并与实际账户及凭据匹配。两个不同 token 字符串不自动算两个 G；同一原生单位的多份材料不增加单位数。

调查通过“撤销目标、检查兄弟仍可用”的效果矩阵支持该 profile 的独立单位划分。一般 SSO 共享会话、跨客户端授权及刷新链的新旧记录关系尚未证明，不能从此扩展出通用计数定理。

## 一手来源

- [Keycloak 26.8.1 官方发行版](https://github.com/keycloak/keycloak/releases/tag/26.8.1)
- [Keycloak 26.8.1 管理文档](https://www.keycloak.org/docs/26.8.1/server_admin/)
- [Casdoor 4.25.0 官方发行版](https://github.com/casdoor/casdoor/releases/tag/v4.25.0)
- [Casdoor 原生安装与数据库说明](https://casdoor.ai/docs/basic/server-installation/)
- [Casdoor 4.25.0 token 控制器源码](https://github.com/casdoor/casdoor/blob/v4.25.0/controllers/token.go)
- [OAuth 2.0 Token Introspection，RFC 7662，2015](https://www.rfc-editor.org/rfc/rfc7662.html)

上述来源用于确认实现、端点与作用域问题；表中的具体结果来自本机原生观测，不把文档叙述冒充已执行测量。发行版校验记录见 [distributions.json](../../experiments/l1/distributions.json)，调查后的配置锁见 [environment.lock.json](../../experiments/l1/environment.lock.json)。
