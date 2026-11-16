> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_author_implementation_audit/MINIMAL_REPRODUCTION_SPEC.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# 最小复现规格：作者UE的Enc→TG→Upd→Dec轨迹

2026-11-10。规格状态：**PREPARED_ENTRYPOINT_PENDING_AUTHOR_ARTIFACT**。实际作者UE执行状态：**NOT_EXECUTED**。本规格准备材料与判据；本轮运行轨迹、正确率估计和性能重现次数均为0。

## 1. 最小外部包及入口

接收一份经作者/论文/机构明确关联目标DOI的不可变代码包或commit，包含UE driver、六配置和依赖说明。来源认证需同时满足：可验证论文关联、不可变版本/完整源码哈希、实际含TG/Upd/Ord/Tensor及调用driver。只有官方Frodo基础库或同名账号时，状态保持UNRESOLVED。

目前作者入口文件、callable和CLI argv均未取得，登记为null。收到后把真实位置写成entrypoints中的文件路径、行号、函数签名或原样argv；本规格没有假定作者提供任何自造CLI选项。来源核验可记录git commit、dirty状态、包SHA256、Python/NumPy/依赖与BLAS/平台版本，源码改动应有单独patch与哈希。

## 2. 固定输入与模型标签

最小第一条为报告640-AES或640-SHAKE之一，参数完整导出n=640、D=15、q=32768、m̄=n̄=8、B=2及χ640/CDF。选择一个在抽样前固定的128位合法消息，例如全零16字节；记录原始bytes、bit顺序和位长。A的生成方式必须实际标明为全矩阵均匀、AES seed、SHAKE seed或其它，不把它们合成一个标签。

976/1344各消息长度按ℓ=B·m̄·n̄导出，通常为192/256位；六配置分别记录。CF-1另需要参数化入口、χ640及随λ增长的D/q证明；单个标准640运行只提供一个有限配置的轨迹。程序支持范围在静态核查后再赋MAPPED/DIFFERS。

随机性规格至少列出Setup、old/new KeyGen、Enc、TG每块U/F/G、Upd R对应的源位置、seed来源/长度、域前缀、XOF输入、输出长度、切片区间、重复/共享关系和调用顺序。可重放材料需提供合成seed/输入字或完整可重现熵轨迹及生成器版本；只有哈希时记录为观察轨迹，不能登记逐币可重放。

## 3. 运行前的静态接收判据

| 顺序 | 要核验的明确条件 | 通过/差异的记录 |
|---|---|---|
| S0 来源 | 作者/机构/论文链接绑定版本，文件哈希匹配 | AUTHENTICATED或UNRESOLVED；缺关联先补证据 |
| S1 参数 | 六配置、CDF/PMF、深度、常量与输出长度导出 | 字段级MAPPED/DIFFERS并附源行 |
| S2 随机性 | A跨代合同，seed独立/复用/域/切片和XOF模型 | 精确law、需统计耦合、需计算混合或UNRESOLVED |
| S3 算法/位序 | TG四块、Upd、形状、额外项、重试，Ord/Tensor匹配 | 逐式映射与置换证据；缺项明确定位 |
| S4 算术 | dtype、每次提升/回绕/取模、符号、编码/packing/舍入 | 环同态或误差证明；条件范围明确 |
| S5 driver | 五操作计时边界、缓存/预处理、消息断言和失败日志 | 代码可执行检查与历史运行证据分别登记 |

上述步骤只做静态对应和材料准备，当前均未执行作者程序。字段齐备后，运行计划可由研究者按其授权范围实施，并保留原始工件。

## 4. 单条轨迹的操作顺序

1. 冻结artifact、依赖、参数、消息及seed规格，生成run_id和配置哈希；公布本条选定的目标模型标签和偏差项。
2. 执行真实Setup，再生成old/new两代key；记录代次、对象ID、A生成/缓存策略及逻辑矩阵A的同一性。若每次KeyGen自生成A，保留两份标识并按实际差异处理。
3. Enc_old(M)取得父密文；用old key解密并记录initial_message、initial_equal与初始异常。为观察未筛选实验，初始比对结果只作记录，后续按预先固定计划继续；若作者driver本身拒绝，则保留该分支与分母。
4. 对old→new调用一次真实TG，记录四块shape、dtype、逻辑/序列化哈希、token_id、key IDs。若内含重试，每一次尝试都保留编号、原因、筛选谓词与接受结果。
5. Upd(token,parent)生成子密文，记录其父ID、新key代次、R生成规格、shape与哈希。一次正常调用的语义与内部循环分别记录。
6. Dec_new(child)记录updated_message、updated_equal、异常/⊥。消息比较发生在正确性记录中；计时窗口是否包括该比较单独标明。
7. 保存按序事件、stdout/stderr/退出状态、原样命令和环境，计算工件清单哈希；使用相同代码/配置/币重放时，分别比对逻辑矩阵与序列化输出，并登记差异。

密文/key/token哈希的规范化需写明shape、模数、行列顺序、整数代表、字节宽度与大小端；同时保留实际序列化哈希。只有哈希相同仅支持采用的序列化下对象身份，通用算法/联合分布仍由静态映射判断。

## 5. 预期证据格式

至少四类文件：artifact_and_environment.json、parameters_and_randomness.json、trace.jsonl、result_and_timing.json，另附原日志和文件清单。每个字段应由实际值填充；待补字段用null并保留状态。以下为**未执行模板**的结构摘要：

```json
{
  "execution_status": "NOT_EXECUTED",
  "paper_doi": "10.46298/fi.14425",
  "artifact": {"authenticated_link": null, "commit_or_archive": null, "sha256": null, "dirty_patch_sha256": null},
  "entrypoints": {"setup": null, "keygen": null, "enc": null, "tg": null, "upd": null, "dec": null, "argv_exact": null},
  "parameters": {"variant": null, "n": null, "D": null, "q": null, "mbar": null, "nbar": null, "B": null, "chi_cdf": null, "max_depth": null},
  "randomness": {"A_generation": null, "cross_generation_A_reuse": null, "seed_manifest": null, "replay_material": null, "call_order": null},
  "arithmetic": {"dtypes": null, "overflow_semantics": null, "modulo_locations": null, "negative_representation": null, "Ord_Tensor_order": null, "rounding": null, "packing": null},
  "objects": {"old_key_id": null, "new_key_id": null, "token_id": null, "parent_id": null, "child_id": null},
  "messages": {"original_hex": null, "bit_length": null, "initial_hex": null, "updated_hex": null, "initial_equal": null, "updated_equal": null},
  "failures": {"initial_error": null, "tg_attempts": null, "filters": null, "retries": null, "update_error": null, "decode_error": null},
  "denominators": {"planned_attempts": null, "initial_correct": null, "completed_updates": null, "all_correct": null, "abort_or_exception": null, "per_operation_timed_calls": null},
  "timing": {"clock": null, "units": null, "operation_windows": null, "preprocessing_and_cache": null, "verification_inside_window": null},
  "model_mapping": {"result_A": "UNRESOLVED", "result_B": "UNRESOLVED", "deviations_and_transfer_bounds": null}
}
```

trace.jsonl每行包含sequence、operation、source_ref、input_object_ids、output_object_ids、key_epoch、seed_domain_ref、retry_index、filter_reason、timing_window和结果状态。原消息、两个解密结果与比较布尔值必须实际记录，不能仅以“程序返回0”替代。

## 6. 正确率与计时的分母

最小轨迹N=1时，只登记一个配置和一组币的行为见证。以后若做统计，先固定计划attempt数，保留全部初始错误、TG/Upd/Dec异常、拒绝与重试。总体全消息正确率以预先定义的全部attempt为分母；程序异常的处理规则与模型事件另列。完成更新数、有效输出数、指定行/坐标分母同时报告，不能通过丢弃异常改变实验。

先完成总体记录，再按initial_equal分组给条件正确率；条件分母为initial_correct，分组包含其中全部最终成功、失败及异常记录。B的单次成功仍是允许事件，单次失败也不能推出其概率下界。分布/采样或筛选差异仍需迁移论证。

计时分别保留N_KG、N_Enc、N_Dec_initial、N_Dec_updated、N_TG、N_Upd；包含A生成、seed抽取、打包、内存分配、预热/缓存或消息验证的范围逐项写明。最小轨迹包含两代KG、一次Enc/TG/Upd以及两次不同用途的Dec，可分别记录而不混合。原论文100次是计时运行口径，重现其均值/标准差还需相同测量边界、硬件/库环境和独立原日志。

## 7. 取得工件后的模型裁决顺序

先填写字段级MAPPED/DIFFERS/UNRESOLVED和确切源行，再填写配置整体状态。A需参数族、公开仿射关系、可逆/噪声与停止预算；B需固定640、A及噪声联合律、未筛选一次更新和舍入。对seed模型使用明确统计耦合或计算引理，保存有限损失；对初始正确条件化使用事件/比率范围。字段或单条输出相符时，结论止于相应范围。

本轮可执行作者入口仍为null，实际消息比对轨迹和率/耗时执行证据均未取得。最能改变当前实现适用裁决的材料是一份可认证作者UE版本，加上完整静态配置/随机性/算术映射及一条消息比对轨迹；来源和静态合同决定如何使用v2.1定理，单次轨迹认证实际代码路径。
