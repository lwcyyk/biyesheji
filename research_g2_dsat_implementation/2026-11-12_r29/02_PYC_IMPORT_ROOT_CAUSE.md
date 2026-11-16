# 导入缓存失败定位

日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助单文件修复、AST/源码/元数据/哈希审查。本轮Runner与测试模块未导入，--help和所有测试未执行，SQL/key/测试进程资源0；外部独立核验待取得。

## 实际链与位置

| 节点 | 原执行文件/函数 | 原位置与对象 |
|---|---|---|
| Runner进入A1 | R28所用Runner.main | 原613行load_group |
| 固定测试源装配 | Runner.load_group | 原533行compile/exec原A1字节 |
| A1顶层导入 | test_dsat_authority_host_activation.py | 19行导入auth_lifecycle核心 |
| 标准加载器 | frozen importlib._bootstrap_external.exec_module/get_code | 995/1091行get_data(bytecode_path) |
| 字节读取入口 | SourceFileLoader.get_data | 1190行_io.open_code |
| 读取审计 | 原Runner.State.audit | 233行READ_SCOPE_REFUSED |
| 失败抛出 | 原Runner.State.refuse | 167行Refusal，继承RuntimeError |

原Runner行号以本轮a9字节快照为准，不能用修改后文件行号解释旧堆栈。真实原文在R26旧run/RESULTS和R28失败分析中，未重写。

## 路径与模式的证据范围

可以确定对象为bytecode_path缓存探测，操作为open_code的只读二进制读取。原audit没有保存具体绝对路径、mode值或数值flags，无法在禁止动态探测的本轮补造现场值。

按标准冷启动、A1导入与未观察到core包exec，静态重建候选为`D:\毕业设计\auth-lifecycle\src\auth_lifecycle\__pycache__\__init__.cpython-312.pyc`。R28只读元数据曾见该候选270B，未读其内容。这个路径属于重建结论，原始直接观测范围保持。

新策略覆盖任何能反向绑定到已锁源的标准当前tag缓存路径，未来将记录实际路径、source/module/SHA、tag、mode/flags、phase和test ID。它不依赖把旧候选误当作完整原日志。

## -B与回退

-B或PYTHONDONTWRITEBYTECODE通常关闭正常导入缓存写入；get_code仍先调用get_data(bytecode_path)。固定CPython3.12.14在1092行捕获OSError后转读source_path；原Refusal属于RuntimeError，导致回退前中止。

本轮保存了同解释器配套源码及SHA，摘录在sources/IMPORTLIB_REFERENCE.txt，覆盖缓存读取、exceptOSError、源码fallback和get_data。新策略以PermissionError/EACCES拒绝缓存，使用标准导入器的正常源码回退。没有执行导入器、测试模块或重演失败来验证该链。
