# 三项来源拒绝与条件修复

| R32实际对象 | object ID | 原拒绝 | journal行 |
|---|---:|---|---:|
| _cffi_backend | 1802759587376 | UNAUTHORIZED_ORIGIN | 572 |
| cryptography.hazmat.primitives.ciphers.algorithms | 1802760328016 | ORIGIN_UNRESOLVED | 588 |
| cryptography.hazmat.primitives.ciphers.modes | 1802760329296 | ORIGIN_UNRESOLVED | 590 |

完整file/spec/loader/路径/摘要/阶段及拒绝依据见 `R33_REJECTED_ORIGIN_ANALYSIS.json`。R32未捕获的规范化路径、文件身份和实际SHA继续UNKNOWN；后续只读文件hash与身份另列，保留其采集时点。三个对象的实际来源绑定均尚待新的合法实时见证；真实来源冲突当前没有取得确认。

_cffi_backend具有明确分类键缺陷：394目录将ABI文件stem记作模块名，实际注册名为_cffi_backend。新映射仅替换这一精确键，要求固定路径同时具有394目录和runtime24的同一SHA pin。原verify_file_origin继续核对declared/spec/ExtensionFileLoader名称、实际路径、samefile、设备/inode/大小/mtime以及SHA。原ABI字符串键被移除，整个目录前缀许可保持为0。

两个cryptography对象的采集缺口来自精确ModuleType判定。新规则仅针对algorithms/modes两条既有模块路径：先验证utils真实模块、SourceFileLoader及SHA `21aed2d106734b47b3c2920741f63c1b57bea381a3ac78a31175e3c00af58ae2`；再要求包装对象的真实class就是该utils字典中的_ModuleWithDeprecations，普通metaclass与精确ModuleType基类匹配。

随后通过内建ModuleType字典描述符读取_module，底层须为普通ModuleType；先保存底层原始观测，再验证全名/file/spec/loader/文件身份/SHA。sys.modules绑定、包装对象、class及_module关系在验证后重检。包装对象已有file/spec/loader字段也须与目标或底层同一元数据相符。整个流程直接读取字典，保持对实例__getattr__的隔离。

满足全部条件时分类为EXPECTED_WRAPPED_SOURCE；缺见证继续ORIGIN_UNRESOLVED，实际路径/身份冲突继续DEPENDENCY_ORIGIN_MISMATCH，摘要冲突继续DEPENDENCY_CHANGED。R32三项全为误报这一结论保持未登记。R30的EXACT_MISMATCH_ORIGIN_UNKNOWN也继续保留。

新增代码通过条件规则静态核对，实际R33来源观测0。crypto导入操作新增0，原生Rust父子模块规则及普通文件验证函数AST保持。
