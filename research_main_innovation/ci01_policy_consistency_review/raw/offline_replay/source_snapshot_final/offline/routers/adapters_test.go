package routers
import (stdcontext "context";"errors";"net/http";"net/url";"sync"
 context "policyreview.local/mockcontext"
 object "policyreview.local/mockobject"
)
// In-memory session store. Persistence is recorded as a boolean only.
type lazySessionStore struct{lock sync.Mutex;ephemeral bool;values map[interface{}]interface{}}
func(s *lazySessionStore)Get(_ stdcontext.Context,k interface{})interface{}{return s.values[k]}
func(s *lazySessionStore)Set(_ stdcontext.Context,k,v interface{})error{s.values[k]=v;return nil}
func(s *lazySessionStore)Delete(_ stdcontext.Context,k interface{})error{delete(s.values,k);return nil}
func(s *lazySessionStore)SessionRelease(_ stdcontext.Context,_ http.ResponseWriter){}
func responseError(ctx *context.Context,msg string,args ...interface{}){ctx.Denied=true;ctx.Reason="AUTHENTICATION_OR_LOOKUP_ERROR"}
func responseInvalidToken(ctx *context.Context,t *object.Token,code,msg string){ctx.Denied=true;ctx.Reason="SOURCE_TOKEN_REJECTED"}
func denyRequest(ctx *context.Context){ctx.Denied=true;ctx.Reason="CLIENT_API_RESTRICTION"}
func getUsernameByClientIdSecret(ctx *context.Context)(string,error){if ctx.Input.Query("clientId")!=""||ctx.Input.Query("clientSecret")!=""{return "",errors.New("extra credential forbidden in fixture")};return "",nil}
func getUsernameByAccessKey(ctx *context.Context)(string,error){if ctx.Input.Query("accessKey")!=""{return "",errors.New("extra credential forbidden in fixture")};return "",nil}
func checkUserPasswordWithoutMfa(a,b,c,d string)error{return errors.New("password authentication outside fixture scope")}
func getAcceptLanguage(ctx *context.Context)string{return "en"}
func newContext(path string,values map[interface{}]interface{})*context.Context{
 copied:=map[interface{}]interface{}{};for k,v:=range values{copied[k]=v}
 return &context.Context{Input:&context.Input{CruSession:&lazySessionStore{values:copied},Data:map[interface{}]interface{}{},Queries:map[string]string{}},
  Request:&http.Request{Method:"POST",URL:&url.URL{Path:path},Host:"fixture.invalid",Header:http.Header{}}}
}
// No resource mutation. This is the explicitly approved downstream mock policy.
func evaluate(ctx *context.Context,path string)(string,string,bool,string){
 AutoSigninFilter(ctx)
 return evaluateAfterAuth(ctx,path)
}
func evaluateAfterAuth(ctx *context.Context,path string)(string,string,bool,string){
 if ctx.Denied{return "DENY",ctx.Reason,false,""}
 gate:=checkDynamicClientSession(ctx,path)
 if !gate||ctx.Denied{return "DENY",ctx.Reason,gate,""}
 owner,name:=getSubject(ctx)
 if owner=="anonymous"||name=="anonymous"{return "DENY","NO_AUTHENTICATED_SUBJECT_AFTER_POLICY",gate,""}
 if owner!="fixture"||name!="alice"{return "CONTEXT_INSUFFICIENT","MOCK_POLICY_HAS_NO_RULE_FOR_SUBJECT",gate,owner+"/"+name}
 return "ALLOW","CLIENT_GATE_CONTINUES; MOCK_SELF_POLICY_ALLOWS",gate,owner+"/"+name
}
