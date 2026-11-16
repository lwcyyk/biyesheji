# 冻结44项实际结果

最终原始来源：`2026-11-11_r15_activation_offline/run_005/RESULTS.json`与stdout.log。A1_ACTUAL_RESULTS是原字节副本。

| 分母 | PASS | FAIL | ERROR | SKIP | 内部检查 |
|---|---:|---:|---:|---:|---:|
| 新A01–A20 | 20 | 0 | 0 | 0 | 558 |
| 原H01–H24回归 | 24 | 0 | 0 | 0 | 1361 |
| 合计冻结身份 | 44 | 0 | 0 | 0 | 1919 |

新增独立测试分母为20；故障、并发、复用和CLI场景作为原用例内部检查展开。原H1测试文件/断言、runner、R14锁保持原字节，由新runner受控加载原测试类，未执行旧runner预检或修改旧hash使其通过。

## 五轮历史

| run | 新测试 | H1回归 | 变化 |
|---|---|---|---|
| 001 | 20 PASS | 24 PASS | 初始实现和原范围验证 |
| 002 | 19 PASS/1 FAIL | 24 PASS | A09发现重新创建issuer、改来源别名后同一授权SELECT累计2次 |
| 003 | 20 PASS | 24 PASS | 新模块增加进程级connection/授权/epoch/scope命名空间锁，阻止重新挂载 |
| 004 | 20 PASS | 24 PASS | 补全完整a/W等价、CLI重连和注册/遥测计量 |
| 005 | 20 PASS | 24 PASS | 结束阶段观测属性故障安全丢弃数据、保持计费并清理inflight；最终冻结 |

五轮argv、Python/SQLite版本、源/输入hash、代码快照、stdout、错误和结果均保留。run_002的issuer_recreation_escape原始条目实际记录了2次SELECT和成功状态，修复后未删除或替换该证据。

## 新20项

| ID | 通过的核心条件 |
|---|---|
| A01 | 默认挂载关闭，属性陷阱未触发，零源I/O |
| A02 | 同Store/lock/connection绑定；替换锁/连接拒绝 |
| A03 | 字符串、dict、伪造ticket/peer无效 |
| A04 | 裸LOCAL/注册字符串拒绝；默认合成另由24回归核验 |
| A05 | 合成受信HMAC上下文经实际核心到达原R12适配器 |
| A06 | 广权限controller及Agent默认无读取身份 |
| A07 | scope/grant/rid/path扩展拒绝；跨scope目标rid无法替换 |
| A08 | 当前撤回/过期在源前拒绝 |
| A09 | 三permit/三线程最多1读；重放、新permit、新issuer/别名不重置 |
| A10 | 旧epoch、旧ticket无法重新挂载或读源 |
| A11 | 固定SQL相同、完整(a,W)等价、版本/Schema、无额外源读取 |
| A12 | 长度/Schema/缺行在key前拒绝 |
| A13 | 不结束外来活动事务；回调重入无第二次读 |
| A14 | 日志/key/decode/返回故障及软超时保留槽/费用 |
| A15 | 无源DML/旧call；旧分派保留并与新分支隔离 |
| A16 | canary、repr、pickle、输出别名和闭合摘要检查 |
| A17 | Store之后/Handler之前的AST挂载位置；真实依赖未导入 |
| A18 | CLI严格参数、单次离线调用、默认关闭、重连后replay |
| A19 | 一读+6额度规则；预算失败只占槽，不执行SQL；无rearm |
| A20 | 源内撤回在出域前丢弃数据，保留费用/缺口 |

## 不变量关联

A1-P1→A01/A03/A04；P2→A02/A05/A17；P3→A05–A08/A20；P4→A09/A13/A18/A19；P5→A10/A14/A19；P6→所有invoke世界hash及A09批次/A15；P7→A11–A14/A19和SESSION_GATE_AUDIT；P8→所有输出验证/A16/A18；P9→原24项实际回归；P10→runner审计及A17。

18个自有内存SQLite连接，连接上限32。网络/子进程/私密文件/文件DB/ATTACH/扩展/越界写入尝试0，生产模块导入列表为空。业务拒绝、SOURCE_BINDING_CONFLICT、UNKNOWN与资源错误满足预期时记PASS，精确业务状态逐项留在原始JSON。

阶段限制：服务挂载是AST验证＋纯核心执行，真实服务导入与生产身份仍未验证。SQLite3.53.1仅是本次隔离解释器实际内存引擎版本，不能代替未来Authority部署版本。
