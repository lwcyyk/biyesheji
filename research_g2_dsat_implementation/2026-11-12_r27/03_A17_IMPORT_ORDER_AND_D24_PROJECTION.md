# A17导入顺序与D24双文件投影

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助单文件测试基础设施实现与静态审查；本轮未导入或执行新Runner，未运行--help、测试、SQLite或测试子进程。外部独立复核待取得。

## A17保持

PHASES固定A1→H1→D1A。模块顶层仅18个标准库import，版本预检读取metadata/hash，不importcryptography。load_group只在当前phase被调用，先完成A1/H1后才读取并执行D1A测试字节。原A17源和断言保持。

load_group在A1/H1入口检查cryptography/services/storage/materials尚未进入缓存；audit进一步拒绝前阶段的crypto导入和所有阶段的生产services/storage/materials导入/执行。原测试只读services源进行AST检查，符合该边界。

新case alias必须不存在，普通注册后执行固定源；不删除或替换真实生产模块缓存，不伪造crypto。项目模块、原case、crypto/SQLite/ctypes实际origin/hash未来按阶段及POSTCHECK保存；原R25未单独dump的完整模块列表不在本轮补造。

## 从R26取得两个准确输入

| 名称 | 冻结SHA-256 | 字节 |
|---|---|---:|
| test_metadata.json | `1c6283d77d75d9617adff2b06cea39bc1658aa4b9c0d9ee2e823fcc2c8d50037` | 1032 |
| test_request.json | `90cf2149c79ccd43caa82aa8da51d6542b5776ac8bd9ec5ecc01cb163f9f0c69` | 287 |

原始绝对路径均位于R22 r19_24_002，已进入R26保护清单；R19原留存的同名版本也具有相同hash。R27_D24_PATH_PROJECTION逐项保存原路径、R26来源、目标和逻辑路径。这两份是原D24生成产物的历史冻结版本，不增加原10fixture集合。

本轮用AST常量与已锁JSON作静态代入，复核RuntimeConfig digest、固定process向量及metadata/request字段；得到的规范JSON摘要分别与上述两份原文件一致。仅保存证明数据和摘要，未调用项目函数、运行D24或创建投影副本。证据见sources/D24_STATIC_SUBSTITUTION.json。

## 有限映射及量词

逻辑域只含LOGICAL/test_metadata.json和LOGICAL/test_request.json；LOGICAL为旧R19下一个从未创建的唯一虚拟前缀。物理域仅新RUN中的同名两文件。对任一D24产生的bytes，写入前必须匹配对应冻结hash；任一叶名、父路径或hash不同均PATH_PROJECTION_REJECTED。

成功写入时，原规范字节原样进入新副本；read facade每次检查active D24、目标路径身份及SHA后，才提供exists/is_symlink/lstat/stat/parents/read_bytes。旧原文只读，无内容/Schema转换。生产read_offline_json先按原逻辑前缀校验，再通过受控Path provider访问物理文件；生产实现/白名单源字节保持。

writer和provider只在OrderedSuite选中D24时激活，覆盖原setUp/body/tearDown；A1/H1与D01-D23不受影响。with退出无论成功失败都先恢复原runtime.Path和CONFIG.output，再记录恢复状态。非精确两个路径在active provider中直接拒绝，目录穿越/别名/硬链接/重解析均无法扩大集合。

本投影仅支持冻结D24的测试文件等价，不能据此宣称生产白名单允许任意R26路径。动态运行仍需确认上下文实际恢复及原正例通过。
