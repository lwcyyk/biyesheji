# M5 到 M6 的实际接线差异

日期 2026-11-06。依据 M5、M2/M4 报告与本轮源码核对，按成熟部署集成登记。

| 入口/资源 | M5 状态 | M6 接线与核验 |
|---|---|---|
| R 原生模块 | 运行包只包含 fake provider 依赖 | 补齐 native_provider、native_http、enumeration；在真实受限主令牌内加载 |
| 材料 | legacy synthetic 字符串 | schema 2 登录材料与 AT/RT 束，复用签名验证、权威 AES-GCM 和来源绑定 |
| inbox/标识日志 | 合成文件，真实渠道未联合运行 | M6-01 完整加密 inbox 与标识日志启用；M6-02 两者关闭 |
| 审计 | M5 使用合成私密目标；M4 单向封存仍缺 OS 域 | 复用 RSA-OAEP/AES-GCM 封存，真实 RSA 私钥置于独立评分 DACL 域 |
| 原生 HTTP 预算 | 旧文件位于 batch 根 | 可选 http_budget 子目录，赋予 R 写权限；batch 父目录只读，评分私钥目录独立保护；旧 profile 默认路径继续兼容 |
| 管理/恢复 | M5 分角色能力，fake backend | 同一 Controller/Authority 路由；真实 provider 在 R 域运行，代理仍只持自己的接口能力和句柄 |
| 原环境凭据和 AS 数据库 | M5 登记对象范围未覆盖 | 预检发现 .runtime/l1 的 Users 读取权限。研究者额外授权后，备份并收紧目录 DACL 与继承权限，原始文件内容保留 |
| PID/令牌 | M5 有 SID/IL/进程访问测试 | 增加实际 token 默认 DACL 与进程对象 DACL 回读，故障实例逐 PID/创建时间/映像记录 |
| 结果未知与枚举 | M4 全托管代码流，统一可信用户 | M6-02 在隔离代理存活时恢复旧缓存和权威，运行者凭获准组织枚举取得新材料 |

实现定位：auth-lifecycle/src/auth_lifecycle/online_state 下的 NativeIsolationLab、run_case、NativeHTTP、CasdoorProvider；脚本 score_native_isolation.py 使用独立规则。M5 当前默认令牌支持 SID 保持原配置。去除系统读取 SID 的两个开发探测失败记录保留在 dev_token_01/02，原生请求均为 0。

开发首轮全仓 148 项中，一项旧 mock 传输替换后丢失预算路径的用例报错。适配器改为在初始化时保留预算路径，避免依赖被替换的传输对象。原始日志与源码保存在 FULL_REGRESSION_V1_FAILURE.log、REGRESSION_V1_SOURCE_LOCK.json 和 regression_v1_source。修复后全仓 148/148 通过。

密码学辅助线 FROZEN；新增候选机制为 0。
