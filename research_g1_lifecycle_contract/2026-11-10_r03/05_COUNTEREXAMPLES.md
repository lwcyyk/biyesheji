# 反例与具体失败路线

全部为源码条件下的纸面轨迹，新增原生/测试/求解执行0。符号材料满足R02固定源合同；不需要真实秘密值。

## 1. CE1：LOST错误缩K而提前成功

初态p有效、gA/gB批准有效、b独立。甲rA持久放行，spent=1；AS Insert c并删除p，响应丢失。运行观察LOST。正确K包含W2，settle:i继续存在。

错误路线只保留“没有新凭据且不会再创建”的解释，删去W2并把settle:i设空。随后用户撤回甲，p的UserInfo/内省拒绝或revoke未找到行仍成功；乙一次操作成功。错误模型把这些条件写成A_native_closed/B_operation_observed且无义务，从而可把此节点视为终态。

真实c仍可能有效。最短关键序列为：放行→隐藏创建/丢响应→LOST错误缩K→撤回→父失效观察→乙成功/错误完成。违反P1/P2的包含及P7/P8终态反映。即使一个错误输入表内部delta一致，有限schema/策略检查也没有自动补全真实源后继的能力。本例不登记任何实际机器ACCEPTED。

修正：LOST取全部相容后继并集，保留settle:i；只有可靠同源创建见证饱和上界或独立无效果/终态证据，才可结清相应余额。父材料当前失效不承担该证明。

## 2. CE2：父已撤销，在途子代仍可创建

甲rA已release。AS读取p并通过有效性/用户/scope检查，暂停在新Token插入前。用户撤回甲，随后可信处置使p失效；此时AT UserInfo拒绝、RT内省inactive可均已观察。旧handler用已加载且先前检查通过的父对象继续生成/Insert c；客户端仍可能没有c材料。

若关闭只依父失效，之后c出现便反驳该判断。该轨迹由R02 Go586—705/738—758、ExpireToken351—366的分离读写允许。c_i=1仍成立，未用掉的一个潜在创建槽必须保留。

额外条件分别为：目标入口/未来派生封口；所有在途创建已入I；可靠不同见证或无效果终态；c及声明后代范围被覆盖；接受路径失效持续、无重激活/时钟回退绕过。条件不足时返回UNKNOWN/settle:i，不能从父撤销ACK获得全世系或C_effect。

## 3. CE3：known_handle不能凭空解除opaque责任

在PAPER_A_SOURCE中，LOST增加session `opaque:pending_i#refresh_i#0`。之后只观察p失效。

若把它加入known_handle cleanup，a/model.prepare明确禁止known_handle的session以opaque:开头；若改成account_root并宣称applied=true，它会在source语义中删除这个session，但真实AS没有相应“排除未来迟到创建”的栅栏合同。CE2给该映射反例。单改session名称为known也不能补出真实句柄/来源。

即便后来可信c确实已处置，这份无cleanup源样例仍保留opaque，导致额外UNKNOWN/无有界胜策。结论限定这条session直接编码；没有证明所有A间接编码都需要新schema。

## 4. CE4：当前W门不保证强制撤回的派发

从实际LOST后K_U接管，用户要求撤回。withdraw_a满足当前批准/账户/预算/转移条件，对全部u都保持b和未结责任，后继v正确记录C_local。

在完整例子中v仅有dispose_p，且可观察P_DISPOSAL_UNKNOWN→fp；fp是严格义务非空的停止节点。因而v不在任何W_h，withdraw_a也不在当前W菜单。BoundedController的参考后继检查会拒绝该接线；使用h更多仍不能消除显式失败分支。

一个更小的结构反例仅需两状态：u有待结settle:i且甲active；withdraw→v撤回甲但仍有settle:i；v无终态路径。withdraw即时合法且安全，仍无法通过保证完整关闭的W门。此例区分“必须立即接受的外部撤回事件”和“保证有界闭合的可选计划动作”的合同。

当前持久Controller直接执行用户撤回，没有调用研究W门。本反例裁定未来将该事件完全放进此门的具体路由，保留现有W算法在原有完整终态语义下的正确性。

## 5. CE5：乙支持的时间/实际合同不能由标签替代

若b在模型执行期间到期或用户撤回乙，实际乙能力可消失；仍在所有节点硬填support:b就违反P6。两个token字符串不同也不能排除共享原生撤销影响。

当前样例显式使用B-independent/B-window。扩大范围时要加入相应失败/unsafe分支或当前性重建。B过去成功仅证明其当次操作，不能覆盖未来刷新和全部业务。用户最小合同的原生前提仍由G1负责。

## 6. CE6：保守责任编码不自动满足现有关系检查器

取一个显式具体表节点只含support:b，抽象表额外加session:opaque及close义务表示未确定出现的风险；其余安全目标保持。即使另有适当的风险抽象证明，当前abstraction.check_relation要求capabilities集合相等，会报capability_mapping；它只允许义务包含而非任意cap重解释。

因此，不能把A的潜在风险session直接当作已被该检查器认证的物理能力映射。可以先在具体合同中同样定义“未结风险”标签再检查有限表关系，或提出受证明约束的检查器扩展；原生映射仍需独立证明。该例限定当前identity-cap关系接口。

## 7. 反例范围

CE1/CE2反驳错误原生关闭；CE3定位session直接映射的解除障碍；CE4定位W执行目标/事件路由；CE5定位真实保留前提；CE6定位检查器允许的关系类型。它们均未给出候选相对最强通用方法的必要代价差，也不排除通用有限状态机正确建模本场景。
