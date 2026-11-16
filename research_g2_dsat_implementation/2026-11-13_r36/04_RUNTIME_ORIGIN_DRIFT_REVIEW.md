# 12项运行时差异

**差异分类完成，来源准入仍为RUNTIME_ORIGIN_UNRESOLVED。** 7个现存文件全文SHA不同，5个旧元数据路径缺失；12项当前状态均与R35入场记录一致。旧SHA/当前SHA、精确路径、stat身份、版本证据和影响逐项列于R36_RUNTIME_ORIGIN_DRIFT_AUDIT。

公共根为 `C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python`；site-packages位于其Lib下。五份pycparser缺失路径均在Lib/site-packages。

| ID | 对象 | 内容差异 | 身份比较 |
|---|---|---|---|
| RT01 | `DLLs/_sqlite3.pyd` | 内容SHA改变 | 文件ID改变已证 |
| RT02 | `DLLs/sqlite3.dll` | 内容SHA改变 | 旧文件ID未记录 |
| RT03 | `site-packages/_cffi_backend.cp312-win_amd64.pyd` | 内容SHA改变 | 旧文件ID未记录 |
| RT04 | `site-packages/cffi-2.1.1.dist-info/RECORD` | 内容SHA改变 | 旧文件ID未记录 |
| RT05 | `site-packages/cryptography/hazmat/bindings/_rust.pyd` | 内容SHA改变 | 文件ID改变已证 |
| RT06 | `pycparser-3.11.dist-info/INSTALLER` | 旧路径缺失 | 旧文件ID未记录 |
| RT07 | `pycparser-3.11.dist-info/METADATA` | 旧路径缺失 | 旧文件ID未记录 |
| RT08 | `pycparser-3.11.dist-info/RECORD` | 旧路径缺失 | 旧文件ID未记录 |
| RT09 | `pycparser-3.11.dist-info/WHEEL` | 旧路径缺失 | 旧文件ID未记录 |
| RT10 | `pycparser-3.11.dist-info/licenses/LICENSE` | 旧路径缺失 | 旧文件ID未记录 |
| RT11 | `python.exe` | 内容SHA改变 | 旧文件ID未记录 |
| RT12 | `python312.dll` | 内容SHA改变 | 旧文件ID未记录 |

只有_sqlite3和_rust取得旧journal中的device/inode/size/mtime身份，可直接确认其文件ID发生变化；其余旧身份未保存，保持UNKNOWN。两项旧/新size分别相同，不能依据当前证书表推断文件相对旧版增长。

## 版本与来源证据

Python exe/dll与_sqlite3的PE版本标签仍3.12.14；当前sqlite3.dll的PE资源为3.53.1.0，旧SQLite准确版本未取得，加载后的SQLite版本本轮未查询。CFFI METADATA仍2.1.1，cryptography仍50.0.2；PE标签/包标签一致仅证明标签层事实。

旧pycparser3.11的五份元数据缺失，当前pycparser-3.12.dist-info/METADATA声明3.12，pycparser/__init__.py原文也声明3.12。现象与包替换一致，具体安装事务、操作者和授权来源未取得。

本地runtime.json声明bundleVersion=26.1112.11011、pythonVersion=3.12.14、win32/x64。旧runtime24锁没有绑定旧bundle manifest，故当前版本只能作为打包更新线索，无法自动证明12项变更的原因与合法性。

## PE/RECORD的有限桥接

6个当前PE均带15664字节尾部WIN_CERTIFICATE表。静态字节变换在RAM中截去证书区并清零security目录与checksum，未修改原文件或加载执行目标DLL。此规范化CFFI与Rust字节分别精确匹配当前RECORD声明的对应hash/长度；其中cryptography的RECORD全文hash还与旧冻结pin匹配，CFFI的RECORD本身已变。

这是具体的字节投影关联。原有签名二进制全文仍与旧pin冲突；没有旧完整二进制，就无法证明差异仅在签名区。证书签名信任、签名者/安装事务和旧新加载行为等价均待核。该投影没有替换原验证规则或来源锁。

## 对68与联合证据的影响

Python原生内容身份影响所有68项的导入、JSON/异常、FileIO、线程等运行条件；同3.12.14标签及stdlib源码一致不足以建立完全相同行为。SQLite两个二进制影响A1/D1A连接、执行、回滚、关闭和计数。CFFI/Rust影响D1A的crypto/native来源与AES路径；A17的提前导入排除仍需原合同验证。pycparser代码是否实际进入冻结68路径未由本轮动态观察；元数据pin冲突本身已经使原完整环境校验失败。

D24原黄金JSON/投影源码与工程源摘要保持，但当前解释器二进制不同，无法以源码相同证明同运行时。R25原54 PASS继续有效地描述历史构建；未来68与其同运行时联合122证据尚未取得。

运行时审定保留四层：SOURCE_CONTENT_MATCH=false；RUNTIME_FILE_ID_MATCH两项false/其余UNKNOWN；RUNTIME_VERSION_MATCH仅部分标签相同；RUNTIME_BEHAVIOR_UNVERIFIED=true。旧R25/R29/R31/R33/R35来源指纹保持原值。

后续运行时来源精化的最小范围已经登记为延后责任：取得权威bundle/安装或原运行时恢复来源、精确签名投影关系、pycparser版本/目录变更责任，再由研究者独立批准后继来源锁。本轮唯一主动申请仍是证据表示合同审批。
