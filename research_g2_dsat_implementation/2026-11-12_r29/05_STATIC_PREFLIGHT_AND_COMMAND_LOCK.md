# 静态验收与执行合同

日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助单文件修复、AST/源码/元数据/哈希审查。本轮Runner与测试模块未导入，--help和所有测试未执行，SQL/key/测试进程资源0；外部独立核验待取得。

**38项静态检查通过，command_executable=true；execution_authorized=false，actual_suite_runs=0。** 动态导入和68用例仍为NOT_RUN；本轮没有运行Runner或--help。

检查涵盖原失败链、缓存拒绝与OSError回退、双向路径/tag、源码SHA、拒绝分支/字段、无目录前缀放行、394清单、exec校验、A17/预加载状态、D24 AST保持、原68与fixture、独立R29根、单次预算、控制JSON字段、旧材料及当前候选cache元数据。

所有38项结果见R29_STATIC_PREFLIGHT.json。具体命题均是对冻结源/输入/本机假设的静态结论，没有提升为真实导入成功或68PASS。

## 手工控制流挑战

| 输入情形 | 静态结论 |
|---|---|
| 已锁应用__init__对应当前tag缓存，只读且源SHA正确 | 缓存不读，PermissionError→固定get_code转读源 |
| 已锁CLI helper对应缓存，发生于D24 | 同样回退，JSON投影只作用原reader.Path且范围不变 |
| 任意未知.pyc或错误tag | 致命READ_SCOPE_REFUSED并保存路径/原因 |
| 已锁源被修改或路径有重解析/别名 | 致命拒绝，不进入预期回退 |
| Python目录内未列数据/配置 | 不因目录归属获得许可，继续拒绝 |
| r+或其他cache写入 | 输出guard拒绝，-B保持无正常cache写 |
| 正常cache拒绝后有人尝试删模块缓存 | 无此实现，alias仅对不存在的名字正常注册 |

## 无占位argv

```text
["C:\\Users\\a1887\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "-I", "-B", "-X", "utf8", "D:\\毕业设计\\auth-lifecycle\\scripts\\run_dsat_current_build_regressions.py", "--suite", "regression68", "--output-root", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r29\\verification_runs", "--approval-ref", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r29\\verification_runs\\RUN_APPROVAL_RECEIPT.json"]
```

工作目录为`D:\毕业设计\auth-lifecycle`。Runner的3个参数真实存在；Python-I/-B/-Xutf8保持，optimize=0与摘要在预检中核对。

命令指向新R29根和R29批准schema。当前只保存approved=false模板，未来真实回复字段的占位不属于argv；实际receipt与目录未创建。

未来准备必须绑定当前command/resource lock SHA、Runner新SHA、同工程摘要、真实研究者回复及1次/0重跑。R28剩余额度0不复用。一次实际启动失败、超时或部分完成也消耗额度，代码/预算不匹配就停止。

新source调用图将原R28不可见的尝试路径列为后续真实记录字段；现场未记录的绝对路径与mode数值继续保留未知，不能由静态代入改写原始证据。
