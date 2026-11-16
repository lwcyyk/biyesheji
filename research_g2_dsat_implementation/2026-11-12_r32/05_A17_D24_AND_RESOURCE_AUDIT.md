# A17、D24、资源与历史

A17实际PASS，原关键断言MOUNT_AFTER_STORE_BEFORE_HANDLER及NO_FAKE_OR_REAL_PRODUCTION_DEPENDENCY_IMPORT均为true。A1_loaded和A1_finished模块集合均无cryptography；原测试及导入屏障保持，sys.modules伪造/删除数为0。

D24实际PASS，原P1A_OFFLINE_CLI_VALID_RECORD及拒绝未知argv/净化输出断言均为true。仅两份冻结JSON被投影；原输入与新目标摘要分别一致：metadata为 `1c6283d77d75d9617adff2b06cea39bc1658aa4b9c0d9ee2e823fcc2c8d50037`，request为 `90cf2149c79ccd43caa82aa8da51d6542b5776ac8bd9ec5ecc01cb163f9f0c69`。实际context_restored=true，生产读取白名单保持。投影异常清理的额外故障分支保持静态范围。

| 资源 | 最新实际记录与边界 |
|---|---|
| suite / 自动重跑 | 1 / 0，额度剩余0 |
| 内存SQLite累计 | A1=18，H1=0，D1A=1，总19；D1A组后检查点 |
| SQLite活跃峰值 | 18；D1A组后尚活跃1，发生在正常finally清理前 |
| SQL execute / rollback | 376 / 1；最新组后检查点 |
| Python线程创建/峰值 | 12 / 6，含watchdog；最新组后检查点 |
| 子进程/网络/文件SQLite/越界写入 | 最新组后meter均0 |
| 缓存探测 | D1A组后105条去重记录、106次，缓存内容读取0；最终增量UNKNOWN |
| 输出 | 10文件、2目录、2,075,679字节，实际在13路径/2MiB内 |
| 日志 | COMMAND stdout268字节，stderr0字节，suite stdout5745字节 |
| 时间 | 开始09:49:23.851686 UTC，退出观测09:50:17 UTC（秒级）；精确最终elapsed meter缺失 |
| 最终关闭计数、最终meter、峰值RAM | UNKNOWN，RESOURCE_AUDIT/ledger拒绝后没有实值落盘 |
| 原生线程/VFS及额外OS泄漏实验 | UNKNOWN / NOT_RUN |

`R32_RESOURCE_BUDGET_SATISFIED=false`表示完整资源合同缺证；实际物理输出未越过上限。已获得的组后计数在对应边界内，结束清理后的数值继续保持UNKNOWN。原进程native退出1已观测，保留全部获准证据文件，无删除、截断或补跑。

2207份执行前保护文件前后SHA全部相同，包含原2176项、R31全部30份静态文件和当前Runner。42工程、3测试、10fixture、24运行时及394代码目录项按冻结清单核对。R25专项证据、R28/R30失败证据和历史SOURCE_LOCK保持原字节。R32汇总材料按用户交付要求单列，运行资源计费对应R31固定命名空间。

本轮真实服务、部署、业务数据库、真实密钥、RPC、P1/P2及其他受限阶段执行均为0。
