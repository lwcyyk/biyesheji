# 本轮交付：原生记录关系验证与停止条件审查

## Material Passport

origin_skill: academic-research-suite；origin_mode: construct-validate-review；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: source-binding-delivery-01；repro_lock: null。

**有界辅助模块的实现与验证材料已经形成；较强独立创新性仍未确认，因此不能声称已满足“创新点和工作量都达到后停止调研”的条件。** 工作量无需再靠堆积功能增加，剩余应聚焦直接先例与贡献审查。

本轮新增的实质实现是：在真实 MPC 内用共享密钥计算 AES-GCM 标签差和声明明文差，再把同一计算中的残差交给诊断层。此前 native_demo.py 只由明文驱动者生成残差；旧文件保留，本轮没有重新归类历史证据。

八种记录场景经过新方案、原 moments、coordinate 三种方法的同输入核对；新方案另作语义重放。域外密钥份额在任何诊断输出前触发预期拒绝。基本算术经全部字节域乘法、S-box、AES已知向量和独立GCM库验证。

## 入口

- [记录关系、条件性论证、成本和复现](SOURCE_BINDING_2026-11-03.md)
- [创新性、工作量及停止条件审查](CLOSURE_REVIEW_2026-11-03.md)
- [源代码与实验生成器](source_binding/build_experiment.py)
- [实际执行的 MPC 程序](source_binding/generated01/bind_gcm.mpc)
- [完整证据、原始结果哈希与源文件快照](results/source_binding_delivery01/manifest.json)

总成本主要来自标准AES/GCM关系计算。新方案消耗16,297个triples，原moments为16,269，coordinate为16,220；不能据此宣称端到端性能优势。所有方法获得相同密钥份额、原生记录信息和底座能力。

仍缺：2026/946全文逐算法对照、创新优先权确认、会话密钥与服务身份的绑定、TLS握手与状态时效、生产级可信结果传输和全面恶意行为审计。当前为两条16字节AES-128-GCM记录、96位nonce、同机两方、GF(2^128)数据域及40位底座统计参数的开发原型。

本轮所有新增内容位于独立密码学研究目录；主线仓库、原DOCX和过去源码/实验均保持原状。
