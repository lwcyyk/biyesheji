# 指定离线测试与独立CLI实际结果

## 1. 命令和分母

解释器：`C:/Users/a1887/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`，CPython3.12.14。pytest未安装，使用标准库unittest等价入口；runner只加载两个获准模块，未发现/执行整仓测试。

实际命令为主工程下`scripts/run_dsat_offline_tests.py --records-root D:/毕业设计/research_g2_dsat_implementation/2026-11-10_r06 --run-id run_001`，修复后同命令改run_002，观察归一收紧及增加两项回归后为run_003，防御性输入快照/输出别名回归后为run_004。完整argv、输入/代码哈希、堆栈和逐项时间见TEST_RUNS.json及runs目录。

| 运行 | 总数 | PASS | FAIL | ERROR | SKIP |
|---|---:|---:|---:|---:|---:|
| run_001 | 74 | 72 | 0 | 1 | 1 |
| run_002 | 74 | 73 | 0 | 0 | 1 |
| run_003 | 76 | 75 | 0 | 0 | 1 |
| run_004（最终） | 77 | 76 | 0 | 0 | 1 |

唯一跳过项是缺成熟依赖的优化器执行，不能计成S2已求解。首轮A11错误为夹具对象别名导致权威快照也被改写，程序已安全拒绝；测试误期待局部结果字段。修正仅涉及新合成A11和其清单。原输入/日志/堆栈保留。

run_003收紧有效状态归一：HTTP500或performed=false携带的active=false仅存reported_active，有效active为None，同时记录缺证；原D_P不会被这种值扩张。run_004把入口数据复制为固定JSON快照，输出scope列表不共享调用者输入；新增别名回归通过。最终代码与run_004测试前哈希一致。

## 2. 24例

最终24例断言：PASS24、FAIL0、ERROR0、NOT_RUN0。下表是投影的实际业务状态，和测试是否满足预期分别统计：

| 投影状态 | 数量 |
|---|---:|
| UNKNOWN_PENDING | 14 |
| OPEN_FRONTIER | 3 |
| INSUFFICIENT_COVERAGE | 1 |
| REJECT_UNAUTHORIZED | 4 |
| STALE_EVIDENCE | 2 |

这些保守输出是通过断言的预期。提供独立数学证书后，A01/A06/A24另得到条件材料证明；A19得到数学不可行冲突。所有案例的真实原生资格仍为SOURCE_OR_REFINEMENT_GAP。

## 3. 核心数学检查

| 样例 | 实际检查结果 |
|---|---|
| A01 A/V | m=d分别3/1，R=H=0；完整流与残量势通过 |
| A06 A/V | m=d分别3/1，R=H=0；无需程序枚举六种归属，最优性证书支持全称最小值 |
| A19 | 要求流4，不足流/割容量3，VALID_MATH_INFEASIBILITY；EVIDENCE_CONFLICT，R/H未定义，O保持 |
| A24 A/V | 数学R/H=0；await_terminal:i1继续，global_complete=false |
| A06缺v1失活 | A/V均R=0、H=1，条件关闭false |
| A06第四来源 | A/V均R=H=1，条件关闭false |
| 活批准/漏后代 | 旧数学切片H=0可保留，条件scope资格false |

流和势/割是R05或本轮明确的手工给定向量，未由优化后端生成。它们确实经过新检查器执行，不能用这项结果替代未完成的S2求解。

## 4. 对抗与边界

实际覆盖重复birth/缺birth、来源交叉/冲突、假来源标志、历史删除、迟到隔离、未知容量、readonly B执行责任、陈旧/跨批准/旧许可、真假整数、原大容量/空U/空T、重复/非法E、输入/流/费用/正反残量势/割篡改、摘要和外部版本pin、资源超限、O删除和原生/全局声明越界。

S1函数在禁止open/Path.open/socket构造的上下文中运行通过；新模块/独立检查器AST只含已审离线/标准库导入，没有storage/services/native_provider或求解器依赖。检查器CLI在独立进程另执行12次，11个正向证明接受、1个坏摘要拒绝；见runs/cli_001/CLI_RUNS.json。

## 5. 费用记录

run_004的24例C_compile中位数3,319,800ns（启用tracemalloc）；单例Python追踪分配峰值最大82,750bytes，包含防御性JSON快照。单独typed parse是额外计时的一遍，不与C_compile相加当同一阶段。网络构造、证明绑定、直接检查、输入/输出和证书字节逐例保存于evidence/PERFORMANCE.json。

A01/A06/A24的两目标规范化证书合计分别7,530/7,640/7,728bytes，A19为2,970bytes；磁盘pretty JSON字节另在proof清单。检查器CLI时间包括解释器启动/文件读取，不代表纯算法或密码管理器端到端时延。

C_flow=NOT_RUN_DEPENDENCY_BLOCKED；全部原生费用NOT_MEASURED，本轮原生调用0。未开展压力测试或真实服务性能测试。
