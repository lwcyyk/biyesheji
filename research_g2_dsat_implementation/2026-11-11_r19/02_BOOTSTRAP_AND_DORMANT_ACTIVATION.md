# 启动桥、Dormant 与接纳边界

日期：2026-11-11。范围：研究者本轮明确批准的成熟工程接线与离线验收。证据为本对话内模型辅助实现、实际执行与知情源码复核；外部独立验证待取得。


## 实际离线顺序

`RuntimeConfig.from_confirmed` → 替身路径事实 → 依赖事实 → Schema2 事实 → `construct_store` 一次 → `bind_store` → 替身 listener 一次 → 封闭元数据 → `finally` 关闭拥有资源。D11 检查确切事件序列、构造次数、world 摘要保持及零 SQL/key/read。

规范 seed 单独构造。它保持一个 grant 和一个 QUEUED 请求，预算 limit=1、reserved=1、spent=0；请求 digest 使用既有 `normalized_request` 与 caller 规则。version=2、两条历史明确标为合成准备来源。D07 校验字段关系，D08 使用公开固定向量加密、在拥有的 `:memory:` SQLite 中建 Schema2 并往返核验。此过程没有连接实际 AuthorityStore。

未来真实顺序仍须保持：新根/ACL → 批准 manifest/源/依赖 → 新 state/TLS 材料 → 规范 seed 加密和新 Schema2 → 唯一 Store → Dormant 绑定 → Handler/TLS → runtime 元数据。真实总 SQL 与文件预算待冻结；R18 中预置库后构造约 7 次 SQL 只覆盖构造阶段，准备器费用另计。

## 两种绑定证据

1. 新 `RuntimeContext` 的离线 registry 捕获同一 Store/connection/lock，计注册次数并返回 `DORMANT_SOURCE_BOUND` 元数据；直接构造、重复绑定、替换 lock、关闭后复用均有拒绝检查。该 registry 保存配置、source digest、epoch 的离线关联，当前没有真实会话激活发行者。
2. 既有 R16 的 `mount_authority_host`、可信 ticket/peer 与进程内 `_SESSION_NAMESPACES` 继续保留。原 20 项 A1 和 24 项 H1 在原断言下通过，覆盖会话总量、并发、重放、issuer 重建和来源别名。新 `services.serve` 保留既有默认 ticket 路径。

二者在离线证据中分别验证。当前完整真实链尚需证明：可信 OS/启动发行者 → 实际 epoch/config/source → 授权会话 ID/读 scope → R16 mount ticket → 同一 Store → 总量槽。D14/D15 只验证离线字段与关闭状态，跨真实进程重启的旧授权失效需要未来实际 issuer/epoch 合同。该责任记录为 `SOURCE_OR_REFINEMENT_GAP`。

## 实际 services 钩子

`serve` 新增可选 keyword；给定 runtime context 时，接纳检查位于配置读取之前。当前离线上下文在此安全拒绝。现有 Store 构造之后绑定 context，再执行原 R16 mount 与 Handler 定义；listener/TLS 准备后上报引用，`serve_forever` 使用 finally 清理。

D23 通过 AST 校验上述位置与默认兼容性。该检查保证所核对的源码顺序，实际服务行为仍待 D1-B 验证。未来打开 live 路径前，还须扩展异常清理包络，使 Store 构造后至 TLS/ready/serve 前的所有失败均关闭拥有资源，并验证真实 `shutdown` 调用上下文；当前 `serve_forever` 外围 finally 的覆盖面有限。

## Dormant 和资源清理

离线上下文的 `issue_permit` 与 `read_state` 固定拒绝 P2；绑定操作自身零 SQL、零 key、零 world 修改、零 Provider、零 permit。D12/D13 及 D11 验证这些属性。默认挂载状态与未来 P2 接纳分别管理。

listener 替身返回后先登记为拥有资源，再校验 loopback/port/TLS，策略拒绝时仍进入清理。D20 覆盖端口冲突和非法地址，D21 覆盖 shutdown 抛异常后继续 server_close/connection.close。所有成功/失败为离线拥有对象；无真实进程停止操作。

## 元数据

P1a 当前接受一个精确请求（environment、PID、创建时点、epoch、source/config digests），通过 provider 读取单目标并验证封闭字段、大小和脱离内部引用。实际测试的 PID、epoch、source digest 均为合成替身值，`source_kind=OFFLINE_SIMULATION`，`INSTANCE_RUNNING=false`。

元数据中的相对 DB/key 路径只表示约定引用。它们没有证明实际文件存在、ACL 正确、进程拥有 endpoint 或真实源码匹配。P1a 真实 provider 与独立授权待补。

P1b 保持 R18 延期范围，仅提供两条固定 PRAGMA 的静态合同。D08 的公开内存 Schema2 验证和 P1b 实际运行核验分别登记。P1b 专用脚本未创建。
