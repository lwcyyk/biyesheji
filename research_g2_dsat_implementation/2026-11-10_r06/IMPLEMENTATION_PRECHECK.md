# R06实施前检查

2026-11-10。用户本轮明确授权S1—S2离线成熟代码、合成夹具及两个指定测试；旧候选创新门、S3真实写回和S5原生边界继续保留。

- 工程根为D:/毕业设计/auth-lifecycle；无Git元数据。以BASELINE.json逐字节锁定现有源码/测试/脚本与R05输入，无法用Git判定“用户未提交修改”；保留全部已有文件。
- 新增dsat_projection.py、dsat_types.py、dsat_flow.py、check_dsat_certificate.py及两个指定测试/合成夹具，路径初查无冲突。运行层storage/services/native_provider、旧证书/摘要/窗口及pyproject保持原字节。
- 本地3.10/3.12/3.14均无NetworkX/等价已知流库；用户确认没有安装。缓存/工作区定点检索未找到本地NetworkX包，另有一个无关缓存目录拒绝访问。禁止联网安装，S2优化求解按缺库分支阻塞；网络构造和独立检查继续实施。
- pytest未安装，采用标准库unittest，只加载test_dsat_projection.py和test_dsat_certificate.py。独立检查器仅处理本轮冻结的合成输入。
- 所有字段/权限/来源信任均为显式SYNTHETIC_CONTRACT，不能提升为真实原生认证。输入严格白名单，输出最小元数据，真实secret、.runtime、Provider初始化和在线AuthorityStore均不触及。
- 测试运行前审查导入/文件/网络副作用；测试允许读取合成夹具和写本轮结果，不调用真实服务、不跑整仓或旧原生批次。

结论：S1、独立检查器、合成输入和限定测试准入；最小费用流后端缺依赖，保持PARTIAL_IMPLEMENTATION。没有安装新包、启动新算法或扩大原生操作。
