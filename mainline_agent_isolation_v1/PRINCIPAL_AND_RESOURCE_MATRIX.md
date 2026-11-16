# M5 主体、资源与入口

本轮采用 Windows 受限主令牌、限制 SID、显式 DACL 和完整性级别。A/B 各有一个低完整性代理权限域。R、权威和假适配器作为三个进程共享一个收窄后的可信服务域。评分及配置主体使用现有可信用户令牌。SAM 账户新增数为 0。

所有令牌的 TokenUser 仍为 S-1-5-21-3999791725-3004789629-844009965-1001。各批次随机限制 SID、真实 PID、启用组和特权保存在该批 ENVIRONMENT_LOCK.json、SETUP_CONTROLS.json 与 trusted/control/*_isolation.json。代理权限域依赖受限令牌的双重访问检查。

| 主体 | 资源 | 允许动作 | 实际保护与核对 |
|---|---|---|---|
| A | agents/A | 读取自己的调用配置，读写工作文件 | A 独有限制 SID 的 FA；低完整性标签；M5-01 正向控制 |
| B | agents/B | 同上 | B 独有限制 SID 的 FA；低完整性标签；M5-02 正向控制 |
| A/B | assets | 读取代码、运行库和公开 TLS 证书 | 仅 A/B/R 的 GRGX；无写权限；秘密配置另存 |
| A/B | Controller/call、status | 自己的任务；自己的状态投影 | 本地 TLS、随机 Bearer 能力鉴别；caller 由配置映射确定；事务内检查任务、账户、受众、代次和预算 |
| A | B 句柄 | 允许知道句柄，执行仍须通过主体绑定 | M5-07 主动交付 B 句柄，使用 A 能力调用 |
| A/B | trusted/secure | 无读取或写入权限 | 仅可信用户、SYSTEM 和 R 限制 SID；OWNER RIGHTS 限制隐含所有者改 DACL 能力；M5-03/04 |
| A/B | trusted/authority、provider、cache | 无文件读取/修改权限 | 同上；数据库 AES-GCM 加密，密钥位于 secure；M5-03/04 |
| A | 本批 R/权威/适配器 PID | 无敏感进程访问权限 | 进程与线程 DACL 仅可信用户、SYSTEM、R；M5-05 测内存、复制句柄、终止、线程和 DACL 访问 |
| R 服务域 | trusted | 加载密钥、数据库和适配器配置；写安全投影 | R 限制 SID FA；中完整性；进程权限与 A/B 分离 |
| R 服务域 | scorer_private | 无文件读取权限 | DACL 仅现有可信用户和 SYSTEM；等效 R 主令牌进程实测读取私钥拒绝 |
| 管理调用者 user | 批准、撤回、受控材料处置、对账、状态 | 可信管理操作 | 独立 Bearer 能力，仅保存在 trusted/secure；M5-06 代理负例及正常批准/撤回控制 |
| 恢复调用者 recovery | recover | 取得权威当前投影并恢复 | 单独能力；管理身份恢复调用被拒绝；恢复身份批准调用被拒绝；M5-06/12 |
| 权威服务调用者 controller | 事务服务 | 已配置的事务操作 | 服务间独立能力；代理能力用于权威接口时拒绝 |
| 适配器调用者 adapter | 假 provider | perform、lookup | 服务间独立能力；代理直接 lookup 拒绝 |
| 评分/配置主体 | scorer_private 与全批真值 | 设置预期、独立只读评分、限域清理 | 可信基础 OS 用户；R 进程未取得评分私钥；评分访问路径单独记载 |

支持限制 SID 为 BUILTIN Users、Everyone、Restricted Code。它们用于系统文件、启动对象和密码库初始化。M5 可信目录及进程 DACL 对这些 SID 均无授权 ACE。显式 OWNER RIGHTS 的 RC ACE 收窄所有者隐含权限，可信用户仍有显式完整权限；代理改写可信文件 DACL 另作实际攻击测试。

## 实际入口

- 历史实验 Gate 与 provider 调查：experiment/providers.py。M5 仅读取其结果；本批调用链使用假 provider。
- L0 算法控制器：auth_lifecycle/controller.py，保留原作用域。
- 持久运行层：online_state/services.py 的 Controller.call、serve.Handler.do_POST；AuthorityStore.admit/release/revoke/record 承担事务检查。
- M5 启动入口：scripts/agent_isolation.py 与 Start-M5Isolation.ps1；isolation_acceptance.IsolationLab 建立本批目录和能力配置。
- OS 边界：windows_isolation.launch_restricted 使用 CreateRestrictedToken、SetTokenInformation 和 CreateProcessAsUserW；bInheritHandles=False；显式环境白名单；全过程使用主令牌。
- 管理、恢复、对账、材料补收接口沿用 services.py 的角色路由。M5 对管理/对账/补收覆盖代理鉴别负例，对假 provider 原生处置能力的业务效果保持原范围。

代码路径均相对 D:\毕业设计\auth-lifecycle\src\auth_lifecycle。完整源码定位、散列及补丁随交付保存。
