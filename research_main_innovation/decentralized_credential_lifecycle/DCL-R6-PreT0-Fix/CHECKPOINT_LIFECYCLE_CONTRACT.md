# 检查点生命周期合同

Material Passport：PreT0Recovery-static-1/r3；原RootIPC检查点保留严格语义。

|对象|创建者/阶段/前提|持久化与读取|失败处理|
|---|---|---|---|
|sealed ticket/claim|原bootstrap与Owner；原预检/一次认领|原memfd/Root私有记录/FD和Owner身份，代码保持|原始拒绝，结束当前启动|
|pt_context|初始Root child；有效活体sealed Session|Root私有exclusive文件及目录同步；身份/源/boot/授权/Tcb期限|缺失或冲突拒绝预窗|
|pt_phase|Root生命周期层；单调阶段|Root私有phase及追加事件，序号/前SHA|非法回退/记录缺失停止|
|runtime intent|Root qualified分支；所有运行对象尚无|exclusive持久标记，先于T0|重入拒绝；部分初始化保留|
|T0/state|原_root launcher；intent有效、停止未发布|原Root发布；真实时钟和原1800/1740关系|失败即关闭，禁止填入假值|
|counter/COMMITTED intent|原init_counter；真实state及再检查|原预算核心不改；仅创建一次|中断保守保留，无退款或重置|
|PT_RUNTIME_CHECKPOINT|runtime_ready；state/counter确已建立|Root:989/0640，绑定window/初始化ID/源/预算inode-cap-magic|运行态缺失/身份错/损坏拒绝|
|RUNTIME_ARMED|Root；STOP_ARMED/Owner/父TasksMax等通过|更新同一checkpoint的phase/sequence|未armed不启动工作service|
|C00及后继资格|原controller/Root；合法运行窗和工作gate|原实际八字段、pidfd及全部既有证据|原判据保持|

专用prewindow_checkpoint只在活体认证initial_query_scope中使用；其允许对象仅为静态/授权/启动上下文与OS部署查询。原RootIPC.checkpoint依然默认要求运行state；运行恢复的manager查询不获得预窗token。预窗scope看到runtime intent或任何运行对象即拒绝，避免全局allow_uninitialized绕过。

运行检查验证counter不可变部分（magic/cap/device/inode）和intent文件存在/类型。并发used/intent的一致性仍由原预留锁及正式账审查负责，避免把合法PREPARED瞬间误判损坏。实际预算内容/身份错误继续由原核心和当前checkpoint共同阻断。

[最终生命周期代码](evidence/SOURCE_FINAL_R3/src/startup_lifecycle.py) · [既有语义保持](evidence/PROTECTED_SEMANTICS_CHECK.json)。
