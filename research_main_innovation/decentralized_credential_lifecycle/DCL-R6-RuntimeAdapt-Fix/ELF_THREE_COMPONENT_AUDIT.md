# 三个ELF组件独立身份审查

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

三项均为ELF64、小端、Machine62（x86-64/AMD64），三个主要/usr/lib路径均为普通Root文件，最终目标与路径相同。已记录的/lib64及解释器别名另有精确symlink文本和resolve目标绑定。

|artifact_id|字节数|GNU Build-ID|SHA-256|
|---|---:|---|---|
|ld-linux-x86-64.so.2|236616|231ab65dd867a89dce29cb958fd5ca50abb1aa34|5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f|
|libc.so.6|2129424|8cebda42d140fc2b09639f8b13a5d5f2e617ef09|755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a|
|libm.so.6|952616|f772fc0c42a75e38f138f8b66f1ebc8aad060525|5dcc4d25466e29ca390ed6fabb371c69b65dff6fa4e91c34561057a020d6994a|

|对象|DT_NEEDED/符号关系|来源与裁决|
|---|---|---|
|ld-linux|无DT_NEEDED；提供GLIBC_PRIVATE等版本定义|libc6:amd64 8.12，静态匹配|
|libc|需要同名ld-linux；含GLIBC_PRIVATE与GLIBC_ABI_DT_RELR等|同一libc6包，静态匹配|
|libm|需要libc与ld-linux；最高已观察定义包含GLIBC_2.39|同一libc6包，静态匹配|

旧8.9包三个成员与旧锁SHA完全相符，新的版本定义名称集合无增加/删除。该比较仅覆盖GNU版本命名集合，不能证明函数行为、线程调度或资源占用相同。Build-ID与Native readelf及独立纯ELF-note解析3项一致；Build-ID并未替代SHA。

真实路径、别名、文件大小/uid/gid/mode、包信息、所有版本定义/需要列表、readelf -h/-n/-d/-V/-l原输出分别保留。没有对目标ELF使用ldd执行检查；ldd仅运行受信系统工具的--version。

[三组件完整字段](evidence/ELF_ABI_AUDIT.json) · [路径/别名和旧成员导出](evidence/PLATFORM_EXPORT.json) · [新旧版本集合](evidence/OLD_NEW_SYMBOL_COMPARISON.json) · [新旧pin](evidence/RUNTIME_PIN_DIFF.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
