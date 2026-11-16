// Generated verbatim declarations from Casdoor (Apache-2.0); see SOURCE_EXTRACTS.json.
package routers
import (stdcontext "context"; "encoding/json"; "fmt"; "strings"; "time"; "net/http"
context "policyreview.local/mockcontext"
object "policyreview.local/mockobject"
util "policyreview.local/mockutil"
mcpself "policyreview.local/mockmcp"
controllers "policyreview.local/mockcontrollers"
logs "policyreview.local/mocklogs"
conf "policyreview.local/mockconf")

var dynamicClientApis = []string{
	"/api/userinfo",
	"/api/user",
	"/api/mcp",
	"/api/login/oauth",
}

var crossOrgClientApis = []string{
	"/api/userinfo",
	"/api/user",
	"/api/login/oauth",
}

const requestCredentialUserKey = "requestCredentialUser"

func checkDynamicClientSession(ctx *context.Context, urlPath string) bool {
	aud, ok := ctx.Input.Session("aud").(string)
	if !ok || aud == "" {
		return true
	}

	application, err := object.GetApplicationByClientId(aud)
	if err != nil {
		responseError(ctx, err.Error())
		return false
	}
	if application == nil || isClientSessionApiAllowed(application, getSessionUser(ctx), urlPath) {
		return true
	}

	// a request that carries the access token itself is the client using it: keep it within the token's limits
	if credentialUser, _ := ctx.Input.GetData(requestCredentialUserKey).(string); credentialUser != "" {
		denyRequest(ctx)
		return false
	}

	// otherwise it is the browser, sending only the cookie that the token-authenticated response left behind:
	// sign that session out and go on as anonymous, so the login page and the rest of Casdoor keep working there
	err = clearSessionOfToken(ctx)
	if err != nil {
		responseError(ctx, err.Error())
		return false
	}
	return true
}

func isRestrictedClientSession(ctx *context.Context) (bool, error) {
	aud, ok := ctx.Input.Session("aud").(string)
	if !ok || aud == "" {
		return false, nil
	}

	application, err := object.GetApplicationByClientId(aud)
	if err != nil || application == nil {
		return false, err
	}
	return !isClientSessionApiAllowed(application, getSessionUser(ctx), "/login/oauth/authorize"), nil
}

func isClientSessionApiAllowed(application *object.Application, userId string, urlPath string) bool {
	if isCrossOrgClient(application, userId) {
		return util.InSlice(crossOrgClientApis, urlPath)
	}
	if application.IsDynamicClient() {
		return util.InSlice(dynamicClientApis, urlPath) || strings.HasPrefix(urlPath, "/api/server/")
	}
	return true
}

func isCrossOrgClient(application *object.Application, userId string) bool {
	if application.Organization == "built-in" || userId == "" || object.IsAppUser(userId) {
		return false
	}
	owner, _ := util.GetOwnerAndNameFromIdNoCheck(userId)
	return owner != application.Organization
}

func getUsername(ctx *context.Context) (username string) {
	username, ok := ctx.Input.Session("username").(string)
	if !ok || username == "" {
		username, _ = getUsernameByClientIdSecret(ctx)
	}

	session := ctx.Input.Session("SessionData")
	if session == nil {
		return
	}

	sessionData := &controllers.SessionData{}
	err := util.JsonToStruct(session.(string), sessionData)
	if err != nil {
		logs.Error("GetSessionData failed, error: %s", err)
		return ""
	}

	if sessionData.ExpireTime != 0 &&
		sessionData.ExpireTime < time.Now().Unix() {
		err = ctx.Input.CruSession.Set(stdcontext.Background(), "username", "")
		if err != nil {
			logs.Error("Failed to clear expired session, error: %s", err)
			return ""
		}
		err = ctx.Input.CruSession.Delete(stdcontext.Background(), "SessionData")
		if err != nil {
			logs.Error("Failed to clear expired session, error: %s", err)
		}
		return ""
	}

	return
}

func getSubject(ctx *context.Context) (string, string) {
	username := getUsername(ctx)
	if username == "" || isCrossOriginCookieRequest(ctx) {
		return "anonymous", "anonymous"
	}

	// username == "built-in/admin"
	owner, name, err := util.GetOwnerAndNameFromIdWithError(username)
	if err != nil {
		panic(err)
	}
	return owner, name
}

func isCrossOriginCookieRequest(ctx *context.Context) bool {
	method := ctx.Request.Method
	if method == http.MethodGet || method == http.MethodHead || method == http.MethodOptions {
		return false
	}
	if strings.HasPrefix(ctx.Request.URL.Path, "/api/saml/logout/") {
		return false
	}

	origin := ctx.Request.Header.Get("Origin")
	if origin == "" || util.IsCredentialedOrigin(origin, conf.GetConfigString("origin"), ctx.Request.Host) {
		return false
	}

	requestCredentialUser, _ := ctx.Input.GetData(requestCredentialUserKey).(string)
	return requestCredentialUser == ""
}

func AutoSigninFilter(ctx *context.Context) {
	urlPath := ctx.Request.URL.Path
	if strings.HasPrefix(urlPath, "/api/login/oauth/access_token") {
		return
	}
	// The RFC 7591/7592 DCR endpoints authenticate themselves: the bearer value is the
	// application's "registration_access_token", which is not a row in the "token" table.
	if strings.HasPrefix(urlPath, "/api/oauth/register") {
		return
	}
	if urlPath == "/api/mcp" {
		var req mcpself.McpRequest
		if err := json.Unmarshal(ctx.Input.RequestBody, &req); err == nil {
			if req.Method == "initialize" || req.Method == "notifications/initialized" || req.Method == "ping" || req.Method == "tools/list" {
				return
			}
		}
	}
	//if getSessionUser(ctx) != "" {
	//	return
	//}

	// GET parameter like "/page?access_token=123" or
	// HTTP Bearer token like "Authorization: Bearer 123"
	accessToken := ctx.Input.Query("accessToken")
	if accessToken == "" {
		accessToken = ctx.Input.Query("access_token")
	}
	if accessToken == "" {
		accessToken = parseBearerToken(ctx)
		if accessToken != "" {
			skipSessionPersistence(ctx)
		}
	}

	if accessToken != "" {
		token, err := object.GetTokenByAccessToken(accessToken)
		if err != nil {
			responseError(ctx, err.Error())
			return
		}

		// an ID-JAG is a grant to be redeemed at another authorization server, not an access token
		if token == nil || token.TokenType == "ID-JAG" {
			responseInvalidToken(ctx, nil, "invalid_token", "Access token doesn't exist in database")
			return
		}

		isExpired, expireTime := util.IsTokenExpired(token.CreatedTime, token.ExpiresIn)
		if isExpired {
			responseInvalidToken(ctx, token, "invalid_token", fmt.Sprintf("Access token has expired, expireTime = %s", expireTime))
			return
		}

		// The token's user may have been forbidden or deleted after the token was issued
		isUserActive, err := token.IsUserActive()
		if err != nil {
			responseError(ctx, err.Error())
			return
		}
		if !isUserActive {
			responseInvalidToken(ctx, token, "invalid_token", "The user is forbidden to sign in, please contact the administrator")
			return
		}

		// Validate DPoP proof for DPoP-bound tokens (RFC 9449).
		if token.TokenType == "DPoP" {
			dpopProof := ctx.Request.Header.Get("DPoP")
			if dpopProof == "" {
				responseInvalidToken(ctx, token, "invalid_dpop_proof", "DPoP proof header required for DPoP-bound access token")
				return
			}
			htu := object.GetDPoPHtu(ctx.Request.Host, ctx.Request.URL.Path)
			jkt, dpopErr := object.ValidateDPoPProof(dpopProof, ctx.Request.Method, htu, accessToken)
			if dpopErr != nil {
				responseInvalidToken(ctx, token, "invalid_dpop_proof", fmt.Sprintf("DPoP proof validation failed: %s", dpopErr.Error()))
				return
			}
			if jkt != token.DPoPJkt {
				responseInvalidToken(ctx, token, "invalid_token", "DPoP proof key binding mismatch")
				return
			}
		}

		application, err := object.GetApplicationByUserId(fmt.Sprintf("app/%s", token.Application))
		if err != nil {
			responseError(ctx, err.Error())
			return
		}
		if application == nil {
			responseError(ctx, fmt.Sprintf("No application is found for userId: app/%s", token.Application))
			return
		}

		var userId string
		if token.GrantType == "client_credentials" {
			userId = object.GetAppUserId(application)
		} else {
			userId = util.GetId(token.Organization, token.User)
		}
		setSessionSigninToken(ctx, userId, token)
		setSessionUser(ctx, userId)
		setSessionOidc(ctx, token.Scope, application.ClientId)
		return
	}

	err := clearSessionOfRevokedToken(ctx)
	if err != nil {
		responseError(ctx, err.Error())
		return
	}

	// "/page?clientId=123&clientSecret=456"
	userId, err := getUsernameByClientIdSecret(ctx)
	if err != nil {
		responseError(ctx, err.Error())
		return
	}
	if userId != "" {
		skipSessionPersistence(ctx)
		setSessionUser(ctx, userId)
		return
	}

	// "/page?accessKey=123&accessSecret=456"
	userId, err = getUsernameByAccessKey(ctx)
	if err != nil {
		responseError(ctx, err.Error())
		return
	}
	if userId != "" {
		skipSessionPersistence(ctx)
		setSessionUser(ctx, userId)
		return
	}

	// "/page?username=built-in/admin&password=123"
	userId = ctx.Input.Query("username")
	password := ctx.Input.Query("password")
	if userId != "" && password != "" && ctx.Input.Query("grant_type") == "" {
		err = checkUserPasswordWithoutMfa(userId, password, util.GetClientIpFromRequest(ctx.Request), getAcceptLanguage(ctx))
		if err != nil {
			responseError(ctx, err.Error())
			return
		}

		setSessionUser(ctx, userId)
	}
}

func getSessionUser(ctx *context.Context) string {
	user := ctx.Input.CruSession.Get(stdcontext.Background(), "username")
	if user == nil {
		return ""
	}

	return user.(string)
}

func setSessionUser(ctx *context.Context, user string) {
	ctx.Input.SetData(requestCredentialUserKey, user)

	err := ctx.Input.CruSession.Set(stdcontext.Background(), "username", user)
	if err != nil {
		panic(err)
	}

	// https://github.com/beego/beego/issues/3445#issuecomment-455411915
	ctx.Input.CruSession.SessionRelease(stdcontext.Background(), ctx.ResponseWriter)
}

func setSessionSigninToken(ctx *context.Context, userId string, token *object.Token) {
	tokenId, _ := ctx.Input.CruSession.Get(stdcontext.Background(), object.SessionSigninTokenId).(string)
	if tokenId == "" && getSessionUser(ctx) == userId {
		return
	}

	err := ctx.Input.CruSession.Set(stdcontext.Background(), object.SessionSigninTokenId, token.GetId())
	if err != nil {
		panic(err)
	}
}

func setSessionOidc(ctx *context.Context, scope string, aud string) {
	err := ctx.Input.CruSession.Set(stdcontext.Background(), "scope", scope)
	if err != nil {
		panic(err)
	}
	err = ctx.Input.CruSession.Set(stdcontext.Background(), "aud", aud)
	if err != nil {
		panic(err)
	}
	ctx.Input.CruSession.SessionRelease(stdcontext.Background(), ctx.ResponseWriter)
}

func clearSessionOfRevokedToken(ctx *context.Context) error {
	tokenId, _ := ctx.Input.CruSession.Get(stdcontext.Background(), object.SessionSigninTokenId).(string)
	if tokenId == "" {
		return nil
	}

	token, err := object.GetToken(tokenId)
	if err != nil {
		return err
	}
	if token != nil && token.ExpiresIn > 0 {
		isExpired, _ := util.IsTokenExpired(token.CreatedTime, token.ExpiresIn)
		if !isExpired {
			return nil
		}
	}

	return clearSessionOfToken(ctx)
}

func clearSessionOfToken(ctx *context.Context) error {
	for _, key := range []string{"username", "SessionData", "accessToken", "scope", "aud", object.SessionSigninTokenId} {
		err := ctx.Input.CruSession.Delete(stdcontext.Background(), key)
		if err != nil {
			return err
		}
	}
	ctx.Input.CruSession.SessionRelease(stdcontext.Background(), ctx.ResponseWriter)
	return nil
}

func parseBearerToken(ctx *context.Context) string {
	header := ctx.Request.Header.Get("Authorization")
	tokens := strings.Split(header, " ")
	if len(tokens) != 2 {
		return ""
	}

	// Accept both "Bearer" (RFC 6750) and "DPoP" (RFC 9449) authorization schemes.
	prefix := tokens[0]
	if prefix != "Bearer" && prefix != "DPoP" {
		return ""
	}

	return tokens[1]
}

func skipSessionPersistence(ctx *context.Context) {
	if store, ok := ctx.Input.CruSession.(*lazySessionStore); ok {
		store.lock.Lock()
		store.ephemeral = true
		store.lock.Unlock()
	}
}

