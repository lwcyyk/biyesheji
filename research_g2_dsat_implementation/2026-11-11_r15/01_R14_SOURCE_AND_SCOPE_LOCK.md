# R15：来源、实际状态与权限

2026-11-11，Asia/Shanghai。当前对话内知情模型辅助静态工程审查，外部独立安全审查待取得。阶段为`H2_PREFLIGHT_ONLY`。本轮工程源码修改、项目模块执行、测试、数据库连接、运行环境查询、真实key读取和RPC调用均为0。

## 继承与复核

R14目录实际19件文件已全文读取或完整JSON解析，四轮RESULTS和stdout.log静态核读，最终代码、夹具、结果副本和交付hash已核对。记录见sources/R14_EVIDENCE_REVIEW.json。

- 最终run_004：24/24 PASS，1361条检查满足；旧测试重跑0。
- 73次**常规接口调用**及3组并发/排序场景产生80份输出；其中34次实际进入合成源读取。73这个数字包含门前拒绝，不表示73次世界状态解密。
- 合成世界前后摘要相同，34次模拟额度支出、33条源遥测成功、33次模拟key读取、32次模拟decode尝试。真实SQL/key/服务调用均0。
- run_002的返回异常计费缺陷及修复链保持原记录；后两轮24项通过。其失败调用逐调用条目不完整的记录限制继续注明。
- 原1259次保护比较均匹配；连同R14交付、H1实际源码/输入、原始结果等，本轮初检1289次比较（929不同路径）匹配。保护范围逐路径留存于sources/PRECHECK_LOCK.json。

保持`H1_IMPLEMENTED`、`H1_SYNTHETIC_TESTS_PASSED`。本轮结果属于源码支持和准入规格，真实部署验证继续待取得。

## 当前源码短ID

源码根为`D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/`。本轮C系列独立命名，行号绑定SOURCE_LOCK中的SHA。

| ID | 文件 | 核读范围 |
|---|---|---|
| C01 | storage.py | 21–159、197–259及版本/来源相关定义 |
| C02 | services.py | Controller初始化/恢复/权限与serve/Handler完整路径 |
| C03 | protocol.py | 全文 |
| C04 | lab.py | 初始化、配置权限、生命周期47–125；相关原结论复用 |
| C05 | dsat_authority_read.py | R12全文既有核读复用；当前scope、原请求验证、context、读路径和输出定向复核 |
| C06 | dsat_authority_read_host.py | 当前473行全文 |
| C07 | cli.py | 全文 |
| C08/C09 | migration.sql / migration_2.sql | 全文 |
| C10/C11 | H1测试 / runner | 继承最终运行快照并定向复核RPC、许可、故障与执行边界 |
| C12/C13/C14 | pyproject.toml / H1 venv的pyvenv.cfg / materials.py | 声明的online-state可选依赖、解释器元数据、密码学导入段落 |
| D01 | R13保存的sqlite_pragma.html | 本轮读取table-valued PRAGMA相关段落，复用既有官方获取记录 |

`sources/SOURCE_EXCERPTS.md`保存带行号摘录。SOURCE_LOCK区分当前磁盘源码hash与实际运行版本；本轮从未查询运行进程，磁盘hash不能自行证明进程加载了同一版本。

## 本轮新增的准入责任

1. H1每张permit单用；RPC可再次发行新permit，尚无“一个H2授权总共一次读”的会话级闸门。[C06:305–320；C10的OfflineAuthorityRPC]
2. H1硬性限制SYNTHETIC_ONLY，context也固定使用该标签；SQL计数固定0、key观测未知。真实注册需要受信来源对象和计量接口。[C06:359–370,426–431]
3. 当前Authority Handler识别Bearer后，旧分派没有接收identity。新的读取操作必须直接取得认证上下文，并绕开普通call事务。[C02:301–320；C01:134–148]
4. Store的cipher每次重新读取key文件；已初始化对象不意味着新增读可以省掉key访问。[C01:103–120]
5. H1域内可观察全部tuple记录，首次P2还需核对预定grant和已指定rid；最终对外仍采用原最小摘要，避免扩大字段范围。
6. 已批准H1 venv的常规site-packages中未发现cryptography包目录，且include-system-site-packages=false；pyproject声明online-state可选依赖cryptography==50.0.2。其它导入路径及服务端实际环境仍未知，H1的标准库通过结果未验证services/storage可导入。本轮只查元数据，未执行导入或安装。

这些为成熟接线与来源保证的新增工程责任，未改变A/B/AB或既有数学结论。

## 权限来源

本轮附件：`C:/Users/a1887/.codex/attachments/859645b2-d5eb-43f3-bdc5-11a30ff9f3b3/已粘贴的文本.txt`。第一节仅允许静态分析和授权申请，第十二节区分P1/P2，第十六节明确入口缺失时优先最小激活的离线实施申请。

因此本轮只形成一份可审批的**离线激活实施申请**及P1/P2待填值模板；未获得的运行身份、实例、路径和scope全部保持null/UNRESOLVED。没有通过扫描.runtime、secure、进程列表或数据库来填值。
