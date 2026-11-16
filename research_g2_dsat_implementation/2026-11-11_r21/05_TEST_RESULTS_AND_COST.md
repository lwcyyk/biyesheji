# 测试结果与费用

日期：2026-11-11。范围：R21明确批准的九目标及离线合成验收。过程为本对话内模型辅助实现、实际执行与知情复核；外部独立核验待取得。


最终原始执行：TOTAL120、PASS120、FAIL0、ERROR0、SKIP0、BLOCKED0、NOT_RUN0；内部检查2366（新310＋原137＋原1919）。最终完整合同验收：TOTAL120、PASS117、FAIL0、ERROR0、SKIP0、BLOCKED3、NOT_RUN0。

F23/F26/T45的单元测试通过，但更强跨进程条件仍有源级缺口。D1B1_ACTUAL_RESULTS.json同时保留raw_execution_status与contract_acceptance_status。原始RESULTS/stdout保持，验收数没有通过改写测试制造。

| 最终suite | 执行PASS | 内部检查 | elapsed ns |
|---|---:|---:|---:|
| new52_002 | 52 | 310 | 11425682200 |
| r19_24_002 | 24 | 137 | 965285700 |
| legacy44_002 | 44 | 1919 | 1127940900 |

最终suite时段合计13,518,908,800ns。时段从main内clock开始至构造结果，解释器/顶层导入、尾部结果及索引写入未单独计入；数值代表该测量窗口。

实际命令模板：

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_live_lifecycle_tests.py' --suite new52
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_live_lifecycle_tests.py' --suite r19_24
& 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\Scripts\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_live_lifecycle_tests.py' --suite legacy44
```

每个模板实际执行两次，总6次，达到R20每suite一次重跑的上限。首轮也全部通过；随后知情代码复核补强句柄关闭、lease复核、连接配置异常清理、加载来源和拒绝断言，再执行最终三组。240为含重复的用例执行次数，最终独立分母保持120。未发生测试FAIL/ERROR或early failure。全部6轮保留。

R19兼容D24采用测试Path provider：原始逻辑R19路径与准入判断保留，物理读写映射到新R21 run。原runtime源/原断言保持。这是旧策略兼容性证据，无法证明R19生产读取器直接接受R21路径。

| 最终新52资源 | 实测 | 上限/范围 |
|---|---:|---|
| 文件SQLite连接 | 11 | 104；每case至多2 |
| execute尝试/返回/失败 | 75/73/2 | 失败为主动ATTACH拒绝及访问已关闭连接 |
| 显式rollback调用 | 1 | 初始化失败清理单列 |
| state测试key生成 | 2 | 2 |
| TLS测试材料生成/SSLContext加载 | 1/2 | 2/2 |
| 拥有stub创建/强制终止 | 6/0 | 8/仅拥有对象 |
| 新工作线程＋watchdog/观察峰值 | 12＋1/4 | 16/4 |
| 私有子目录/最终前记录目录 | 21/22 | 64 |
| 成功取得实例锁 | 47 | 父测试进程计数；child另有实际锁证据 |
| 峰值working set | 51,302,400B | 实际当前测试进程，含导入及harness |

R19域内存连接1，legacy域18；两组无services/storage/materials导入，legacy无crypto导入。新52允许导入服务定义和真实测试Store，运行服务进程0。

所有轮累计：stub12、文件SQLite22、R19内存2、legacy内存36、state key4、TLS材料2、SSLContext4，均在获批累计预算内。原始执行正常不等于完整契约全部通过。

成本覆盖代理见下表；分类重叠，无法求和替代整体时段。精细ledger只计选定调用，未隔离的生成/日志fsync/平台I/O按实际局限登记。

| 类别 | 覆盖case | inclusive case ns |
|---|---|---:|
| C_source_validation | F03,T31 | 353537400 |
| C_identity | F02,T32,T39,T41 | 596418700 |
| C_initialization | F07,F08,F09,T34 | 338808400 |
| C_database | F14,T35,T50 | 627050600 |
| C_key | F10,F11,T34 | 207381400 |
| C_tls | F12,F13,T36 | 902419100 |
| C_logging | F14,T49 | 364147400 |
| C_host | F15,T38 | 477659300 |
| C_listener | F16,F17,F18,T40 | 1703147200 |
| C_shutdown | F20,F21,T42 | 898306600 |
| C_recovery | F22,F23,F25,T43,T44 | 662343500 |
| C_cleanup | F06,F19,T37 | 627422400 |
| C_retry | F26,F27,F28,T45,T46 | 1530694400 |

实际物理分配峰值、VFS写放大、完整OS线程峰值及旧两域内存峰值NOT_MEASURED。输出树当前逻辑文件字节和清单在D1B1_RESOURCE_LEDGER.json。真实D1-B2性能全部NOT_MEASURED。
