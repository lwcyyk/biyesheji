# Stage 2剩余缺口

> 当前产品名为 VPass；本清单按 Spec 2.1.0 / G6 边界继续跟踪。

## P0：进入第三阶段前仍需持续跟踪

| 缺口 | 当前状态 | 下一步验收 |
|---|---|---|
| 新设备可信初始检查点产品流程 | PARTIAL | 已有设备/Recovery承诺/带外摘要三条流程均有端到端测试；云TOFU不能高风险写 |
| 撤销三层API/UI组合 | PARTIAL | 三层独立状态可查询，旧密码风险可见，网站修复四态逐项持久化 |
| 研究模块组合接线 | PARTIAL | 本地客户端接口的state/sync/device端点接入真实研究端口，不再只排队；仍保留生产边界 |
| 冲突多进程试验 | PARTIAL | 两个独立本地安全客户端/SQLite进程经HTTP同步产生分支并由Authority发现、裁决、恢复 |
| FinalOrder与透明日志最终化联动 | PARTIAL | provisional回执进入日志/checkpoint后状态转换可恢复；分叉停止高风险写 |

## P1：安全实现

| 缺口 | 状态 |
|---|---|
| OS key store/硬件支持 | NOT_IMPLEMENTED |
| 真实Chrome/Chromium Native Messaging自动化 | NOT_IMPLEMENTED |
| 真实E4 Connector、issuer治理、nonce与撤销 | NOT_IMPLEMENTED |
| 生产服务认证、TLS、租户隔离与高可用 | NOT_IMPLEMENTED |
| 外部密码学/安全审计 | UNVERIFIED |

## P2：第三阶段证据

- 建立每次测量原始JSONL/CSV、错误样本、环境和确定性汇总；
- 使用两个独立进程和真实HTTP测量10k初始/增量同步；
- 把Stage 2定向故障测试保持为`LOCAL_INTEGRATION`；
- 重跑并保存第三阶段工作树的govulncheck/SBOM/license/secret scan；
- 为每个论文数值绑定claim ID、证据等级、数据范围和日期；
- 对完整L1～L5与Merkle微基准分别测量，禁止复用历史`2.302853 ms`作为最终G7结果。

## P3：后续研究

- 生产多节点/BFT Final Order Authority；
- 公网/生产同步存储部署；
- 移动端和低配设备性能；
- 真实网站E4生态；
- SCOPE-ZK实现和E8比较。

## 阶段判断

项目已具备进入第三阶段“实验与证据冻结准备”的代码基础。项目尚不具备进入G7研究原型冻结或生产发布的条件。SCOPE-ZK、生产共识、真实E4和公网生产同步存储继续明确为`NOT_IMPLEMENTED`。
