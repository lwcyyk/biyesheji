# R17范围与R16来源绑定

2026-11-11，Asia/Shanghai。当前对话内知情模型辅助部署准入审查，外部安全核验待取得。本轮为ANALYSIS_ONLY，工程源码修改、项目模块执行、测试、部署、运行进程查询、DB/key访问、RPC和P1操作均为0。

## 继承的实际结果

R16目录22件文件已全文读取或JSON完整解析，五轮原始RESULTS与stdout.log静态核对。最终run_005原字节副本、六份执行源码及输入hash相符；20项新测试、24项H1回归、558＋1361=1919条检查满足。18个内存SQLite连接和故障/修复证据保留，未重跑。

本轮初检1355次来源比较全部匹配。R16两个获准修改文件按其**最终**版本锁定；更早的旧版本引用通过R16明确的新旧版本映射与原字节快照继承，未将旧hash直接冒充当前代码。sources/PRECHECK_LOCK及R16_BINDING列出准确范围。

保持A1_IMPLEMENTED、A1_SYNTHETIC_TESTS_PASSED；真实服务导入、生产身份、WAL/ACL/AES-GCM和实际部署仍未验证。

## 新目标选择

研究者本轮对一次性环境询问回复“1”，按第一选项登记为**全新隔离专用Authority实例，只使用合成数据**。该回复仅固定环境类型；environment_id、负责人、部署根目录、服务主体、Python、端口和数据范围尚未提供。D1/P1/P2授权值继续为PENDING。

source receipt见sources/TARGET_SELECTION_RECEIPT.json。所有实际运行字段继续UNRESOLVED，不用历史实验路径、示例账户或假PID代填。

## 定向来源与阅读范围

工程根为D:/毕业设计/auth-lifecycle。短ID绑定SOURCE_LOCK中的SHA和摘录行号。

| ID | 来源 | 范围 |
|---|---|---|
| C01 | online_state/services.py | serve 277–365、Controller初始化/恢复及SingleActive |
| C02 | online_state/storage.py | 构造47–91、execute/cipher/read_state 93–120、旧call和来源处理 |
| C03 | online_state/dsat_authority_host_activation.py | 当前393行，重点issuer/注册、全局K、read gate、认证/dispatch |
| C04 | online_state/dsat_authority_read_host.py | 当前受控最终版；注册接口、claim、计费/清理及白名单 |
| C05 | scripts/read_dsat_authority_once.py | 全文；offline-only/真实transport缺失 |
| C06 | online_state/lab.py | 初始化47–102、启动/关闭116–199 |
| C07/C08 | online_state/cli.py / scripts/online_state.py | 全文；旧入口及参数 |
| C09 | online_state/protocol.py | EventLog、TLS Client和write_json |
| C10/C11 | migration.sql / migration_2.sql | 全文 |
| C12 | pyproject.toml | 依赖与SQL包数据声明 |
| C13/C14 | isolation_service.py / native_isolation_service.py | 启动诊断、配置/环境处理 |
| C15 | scripts/m6_environment_acl.py | 全文静态；硬编码旧.runtime及可写ACL，不执行 |
| D01 | README.md | 在线状态与实验入口指引 |
| D02 | docs/experiments/README.md、AUDIT.md | 历史原生环境/私密区边界；不跟进.runtime |
| D03 | mainline_online_state_v1/ACCEPTANCE_REPORT.md | 全文；历史合成TLS/Authority与清理记录 |

检索仅限研究/工程中的已提供非秘密文档与源码。未打开.runtime、secure、真实配置、数据库或凭据。顶层目录名出现不构成运行环境确认。

## 权限

R17附件只允许文档/静态分析，第六节将D1/P1a/P1b/P2分开，第七节要求命令真实存在且目标已定。当前缺失的目标和脚本/桥接条件都写入阻塞，不据A1通过执行任何环境操作。A/B/AB及既有数学/先例裁决沿用。
