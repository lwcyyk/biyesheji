# 限定 Casdoor 原生 profile 与接受合同

2026-11-05。本轮是 ONLINE_TRUSTED_STATE_V1 的成熟原生适配实例，密码学辅助线保持 FROZEN。以下配置在本批首次请求时核验并写入 raw/batch01/ENVIRONMENT_LOCK.json；不符时停止采样。

## 固定范围

- Casdoor 4.25.0，本机 http://127.0.0.1:18081。可执行文件与既有发行 ZIP 的摘要相符，记录实际进程路径。源码参照 commit 528a0213f01caf70b9f41009cbf7b2f67bdd67ec，源码与发行物的可复现构建继续未决。
- 既有组织 l1-study、应用 app-l1-0、client_id l1-client-0。仅读取配置，password/refresh_token grant、JWT、AT/RT 各一小时配置及刷新轮换开启由实际环境核验。
- 四个随机新账户，每个场景一个。每个账户的 A.g0/B.g1 独立批准和 password 发行来源分别保存。后续支持关系通过原生记录和接受观察核对。
- 资源接受为 fresh、cookie-free GET /api/userinfo，仅提交 Bearer AT，成功要求 HTTP 200 且 sub 与该账户 ID 一致。内省和 RT 刷新拒绝各自记录。
- 历史 password grant 用于版本化实验，生产授权流程另有选型与验收职责。

预算为环境/建户 40、方法 60、独立测量 80、清理 60，总上限 240。原生 HTTP 在发送前通过独立 SQLite 账本分配序号并消耗对应预算。重试、失败、查询全部占槽。采样器不自动重采，出现违反、越权、泄漏、环境冲突或收尾额度风险时转入清理。

## 材料和调用来源

schema 2 材料分为 casdoor_login 与 casdoor_oauth。登录材料包含预期账户、用户名、密码、issuer 和 client。OAuth 材料保存实际返回的 AT、RT、token_type、scope、expires_in、id_token。未返回的可选字段明确为 null。响应原始字段与 derived 栏的验证后 claims、引用摘要、请求 scope 和标识候选分别保存。

AT 使用冻结 JWKS 验证 RS256 签名和 issuer/sub/audience/时间。该 Casdoor 源码只给 AT 设置 kid，RT 以同次 AT 指定公钥验证，并核对相同账户和客户端。JWT jti 只登记为标识候选，实际原生撤销单元由限定账户 token 行另行映射。

rid、attempt_id、批准实例、代次、调用者、账户、受众和完整规范请求摘要持续绑定。refresh/userinfo 的 source_rid 必须指向同一批准、同一来源且已登记可用的结果。代理不能提交任意 URL 或原生 token 值。

旧 schema 1 保持原加密行布局与 AAD，通过 user_version 迁移至 2。原合成字符串仍可读，既有请求摘要保持原始规范化方式。开发测试使用旧 schema 测试副本验证兼容，原副本继续保留版本 1。

## 三个结果时点

1. 适配器收到原生响应，native_response_received 记录原生请求序号。
2. 若当前 profile 启用 operational inbox，密文追加并 fsync 后记录 operational_result_durable。
3. 控制器成功把结果和材料提交权威后，事务版本表示运行层已持久接纳。

M2-02 在第二点之后延迟交付，允许 B 的其他调用继续。M2-03 明确关闭 operational inbox，在控制器收到响应后、结果权威登记前终止控制器。评分通道保存的原生 HTTP 密文属于额外真值，恢复运行者的 lookup 接口不会读取它。

| 边界 | 恢复处理 |
|---|---|
| 放行已提交，发送尚未确认 | 保留 DISPATCHED_UNKNOWN 与预算消费 |
| 请求可能到达 AS | 缺少终态依据时继续未知 |
| AS 已生成但响应丢失 | 运行者缺少材料时继续未知，评分者额外真值单列 |
| 适配器已收到且 operational inbox 已持久保存 | 仅按完整 attempt/source 绑定补收相同结果 |
| 控制器收到但权威登记前崩溃，且 inbox 未启用 | 继续未知，不从评分私有通道补入 |
| 权威已接纳，控制器重复补收 | 相同结果幂等，不同正文/来源冲突 |

原生 profile 当前没有足以支持本模型自动重放的 attempt 幂等、终态查询或无效果保证。本批未知请求不自动重发。

## 撤回和处置范围

LOCAL_REVOKE_COMMITTED 在权威事务提交后发出，阻止该旧批准的新放行。已经放行的请求保留原责任。

管理员 fixture 可对已知、隔离的原生结果请求一次持久处置尝试。适配器以该材料 RT 调用 revoke，并另查 AT 的 UserInfo 和内省。只有当前观察表明该已知单元不再接受时，登记 KNOWN_UNIT_INACTIVE/DISPOSED。响应和原始来源保留。单次 HTTP 200 自身只记录撤销请求的原生响应。

源码 object/token_oauth_util.go 的 RevokeToken 先按 token 值寻找记录，未找到也可成功返回，对已找到的当前记录调用 ExpireToken。RefreshToken 创建新记录并处理旧记录。父材料的撤销响应和后继材料的状态各自判断。

独立评分分别核验已知 A 单元、已知后继、B 保留、未知义务和完整性前提。M2-03 允许评分者观察到运行者未知的 A 子代仍接受，同时要求运行者保留对应未知责任。整个合同不以本地 ACK 宣告全部后代或业务外部效果终结。

账户禁用/删除在 B 保留评分窗口以后，只用于本批收尾。清理可使用该批额外真值处置本批账户中的已知材料。运行态未知责任和收尾后的原生状态分别报告。

## 托管与观察权限

R、权威、适配器和测试 OS 用户可信。服务间能力凭据分角色配置，代理只持句柄和自身接口身份。原生材料只进入可信进程、权威密文、适配器密文 inbox、受保护的原生证据和固定端点传输。

公开日志保留标识、事务版本、字节数、HTTP 状态和引用。native HTTP 密文证据、账户密码、应用 secret 和密钥位于本批 secure 目录，Windows DACL 限定当前测试用户及 SYSTEM。独立测量按精确新账户过滤读取原生数据库，额外路径和查询数单列。API 身份检查与真实不可信 OS 用户隔离分别验收。
