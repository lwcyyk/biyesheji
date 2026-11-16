# MR-1必要证据、版本与读取索引

本轮只读。所有主稿用账户U0、客户端C0、批准P_A/P_B和已存rid A0/A1/B0等抽象标识；没有导出原生凭据、句柄秘密或账号值。没有打开secret材料文件、解密HTTP或连接在线AS数据库。

## 冻结主证据

根目录：[M2-03原始轨迹](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/M2-03)。

- [ENVIRONMENT_LOCK](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/ENVIRONMENT_LOCK.json)：版本/二进制摘要/原配置及源码参照，构建关系UNPROVED。
- [原始SOURCE_LOCK](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/SOURCE_LOCK.json)与source_snapshot：16个文件全部hash相符，结果在SOURCE_BINDING.json。
- [outcome](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/M2-03/runner/outcome.json)：ack/A_after_ack/B_continue/lookup_unknown/disposal_A0。
- [初态投影](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/M2-03/runner/initial_visible.json)：version8，两批准及两个初始结果。
- [终态投影](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/M2-03/runner/final_visible.json)：version17，A1仍UNKNOWN义务，A0已named处置。
- [最终原生观察](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/M2-03/scorer/final_native.json)：rows[0]A0阴性、rows[1]B0阳性、rows[2]A1阳性且runner_has_result=false。发送序号72–78。
- [原生适配器事件](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/M2-03/provider/native_events.jsonl)：第5行A1原生成功序号67；没有operational_result_durable事件。
- [控制器事件](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/M2-03/controller/events.jsonl)：第19行after_effect屏障，后续恢复/版本11撤回，第31行lookup UNKNOWN，第34行known处置。

只保存必要白名单事实的JSON指针/行定位和摘要见EVIDENCE_INDEX.json；没有复制上述原始记录。

## 锁定代码的实际读取

实际读源码位置均在`mainline_native_casdoor_v1/source_snapshot`，不把未来修订运行器回投旧轨迹：

- native_provider.py：全部。lookup只查运行收件箱；perform固定来源及操作；dispose结合named观察。
- storage.py：call及grant/admit/release/record/revoke/prepare_disposal/record_disposal。重点157–331行的绑定、来源、预算和本地事务。
- services.py：Controller及HTTP角色鉴别部分。SingleActive、恢复、grant/revoke/交付/处置和source转交。
- native_acceptance.py：preflight、configure_case、run_case、run_native及故障分支；M2-03明确关闭inbox。
- lab.py：初始化角色/权限和可信OS/目录边界。
- native_http.py：固定菜单、Cookie限制、发送前记账及加密证据；只读，没有调用。
- materials.py：类型/投影/身份约束；没有从实际材料运行验证函数。
- measure_native_casdoor.py：observe全部；final只有已知A材料会被测RT，未知A1没有被该测量刷新。
- 其他锁内文件只核hash，未声称全源码逐行审阅。

提供方参照代码为CI归档的Casdoor checkout：commit528a0213…；object/token_oauth_util.go的351起ExpireToken、370起RevokeToken、562起RefreshToken及后续新记录/轮换部分。只读Git对象和工作文件blob一致：

```text
object/token_oauth_util.go  a78ae71307ef2ae135c322512c481082944ae9d5
object/token.go             20bc03cf9ef28beaaedbcc1d7093753da932bcd6
controllers/token.go        520b0e6011542f51e2656bbba345ed617843e200
```

它只作源代码参照；没有升级可复现构建，也没有把其他配置分支当成当前实测。

## 评分修订与未混用范围

[既有M2-03离线复核](D:/毕业设计/mainline_native_casdoor_v1/review/M2-03_recheck.json)和[原修正收据](D:/毕业设计/mainline_native_casdoor_v1/review/SCORER_CORRECTION.json)区分原restart计数假报警与真实原生事实。原scorer/result.json保持SAFETY_FAILURE；复核PASS没有清空A1义务。本轮未重跑原/新评分器。

M2-04、其本地supplement、M2-02持久inbox、survey/pilot的其他资源策略以及CI01的raw-RT/其他应用/Cookie/会话观测均未用于补本case。CI归档只读取合同/能力矩阵和裁决边界，用于防止跨profile外推，不重开已归档缺陷。

## 账本读取

[归档预算库](D:/毕业设计/mainline_native_casdoor_v1/raw/batch01/native_budget.db)以mode=ro&immutable=1打开。内部用序号63对应账户过滤，限制原前缀≤88；未导出actor原值。COST_INDEX.json保留操作/状态/长度及聚合索引，查读前后DB字节相同。

[历史成本汇总](D:/毕业设计/mainline_native_casdoor_v1/COST_AND_RESULTS.json)只取records中的M2-03条目（SQL104、commit17、逻辑字节394129）；不将整批114次当成单case迁移成本。当前原生/在线AS查询均0。

## 理论及B依据

MT-1 VALUE/DECISION、当前B MODEL/engine.py、experiment/planning.py均按输入哈希固定。B菜单和G函数为当前代码事实；M2-03的实测运行没有调用该B引擎执行迁移。主理论、下界和优先权不在本轮重审。

INPUT_HASHES.json列必要原文/日志/代码hash；DELIVERY_VALIDATION.json只作字节/路径/文档检查。哈希和同上下文反方分析不构成新增独立数学或安全验证。
