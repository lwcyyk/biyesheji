# 认证实现与实验基础审计

## 审计结论

本阶段之前的 A/B/AB 是可执行的有限模型算法与自写夹具，**没有原生认证服务部署**。本阶段新增了两个完整上游身份服务的受控部署和真实 HTTP 适配。不能把原 L0 的“具体状态/真实分支”当成网站状态，也不能把下面的资源夹具算成第三个认证实现。

| 类别 | 项目内对象 | 实际作用与证据边界 |
|---|---|---|
| 自写认证夹具/模型 | `src/auth_lifecycle/fixtures.py`、`adapters.TableAdapter`、`a/plant.py`、B fixtures | 有限合成状态、观察与效果；无原生 OAuth 服务请求 |
| 自写实验资源与故障层 | `experiment/resource.py`、`journal.Gate`、调查脚本 | 受控资源策略、缓存、批准、预算、丢响应和调度；不是原生 AS 功能 |
| 原生组件/基础库 | cryptography 50.0.2、Java 21.0.9、H2、SQLite | 密码验证、运行时与存储；不单独算认证实现 |
| 完整独立认证实现 1 | Keycloak 26.8.1 官方发行版 | 原生用户/客户端/会话、OAuth token、refresh、revoke、introspection、管理员会话终止；Java/Quarkus/H2 |
| 完整独立认证实现 2 | Casdoor 4.25.0 官方发行版 | 原生组织/用户/应用、OAuth token/refresh/revoke/introspection、用户禁用及令牌失效；Go/SQLite；含上游完整前端 |

“完整实现”表示运行完整上游产品而不是手写认证接口；不表示本轮覆盖其所有认证流或所有部署模式。当前使用受控 password grant，未覆盖授权码/PKCE、MFA、SSO 多客户端共享浏览器会话或集群部署。

## 部署事实

- Keycloak：`127.0.0.1:18080`，管理健康端口 `127.0.0.1:18082`，专用 realm `l1-research`，自有生成测试用户。
- Casdoor：`127.0.0.1:18081`，专用组织 `l1-study` 和应用 `app-l1-0/1`，独立本地 SQLite。没有使用本机已有 PostgreSQL/Redis。
- 上游二进制、数据库、管理员口令及原始服务日志放在 `.runtime/l1/`，不加入公开数据或 Git；公开运行日志只保存凭据指纹。
- 发行版下载、上游校验值与本地 SHA-256 见 `experiments/l1/distributions.json`。Keycloak 使用上游 SHA-1 文件校验并另记 SHA-256；Casdoor/JRE 使用上游 SHA-256。没有声称完成供应链审计。
- Casdoor 非研究协议 LDAP/LDAPS 设为 0；RADIUS 在该版本没有使用的关闭开关，本实验配置为非法端口 -1 使其不监听，原生日志明确记录该可选服务未启动。HTTP 监听已实际核对为回环。

本机 Docker 已安装但引擎未运行。自动批准审查拒绝启动 Docker Desktop，仅返回“blocked by policy”；未通过其他入口重试该动作。本阶段采用项目目录内的便携原生进程，不修改系统服务或生产账户。

## 调查后固定的语义范围

版本和配置在原生调查后固定到 `experiments/l1/environment.lock.json`，状态为 **PINNED_FOR_NATIVE_PILOT_ONLY**。这不是确认性研究阈值或样本的预注册。

初次连通发现并处理的原生差异：

1. Keycloak 令牌未包含内省客户端受众时，内省可返回 active:false。实验添加明确 audience mapper 后，再分别核验发行客户端与另一客户端；不能将先前 false 解释为凭据已失效。
2. Casdoor 的 built-in 组织属于全局管理员域，禁止按普通用户测试。实验改用独立 l1-study 组织，而非绕过该限制。
3. Keycloak 根处置为终止该用户的会话；Casdoor 本实验的根处置为**禁用该自有测试账户并使其令牌失效**。两者对后续重新登录的含义不同，不当成等价的可恢复 logout。

原 A、B、AB 源文件保持；本阶段增加 `experiment/`、L1 脚本、协议与数据。旧有限枚举、开发测试和旧假设登记表不改写为 L1 或正式假设通过。
