# 原生接线前的接口映射

2026-11-05。本轮采用已确认 ONLINE_TRUSTED_STATE_V1，候选密码机制状态为 FROZEN。源码修改前清单与副本已保存在 PRECHANGE_MANIFEST.json 和 prechange/。

| 现有入口 | Casdoor 对应能力 | 必要修改与边界 |
|---|---|---|
| FakeProvider.perform | password 发行、refresh_token 刷新、cookie-free UserInfo | 新增显式启用的限定原生 profile，固定方法、字段、端点和账户；默认保留假 provider |
| 单字符串 material | AT/RT 及元数据束、初始登录材料 | 使用有类型的材料束，区分原生字段、来源与推导字段，兼容旧合成字符串 |
| payload.value | issue 的空参数、refresh/userinfo 的 source_rid | 请求摘要覆盖新载荷；来源材料仅从同批准的已登记结果解析 |
| FakeProvider.lookup | 原生 AS 缺少当前模型所需的 attempt 结果接口 | 仅可补收可信适配器已持久接收的精确结果。未持久接收时保持 UNKNOWN |
| Controller.record_result | 原响应与 rid/attempt/origin/摘要绑定 | 校验签名、账户、客户端，再原子登记完整束。原生响应丢失保持原义务 |
| 本地 revoke | LOCAL_REVOKE_COMMITTED | 继续只承诺本地新放行截止，原生逐材料处置另行登记 |
| QUARANTINED | 已知旧代次结果的原生撤销 | 增加持久处置尝试和原生响应收据，HTTP 200 的含义单独验证 |
| 独立效果真值 | 原生 HTTP 记录与限定账户原生状态 | 运行者和评分者通道分别保存。评分者额外材料不得回流运行决定 |

现有实验 providers.Casdoor.setup 包含组织/应用创建或更新。本轮仅复用所核实实例和已有应用，采用只读应用核验及四个新账户的专用接口，避免触及其他配置。

原生预算在首次 HTTP 前持久化，总量 240，环境/建户 40、方法 60、测量 80、清理 60。每次调用在发送前消耗一个对应槽位，失败和查询照常计费。清理始终拥有独立预留。

本轮三个重要缺口是旧单字符串无法表达真实 AT/RT 关系、FakeProvider 的通用查询强于原生接口、已有本地撤回无法直接承诺原生后代关闭。本轮通过类型模型、明确的适配器持久收件箱和分层原生处置分别处理。

## 实际交付对应

材料实现位于 online_state/materials.py，事务兼容和处置位于 storage.py/migration_2.sql，固定原生传输与预算位于 native_http.py，适配器位于 native_provider.py。services.py 仅在受保护配置显式指定 native_profile 后创建真实适配器，默认继续使用 FakeProvider。

native_acceptance.py 与 scripts/native_casdoor.py 提供四轨迹入口。measure_native_casdoor.py 共享受限传输/预算工具，使用独立观察规则。score_native_casdoor.py 独立解释权威状态、来源和测量结果。该共享传输部分按可信输入基础登记。

四条原生轨迹均已完成。M2-03 的原始评分启动次数规则产生假阳性，保留原判定并在受保护副本上复核。仅原未采样 M2-04 使用原账户/预算槽位续行。后续的中断期接纳缺项用零原生请求本地补核单独登记。
