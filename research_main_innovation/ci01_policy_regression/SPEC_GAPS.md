# 未决规范逐项登记

保留上一阶段的60项SPEC_UNRESOLVED。行为变化独立记录；尚无新产品规范或设计决定将这些项升级为通过。所有输入仍为合成状态。

|用例|上下文/对象状态|缺少的规范|原始实际结果|本轮预期|
|---|---|---|---|---|
|M005|regular / bearer / present / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M006|regular / bearer / present / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M007|regular / bearer / present / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M008|regular / bearer / present / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M013|regular / bearer / missing / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M014|regular / bearer / missing / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M015|regular / bearer / missing / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M016|regular / bearer / missing / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M017|regular / bearer / disabled / complete / valid / edit_display_name|DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M018|regular / bearer / disabled / complete / valid / read_userinfo|DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M021|regular / bearer / disabled / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M022|regular / bearer / disabled / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M023|regular / bearer / disabled / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|M024|regular / bearer / disabled / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|M029|regular / cookie / present / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M030|regular / cookie / present / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M031|regular / cookie / present / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M032|regular / cookie / present / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M033|regular / cookie / missing / complete / valid / edit_display_name|普通应用删除后存量会话/允许API的完整生命周期合同|ALLOW|SPEC_UNRESOLVED|
|M034|regular / cookie / missing / complete / valid / read_userinfo|普通应用删除后存量会话/允许API的完整生命周期合同|ALLOW|SPEC_UNRESOLVED|
|M037|regular / cookie / missing / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|ALLOW|SPEC_UNRESOLVED|
|M038|regular / cookie / missing / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|ALLOW|SPEC_UNRESOLVED|
|M039|regular / cookie / missing / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M040|regular / cookie / missing / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M041|regular / cookie / disabled / complete / valid / edit_display_name|DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M042|regular / cookie / disabled / complete / valid / read_userinfo|DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M045|regular / cookie / disabled / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M046|regular / cookie / disabled / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M047|regular / cookie / disabled / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|M048|regular / cookie / disabled / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|M053|dcr / bearer / present / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M054|dcr / bearer / present / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M055|dcr / bearer / present / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M056|dcr / bearer / present / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M061|dcr / bearer / missing / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M062|dcr / bearer / missing / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M063|dcr / bearer / missing / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M064|dcr / bearer / missing / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M066|dcr / bearer / disabled / complete / valid / read_userinfo|DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M069|dcr / bearer / disabled / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M070|dcr / bearer / disabled / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M071|dcr / bearer / disabled / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|M072|dcr / bearer / disabled / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|M077|dcr / cookie / present / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M078|dcr / cookie / present / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|M079|dcr / cookie / present / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M080|dcr / cookie / present / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|M082|dcr / cookie / missing / complete / valid / read_userinfo|普通应用删除后存量会话/允许API的完整生命周期合同|ALLOW|SPEC_UNRESOLVED|
|M085|dcr / cookie / missing / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|ALLOW|SPEC_UNRESOLVED|
|M086|dcr / cookie / missing / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|ALLOW|SPEC_UNRESOLVED|
|M087|dcr / cookie / missing / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M088|dcr / cookie / missing / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；普通应用删除后存量会话/允许API的完整生命周期合同|DENY|SPEC_UNRESOLVED|
|M090|dcr / cookie / disabled / complete / valid / read_userinfo|DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M093|dcr / cookie / disabled / missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M094|dcr / cookie / disabled / missing / valid / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|ALLOW|SPEC_UNRESOLVED|
|M095|dcr / cookie / disabled / missing / expired / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|M096|dcr / cookie / disabled / missing / expired / read_userinfo|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同；DisableSignin是否覆盖已存在token/session及允许API|DENY|SPEC_UNRESOLVED|
|B12|dcr / cookie / present / aud_missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|
|B13|dcr / cookie / present / id_missing / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|DENY|SPEC_UNRESOLVED|
|B15|dcr / cookie / present / malformed_aud / valid / edit_display_name|来源属性缺失/改型的正常可达性、旧格式识别与独立登录区分，以及相应处理合同|ALLOW|SPEC_UNRESOLVED|

说明：某项同时含明确的到期拒绝条件和来源损坏，仍按历史登记保留未决，不通过观察到拒绝来补齐丢失的产品规范。新增最小补丁只处理可识别的应用绑定上下文；其对这些格的变化进入PAIRED_RESULTS.json单列。

明确独立登录B16有新的认证前提，与丢失来源的旧会话区别登记。源属性均缺失的两个历史可能产生相同剩余上下文，缺少额外依据时不能自行推定来自独立新认证。此处保留信息/规范缺口，不实施新持久协议。
