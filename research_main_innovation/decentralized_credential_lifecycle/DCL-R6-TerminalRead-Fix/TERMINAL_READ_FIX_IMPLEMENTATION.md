# 最小修复实现与修改范围

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

最终TerminalRead-static-1/r1位于独立tr01。59文件＝39 Linux程序＋2 host程序＋18输入，未来Linux部署57项。

|位置|修改理由与行为|
|---|---|
|terminal_evidence.py（新增）|独立只读context、固定Root元数据、SH counter/phase锁、原window/预算/journal/phase/退出核验，历史boot分离及既有native包审查|
|startup_lifecycle.seal_applicability|终态读取分流，不再进入G.state依赖；缺件/错误保存类型和摘要，原纯预窗NA分支保持|
|guard.seal|保持原等待/打包，在等待后读取终态前提、验证活动接口拒绝CLOSED，再由caller写pre-native审查报告|
|guard/boot授权接口|绑定terminal合同及新的显式批准位，未来回执不足时在原生准备前拒绝|
|guard的C00后序|原PT64→PF48后接TR40，然后在同一窗口关闭；full formal prefix的TR资格另核验|
|terminal_regression/oracle（新增）|40固定job/8变异，独立原始trace审查，原预算prepay16＋audit1计费|
|输入/namespace/执行锁|新batch13-r1/tr01/控制目录及必要摘要、顺序与资源界；原Source pf01不覆盖|

13份保护程序含五业务/预算range_core/probe/S驱动/C00Ready/C09/MR套件等字节相同；原PT64/PF48 jobs相同。70成员AST、整个RootIPC/MR模块保持，原slice字节保持。两份host行政文件完全相同，admin_postexit仅固定namespace/源版本调整，流程AST不变。

没有新增运行快照或重写现有journal。terminal_seal_review由sealer在审查后新建，只承载证据。活动态G.state及原PF读取/发布机制保持原AST，原有终态标记不改写。

全部源码路径、前后摘要与文本差异见[FILE_DIFF_INDEX](evidence/FILE_DIFF_INDEX.json)和[完整diff](evidence/FULL_DIFF.patch)。r1源码/输入副本及59项锁完整保留。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
