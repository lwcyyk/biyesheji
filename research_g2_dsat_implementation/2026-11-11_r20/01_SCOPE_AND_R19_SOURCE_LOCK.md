# G2-R20：范围与 R19 实际基线

日期：2026-11-11。本轮为 D1-B0 执行准入审查。证据类型：本对话内知情模型辅助源码审查、合同设计及纸面故障分析；外部独立验证待取得。

本轮已完成真实部署所需的接口、身份、资源、生命周期、清理与分级授权规格。工程修改和项目测试执行数均为 0，部署执行权限保持关闭。文档汇编脚本仅处理文本、JSON、AST 和文件摘要。

## 继承证据

完整读取 R19 六份报告；解析结构化结果、运行历史、文件锁、命令锁和来源记录，并核对全部 2056 条内部检查的既有结果。结果读取属于证据复查，项目测试本轮执行数为 0。

| R19 事实 | 本轮使用范围 |
|---|---|
| 七目标代码落地 | 保留原源码，作为拟议 live 差异的起点 |
| 新 24 项、A1/H1 原 44 项，最终 68 PASS | 继承历史离线结论；本轮无新增 PASS |
| 137＋1919＝2056 条内部检查满足 | 逐记录核对，检查数包含重复断言 |
| CPython 3.12.14 AMD64、crypto 50.0.2 可导入，公开 AES 向量通过 | 限定功能可用性；完整 Authority runtime 兼容性待验 |
| 内存 SQLite、合成替身 | 与真实数据库、TLS、OS 接纳分别管理 |
| 默认 Dormant、R16 总量门回归通过 | 单进程受控合同；真实生命周期保持条件在本轮明确 |
| 部署根未创建，真实访问为 0 | 本轮继续保持 |
| 一次早期编码失败及后续四次 suite | 全部历史证据保留 |

R19 `SOURCE_LOCK.json` SHA-256：`1f19cdcad2be51e870d339e90b8db99935dd45eddd1aed18353c8fdc57189179`。继承结果及摘要定位见 `sources/R19_INHERITED_RECORD_REVIEW.json`。

执行前复查 R19 最终清单与原 1441 个历史来源比较行，差异为 0。合并重复路径后，本轮保护清单有 1133 个文件，包括 R19 报告/离线日志、既有源码及历史资料。R19 的 services 允许修改映射已作为历史事实纳入，本轮既有文件允许修改清单为空。最终复查见 `sources/DELIVERY_QA.json`。

## 参数与权限分开

继续继承已确认的研究者角色、根目录、Python、`h2_*_001` 数据范围和 `127.0.0.1:27443` TLS 策略。确认文件保持原字节：

`D:\毕业设计\research_g2_dsat_implementation\2026-11-11_r18_parameter_confirmation\H2_ENVIRONMENT_CONFIG_CONFIRMED.json`

上述五项参数沿用。本轮无需重复确认。真实 SID、数据库和密钥创建权限、代码实施、端口绑定与后续读取分别属于未来授权。

| 阶段 | 当前状态 | 允许内容 |
|---|---|---|
| D1-A | 已完成离线验收 | 继承 R19 |
| D1-B0 | ANALYSIS_ONLY | 本轮合同、静态分析、报告 |
| D1-B1 | AUTHORIZATION_PENDING | 拟议九目标代码及限定离线测试 |
| D1-B2 | NOT_AUTHORIZED | 拟议新实例初始化、一次启动与停止 |
| P1a/P1b/P2 | NOT_AUTHORIZED | 独立保持 |
| S3-B2/S5 | NOT_AUTHORIZED | 独立保持 |

## 新增的关键源码事实

| 事实 | 当前源码定位 | 影响 |
|---|---|---|
| Authority 未使用进程级单活锁 | `services.py:22` 定义 SingleActive，`:46` 仅 Controller 使用；`:284` Authority 分支直接构造 Store | 需要 Authority 专用锁；现有名称无法承担该保证 |
| Store 构造有返回前资源风险 | `storage.py:60` connect；后续 PRAGMA、日志、marker、配置写入均可失败 | 调用方尚未取得对象，外层 finally 单独不足以捕获连接 |
| 服务清理开始过晚 | `services.py:277`–`:378`，finally 从 serve_forever 处开始 | bind、TLS、Ready 发布失败需统一资源包络 |
| shutdown 有线程前提 | 实际 CPython `Lib/socketserver.py:247`–`:255` | 需要避免在未运行的 loop 或同一线程等待 shutdown |
| 原 HTTP 服务按请求建线程 | `services.py:362` 与 CPython `Lib/http/server.py:146` | 需要有界 live 分支才能声明线程/连接预算 |
| 原初始化器扩大角色与端口 | `lab.py:47` 起生成三角色、密钥与动态端口 | 本实例采用独立 Authority-only 准备器 |
| 原脚本仅支持 offline | `scripts/run_h2_authority_service.py:17` | 六操作当前均缺入口；实际 argv 保持空 |

精确函数行号与源摘要见 `sources/SOURCE_LOCATIONS.json`；完整差异责任见 `D1A_TO_D1B_GAP_MATRIX.json`。本轮对原协议、业务 mutator 和数学算法均无改动。

本轮新合同属于成熟部署工程及安全边界精化。A/B/AB 独立算法创新资格、严格分离门和既有淘汰结论沿用。TYPED_O、O_REVISION、SOURCE_OR_REFINEMENT_GAP 继续保留；COL2026 主动检索暂停，FS23 延期状态沿用。
