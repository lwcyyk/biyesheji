# VPass SQLite migrations

> 迁移文件中的 VDNS-PM 是冻结 legacy wire 标识和历史名称。已发布 SQL 文本、文件名和校验和不因 VPass 展示名迁移而修改。

当前可执行研究原型schema版本为`8`。迁移文件发布后只追加，不覆盖。`0001_initial.sql`属于CP-1历史资产，运行时拒绝把它静默升级为CP-2；新建数据库从`0002_v2_initial.sql`开始并依次应用至`0008_stage2_protocol_closure.sql`。

| 版本 | 名称 | 作用 |
|---:|---|---|
| 1 | `0001_initial` | CP-1历史schema，只供历史验证 |
| 2 | `0002_v2_initial` | CP-2基础、32字节CredentialID、Root/Recovery Capsule、RouteMap与字段对象 |
| 3 | `0003_g2_core` | G2凭据核心与事务投影 |
| 4 | `0004_g3_lifecycle_sync` | 生命周期、站点尝试、同步manifest与冲突 |
| 5 | `0005_g4_vdns_transparency` | VDNS、透明日志、proof与检查点 |
| 6 | `0006_g5_local_api` | 本地API幂等和durable operation |
| 7 | `0007_g6_privacy_response` | 隐私审计与可选事故响应投影 |
| 8 | `0008_stage2_protocol_closure` | 研究型最终序、E0～E5证据和撤销三层状态 |

v8新增`final_order_snapshots_v2`、`final_order_candidates_v2`、`final_order_receipts_v2`、`final_order_checkpoints_v2`、`final_order_resolutions_v2`、`site_confirmation_evidence_v21`和`device_revocation_layers_v2`。这些表只证明Stage 2研究适配器的持久化闭环，不代表生产多节点共识。

## 运行时合同

- 使用SQLite 3.37或更新版本，因为schema使用`STRICT`表。
- 每个连接执行`foreign_keys=ON`、`journal_mode=WAL`、`synchronous=FULL`、`busy_timeout=5000`和`trusted_schema=OFF`。
- Go适配器固定一个连接，领域写使用短`BEGIN IMMEDIATE`事务。
- 网站调用、对象fsync、透明日志RPC、Anvil RPC和高成本KDF不得在数据库写锁中执行。
- 数据库打开时验证所有迁移版本、名称、SHA-256和`integrity_check`。
- `user_version=1`直接返回显式CP-1迁移错误；真实数据必须导出、重加密并产生MIGRATE事件。

## Stage 2迁移身份

`0008_stage2_protocol_closure`的DDL核心SHA-256为：

```text
7c11ff6b5af6959c41c160789f395187440aa385aec441dbe034a32276b13b07
```

摘要覆盖元数据插入前的精确迁移字节，避免自引用。Go运行时对版本2～8的迁移身份逐项验证。`internal/adapters/outbound/sqlite/database_test.go`覆盖新建、逐版本升级、篡改拒绝、schema版本和表数量；`migrations/tests/0008_constraints.sql`覆盖v8约束。

## 验证

仓库使用嵌入式SQLite驱动执行完整迁移链，推荐验证命令为：

```sh
go test ./internal/adapters/outbound/sqlite -count=1
```

系统安装了`sqlite3`时，还可逐个运行`migrations/tests`中的SQL约束烟测。缺少CLI不能写成已执行；Go数据库测试仍会真实应用同一嵌入迁移字节。
