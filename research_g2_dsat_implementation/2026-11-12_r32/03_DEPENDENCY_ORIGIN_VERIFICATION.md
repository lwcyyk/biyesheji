# 实际依赖来源核验

`R32_DEPENDENCY_ORIGIN_VERIFIED=false`。本轮取得实际PRE/POST模块集合、254份分类记录及8轮快照，定位三个被拒绝对象。前六轮快照在声明范围内通过，D1A_finished及POST_TEST快照各拒绝相同三项。

| 模块 | 实际type名称 | 冻结规则分类 | journal行 |
|---|---|---|---:|
| _cffi_backend | module | UNAUTHORIZED_ORIGIN | 572 |
| cryptography.hazmat.primitives.ciphers.algorithms | _ModuleWithDeprecations | ORIGIN_UNRESOLVED | 588 |
| cryptography.hazmat.primitives.ciphers.modes | _ModuleWithDeprecations | ORIGIN_UNRESOLVED | 590 |

其余分类记录为43个TRUSTED_BUILTIN、19个TRUSTED_FROZEN_RUNTIME、178个TRUSTED_RUNTIME_SOURCE和11个TRUSTED_FROZEN_SOURCE。以上为去重分类记录数量，覆盖范围沿用R31，完整对象和阶段引用见 `R32_DEPENDENCY_ORIGIN_AUDIT.json`。声明范围以外的启动模块继续仅登记名称。

`_cffi_backend`的实际file与spec.origin均指向已锁定 `_cffi_backend.cp312-win_amd64.pyd`，loader为ExtensionFileLoader。394目录的module字段却为 `_cffi_backend.cp312-win_amd64`；Runner按该字段生成expected_names，实际注册名 `_cffi_backend` 没有对应键。故本轮实际source_digest/expected_origin被记录为UNKNOWN并拒绝。独立的运行前后文件哈希均匹配既有pin；这项静态文件事实与活模块来源绑定验证分别登记。

另外两个实际对象的type名称为 `_ModuleWithDeprecations`。R31收集器和分类器要求 `type(module) is type(sys)`，因此把包装对象的file/spec等字段记为UNKNOWN，后续拒绝。只读核读已锁 `cryptography/utils.py:73-121`，可见ModuleType子类、_module字段和sys.modules替换；algorithms.py与modes.py均调用deprecated。当前运行缺少包装类对象身份及底层_module的完整实时绑定证据，来源仍受限。

上述两项是本轮观察到的精确接口缺口。未知对象持续被拒绝，FULL_CONTRACT_ACCEPTED=false，native退出1。本轮未注入恶意依赖、摘要篡改或路径替换，相关未触发故障分支保持静态范围。

R30原始记录缺具体模块身份，因此 `R30_EXACT_MISMATCH_ORIGIN_UNKNOWN`继续成立。R32三项拒绝已经定位；历史R30触发者保持其原证据边界。原生Rust父子模块线索没有被当作本轮实际根因。
