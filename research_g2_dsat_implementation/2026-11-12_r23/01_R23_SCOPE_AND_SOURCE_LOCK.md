# G2-R23 范围、版本与静态执行门

审查日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助静态源码、历史记录与文档取证；本轮运行证据为零，外部独立核验待取得。

## 结论

**R23_STATIC_PREFLIGHT_BLOCKED**。研究者已明确批准一次专项运行；本轮实际启动 **0次**，额度剩余 **1次**。依据本次请求第二节“任何关键条件不满足，停止执行并报告准确原因”和第三节“如果需要再次修改代码，应停止本次执行”，在静态阶段停止。源码、fixture及R22历史均保持。

| 检查项 | 结果 | 依据 |
|---|---|---|
| PATCH_PRESENT | TRUE | 已退出子进程的stdin.close处理在当前源码中存在 |
| PATCH_SCOPE_VALID | FALSE | except接纳全部OSError，退出条件仅为poll()!=None，未区分预期关闭竞态与其他I/O错误 |
| SOURCE_HASH_MATCH | TRUE | 8份冻结源码、5份fixture逐项吻合R22最终锁 |
| TEST_COUNT | 54 | 计划ID、AST中54个方法及冻结顺序一致 |
| RUN_BUDGET | 1 | 本次研究者独立批准，已用0，剩余1 |
| AUTOMATIC_RERUNS | 0 | 静态源码中没有suite自动重试；本轮无测试调用 |
| RESOURCE_BUDGET_VALID | BLOCKED | 申请数值已复核；当前固定输出/批准文件位置与R23独立记录约束冲突 |
| OUTPUT_ISOLATION_VALID | FALSE | runner与Windows scope固定R22根，完成运行还会重写旧索引 |

## B1：冻结入口与新证据根冲突

runner第25行固定`OUTPUT`为`2026-11-11_r22_d1b1_closure_offline`；第419行固定从R22记录目录读取追加receipt。第435行向旧输出根登记新槽，第539–541行在完成时读写旧`TEST_RUNS.json`。Windows模块第20行同样固定旧根，第321行只接纳该根的子目录。CLI只支持`--suite`、`--worker`、`--input`，没有输出根切换参数。

本次指示要求新增R23证据目录、R22三轮测试与旧记录保持原字节。直接运行冻结命令会违反旧索引保护条件；写完再恢复或复制证据仍会留下旧记录曾被修改的过程。创建junction、改模块全局量、包装并替换main、添加未公开参数均越过冻结版本合同。本轮选择停止，保留旧receipt与索引。旧追加receipt当前缺失属于入口准备状态，研究者本次授权本身已明确有效；阻塞来自它要求落在旧R22目录。

## B2：最小补丁与本轮异常安全要求

现有补丁完整保留，详情见02。它确认精确拥有子进程已退出，但对异常类型仅检查`OSError`，无法保证非预期错误持续暴露。本轮授权仅验证既有补丁，故未改动代码或断言。

## 版本锁

| 文件 | 当前SHA-256 | 核对 |
|---|---|---|
| dsat_authority_live.py | `9c1099dd9ea83feeb60c92bf106a3c4a4ec88df58c10ca0cba94e0da7aba81bd` | MATCH |
| dsat_authority_lifecycle.py | `4a1f361713e4e8a56766cebfc91284e4e0ae2012f58f698efe82ef90f13b16b7` | MATCH |
| dsat_windows_runtime.py | `0df81f8aba187ac3e4623ee436295e05e15179fc822e8a2d2416348810c91123` | MATCH |
| test_dsat_authority_live_lifecycle.py | `7b0564964a880746db58df9adfb611d5ce3be8f4aef2b976c96c2992e5e5ba91` | MATCH |
| run_dsat_authority_live_lifecycle_tests.py | `566436a1e4d45e4dfd310e2994f336834dc8c77ffbe65808b0452e94952a367d` | MATCH |
| services.py | `b4589916889a1c287a19560cc94fbb2b3dd0b058d6f08314d8f60997f50c86f6` | MATCH |
| storage.py | `6026d4ef80295aa1a0ede4114253eeb7c2850244a51020b3e4caa7d6c4ec960e` | MATCH |
| run_h2_authority_service.py | `dfada9a27fb5be95919775bda345478a6df50fd2930a9999d5e98710e7a7f25b` | MATCH |

5份fixture及解释器摘要见`R23_SOURCE_LOCK.json`。R22部分`lines`元数据沿用旧计数；本轮另记实际行数，版本判断采用字节SHA-256和AST。原始首轮与当前版本的差异共2份源码：Windows关闭补丁和runner追加授权槽；精确diff沿用R22记录。

## 冻结命令与静态入口

计划解释器：`C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`，3.12.14 AMD64。解释器实际版本与SHA在JSON中。计划工作目录：`D:\毕业设计\auth-lifecycle`。本轮仅以该解释器进行文档/摘要/AST检查，项目模块导入0、suite启动0。

冻结argv（本轮未执行）：

```text
["C:\\Users\\a1887\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "-B", "D:\\毕业设计\\auth-lifecycle\\scripts\\run_dsat_authority_live_lifecycle_tests.py", "--suite", "new54"]
```

输入为`D:\毕业设计\auth-lifecycle\tests\fixtures\dsat_authority_live_lifecycle`五份冻结JSON；测试计划从R22读取。未发明runner参数。

完整顺序：X01、X02、F01、F02、F03、F04、F05、F06、F07、F08、F09、F10、F11、F12、F13、F14、F15、F16、F17、F18、F19、F20、F21、F22、F23、F24、F25、F26、F27、F28、T29、T30、T31、T32、T33、T34、T35、T36、T37、T38、T39、T40、T41、T42、T43、T44、T45、T46、T47、T48、T49、T50、T51、T52。

## 阅读和历史固定

完整按字节读取R22交付目录39份文件；全部JSON完成解析，文本完成读取，相关Python完成AST核对。数学/工程语义复核聚焦补丁、runner、安全边界、54项断言、三轮实际结果与资源记录。目录级机器读取与逐字段独立审查各自记录。R22七份主稿及申请已经核读，历史源码快照、原失败和SOURCE_LOCK保留。

重新核验原保护清单中1194份应保持文件，全部匹配；5份获准原始源码快照也匹配其before SHA。另固定R22目录全部39份文件和旧输出391份公开证据的摘要。13份历史私有合成DB/key/PEM类文件仅登记路径及大小，本轮未读取内容或公开摘要；该部分的字节级结论不由元数据推出。最终前后比较见`HISTORY_INTEGRITY_FINAL.json`。

本轮写入范围仅本R23目录，工程写入0。D1-B2、P1a/P1b/P2、S3-B2/S5沿用独立授权门。
