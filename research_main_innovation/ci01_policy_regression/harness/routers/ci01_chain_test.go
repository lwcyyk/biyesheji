//go:build ci01audit

package routers
import (
 stdcontext "context"
 "bytes"
 "encoding/json"
 "fmt"
 "io"
 "net/http"
 "net/http/httptest"
 "os"
 "path/filepath"
 "testing"
 "github.com/beego/beego/v2/server/web"
 beecontext "github.com/beego/beego/v2/server/web/context"
 "github.com/beego/beego/v2/server/web/session"
 "github.com/casdoor/casdoor/authz"
 "github.com/casdoor/casdoor/ci01audit"
 "github.com/casdoor/casdoor/controllers"
 "github.com/casdoor/casdoor/object"
)
type ci01Case struct{
 ID string `json:"id"`;Client string `json:"client_type"`;Auth string `json:"authentication_context"`;AppState string `json:"application_state"`;Source string `json:"source_information"`;Session string `json:"session_state"`;Operation string `json:"operation"`;TokenState string `json:"source_token_state"`;Expected string `json:"expected"`;Basis []string `json:"expectation_basis"`
}
type ci01Result struct{
 ID string `json:"id"`;Expected string `json:"historical_expected"`;Actual string `json:"actual"`;HTTP int `json:"http"`;BusinessStatus string `json:"business_status,omitempty"`;DisplayChanged bool `json:"synthetic_display_changed"`;UserinfoAccepted bool `json:"synthetic_userinfo_accepted"`;Stages []ci01audit.Event `json:"stages"`;Counts map[string]int `json:"observed_costs"`;FrameworkError string `json:"framework_error,omitempty"`;PostSession map[string]bool `json:"post_session_fields_present,omitempty"`
}
var ci01Current *ci01Case
var ci01Phase string
var ci01Outbound int
type ci01NoNetwork struct{}
func(ci01NoNetwork)RoundTrip(req *http.Request)(*http.Response,error){ci01Outbound++;return nil,fmt.Errorf("CI01 blocks all runtime HTTP; requested host %s",req.URL.Host)}

func ci01FixtureIO(ctx *beecontext.Context){
 if ci01Phase!="target"||ci01Current==nil{return}
 c:=ci01Current
 // Context fault inputs from the old 113-case suite are injected at the same
 // post-authentication/pre-authorization boundary, using the real session API.
 if c.Auth=="native_login"{
  controller:=&controllers.ApiController{};controller.Ctx=ctx
  controller.SetSessionUsername("fixture/alice")
 }
 switch c.Source{
 case "missing":_ = ctx.Input.CruSession.Delete(stdcontext.Background(),"aud");_ = ctx.Input.CruSession.Delete(stdcontext.Background(),object.SessionSigninTokenId)
 case "aud_missing":_ = ctx.Input.CruSession.Delete(stdcontext.Background(),"aud")
 case "id_missing":_ = ctx.Input.CruSession.Delete(stdcontext.Background(),object.SessionSigninTokenId)
 case "scope_missing":_ = ctx.Input.CruSession.Delete(stdcontext.Background(),"scope")
 case "malformed_aud":_ = ctx.Input.CruSession.Set(stdcontext.Background(),"aud",17)
 }
 if c.Session=="expired"{_ = ctx.Input.CruSession.Set(stdcontext.Background(),"SessionData",`{"ExpireTime":1}`)}
}
func ci01InstallFramework(t *testing.T,out string){
 t.Helper()
 http.DefaultTransport=ci01NoNetwork{}
 t.Setenv("origin","https://fixture.invalid");t.Setenv("originFrontend","https://fixture.invalid")
 t.Setenv("driverName","sqlite3");t.Setenv("dataSourceName",filepath.Join(out,"synthetic.db"));t.Setenv("dbName","")
 t.Setenv("isDemoMode","false");t.Setenv("forceLanguage","en");t.Setenv("enableErrorMask","false")
 if err:=object.Ci01InstallStorage(filepath.Join(out,"synthetic.db"));err!=nil{t.Fatal(err)}
 authz.InitApi()
 web.BConfig.CopyRequestBody=true
 web.BConfig.WebConfig.Session.SessionOn=true
 web.BConfig.RunMode="test"
 web.BConfig.EnableGzip=false
 web.BConfig.WebConfig.EnableXSRF=false // frozen main does not enable Beego XSRF; native Origin guard remains active
 sessions:=filepath.Join(out,"sessions");if err:=os.MkdirAll(sessions,0755);err!=nil{t.Fatal(err)}
 manager,err:=session.NewManager(FileSessionProvider,&session.ManagerConfig{CookieName:"ci01sid",EnableSetCookie:true,Gclifetime:3600,Maxlifetime:3600,ProviderConfig:sessions})
 if err!=nil{t.Fatal(err)};web.GlobalSessions=manager
 web.BeeApp.Handlers=web.NewControllerRegister()
 InitAPI()
 web.InsertFilter("*",web.BeforeStatic,func(ctx *beecontext.Context){_,found:=web.BeeApp.Handlers.FindRouter(ctx);ci01audit.Record("route_resolved",found,ctx.Request.URL.Path)})
 web.InsertFilter("*",web.BeforeStatic,RequestBodyFilter)
 web.InsertFilter("*",web.BeforeStatic,ContentTypeFilter)
 web.InsertFilter("*",web.BeforeStatic,UploadedFileFilter)
 web.InsertFilter("*",web.BeforeRouter,StaticFilter)
 web.InsertFilter("*",web.BeforeRouter,AutoSigninFilter)
 web.InsertFilter("*",web.BeforeRouter,ci01FixtureIO)
 web.InsertFilter("*",web.BeforeRouter,CorsFilter)
 web.InsertFilter("*",web.BeforeRouter,TimeoutFilter)
 web.InsertFilter("*",web.BeforeRouter,ApiFilter)
 web.InsertFilter("*",web.BeforeRouter,FieldValidationFilter)
 web.InsertFilter("*",web.BeforeExec,func(ctx *beecontext.Context){ci01audit.Record("controller_dispatch",true,ctx.Request.URL.Path)})
 // Prometheus and external request-log sinks are omitted (observation I/O only).
}
func ci01Request(method,path string,payload []byte,cookies []*http.Cookie,bearer bool,origin string)*httptest.ResponseRecorder{
 req:=httptest.NewRequest(method,"https://fixture.invalid"+path,bytes.NewReader(payload));req.Host="fixture.invalid"
 if payload!=nil{req.Header.Set("Content-Type","application/json")};req.Header.Set("Accept-Language","en")
 if origin!=""{req.Header.Set("Origin",origin)}
 if bearer{req.Header.Set("Authorization","Bearer synthetic-at")}
 for _,cookie:=range cookies{req.AddCookie(cookie)}
 response:=httptest.NewRecorder();web.BeeApp.Handlers.ServeHTTP(response,req);return response
}
func ci01Run(t *testing.T,c ci01Case,control string)ci01Result{
 t.Helper();if err:=object.Ci01ResetFixture(c.Client);err!=nil{t.Fatal(err)}
 ci01Current=nil;ci01Phase="seed"
 var cookies []*http.Cookie
 if c.Auth=="cookie"{
  seed:=ci01Request("GET","/api/userinfo?accessToken=synthetic-at",nil,nil,false,"")
  var body map[string]interface{};_ = json.Unmarshal(seed.Body.Bytes(),&body)
  if seed.Code!=200||body["sub"]!="fixture-user-id"{t.Fatalf("seed failed: %d %s",seed.Code,seed.Body.String())}
  cookies=seed.Result().Cookies();if len(cookies)==0{t.Fatal("native session cookie not created")}
 }
 if err:=object.Ci01SetStates(c.AppState,c.TokenState);err!=nil{t.Fatal(err)}
 fault:="";if c.AppState=="lookup_error"{fault="application"};if c.TokenState=="lookup_error"{fault="token"}
 if fault!=""{if err:=object.Ci01Fault(fault,true);err!=nil{t.Fatal(err)}}
 if control=="field_admin"{if err:=object.Ci01SetDisplayPolicy("Admin");err!=nil{t.Fatal(err)}}
 path:="/api/update-user?id=fixture/alice&columns=displayName";method:="POST";payload:=[]byte(`{"owner":"fixture","name":"alice","displayName":"after"}`)
 if c.Operation=="read_userinfo"{path="/api/userinfo";method="GET";payload=nil}
 if control=="wrong_target"{path="/api/update-user?id=fixture/bob&columns=displayName";payload=[]byte(`{"owner":"fixture","name":"bob","displayName":"after"}`)}
 if control=="public_health"{path="/api/health";method="GET";payload=nil}
 origin:="https://fixture.invalid";if control=="cross_origin"{origin="https://other.invalid"}
 ci01Current=&c;ci01Phase="target";ci01audit.Begin()
 response:=ci01Request(method,path,payload,cookies,c.Auth=="bearer",origin)
 ev,counts:=ci01audit.End();ci01Current=nil;ci01Phase=""
 if fault!=""{if err:=object.Ci01Fault(fault,false);err!=nil{t.Fatal(err)}}
 display,err:=object.Ci01DisplayName();if err!=nil{t.Fatal(err)}
 var body map[string]interface{};_ = json.Unmarshal(response.Body.Bytes(),&body)
 status,_:=body["status"].(string);accepted:=response.Code==200&&body["sub"]=="fixture-user-id"
 changed:=display=="after"
 actual:="DENY";if changed||accepted{actual="ALLOW"}
 if control=="public_health"&&response.Code==200&&status=="ok"{actual="ALLOW"}
 if response.Code>=500{actual="INCONCLUSIVE"}
 res:=ci01Result{ID:c.ID,Expected:c.Expected,Actual:actual,HTTP:response.Code,BusinessStatus:status,DisplayChanged:changed,UserinfoAccepted:accepted,Stages:ev,Counts:counts}
 if c.Auth=="cookie"||c.Auth=="native_login"{
  observedCookies:=cookies;if len(observedCookies)==0{observedCookies=response.Result().Cookies()}
  probe:=httptest.NewRequest("GET","https://fixture.invalid/offline-session-read",nil)
  for _,cookie:=range observedCookies{probe.AddCookie(cookie)}
  stored,readErr:=web.GlobalSessions.SessionStart(httptest.NewRecorder(),probe)
  if readErr!=nil{t.Fatal(readErr)}
  res.PostSession=map[string]bool{}
  for _,key:=range []string{"username","aud","scope",object.SessionSigninTokenId}{v:=stored.Get(stdcontext.Background(),key);res.PostSession[key]=v!=nil&&v!=""}
  // Observer-only storage read, outside the measured target-operation counters.
 }
 if actual=="INCONCLUSIVE"{res.FrameworkError=response.Body.String()}
 return res
}
func TestCI01FullPermissionChain(t *testing.T){
 out:=os.Getenv("CI01_OUTPUT");input:=os.Getenv("CI01_CASES");if out==""||input==""{t.Fatal("CI01_OUTPUT and CI01_CASES required")}
 if err:=os.MkdirAll(out,0755);err!=nil{t.Fatal(err)}
 ci01InstallFramework(t,out)
 file,err:=os.Open(input);if err!=nil{t.Fatal(err)};defer file.Close();data,err:=io.ReadAll(file);if err!=nil{t.Fatal(err)}
 var wrapper struct{Cases []ci01Case `json:"cases"`};if err=json.Unmarshal(data,&wrapper);err!=nil{t.Fatal(err)}
 results:=[]ci01Result{}
 for _,c:=range wrapper.Cases{c:=c;t.Run(c.ID,func(t *testing.T){
  result:=ci01Run(t,c,"");results=append(results,result)
  if result.Actual=="INCONCLUSIVE"{t.Error("framework outcome inconclusive")}
  // Baseline mismatches remain observations and are adjudicated in paired analysis.
 })}
 controls:=[]struct{id,kind,client,expected string}{{"X_ORIGIN","cross_origin","regular","DENY"},{"X_FIELD","field_admin","regular","DENY"},{"X_TARGET","wrong_target","regular","DENY"},{"X_ANON","public_health","dcr","ALLOW"}}
 for _,x:=range controls{x:=x;t.Run(x.id,func(t *testing.T){
  c:=ci01Case{ID:x.id,Client:x.client,Auth:"cookie",AppState:"present",Source:"complete",Session:"valid",Operation:"edit_display_name",TokenState:"live",Expected:x.expected}
  result:=ci01Run(t,c,x.kind);results=append(results,result);if result.Actual!=x.expected{t.Errorf("integration control expected %s got %s",x.expected,result.Actual)}
 })}
 bytes,err:=json.MarshalIndent(map[string]interface{}{"results":results,"runtime_HTTP_attempts":ci01Outbound,"new_real_accounts":0,"native_service_calls":0},"","  ");if err!=nil{t.Fatal(err)}
 if err=os.WriteFile(filepath.Join(out,"chain_results.json"),bytes,0644);err!=nil{t.Fatal(err)}
 if ci01Outbound!=0{t.Fatal("unexpected outbound runtime HTTP attempt")}
}
