# 静态准入与历史完整性

本轮总体为R42_STATIC_PREFLIGHT_BLOCKED。

| 层次 | 实际状态 |
|---|---|
| SPEC_REVIEWED | true；28身份、输入、故障与取证方法已审阅 |
| DRIVER_IMPLEMENTED | false；创建条件尚未满足，文件不存在 |
| STATIC_VERIFIED | false；驱动AST/路径/副作用不可在无代码时认证 |
| DYNAMIC_NOT_RUN | true；28个NOT_RUN，动态suite次数0 |
| 实际输入pin与六函数身份 | 已核对一致 |
| 原28字段和ID | 全部保留，R40/R41原字段差异0 |
| Fault specification ready | 尚待T20范围和资源门；设计已交付 |
| 可执行source/command/resource | 未闭合，argv=null |

## 独立阻塞

1. R41创建标记为false，其内容是phase_A_requested；按R42条件保留规格路径。
2. 专用驱动及源码摘要缺失，AST和输出强制执行机制没有实物。
3. T20原0调用数的主操作/全程范围未显式规定；计数提案已具体化，原预期没有改写。
4. 资源累计量、fault/lock/目录及整进程内存/监督机制缺上限；完整取证负载及运行时来源闭包待实际源证明。

## 容量与其他门

R41修复使原来被Poison阻断的一些既有收尾调用恢复资格。其调用图没有新增Journal循环或新receipt路径，正常检查点仍为232+O+C+W，O/C/W继续采用R39定义：不同ORIGIN_OBSERVED、不同ORIGIN_CLASSIFIED及WRAPPED_ORIGIN_OBSERVED条数。

原13cap、2MiB及90/115/120限制保持。新增21字段、910B部件原始界、直接检查点失败分类行和重复嵌套必须计入异常联合需求；单项界与存储guard各保留其范围。T01等模型前提没有变成完整68运行可达证据。

即使未来全部28项通过，也只支持已列局部性质。G2完整L0容量UNPROVEN、G3九组原完整内容义务、G4七变化/五缺失及D1-B1部分实现继续分别管理。

## 保全

R41的2457项当前基线加R41全部26文件，共2483项纳入本轮结尾核对，含5个既存缺失。旧42份SOURCE_LOCK按原字节保留。Runner和原55项工程/测试/fixture pin保持，拟驱动路径在入口、出口都应不存在。

本轮只写R42文档/结构化数据。没有运行目标函数、导入Runner/测试、创建实际test Journal/SQLite/密钥/测试子进程或服务。static verification与未来dynamic PASS分别登记。
