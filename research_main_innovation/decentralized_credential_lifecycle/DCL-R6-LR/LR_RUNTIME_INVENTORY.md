# LR：现有Linux运行时清单

2026-11-10。Material Passport：PLATFORM_READONLY_LR＋静态ELF读取。35条Linux只读/版本查询，Python仅执行一次`--version`；业务模块/导入/校准/模型执行均0。全部argv在启动前登记于[命令计划](evidence/LR_COMMAND_PLAN.json)，实际结果见[总记录](evidence/LR_COMMAND_RESULTS.json)。

## 1. 发现与真实身份

find仅搜索`/usr/bin`、`/usr/local/bin`、`/opt`，不跟随符号链接、不跨文件系统。发现`/usr/bin/python3`、`/usr/bin/python3.12`、`/usr/bin/python3.12-config`。前两者归一到同一解释器；config归一到`x86_64-linux-gnu-python3.12-config`，作为构建辅助工具登记，未将其当作解释器运行。

|字段|实际值/证据|
|---|---|
|规范路径|/usr/bin/python3.12；命令05|
|版本|Python 3.12.3；命令09，仅--version|
|默认别名|/usr/bin/python3→/usr/bin/python3.12；命令05/07、python3-defaults本地包记录|
|文件|8,020,928字节，regular file，0755，root:root；命令06|
|SHA-256|e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f；命令08|
|本地包归属|python3.12-minimal，3.12.3-1ubuntu0.17，amd64，source=python3.12；命令03/07/10|
|发行版|os-release报告Ubuntu24.04.5 LTS/Noble；命令28，保留其报告值|
|本地缓存来源|noble-updates/main及noble-security/main，已装与候选均3.12.3-1ubuntu0.17；命令04|
|原生性|ELF64 little-endian，e_machine=62/x86-64；本地静态读取摘要与Linux sha256sum相同|

ELF通过本地WSL UNC只读文件接口读取已发现的解释器，未复制二进制、未调用ldd或执行loader/新程序。该行政读取与Linux命令分开登记：[LR_ELF_AUDIT](evidence/LR_ELF_AUDIT.json)。这提供了Linux原生映像证据。

本地包登记和缓存origin支持发行来源归类；未下载官方deb或校验其签名载荷与本机字节一致性。SHA识别的是当前实际文件，包来源真实性/完整运行时闭包仍有后续责任。

## 2. 标准库与动态链接

标准库目录`/usr/lib/python3.12`及`lib-dynload`实际存在。json、hashlib、pathlib的元数据/包归属由11/33取得；35对json四文件、hashlib、copy、pathlib、collections和functools等关键文件留有摘要。libpython3.12-minimal/stdlib包均为3.12.3-1ubuntu0.17。当前仅锁关键文件，未将这些摘要充作完整标准库/扩展模块依赖闭包。

|静态ELF项|实际值/对应标准包|
|---|---|
|PT_INTERP|/lib64/ld-linux-x86-64.so.2→/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2；libc6|
|DT_NEEDED|libm.so.6、libz.so.1、libexpat.so.1、libc.so.6|
|RPATH/RUNPATH|本映像两项均为空|
|libc6:amd64|2.39-0ubuntu8.9|
|zlib1g:amd64|1:1.3.dfsg-3.1ubuntu2.3|
|libexpat1:amd64|2.6.1-2ubuntu0.6|
|libssl3t64:amd64|3.0.13-0ubuntu3.16；相关标准库包依赖，区别于解释器直接DT_NEEDED|

31–35取得库文件包归属、真实链接目标与五个loader/直接库文件摘要。实际loader搜索、缓存、环境和后续扩展模块映射未动态观察；解释器启动成功也无法证明全部业务依赖闭包已可用。libpython3.12t64已安装，但本解释器DT_NEEDED未包含libpython；保留静态链接解释器与共享库包的区别。

## 3. 版本范围与路线含义

限定搜索未发现3.13/3.14；本地apt-cache policy只输出3.12条目。这些事实限于已查路径和当前缓存，未宣称全盘缺失或发行源永远不提供3.14。原P两路径缺失的原始结论保留，本轮增补已有3.12这一事实。

建议路线L2：复用该原生3.12作为新合同候选。版本/路径/摘要已可具体审批；语义兼容、初始AS/映射和实际资源限制仍待获准测试。原3.14要求保留，当前没有切换默认解释器、安装或自动采用新运行时。
