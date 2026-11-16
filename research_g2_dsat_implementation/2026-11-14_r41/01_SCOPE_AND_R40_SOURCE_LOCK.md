# R41实施范围与来源锁

本轮按研究者R41独立授权，完成现有Runner的工程维护修复和静态复核。动态测试0，28项继续NOT_RUN，EXECUTION_AUTHORIZED=false。新算法贡献0，严格分离门继续约束任何新候选机制。

授权附件：`C:\Users\a1887\.codex\attachments\c5a324b8-d720-4c15-89cc-95790815ab09\已粘贴的文本.txt`，SHA-256：`aab8b5f27cc43575f154116f795bebccfa4e28314dccbd58fd0754270dac79cb`。R40原申请中的approved=false保留原字节；本轮授权以新附件为依据。

## 修改前锁核验

R40的24份交付完整读入，所有JSON完整解析，五份报告核读；R40 SOURCE_LOCK全体输入及交付pin在修改前均匹配。R40锁SHA为 `250ba94c135cb0a13a0504d981a6171d7602338297d276e1c90f99d9c48f10b0`。

唯一文件：`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`。

- old_sha256：`33276c053116537db4c8921410f860968dc966fbc99cc42b798fdf836c9c601e`，116336字节。
- new_sha256：`245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f`，125930字节。
- 源文件增量：9594字节，保留CRLF。源文件体积与运行证据容量分别计费。

五个获准原函数由R40 JSON直接提取：State.commit_case_record、State.safe_checkpoint、State.checkpoint、State.reserve_bytes、State.io_write。各自修改前原始字节摘要、AST摘要和行范围见R41_PATCH_SCOPE_LOCK与R41_CODE_DIFF。本轮新增一个6行局部helper State._checkpoint_rejection，属于R40允许的至多一个有界helper。

逐函数去除修改区及一处helper分隔空行后，Runner其余原字节完全一致；整个模块剥离这些函数后的AST也一致。原import、常量、其他函数、原68测试和fixture均保持。

## 历史保护

入口核验R40继承2433项，含5项既存缺失和40份历史SOURCE_LOCK；另外保护R40全部24文件。结尾核对总计2457项，唯一允许变化为上述Runner，R40及更早记录保持原字节。具体结果由sources/HISTORY_AFTER给出。旧锁中的Runner pin继续代表旧构建，保留其历史意义。

## 实际操作边界

本轮只有一个现有工程文件修改，外加本R41取证目录中的报告、JSON、源快照和diff。原42工程源码、原测试、fixture、依赖、G4锁和R37合同保持。Runner及抽取函数执行0，动态导入0，动态测试0，SQLite/SQL0，测试子进程0，网络/监听/RPC0，密钥/TLS0，真实部署0。

Python工具只执行文本/AST、JSON、哈希、源差异和独立整数/静态数据编码。一次取证工具的原字节骨架断言先识别出helper新增分隔空行，随后按精确授权插入区核对通过；工具没有执行项目代码。过程说明见sources/STATIC_SCOPE_CHECK_NOTE。

本轮证据属于当前对话内知情模型辅助工程实现与静态审查，外部独立核验待取得。
