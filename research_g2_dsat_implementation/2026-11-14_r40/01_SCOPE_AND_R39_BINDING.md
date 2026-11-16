# R40范围、R39绑定与保全

本轮完成 Write 前拒绝的 Poison 分类静态审定和修复规格冻结。裁决为 `R40_PATCH_SPEC_READY`，代码实施、动态验证及完整68项回归继续等待各自准入。证据属于当前对话内知情模型辅助源码与纸面审查；独立外部核验待取得。

## 授权与实际操作

授权来自附件 `C:\Users\a1887\.codex\attachments\9229a78f-3d0c-461f-a249-2fdabd18fc37\已粘贴的文本.txt`，SHA-256为 `f3364c9921d269150e16038b85dcccf5119fa6ef5efb24a1ff6f102cb1138e16`。允许本轮新增报告、JSON及静态数据证书。本轮只向本R40目录写入这些取证材料。

| 操作 | 实际数量/状态 |
|---|---|
| Runner、工程、测试、fixture修改 | 0 |
| Runner/项目函数执行或动态导入 | 0 |
| 动态测试、suite、测试子进程 | 0 |
| SQLite创建或连接、测试密钥/TLS创建或访问 | 0 |
| 网络、RPC、监听、真实服务/部署 | 0 |
| 依赖变更、运行时来源重新接纳、历史锁改写 | 0 |
| 执行权限 | `EXECUTION_AUTHORIZED=false` |

独立Python工具仅执行文本/AST、JSON、哈希链、整数与惰性数据字节计算。工具没有导入Runner、测试模块或抽取的项目函数。静态编码样本与未来测试的 `NOT_RUN` 身份分别管理。

## 输入读取与哈希

R39目录的6份主稿和全部22份JSON已完整读入；结构化大表按共有字段与逐项差异核对，57个原异常ID全部保留。逐文件长度、SHA、完整JSON解析及字段遍历登记于 `sources/R39_READ_AND_BINDING_MANIFEST.json`。Runner共2078行全文核读并只解析AST。

Runner：`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`，116336字节，SHA-256：

`33276c053116537db4c8921410f860968dc966fbc99cc42b798fdf836c9c601e`

R39历史锁 SHA-256：`d6e803a6b58d73506ea79d5a2e6186036a8cc29a15ccb3c302422d61ce26a8b0`。本轮继续保留R38补丁及R37证据表示合同原字节。R37合同文件哈希为 `06230f8639ba3ee6624a766cd202f197221abbf0adb6c083e142ea02c052d235`，正文规范化哈希为 `49a6660d12d1595be34e9374a9dab337dc81f236582e0719d90ed9bf8ebac277`；二者范围有别。

## 继承事实

1. R39裁决继续为 `R39_STATIC_PREFLIGHT_BLOCKED`。正常检查点式为 `232+O+C+W`：O是去重的 `ORIGIN_OBSERVED` 条数，C是去重的 `ORIGIN_CLASSIFIED` 条数，W是 `WRAPPED_ORIGIN_OBSERVED` 条数。O/C各至多4096，正常W至多6；8430是需求松包络，实际8320构造尝试guard继续有效。
2. 已存前缀的条件存储上界2000167字节；2MiB预算2097152字节；两者差96985。完整正常/异常必需L0尺寸均为UNPROVEN。guard及存储包络分别承担其原责任。
3. X57是已到达、可适配、健康确认前缀与调度前提下的局部反模型。完整冻结输入级全局字节超额反例仍未取得。
4. R37的16项APPROVED、12项限定批准、9项CONTRACT_CHANGE_REQUIRED保持。9项原完整内容义务继续存在。
5. R36登记的7个运行时内容变化及5个旧路径缺失，本轮按12项具体旧路径重新核对，当前哈希/缺失状态与R36一致。详见 `sources/G4_PIN_RECHECK.json`。这项一致性表示历史漂移结论保持，来源准入仍待完成。
6. R35命令 `command_executable=false`，预算合同 `full_required_output_bound_proved=false`；旧命令仍指向旧Runner pin。本轮没有生成可执行的新命令，也没有把禁用门视为容量证明。

## 历史保护

继承R39的2405项保全条目，含5个预先缺失路径；另将R39全部28个文件加入保全。入口与结尾按逐文件哈希/缺失状态核对。原55项工程/测试/fixture pin、历史SOURCE_LOCK以及旧失败日志均保留。最终结果见 `sources/HISTORY_AFTER.json`；新R40锁的自哈希由外部最终回读给出，锁内部排除自身。

实际源定位与三处Poison赋值见 `R40_POISON_SOURCE_TRACE.json` 和 `sources/STATIC_SOURCE_FACTS.json`。本轮减少重复容量推导，将新增论证集中于边界分类、前缀和剩余收尾资格。
