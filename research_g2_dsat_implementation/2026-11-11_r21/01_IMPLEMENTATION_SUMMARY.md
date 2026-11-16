# G2-R21实施摘要

日期：2026-11-11。范围：R21明确批准的九目标及离线合成验收。过程为本对话内模型辅助实现、实际执行与知情复核；外部独立核验待取得。


九个逻辑目标均已落地。最终三组单元运行结果为 **120 PASS，FAIL/ERROR/SKIP/BLOCKED/NOT_RUN均0**，2366条内部检查满足。交付源码审查另发现跨进程接纳责任尚未闭合：**完整合同验收为117 PASS、3 BLOCKED**，整体状态为 **D1B1_PARTIAL_IMPLEMENTATION**。

两套统计分别保留。120是本轮真实重跑的52＋24＋44，不包含R19历史通过数；3个阻塞来自F23/F26/T45的较强跨进程条件，单元runner原始输出保持原字节。

| 九目标 | 实物 |
|---|---|
| services.py | 保留旧服务；新增受控offline listener工厂、LiveContext在配置I/O前拒绝真实运行 |
| storage.py | 可选strict bootstrap路径，原默认和业务方法保持 |
| run_h2_authority_service.py | 六操作offline parser和受控分派，原D1-A参数兼容 |
| dsat_authority_live.py | opaque test issuer/context、来源/实例/epoch/同Store关联、P2固定拒绝 |
| dsat_authority_lifecycle.py | 所有权栈、真实新文件SQLite15SQL、strict Store7SQL、阶段/日志/分类恢复 |
| dsat_windows_runtime.py | 真实自有Windows SID/PID/创建时点/file-ID、私有DACL、独占锁、句柄交接、Event及stub管理 |
| test_dsat_authority_live_lifecycle.py | F01–F28/T29–T52，增强子断言保持原ID |
| run_dsat_authority_live_lifecycle_tests.py | 三域runner、固定worker协议、拒绝钩子、日志/快照/预算 |
| 新fixture树 | 原冻结计划、确认配置、公开向量副本及新合成哨兵 |

仅修改3个既有文件，新增5个Python文件及1个fixture子树。研究目录中的汇编脚本仅处理报告、哈希和JSON。源码及入口定位见D1B1_FILE_LOCK.json。

实际底层行为包括11次新临时文件SQLite连接、6个拥有的测试子进程、2个测试state key、1套TLS测试材料和2次SSLContext加载。Authority网络服务、真实RPC、P1/P2、生产库和密钥访问全部0。

本轮离线核心提供了可复现的启动/失败关闭基础。独立shell中的分阶段操作、真实部署接纳、原生有界网络适配与一次性启动批准仍须补齐，当前材料没有把它们登记为可部署成品。
