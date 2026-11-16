# R26范围与R25证据核验

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助静态源码/计划/历史证据审查；本轮项目模块导入、工程修改、suite和测试子进程均为0。

## 本轮裁决

当前工程构建和68项清单已固定；执行准入登记 **R26_STATIC_PREFLIGHT_BLOCKED**，具体阻塞为 **REGRESSION_ENTRYPOINT_MISSING**。现有入口固定历史输出或只批准54项。新入口尚未实现，因此command_executable=false、runner/argv=null。没有生成可直接执行的68项命令。

本轮只写R26静态材料。工程源码、原测试、fixture、历史SOURCE_LOCK修改0；所有68项状态NOT_RUN_IN_R26。没有运行测试发现器、导入测试模块、创建SQLite/key、测试子进程或verification_runs。R25已耗尽的54项额度保持0，不转换成68项许可。

## 已读取与复核

完整读取R25六份主稿、五份结构化结果和来源/最终QA；实际读取R24原始RESULTS及准入、原R14/R16/R19计划与实际结果、相关runner和当前测试源。按字节/JSON/文本读取历史记录602份，记录于`sources/READING_AND_HISTORY_BASELINE.json`。历史目录级读取与针对入口、预算、依赖、断言的语义审查分别记载。

R25实际54 PASS、其余0、退出0、一次执行/自动重跑0保持。F24败者flush/close实际EINVAL22且poll确认exit0，8个worker有退出与关闭记录；F23/F26/T45为当轮实际复验。EPIPE等未触发分支保持原静态范围。R25原始RESULTS SHA：`abf9b4f8ec5dc2a0e5518beb6d546c601a09e2e73dbad8a59f918cebb97e571e`。

## 当前构建身份

source_revision：`R25_ACTUAL_abf9b4f8ec5dc2a0e5518beb6d546c601a09e2e73dbad8a59f918cebb97e571e`。

source_digest：`621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9`。

该摘要采用原42条有序path+SHA记录的ASCII规范JSON计算，已经与R25实际cross_A启动grant中的source_digest核对相同；没有以Git提交名代替字节版本。

| R25指定源码 | 当前SHA-256 |
|---|---|
| dsat_authority_live.py | `9c1099dd9ea83feeb60c92bf106a3c4a4ec88df58c10ca0cba94e0da7aba81bd` |
| dsat_authority_lifecycle.py | `4a1f361713e4e8a56766cebfc91284e4e0ae2012f58f698efe82ef90f13b16b7` |
| dsat_windows_runtime.py | `d0e6f281df41335c9aada15b1f700a8eb8decb6b2a13dae6ad21101645602e81` |
| test_dsat_authority_live_lifecycle.py | `7b0564964a880746db58df9adfb611d5ce3be8f4aef2b976c96c2992e5e5ba91` |
| run_dsat_authority_live_lifecycle_tests.py | `527e9728b0485ce3b01a1b555b39a121085505d017ad8598c8923056257c1847` |
| services.py | `b4589916889a1c287a19560cc94fbb2b3dd0b058d6f08314d8f60997f50c86f6` |
| storage.py | `6026d4ef80295aa1a0ede4114253eeb7c2850244a51020b3e4caa7d6c4ec960e` |
| run_h2_authority_service.py | `dfada9a27fb5be95919775bda345478a6df50fd2930a9999d5e98710e7a7f25b` |

完整42文件、另5份回归测试/CLI辅助文件、24份已由R25前置保护的解释器/SQLite/crypto依赖文件均在`R26_CURRENT_BUILD_LOCK.json`。42份工程源与R25一致，无未经确认变化。68项需要的3个测试文件及2个CLI补充文件单列，不把它们虚构成R25全部实际导入过的模块。

解释器固定为`C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`，与R25相同；Python3.12.14 AMD64、cryptography50.0.2、cffi2.1.1、pycparser3.11及SQLite二进制指纹保持。完整逐模块加载origin清单并未在R25原文中单独导出；R25的T31/scope来源检查通过与本轮静态预期路径分别登记。未来68项必须实际保存各阶段module.__file__/__spec__.origin及摘要。

## 历史完整性

去重保护清单2045份，当前全部匹配；继承R25锁的项目与本轮补充快照项目各自注明来源。R14/R16/R19/R21/R22/R23/R24/R25原报告、旧失败、来源锁与R25原始运行全部只读。13份私有合成DB/key类材料仅记录元数据，不输出秘密摘要，不将元数据比较提升为内容字节证明。

R24新增receipt、验证树和R25总结属于此前明确授权的合法新增，正常纳入保护清单。R26新材料另存当前目录；原历史列表未因合法新增被判为篡改。
