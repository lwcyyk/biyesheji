# 回归入口、写入与导入审计

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助静态源码/计划/历史证据审查；本轮项目模块导入、工程修改、suite和测试子进程均为0。

**现有安全68项入口未找到。R26_RUNNER_OUTPUT_ISOLATION_VERIFIED=false。** 不调用任何旧runner的main，也不通过修改其常量、源锁或缓存来伪装当前准入。

## 逐入口核查

| 入口 | 实际文件/快照 | 问题 | 可直接复用到R26 |
|---|---|---|---|
| R14_H1 | run_dsat_authority_read_host_tests.py | 固定旧输出/旧索引；旧批准及源版本门 | 无 |
| R16_A1_H1 | run_dsat_authority_activation_tests.py | 固定旧输出/旧索引；旧批准及源版本门 | 无 |
| R19_D1A_or_legacy44 | run_dsat_authority_runtime_tests.py | 固定旧输出/旧索引；旧批准及源版本门 | 无 |
| R21_original | run_dsat_authority_live_lifecycle_tests.py.txt | 固定旧输出/旧索引；旧批准及源版本门 | 无 |
| R22_first_run | run_dsat_authority_live_lifecycle_tests.py.txt | 固定旧输出/旧索引；旧批准及源版本门 | 无 |
| R24_current | run_dsat_authority_live_lifecycle_tests.py | R24固定根且仅new54；额度已用 | 无 |

完整绝对路径、哈希、固定常量、argparse声明、潜在open/write/mkdir/加载点见`R26_RUNNER_OUTPUT_AUDIT.json`。R21和R22按各自实际保存快照审查；当前工程同名文件已经是R24版本，未把快照当成当前源码。

R14原H1没有输出参数，写R13_h1_offline；R16原文件真实名称为run_dsat_authority_activation_tests.py，写R15_activation_offline；R19仅支持d1a/regressions两个选择器，写R19_offline并分两进程；它们的TEST_RUNS会读旧索引后覆盖写入。当前R24虽然保留legacy分支，main在准入前明确拒绝非new54，不能用遗留分支代替68项授权。

旧预检还绑定历史已演进源码；即使某一旧runner当前先被版本门拒绝，它的固定输出仍无法提供未来R26隔离合同。不能删预检或更新历史SOURCE_LOCK使其通过。

## 两个真实装配障碍

### 导入顺序

A17在原测试第498–508行检查sys.modules中尚无cryptography/services/storage/materials。D06第208–215行会调用probe_offline_dependencies，D08/D09调用AESGCM。若按D01–D24再A01–A20排列，即使文件hash完全一致，A17仍有确定的导入污染风险。

新入口的最小方案为A1→H1→D1A，D1A测试模块及crypto检查延迟到前44项完成后才加载。预检只读metadata和二进制hash，避免提前importcrypto。保留全部原断言及原进程内注册状态；禁止清理/替换生产模块缓存、伪造crypto或服务模块来规避检查。

### D24路径合同

runtime.read_offline_json第78–96行只接受配置/fixture或R19离线前缀。直接给原D24配置普通R26 output，会出现：写出R26 JSON→inspect.main读取→PATH_DENIED→退出2，违反原正例退出0。此为纸面源码推导，本轮没有执行该失败轨迹。

R21/R22已有ProjectedOutput/ProjectedRead方案的历史实测可作为新入口实现依据，但当前R24实现仍绑定R24 target，无法直接挪用到R26。拟只映射两个原文件名test_metadata.json/test_request.json：逻辑值保持唯一R19虚拟前缀，物理字节仅写新R26树，旧逻辑目录始终不创建；其他路径保持原行为或拒绝。

新实现需审定有限双射、字节保持、物理父路径/重解析保护、原validator结果及finally恢复runtime.Path。此处是明确测试文件provider调整，未改变生产源白名单；也不能据该适配宣称生产代码已允许任意R26路径。该适配语义责任尚未关闭。

## 导入副作用与真实访问

原测试顶层为标准库、纯核心导入、CONFIG/DETAILS和函数引用登记；configure更新内存字典。SQL创建在A1或D1A注入factory时才发生，H1为假连接。services与Store位置由AST检查，未在原68测试运行中启动服务。D1A的D06实际导入crypto，D08/D09仅公开向量；A18只有受控假transport，默认CLI关闭。

三个CLI辅助脚本在导入时会把由自身位置计算的当前project/src插入sys.path；纯核心还会创建内存注册表/RLock。这些导入状态/内存副作用单列，不涉及文件或服务创建。未来入口需记录并验证同一个已锁源码根，不能笼统声称所有导入完全无副作用。

新driver必须在测试导入前装配隔离audit：只允许已声明phase的:memory:，拒绝所有文件DB/真实key、socket/RPC/子进程，禁止读取旧运行数据库；安装扩展、ATTACH/DETACH也拒绝。所有日志、receipt、索引、失败路径固定到新R26根，无历史fallback，结果独占创建。

## 历史元数据局限

R22两份回归RESULTS.inputs来自通用live54文件锁，未列出它们实际configure的旧fixture集。本轮没有改写该数组；改从R19原new_results.inputs、R16 fixture_hashes、R14 fixture_hashes及受保护字节核对10份原输入。未来68项必须按实际读取fixture输出正确manifest。
