# 固定版本真实权限调用链的离线集成

## Material Passport

提交：`528a0213f01caf70b9f41009cbf7b2f67bdd67ec`。源码由固定提交的官方归档建立`baseline/`工作副本。`fixed/`在原始链验证后复制，权限修复仅作用于独立副本。Go1.26.10通过官方SHA-256核验；依赖与诊断记录见[DEPENDENCY_AND_TOOLCHAIN.json](DEPENDENCY_AND_TOOLCHAIN.json)。

证据层级为**完整选定权限调用链的进程内离线回归**：实际Beego路由/过滤器、Casbin、原生控制器、原生字段权限和隔离SQLite效果均参与。认证服务网络调用0，真实账户操作0。未启动生产服务或HTTP监听器。

## 恢复的真实逻辑

|环节|本轮实际执行|证据与定位|
|---|---|---|
|实际路由|`routers.InitAPI()`注册原路由，`web.BeeApp.Handlers.ServeHTTP`分派进程内请求|baseline/routers/router.go；Beego v2.3.8 ControllerRegister；请求仅由httptest生成|
|请求/过滤器顺序|RequestBodyFilter、ContentTypeFilter、UploadedFileFilter；StaticFilter、AutoSigninFilter、CorsFilter、TimeoutFilter、ApiFilter、FieldValidationFilter|顺序对照冻结main.go:113–123。fixture属性故障注入位于AutoSignin后、授权前|
|响应终止|真实Beego过滤器执行与ResponseWriter.Started处理|保留默认return-on-output；错误响应使后续过滤器/控制器停止，未用布尔mock模拟框架终止|
|来源与会话|真实casdoor_file provider及Beego文件会话，位于各run隔离目录|源AT在隔离token表；AutoSigninFilter以实际查询参数建立Cookie；没有手写允许谓词|
|Origin与主体|原CorsFilter、getSubject、isCrossOriginCookieRequest、getUsername|同源基准；X_ORIGIN的外来Origin被真实CorsFilter提前拒绝。其他跨源组合仍属范围外|
|客户端限制|原checkDynamicClientSession及其原生应用查询|baseline权限表达式未修正；在fixed中才应用MINIMAL_PATCH.diff|
|全局权限|原authz.IsAllowed、Casbin v2.77.2、原模型与策略|通过原initBuiltInApiModel/Adapter/Enforcer及authz.InitApi装载；原CheckApiPermission仍参与fallback|
|控制器权限|原ApiController.UpdateUser、IsAdmin、CheckPermissionForUpdateUser、FilterUserSelfColumns|使用原GetDefaultAccountItems；显示名默认Self。X_FIELD把该合成组织字段改为Admin以检验真实拒绝|
|效果|原object.UpdateUser写隔离SQLite；实际GetUserinfo输出合成用户sub|读取真实临时行确认显示名从before到after；没有自写self-policy提供最终许可|

内置API模型允许subject与object同名同组织的self关系。正常用户的显示名在原默认AccountItems中允许Self修改。客户端限制缺失时，这两个真实规则确实让三个目标用例到达效果；它们已由实际链验证，前阶段mock影响缺口关闭。

## 替代及插桩边界

外部存储换为独立SQLite与隔离文件会话。`object/ci01_audit_io.go`仅安装存储、创建合成行、使用真实默认配置和注入SQL查询故障；权限判定函数保持原逻辑。应用/源token查询错误通过临时重命名隔离表产生，未替换授权结果。

`OBSERVABILITY.diff`加入阶段事件和窄范围计数：客户端门槛结果、主体、global IsAllowed进入/结果、控制器进入/权限通过、源身份清理及查询。基准文件包含这些观测插桩，其**权限决策逻辑未修改**；不将其称为逐字节未改的源码。观测代码不向策略返回决策。纯原始文件保存在`originals/`，补丁与观测差异分开。

Prometheus、RecordMessage/AfterRecordMessage等外部请求日志汇集环节未装入测试。ApiFilter自身的权限日志/记录逻辑仍执行，相关表和provider配置均为合成/空值。测试进程的默认HTTP传输器拒绝任何出站调用，并记录尝试数；各批次为0。实际浏览器、TLS、代理部署、身份初次认证/密码/MFA、并发调度未验证。

独立登录B16使用原SetSessionUsername并明确声明其新认证前提；来源损坏项通过真实session Set/Delete注入合成故障。初始token是隔离DB中的合成引用，初始发行流程及这些状态在任意生产配置中的可达性不在本轮证明范围。

## 分层见证

|阶段|M081/B02/B04基准版|修复版|
|---|---|---|
|路由解析|真实update-user路由已匹配|相同|
|客户端门槛|返回继续且保留fixture/alice|返回匿名继续，源身份已清除|
|主体识别|已认证fixture/alice|匿名|
|全局权限|真实Casbin/self条件通过|真实全局权限拒绝|
|控制器权限|控制器已进入，原字段检查通过|控制器未分派，记录null/未到达|
|合成效果|SQLite显示名实际变化|无显示名变化|
|后续session存储读取|username/aud/scope/signinTokenId仍在|四项均为空|

没有用函数return true直接登记受保护访问成功；匿名继续X_ANON同时展示“门槛继续、身份为空、公共health可用”。阶段未执行时使用null，不补记为通过。

## 原始运行及证据冻结

`raw/baseline01`首先确认117个输入（113原例＋4框架控制）能够完整执行。M081/B02/B04的真实权限和效果满足[PATCH_GATE.json](PATCH_GATE.json)，随后才创建fixed副本。`raw/fixed01`为首次修复运行。

最终`raw/paired02_baseline`与`raw/paired02_fixed`额外加入目标操作后的实际会话存储读取，输入和测试代码完全相同。原两批保留，原目标请求结果在四批中一致。各最终批次启动前保存源码快照与哈希。基准/修复Go测试退出0表示框架执行及控制有效；基准的3条合同违反由独立配对分析明确登记，未当成合同全部通过。

完整产品main、前端和所有API未运行。本轮已消除所选操作上的模拟下游权限缺口，结论保持为已登记配置、方法和进程内调用链。
