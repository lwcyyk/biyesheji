# GNU libc版本与Ubuntu包审查

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

**GNU libc上游版本仍为2.39；8.9→8.12对应Ubuntu包版本的发行版修订部分。**

实际getconf GNU_LIBC_VERSION输出glibc2.39；ldd --version输出Ubuntu GLIBC2.39-0ubuntu8.12与上游2.39。dpkg-query确认libc6:amd64、libc-bin均2.39-0ubuntu8.12，已安装状态ii，架构amd64。

三个真实/usr/lib路径均由libc6:amd64归属查询命中。dpkg -V libc6 libc-bin exit0且stdout为空；三项实际MD5与/var/lib/dpkg/info/libc6:amd64.md5sums一致。ubuntu-keyring2023.11.28.1包核验同样无差异。Root所有权/普通文件元数据及真实路径均保存。

apt-cache policy显示当前安装/候选版本来自noble-updates/main和noble-security/main。两份对应InRelease使用现有Ubuntu archive keyring经gpgv验证exit0，缓存main/amd64 Packages内容SHA256与签名Release声明的大小/摘要匹配，均含libc6和libc-bin8.12完整stanza。

当前8.12 .deb在已检查本地缓存/临时目录未找到，未下载补齐。已有8.9 libc6缓存包被只读解包，三个旧成员SHA精确匹配旧冻结pin，进一步锚定旧8.9身份。安装文件与签名仓库包之间的payload再提取证据仍缺，现结论依赖受信Root/dpkg数据库与既有keyring。

本地changelog.Debian列出的8.12补丁涉及libio、resolver、动态加载器ORIGIN/AT_SECURE、nscd及gettext等。此处仅报告本机包携带的更新说明，未联网确认各CVE细节；不能由修订号或changelog推出资源行为和全部运行语义等价。

[版本/归属/完整性原输出](evidence/RUNTIME_DISCOVERY.json) · [签名/索引/成员目录](evidence/PROVENANCE_AUDIT.json) · [旧包与changelog](evidence/OLD_NEW_ABI_AUDIT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
