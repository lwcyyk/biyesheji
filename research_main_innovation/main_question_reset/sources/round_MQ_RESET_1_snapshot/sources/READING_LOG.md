# 来源、实际阅读范围与证据定位

日期2026-11-05；主文稿MQ-RESET-1。全部新增文件位于main_question_reset。来源获取记录见RETRIEVAL01–03.json；本轮读入历史材料/源码摘要见INPUT_HASHES.json，全部新增来源哈希见SOURCE_MANIFEST.json。文献结论、手工推导、作者测量与本轮执行状态分别登记。

## 1. 继承的历史材料

完整读取或按当前任务重核以下入口：

- `D:\毕业设计\research_main_innovation\prediction_rematerialization_screen\FINAL_DECISION.md`及`SAME_MODEL_PRIOR_ART.md`：模型修正、已覆盖子族及一般DAG/实际接口未决；没有重开该路线。
- `D:\毕业设计\research_main_innovation\ci02_cost_problem_screen\NOVELTY_DECISION.md`：整份驻留与SC/MC已有归约。
- `D:\毕业设计\research_main_innovation\ci01_policy_regression\FINAL_DECISION.json`：117输入/版配对回归属于完整离线链；一项实现缺陷已修复归档，真实部署/并发/首次披露仍未核。本轮未重跑。
- `D:\毕业设计\workspace_asset_review_2026-11-04\REPORT.md`：资产及CS03工件缺失等级。
- `D:\毕业设计\research_novelty_review_2026-11-04\GAP_CARDS.md`及`research_secret_recipe\REPORT.md`相关段：旧机制、固定标签覆盖及资格限制问题的淘汰边界，防止重命名复活。
- `D:\毕业设计\auth-lifecycle\docs\experiments\CAPABILITIES.md`：原生发行/内省/撤销的作用域。没有把原生OAuth内省写成TSL/PIR接口。

已有DTR/Checkmate/PIR以外的历史原文未重复下载或重新宣布完整阅读。CS03源码与转录没有新线索，本轮未追加搜索，运行数字证据等级保持原状。

## 2. 最新详细计划书和源码

最新按文件名定位的详细计划书为根目录2026-11-04 v1.0原件；文档直接从DOCX的word/document.xml提取，保存LATEST_PROPOSAL.txt。原件与先前资产审查的提取文本交叉使用，未修改DOCX。重点阅读§1证据分层、§4批准/威胁、§7接口边界、§11.1 SC1、§11.3预算及持久对象。文档为需求与拟研究安排，无法当成部署完成证明。

|路径（均以D:\毕业设计\auth-lifecycle\src\auth_lifecycle\开头）|本轮实读定位|
|---|---|
|a/candidate.py|15–38 Shield、41起solve，有限赢集及配置反馈入口|
|b/engine.py|12–27资源/setup/批准；31起inspect；73起available、preserves/goal、93起plan|
|a/bridge.py|16起Feedback及B搜索/冲突检查调用|
|experiment/planning.py|11起原生model，35–63原生plan/单registered世界/空probes及query_needed_profile=false|
|experiment/journal.py|58–105 Gate预算、锁、发送计费、未知结果与义务记录|
|online_state/storage.py|190–225 grant预算与admit；相关状态转移通过源码定位，未执行|
|online_state/native_provider.py|18起CasdoorProvider的原生封装入口；未把内部数据库观察当作运行者免费信息|
|online_state/protocol.py、controller.py|协议/控制入口及字段范围的定向检查，无新功能运行|

这次实际源码重核已确认项目有预算维护原型，继承材料中的系统集成缺口仍按其范围登记。它没有把进程内锁或单权威存储改写为分布式额度协议。

## 3. 本轮取得的两篇K1直接原文

### B15

题名：**Extending Eventually Consistent Cloud Databases for Enforcing Numeric Invariants**。

作者：Valter Balegas、Diogo Serra、Sérgio Duarte、Carla Ferreira、Rodrigo Rodrigues、Nuno Preguiça、Marc Shapiro、Mahsa Najafzadeh。

版本：[arXiv1503.09052v1](https://arxiv.org/abs/1503.09052)，2015-03-31，11页作者稿；本轮未以其他出版修订替换。[全文](https://arxiv.org/pdf/1503.09052)，本地escrow.pdf，SHA256 `2fdd8739f5c9033ba0620c20b09f3248d60296b6814bb1fe727fac43e9a3f49a`。

实读：摘要、§II接口/模型/故障假设，§II-D权利解释，§III bounded counter算法、正确性说明与优化，相关实现限制。PDF p3–4包含R/U/localRights及consume/transfer；p4–5包含正确性与O(n²)到O(n)优化。性能结果未作为本轮测量或新优势使用。原文正确性按其非Byzantine、副本本地串行化、持久状态条件引用；未完成对外部署复现。

### I14

题名：**Coordination Avoidance in Database Systems (Extended Version)**。

作者：Peter Bailis、Alan Fekete、Michael J. Franklin、Ali Ghodsi、Joseph M. Hellerstein、Ion Stoica。

版本：[arXiv1402.2237v4](https://arxiv.org/abs/1402.2237)，2014-10-30，17页作者扩展稿。[全文](https://arxiv.org/pdf/1402.2237)，iconfluence.pdf，SHA256 `f392e0c2a3925f8b69dff6d99a0eaf1ea08f243c8f0af39310f3c56a986032b9`。

实读：摘要、§3系统与Definitions2–5、§4.1 Definition6、§4.2 Theorem1及证明概要，AppendixB Lemma1和主证明关键段，PDF pp4–6/14–15。理论包含事务可用、收敛、全局I-valid及特定merge，本文逐项保留。其他应用分类及性能全表未重推，未据之宣称新的工程速度。

## 4. 状态接口与K2直接近邻

### W25（规范近邻）

**Bitstring Status List v1.0: Privacy-preserving status information for Verifiable Credentials**，W3C Recommendation，2025-05-15。作者Dave Longley、Manu Sporny、Orie Steele；编辑另含Mike Prorock、Mahmoud Alkhraishi。[固定推荐版](https://www.w3.org/TR/2025/REC-vc-bitstring-status-list-20250515/)。本轮取得canonical TR，status_list.html，SHA256 `3cdf3358a09f3b02f2a97e5dac13cf2b63115c2db1260bf7b7c236d8702924ec`。

实读：引言，§2.1/2.2字段，§3算法/验证，§6.1–6.3长度、关联与缓存。原HTML约1847–1855为GZIP/最小位串，2378起隐私、2394起131072 bits、2457起缓存。privacy部分为informative，字段/算法的MUST与隐私建议分别引用。

另取得v1.1编辑草案status_list_editor.html，用于识别版本差别；主文稿规范判断沿用v1.0推荐版。首次TR获取SSL EOF，随后成功；两次记录保留。

### T26（规范近邻）

**Token Status List (TSL)**，Tobias Looker、Paul Bastian、Carsten Bormann，Internet-Draft `draft-ietf-oauth-status-list-21`，2026-06-21，拟Standards Track，非RFC。[固定全文](https://www.ietf.org/archive/id/draft-ietf-oauth-status-list-21.txt)，status_list_ietf21.txt，SHA256 `21e4867a01f73cee2ebc1408d150c87f77898c3d1549ebc25c80fa352221f846`。

实读：摘要、§4–8位串/Referenced Token/HTTP获取/验证、§12.1–12.3、§13.4/13.7。稳定文本行：1269–1277默认GET；1349–1352 exp/ttl优先；1868–1945隐私范围及唯一URI/关联；2198起更新/缓存。没有把ttl解释为严格最新性证明。

### P23（密码学协议近邻）

**One Server for the Price of Two: Simple and Fast Single-Server Private Information Retrieval**，Alexandra Henzinger、Matthew M. Hong、Henry Corrigan-Gibbs、Sarah Meiklejohn、Vinod Vaikuntanathan，USENIX Security2023出版方18页PDF。[原文](https://www.usenix.org/system/files/usenixsecurity23-henzinger.pdf)，simplepir.pdf，SHA256 `b35a02f247018f25b5737257827f627b839b0e175bf4440789f2dc235fdb5d6c`。

实读：摘要/方法概述，§2–3相关工作与PIR-with-hints定义，§4/5构造和成本，§8涉及的输入/单位/微基准范围。PDF p2为作者数据概览，p5–6为§3定义与InformalTheorem4.1/Remark4.1，p7–9为具体算法/递归说明；更新Remark3.1只登记已有更新机会，精确更新费用保持符号。完整安全证明另指作者full version，本轮未取得该证明版；按本PDF明确范围引用。

机器提取有旋转文本警告，未用旋转图页读取关键数值；所引定义/费用来自正文及摘要。MB/GB原文定义为二进制字节单位；不将1GB基准映射成状态列表实际性能。

### RAR（需求/接口补充）

**OAuth 2.0 Rich Authorization Requests**，Torsten Lodderstedt、Justin Richer、Brian Campbell，RFC9396，2023-05，Standards Track。[官方文本](https://www.rfc-editor.org/rfc/rfc9396.txt)，rfc9396.txt。实读§1–2细粒度授权及payment示例、类型/资源端语义相关段。它表达详细授权数据，未被当作跨执行器消费计数器的实现保证。

K2已核读直接近邻包括上述两套状态规范及P23，覆盖角色分别记录；这并不构成整个PIR领域的最新算法穷尽审查。

## 5. 受限动作、缺失来源与优先权纪律

公开搜索连接器三查询返回Transport send error，已按来源名保存说明。随后仅取公开作者/出版方/规范资料。Spiral作者PDF入口TLS证书验证失败；未关闭证书验证。其他公开PDF/作者页面获取有SSL EOF，获取日志逐项保留。

P23参考文献可确认Spiral题名/作者；其全文未取得，覆盖判定为未决。ePrint 2022/368是未取得正文的获取探测，题名/版本对应未由本轮内容核实。经典PIR作者页面及候选PDF同样未取得。检索无结果只作为检索记录。

本轮未声称任何“首次”或独立协议优先权。D1/D2为自含推导与已知模型映射；原始PIR全文缺失不会被转换成新颖性依据。取得原文、读取指定章节、独立证明与外部复核分别登记。

## 6. 复核方式与执行边界

三篇PDF各有结构预检，均PASS；页标来自pypdf生成的`[PDF_PAGE n]`，结构检查不承担语义正确性。pypdf/Poppler相关工具只用于阅读。SOURCE_MANIFEST.json冻结来源，DOCUMENT_VALIDATION.json记录链接、JSON、历史哈希和算术校验。ARITHMETIC_CHECKS.json只计算位数及配额小例，无候选求解/仿真。

全部候选机制、真实账户和原生认证服务操作为0。旧目录未修改；获取公共资料及文档提取不构成主创新机制实现。
