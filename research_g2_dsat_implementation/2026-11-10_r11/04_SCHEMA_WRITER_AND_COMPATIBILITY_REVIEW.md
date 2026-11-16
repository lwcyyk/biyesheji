# writer、物理格式及兼容性审查

## 当前writer覆盖

静态搜索src/scripts、核对AuthorityStore.call白名单和启动wrapper后，声明的非recover handler共有10个：grant、admit、release、record、revoke、prepare_disposal、record_disposal、begin_reconciliation、reconciliation_context、save_reconciliation。同一源码中的世界DML集中在genesis INSERT、统一UPDATE和event INSERT。[C01:80–85,122–148]

完整逐操作字段、风险、a/o、证书依赖及未来回归见`WRITER_AND_OBLIGATION_MATRIX.json`的18类。`WRITER_COVERAGE_REVIEWED`限定锁定仓库路径；实际部署仍为`WRITER_COVERAGE_GAP`，因为复制的运行代码、已有连接、外部DB/key/restore访问及AS写入者当前未盘点。

必须把所有旧handler接到同一typed O推导/变更钩子。不能只给新S3入口更新o，也不能按返回status判断旧handler是否修改了世界：release的REJECTED分支会取消队列并减少reserved。旧包装器正常返回即a+1，拒绝、重复和reconciliation_context均可能在内；其原语义应保留。新S3必须有独立dispatcher/事务入口，拒绝与重放绕开旧统一增版本包装器。

## 具体前沿检查例：reserved已满

纸面状态来自grant+admit之后：grant g active=true、operations包含issue、limit=1、reserved=1、spent=0；请求r为合法同origin的QUEUED issue，attempt/release均null，窗口未激活，原正文摘要已正确保存。其他字段按既有Schema提供。

legacy obligations只收unknown/quarantined及特定window，因此此时可为空。`limit > spent+reserved`也为false。然而release仍会为r产生attempt、转spent并send=true。该例定位“只看自由余额推断无创建机会”的错误。B1应增加queued_creator前沿或等价hold，不能凭空改旧O或原预算。该结论属于接口映射检查；T3、S2数学证明及R10结果保持原有范围。[C01:197–259;C09:121–148]

## Schema and legacy compatibility

真实SQL支持0/1/2，schema2仅修改user_version；加密行和AAD仍为schema1。AES-GCM使用12字节随机nonce、32字节外部key，canonical(state)为明文输入，AAD为固定常量。明文SQL版本和事件表未被该AAD绑定。whole-state解密/重加密成本线性；旧库完整回滚仍可验证原密文。[C01:21,47–120;C14/C15]

B2候选保持authority_state/version/ciphertext及旧请求语义，在加密state.dsat内增加唯一o、typed O与索引，另设同库production proposal/object表。回执/证明/私密scope内容继续用生产加密与权限保护；事件投影只放受控摘要/计数/引用。采用SyntheticJsonCodec会改变秘密存储合同。

AAD3可按现有AES-GCM绑定instance/schema/a或对象kind/key/digest，须有明确格式过渡和旧解码策略。该绑定只能处理相应元数据篡改，整体旧DB/key回滚的排除还依赖独立部署信任。此处是待审设计，本轮没有SQL或密码学实现。

## 迁移及进程门

12门详见`SCHEMA_AND_MIGRATION_GATES.json`。初步备份必须是WAL一致快照；fence/停旧writer后再固定最终迁移基准。只复制authority.db可能遗漏已提交WAL。

SQL事务可以原子建立新表、更新加密namespace/迁移回执与user_version。进程停启、配置/密钥、文件备份与服务激活处于SQL之外，需分阶段留恢复点，失败时保持fence并拒绝服务，避免自动空初始化或无审定回退。

旧程序启动遇schema3可拒绝；已经打开的旧连接并不会因header改变而自动退出。SingleActive锁只在Controller，AuthorityStore的RLock仅实例内。B2需核所有Authority/Controller及复制副本，停止旧writer、限制文件访问并建立新版本事务guard。当前没有执行这些操作。

旧native-attempt-closure/1、CLOSED/1、W_h继续原义。新typed证书和O使用独立版本与消费资格。普通agent status看不到全局typed O，旧严格字段消费者也可能拒绝新字段。重叠typed风险尚未处理时，升级端应阻断旧接口被用作新全局关闭；原单attempt历史回执保留其范围。旧格式兼容与全局判断资格分别验收。
