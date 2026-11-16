# R24范围、来源与源码锁

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助源码修订、纸面分支复核与静态取证；动态验证与外部独立复核待取得。

## 授权与实际工作

研究者已独立批准R23两项阻塞的最小修订。工程修改限定为原有两个文件；新增工程入口0，原测试/fixture修改0。当前实现只服务本轮获准的测试基础设施修复，未提出或实施新的候选安全机制。

| 文件 | 修改前SHA-256 | 修改后SHA-256 |
|---|---|---|
| run_dsat_authority_live_lifecycle_tests.py | `566436a1e4d45e4dfd310e2994f336834dc8c77ffbe65808b0452e94952a367d` | `527e9728b0485ce3b01a1b555b39a121085505d017ad8598c8923056257c1847` |
| dsat_windows_runtime.py | `0df81f8aba187ac3e4623ee436295e05e15179fc822e8a2d2416348810c91123` | `d0e6f281df41335c9aada15b1f700a8eb8decb6b2a13dae6ad21101645602e81` |

修改前原始字节保存于`sources/original`；实际diff见`sources/R24_PATCH.diff`与`R24_CODE_DIFF.json`。原始范围先于修改写入`R24_PATCH_SCOPE_LOCK.json`。这些文件此前已被历史哈希引用，本次用户对这两个位置提供了明确的新修订授权；旧快照、旧锁及旧报告保持。

实际发生变化的顶层定义：

- `run_dsat_authority_live_lifecycle_tests.py`：target、write、run_approval、audit、preflight、worker、main。
- `dsat_windows_runtime.py`：authorize_test_scope、launch_owned_child、finish_owned_child。

另有输出常量与CLI尾部声明变化。Windows函数内的证据/异常处理辅助函数属于`finish_owned_child`局部实现；原业务授权消费入口、journal格式、Store及H2总量门未改。

## 原始依据与阅读范围

完整读取并解析R22/R23共51份交付文件，重点核读R23最终裁决与静态报告、R22原错误、追加申请、三个真实运行记录及SOURCE_LOCK。本轮初始8份冻结源码、5份fixture全部吻合；历史68项当时与R22最终版本一致。全部源定位和摘要保存在`sources/READING_AND_HISTORY_BASELINE.json`。

R22保持121 PASS、1 ERROR，F23/F26/T45/X01/X02历史独立进程见证保持；R23保持54 NOT_RUN、代码修改0、suite启动0。本轮修改不会回写这些历史结论。

## 当前锁与执行边界

`sources/R24_FILE_LOCK.json`固定当前8份指定代码、5份fixture及42份源闭包；原计划54个ID和预期在`R24_VERIFICATION_ADMISSION.json`逐项保存。其字节锁另与原R22计划SHA绑定。原54项测试文件保持完全相同，包括F24原断言。

本轮`ACTUAL_RUNS=0`、`AUTHORIZED_FOR_DYNAMIC_RUN=false`、`REMAINING_RUN_BUDGET=1`、自动重跑0。未导入项目模块或调用项目函数，允许的解析/摘要辅助进程只用于静态文档与源码核验。

独立执行批准位于未来的`RUN_APPROVAL_RECEIPT.json`。当前仅提供approved=false的模板，实际批准文件未创建，验证输出根也未创建。源代码和模板无法替代研究者对本次新源码版本的明确动态批准。

## 历史保持

核验R22目录39份文件、R23目录12份文件、旧输出391份公开文件、原1194份受保护文件摘要；静态结论均匹配。13份历史私有合成DB/key/PEM类材料仅核对元数据，本轮内容读取及私密摘要输出均为0。源闭包中的6份其他指定代码、5份fixture及全部原回归测试保持原字节。

最终前后复核和报告清单见`sources/FINAL_STATIC_QA.json`。哈希固定版本，独立性按实际知情模型辅助过程登记。
