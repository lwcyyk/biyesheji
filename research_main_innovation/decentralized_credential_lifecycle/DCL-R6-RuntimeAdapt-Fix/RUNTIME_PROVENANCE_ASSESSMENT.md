# 运行时来源裁决与条件

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

**分类RTA-1：正常软件包变更，结论CONDITIONAL_PASS。** 正确包归属、已安装版本、无差异dpkg校验、成员目录MD5、升级日志及签名仓库索引相互吻合，未观察到异常替换或来源矛盾。

|证据链|结论|
|---|---|
|当前Root文件→已安装libc6目录|三个MD5匹配；SHA/Build-ID/路径完整|
|已安装包→版本/架构/状态|8.12/amd64/installed，dpkg验证无差异|
|软件源→签名Release→完整Packages|两个gpgv成功、两个完整索引SHA/size匹配，含8.12包SHA256/Filename|
|旧源→8.9包身份|已有旧.deb控制字段及只读成员SHA匹配旧锁|
|新.deb payload再现|本地缺8.12缓存包，未下载；无法独立从签名包payload重提取三个现行成员|
|更新行为来源|日志可说明正常包修订，执行者/自动更新机制未证明|

采用原项目受信Root/kernel/软件包数据库与本机Ubuntu keyring的假设，可以建立受限静态基线。该假设不等于独立外部信任锚或新payload全链再现。本轮没有网络freshness/revocation查询，仓库时效与来源仍限定于现有缓存及已安装可信状态。

下一执行模板新增RuntimeAdapt_provenance_assumptions_explicitly_approved批准位，当前false。若后续执行许可不接受这些前提，应保持RUNTIME_PROVENANCE_UNRESOLVED并停止资格发放；本次没有授予无条件执行批准。补齐8.12已有可信包并独立payload核验是最小强化证据，不自动下载或安装。

[来源决定](evidence/PROVENANCE_DECISION.json) · [可复核签名/目录证据](evidence/PROVENANCE_AUDIT.json) · [保存的完整索引/ELF](evidence/PLATFORM_EXPORT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
