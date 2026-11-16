# 静态、只读查询与兼容检查结果

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

|检查|实际结果|
|---|---|
|业务/模型/Launcher/服务|全部0；T0/R=null|
|原生只读查询|7次WSL封装调用，版本/包/签名/ELF/缓存/日志/最终环境/文件读取条件，raw argv与双流完整|
|44程序|主机AST/3.12文法/内存compile通过；20条运行时身份控制流断言|
|ELF兼容|66冻结入口，114解析对象，剩余DT_NEEDED/版本缺项0；条件性静态解析|
|纯ELF parser探针|主机对3份保存ELF只读解析GNU Build-ID，与Native readelf相同；非业务动态测试|
|源码保护|13文件字节/70成员AST保持，完整RootIPC/MR/Terminal模块保持；host两文件字节保持；PT/PF/TR jobs保持|
|来源|两份InRelease签名与完整索引SHA/size匹配，dpkg目录/文件MD5一致；信任Root/DB/keyring前提明确|
|当前状态|三项当前组件和Python在最终只读检查仍相同；未来/实例/slice未创建|
|执行准备|64文件/44程序/62 Linux项；精确RuntimeAdapt身份及未批准新模板齐备|

RA-1/2/3=CONDITIONAL_PASS，RA-4=PASS_STATIC。新ABI、文件/包元数据和执行时匹配提供必要条件与拒绝策略；未取得资源/服务/TerminalRead动态资格或完整时间证明。

行政分析器的初始systemd-core缺项被父已加载唯一SONAME关系解释并保留初图；冻结器按实际文件集合处理三项glibc，不假定它们在stdlib树内。它们属于分析工具修正，没有修改系统文件、旧执行锁或业务判据。

[机器结果](evidence/STATIC_RESULT.json) · [静态断言与3探针](evidence/SYNTAX_AND_IDENTITY_CONTROL_CHECK.json) · [最后摘要核验](evidence/FINAL_BINDING_REVIEW.json) · [全部只读调用](COMMAND_SUMMARY.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
