# 来源核验根因与证据边界

已定位的触发点为旧 `State.origins_snapshot` 第366行；旧 `main` 第696行在D1A完成后调用它。原谓词要求所有被选依赖的 `__file__` 与非空 `__spec__.origin` 对应相同Path。R30堆栈证明有文件字段时，该一致性谓词失败。

**`EXACT_MISMATCH_ORIGIN_UNKNOWN`。** 旧日志缺少实际module_name/file/spec.origin/loader/expected pin，以及PRE/POST模块集合。当前材料支持函数级定位，实际冲突模块仍待新的合法观测。cryptography的 `binding.py:14` 从 `_rust` 引入 `_openssl, openssl`，仅提供原生派生模块元数据的调查线索。

证据遗失有两条明确控制流：旧快照在整轮验证成功后才append；旧收尾在保存三份最终JSON前再次无保护地核验来源。第一条使拒绝行与部分快照消失；第二条可继续阻断资源、结果及最终receipt。已有EARLY记录只保存首条错误。

新采集见 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:460`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:569`。先保存完整sys.modules名称集合、PRE后的新增/移除名，再将原始字段写入检查点，随后验证；拒绝行及部分快照继续保存。动态模块使用模块自身字典观察，避免由module.__getattr__触发导入。

| 来源类别 | 接受或拒绝依据 |
|---|---|
| 冻结工程/测试 | 精确模块名、文件/spec/loader路径、文件身份和SHA |
| 标准库和锁定第三方文件 | 394目录的精确名称/路径/摘要，SourceFileLoader或ExtensionFileLoader |
| 内建/冻结模块 | 实际Builtin/FrozenImporter对象、_imp注册信息、canonical sys.modules对象；解释器/DLL另按24指纹锁定 |
| 原生派生子模块 | 精确已锁父扩展、逐段父属性链和对象同一性，加明确file/spec形态 |
| fixture | 原10份路径与SHA，module_name为NOT_APPLICABLE |
| 未知、实际冲突、缺文件、摘要异常、读取异常、审计内部异常 | 各自分类，最终合同受限并退出非零 |

原生派生规则见 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:512`。父文件须为固定 `_rust.pyd`，SHA为 `3e2d3a15defdb80e83ddd58693ef6e0eecbd741ae132d68e0b861a4f7577d872`；同时验证父ExtensionFileLoader、原路径身份、子对象通过父模块字典可达且就是sys.modules对应对象。子file/origin允许缺失或精确等于该父二进制；子spec须缺失或具有规范全名且loader为空。实际形态超出规则时保留失败和完整诊断。

覆盖范围为原工程/测试/8个依赖根、394目录中的准确模块名、__main__及内建/冻结注册模块。其他已存在sys.modules项目仅记录名称；例如解释器启动的 `_distutils_hack` 位于既有细粒度核验范围外。这里继续保留该范围限制，整个Python安装目录的读取许可仍为0。全解释器启动链的独立完整取证属于另一个合同。

冻结规则和实际运行观测分别存放。R31实际模块观测列表为空，来源策略的动态接受能力待下一次独立授权运行检验。
