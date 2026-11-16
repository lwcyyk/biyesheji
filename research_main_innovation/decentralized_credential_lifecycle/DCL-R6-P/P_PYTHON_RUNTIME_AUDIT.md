# P：原生 Python 3.14 资格

2026-11-10。Material Passport：只执行白名单第12条ls；Python版本执行、导入、哈希与动态链接检查均为0。

## 1. 真实结果

命令为`wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/ls -l /usr/bin/python3.14 /usr/local/bin/python3.14`，exit=2，stdout为空，Linux stderr分别报告两路径均为“No such file or directory”。WSL原生代理警告与Linux错误混合编码，原始字节和分段解码说明见[命令12](evidence/commands/12.result.json)。

状态：**NATIVE_PYTHON314_UNAVAILABLE**，精确范围为这两个获准路径。未搜索其他目录、PATH、包数据库或虚拟环境；无法据此断言整个发行版不存在任何Python3.14副本。当前也没有足以供最终执行锁使用的native Python路径。

## 2. 后续依赖停止点

|工作|状态|依据|
|---|---|---|
|两个固定路径的存在/元数据核验|完成，路径缺失|第12条原始输出|
|执行native Python --version|UNRUN|本授权排除；路径缺失，依赖条件未满足|
|runtime/stdlib/loader SHA-256|UNRUN|须先有真实路径与后续具体检查许可|
|Python导入/语法/资源接入/模型|UNRUN_RESOURCE_GATE|超出P授权；runtime与资源门均缺|
|安装、下载、编译、回退/Windows Python/新增venv|未执行|本授权§4、§5明确排除|

因此P3=FAIL（未来执行资格）；P阶段路径检查本身已按授权完成。F1/F4业务模块的历史哈希仍有效，但当前无法装配可执行Linux环境。

## 3. 最小变更需求

推荐L首先申请有限只读现有runtime发现与发行包候选查询，在本地确定是否已有3.14、可用版本/来源及拟议路径；随后冻结确切3.14.x、来源摘要、安装影响与目标路径，再提交对应安装申请。当前仅生成需求，不选择未经核验的下载地址/版本/包，也不编造现成安装命令。

如发现另一路径的现有3.14，先补版本/二进制/标准库/链接依赖、初始地址空间和入口映射审计；如确需安装，则单独取得许可。原Windows Python3.14无法作为Linux cgroup worker替代，其他版本的等价性也未审查。该阻碍使最终COMMAND_LOCK中的runtime字段继续UNRESOLVED。
