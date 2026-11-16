# 主体、真实材料与通道权限

本表的相对路径从 batch01 起算。TokenUser 均为可信用户 S-1-5-21-3999791725-3004789629-844009965-1001；有效权限由受限主令牌的限制 SID、IL 和对象 DACL 共同决定。A/B 分别为 Low，R 为 Medium，配置/评分/清理主体使用可信基础用户。SAM 账户新增 0。

| 资源/材料 | 存放或实际通道 | R | A/B | 配置/评分/清理 | 证据 |
|---|---|---|---|---|---|
| 自己的服务能力、任务句柄 | M6-xx/agents/A 或 B | 服务端验证映射 | 仅自己的配置与工作目录 | 配置分发、评分读取 | 合法发行和资源调用成功；A 使用 B 句柄拒绝 |
| 新应用 secret、账户密码 | M6-xx/trusted/secure/native_profile.json | 读取本条运行配置 | 文件读取拒绝 | 创建、配置与清理 | 两条权限预检；M6-01 实际文件攻击 |
| 当前批准、预算、pending、AT/RT/ID token 束 | trusted/authority/authority.db 及 WAL | 经可信权威事务 | 文件读取/写打开拒绝 | 独立只读解密评分 | 实际束与六次原生响应逐字段相等；三个字段均未在数据库文件中出现明文 |
| 权威、provider、TLS 密钥 | trusted/secure | 必要服务读取 | DACL 拒绝 | 配置和审计读取 | R 读取正向控制、代理负例、实际服务功能 |
| 管理与恢复接口能力 | trusted/secure/controller.json、admin.cap | 作为可信服务验证映射 | 仅自己的角色能力 | 独立 user/recovery 能力 | 恢复、对账、补收、处置及材料接口攻击拒绝 |
| operational inbox | trusted/provider/native_inbox.jsonl | M6-01 加密写入并使用 | 实际文件读取/写打开拒绝 | 解密比对 | M6-01 已启用实际文件存在；M6-02 关闭且文件不存在 |
| identifier journal | trusted/provider/identifier_receipts.jsonl | M6-01 启用；M6-02 关闭 | 所在目录无读取权限 | 读取配置与事件 | M6-02 无日志；查询前无 A1 标识输入 |
| 审计公钥 | transport/secure/http-audit-public.pem | 读取并单向封存 | 无运行所需访问 | 配置提供 | R 读取成功，实际密文可由评分者解封 |
| 原生 HTTP 审计密文 | transport/secure/http/*.aes | 写入，不能用公钥解封 | 所在目录无授权 ACE | 独立私钥解封 | 84 个预算槽位与 84 份密文一一对应 |
| 真实 RSA 审计私钥 | transport/scorer_secret/http-audit-private.pem | 实测读取拒绝 | 实测读取拒绝 | 评分/清理可读 | 两条预检均 Win32 5，评分解封成功 |
| 实际私有响应副本 | M6-xx/scorer_private/actual_responses.json | M6-01 实测读取拒绝 | M6-01 实测读取拒绝 | 评分/清理读取 | 实际对象存在，内容原文仅该保护域保留 |
| 全局环境管理口令副本 | management_private/credentials.json | 实测读取拒绝 | 实测读取拒绝 | 环境配置/最终清理持有 | 两条预检与 M6-01 攻击 |
| 原管理凭据与 AS 数据库 | 原 .runtime/l1/secrets.json、casdoor-l1.db | 实测读取拒绝 | 实测读取拒绝 | 必要原生管理、精确只读评分 | 额外 ACL 授权、前后 DACL、两条实际预检 |
| HTTP 预算及原生发送元数据 | transport/http_budget/native_budget.db | 写入与精确计数 | 无文件权限 | 审计读取 | 预算目录独立可写，传输父目录只读 |
| 原环境参照应用 secret、建户意图 | transport/secure/profile_template.json、账户意图 JSON | 无授权 ACE | 无授权 ACE | 环境和收尾使用 | 新建文件受保护，仅 R 自己运行 profile 被授权 |

## 实际限制 SID

| 轨迹 | A | B | R |
|---|---|---|---|
| M6-01 | S-1-5-21-627851036-641978634-1246014279-1001 | 同前缀-1002 | 同前缀-1003 |
| M6-02 | S-1-5-21-1601000040-1189559158-834499708-1001 | 同前缀-1002 | 同前缀-1003 |

完整 SID、每个进程的映像、创建 FILETIME、对象 DACL 见各 ENVIRONMENT_LOCK.json。TokenUser、限制 SID、IL、默认 DACL、特权与环境摘要见 SETUP_CONTROLS.json 及 trusted/control/*_isolation.json。重启的服务继续使用相应 R 域。

进程攻击对本条 R、权威、原生适配器的实际 PID 发起；M6-01 十八项敏感访问拒绝。零原生预检另对本批配置程序和既有 AS PID 18456 检查进程访问，均被拒绝，未修改 AS 进程。代理可继承 canary 不存在有效继承句柄，自身提升至 Medium 的尝试拒绝。

顶层 launch_sanitized.py 的七项环境白名单被配置、评分和测量辅助程序继承；R 服务使用 M5 六项白名单，代理使用五项。角色启动 bInheritHandles=False；顶层 close_fds=True，仅为可信日志设置标准输出/错误。日志、异常、状态投影和代理工作目录按实际秘密集合扫描。全部句柄与所有 OS 全局对象的穷举不在本轮证据中。

原生 AS HTTP 为固定 loopback 明文接口，Controller/权威/适配器接口为本地 TLS。内核、管理员、驱动访问控制及可信服务仍属前提；抓包驱动、侧信道、生产浏览器状态和真实批准 UI 未在本轮验收。
