# 最小有限证书重放

## 运行

安装Python 3.11+后解压整个包。运行仅使用Python标准库；PDF阅读器用于人工阅读。当前实际测试环境及路径见 [PORTABILITY_REPORT.json](PORTABILITY_REPORT.json)。

Windows PowerShell示例；将两个绝对路径替换为本机实际值：

```powershell
python -I -S -B -X utf8 'E:\FrodoReview\replay\run.py' --output 'E:\FrodoReviewWork\run_001'
python -I -S -B -X utf8 'E:\FrodoReview\replay\verify_package.py' --output 'E:\FrodoReviewWork\links_001.json'
```

POSIX同一入口：

```sh
python3 -I -S -B -X utf8 /path/to/FrodoReview/replay/run.py --output /path/to/new_work/run_001
```

`--output`为必须参数，要求新的绝对包外目录；运行前该目录应不存在。cwd可为任意目录。入口先按MANIFEST核全部包内文件，再将frozen输入复制到新工作目录sandbox，执行标量副本。历史目录和包内文件仅被读取。每份脚本硬超时600秒，失败通过非零退出码及具体日志暴露。使用`-I -S -B`隔离用户模块和第三方site，并抑制字节码写入。

## 输入、输出与覆盖

| 运行标签/复用脚本 | 包内输入 | 新工作目录输出及核验 |
|---|---|---|
| author_compute / compute_profile_certificates.py | 冻结DISTRIBUTION_TABLES及官方CDF常量 | 重新生成976/1344整份OFFICIAL_PROFILE_CERTIFICATES；要求与v3冻结证书逐字节相同 |
| author_verify / verify_profile_certificates.py | 新生成证书、包内全部登记来源/输入副本 | CERTIFICATE_CHECK，3194项；完整JSON比较，含CDF/全标签Decode/PGF/全部频率/条件化及640特化 |
| review_976_1344 / recompute_review.py | 新生成官方证书、640固定A证书 | 9196项重建；INDEPENDENT_RECOMPUTATION；两个65536项u16le映射及1484/1000代表；全部数学字段比较 |
| source_event_976_1344 / verify_historical_relations.py | PARAMETER_CERTIFICATES及976/1344卷积原件 | 全部1281/769系数及ε≤2^-1118/2^-1532；与v3 HISTORICAL_EVENT_RELATIONS全对象比较 |
| fixed_A_640 / recompute_certificates.py | 640 FINITE_CERTIFICATES | 385项、H尾73、全频率、初始PGF及I条件端点；完整载荷比较 |
| uniform_Setup_640 / recompute_probability_chain.py | 640 SCALAR及JOINT_SCALAR证书 | 303项、均匀Setup的坐标/行/完整上界和I端点；完整JSON精确比较 |
| A_all_convolutions / ROUND-005 math_verify.py | 三组精确χ常量，与包内全部冻结卷积对照 | 重新卷积三组；完整1537/1281/769整数数组摘要比对；ε640≤2^-751；CF-1有限正确性例；A_EXTRA_CHECKS额外绑定χ640、25μ<1/2及n128的ε≤2^-59 |

主结果绑定另输出 `UNIFIED_SELECTOR_BINDINGS.json`，将三参数×两种A量词的原/条件精确端点绑定至v3统一选择器，核全部显示上界。全卷积比较包括offset、分母、归一化、完整整数数组摘要；源脚本同时重建峰值及32重L₂恒等式。有限例与一般符号定理的证据范围分别保留。

最终汇总 `REPLAY_RESULT.json` 记录命令、cwd、环境、脚本哈希、退出码、完整载荷比较、路径元数据改造、包内全部输入的起止指纹。详细日志位于logs；所有重放产物位于sandbox及工作目录根。`INPUT_FINGERPRINTS_BEFORE/AFTER.json` 必须完全一致。每次使用新目录即可保留多次执行记录。

## 完整数学载荷与元数据比较规则

采用递归整对象比较：字典键集合、列表长度/顺序和每个值精确匹配；二进制平移映射按全部131072字节比较。仅以下**具体JSON Pointer**采用元数据规则：

- review重建结果的 `/script_sha256` 必须等于实际路径适配脚本哈希；冻结值必须是有效SHA-256。该差异由包内差分解释。
- review结果 `/seconds`、`/profiles/976/H/enumeration_seconds`、`/profiles/976/total_seconds`、`/profiles/1344/H/enumeration_seconds`、`/profiles/1344/total_seconds` 仅比较数值类型及非负；它们是运行时钟。
- 两个PGF代表JSON的 `/map_path` 必须实际指向新sandbox内存在的映射；map_sha256及其余全部字段精确比较。
- 640固定A重建的 `/python` 必须等于实际Python版本；冻结值保留其原环境身份。

除此之外零字段排除。原始精确分子、分母、大整数哈希、质量、CDF、频率、全部代表、最大差、分组和条件端点均必须相同。历史脚本的展示近似值也按完整JSON比较；若跨平台运行出现展示浮点差异，入口会报告差异，当前版本保留严格行为。

作者生成器和核对器保持原脚本字节；仅运行工作副本的INPUT_SNAPSHOT/SOURCE_PAGES中path/png改指向sandbox，来源哈希保持，全部被核path均来自包内。三份适配脚本通过FRODO_FI_SANDBOX读取复制后的根，数学语句保持；[适配记录](provenance/SCRIPT_ADAPTATIONS.json) 给出来源哈希与完整差分。运行器中新增的A_EXTRA_CHECKS和选择器绑定属于确定性整数/分数核对，候选机制实现数为0。

## 解释运行结果

PASS说明包内有限数学证书在记录环境下重建并匹配，且输入字节保持。模型解释、符号证明和实际软件迁移分别由H1/H2/H3判断。全部动作均为本地文件、确定性标量算术；该入口的范围涵盖包装/重放，真实UE采样、作者程序执行、Monte Carlo及LWE求解的计数均为0。

## 封存与文件核查

`MANIFEST.json`按包内相对路径列举全部文件，唯一自排除项为自身；其字节哈希可由外部ZIP及.sha256链核对。`PORTABILITY_REPORT.json`被MANIFEST覆盖。ZIP及其.sha256放在包外，ZIP哈希对象为最终压缩字节。包的阅读副本、运行输入和路径适配记录均被清单覆盖。

标量子进程另经replay/scalar_launcher.py记录全部文件打开事件：数据读取及写入限新工作目录，Python运行时文件按只读路径允许。审计JSONL随实际测试记录保存。
