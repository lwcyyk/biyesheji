# B1实施前核对

2026-11-11（Asia/Shanghai）。R12明确批准R11限定开发/离线验收。

- R11的900项来源检查、其交付QA及原779项历史范围均匹配；未发现待覆盖的用户修改。
- 仅新建dsat_authority_read.py、新测试、新夹具子树和限定runner，现有源码零修改。
- 既有read_state一次SELECT配对a/W，execute会记录遥测并消耗operation预算；本轮以reader/lock替身验证这些边界。
- 避开AuthorityStore构造器、call分派、Controller/Provider、SQLite、密钥及.runtime。
- 原请求handle只在合成可信源内参与旧完整请求摘要校验；公开staging使用字段白名单。
- 全部collection按账户/audience/task/caller/generation过滤；保留旧消费者与S1-v1的兼容缺口。
- 33项B1获准；B15/B27/B28为B2，保留36项分母并登记BLOCKED。
- 运行产物沿R11冻结目录2026-11-10_r12_b1，实际执行日期为2026-11-11；实施报告置本目录。
- 没有额外依赖或权限需求；真实连接与B2/S5保持关闭。

细项SHA与路径见sources/PRECHECK_LOCK.json，授权原文绑定见APPROVAL_RECEIPT.json。
