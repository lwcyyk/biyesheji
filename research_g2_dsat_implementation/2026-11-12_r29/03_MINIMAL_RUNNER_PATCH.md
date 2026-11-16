# 最小Runner补丁

日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助单文件修复、AST/源码/元数据/哈希审查。本轮Runner与测试模块未导入，--help和所有测试未执行，SQL/key/测试进程资源0；外部独立核验待取得。

## 采用的策略

采用R28指定的**拒绝缓存内容、回退到已锁源码**策略，属于源码优先加载的受控实现。原3个测试模块继续直接compile其已核对字节；应用包和原CLI helper的标准SourceFileLoader通过OSError回退读取原.py。包结构、相对导入与模块正常注册由原导入器保持。

修改顶层定义：controls、State、load_group、main；另有errno标准库import、控制锁schema及命名空间常量。原生产模块/reader和测试源码没有变化。

## 预期探测的完整条件

1. open分类为只读，后缀.pyc。
2. source_from_cache反推得到明确.py，属于当前47源/单独Runner或394条运行时代码清单。
3. cache_from_source(source,optimization="")重新生成的当前tag路径与请求完全相同。
4. 源和缓存路径元数据通过规范组件、重解析和硬链接检查；不打开缓存内容。
5. 源SHA匹配。
6. 记录绑定和操作字段，再抛PermissionError/EACCES；缓存bytes_read=0。

固定get_code捕获该OSError后读取原source；source/exec/origin检查仍然成立。预期探测单列meter.expected_cache_probes、按路径去重计数，不加入致命denials；它代表确实拒绝cache的政策决定，不声称cache文件不存在。

## 其他分支

未映射、错误tag、未知源、SHA变化、symlink/hardlink或I/O异常均记录路径、mode/flags、phase、derived source、原因及原cause，再以READ_SCOPE_REFUSED终止。普通未知读取仍保留该拒绝语义。对源码I/O失败会保留原OSError原因，不能把它误分类成预期cache回退。

缓存写入继续走原严格输出白名单，.pyc不在13个名字中，因此不被允许。没有全局.pyc读取白名单，没有读取cache字节，没有删sys.modules或mockcrypto。

新入场还要求optimize=0并拒绝预先加载的project/case模块，保持锁定flags和新过程源身份；原A17断言保持原字节。

## 读取权限收紧

旧代码无条件允许Python安装目录、当前record目录以及output目录读取。现在普通读取按明确历史/控制/源文件集合、运行时代码清单或13个输出名判定。

运行时清单394个精确.py/.pyd文件分别具有path、SHA、module和来源理由，AST导入闭包包括父包初始化，声明包范围限crypto/cffi/pycparser代码；编码和import支持另列。该清单是静态保守代码包络，不能解释为394文件均必需或已经实际读过。未知数据/配置/其他package文件继续拒绝。

相对旧Python前缀规则，新增cache内容权限0，普通目录权限收紧；新增R29控制JSON仅服务本次锁定。原24关键runtime指纹保持，其余新清单指纹不伪称R25已逐文件观察过。
