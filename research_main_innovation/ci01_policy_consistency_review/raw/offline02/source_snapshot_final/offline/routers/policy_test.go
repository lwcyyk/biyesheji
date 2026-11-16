package routers
import (
 "encoding/json"
 "errors"
 "fmt"
 "os"
 "path/filepath"
 "testing"
 "time"
 object "policyreview.local/mockobject"
 controllers "policyreview.local/mockcontrollers"
)
type Case struct {
 ID string `json:"id"`
 Client string `json:"client_type"`
 Auth string `json:"authentication_context"`
 AppState string `json:"application_state"`
 Source string `json:"source_information"`
 Session string `json:"session_state"`
 Operation string `json:"operation"`
 TokenState string `json:"source_token_state"`
 Expected string `json:"expected"`
 Basis []string `json:"expectation_basis"`
 FixtureNote string `json:"fixture_note,omitempty"`
}
type Result struct {
 ID string `json:"id"`
 Actual string `json:"actual"`
 Reason string `json:"reason"`
 GateContinues bool `json:"gate_continues"`
 AuthenticatedSubjectRetained bool `json:"authenticated_subject_retained"`
 Expected string `json:"expected"`
 ContractCheck string `json:"contract_check"`
 InvariantStatus string `json:"carrier_restriction_invariant"`
}
func setup(client string)*object.Application{
 object.Reset()
 app:=&object.Application{Name:"app-fixture",ClientId:"client-fixture",Organization:"fixture"}
 switch client{
 case "dcr":app.Tags=[]string{"dcr"}
 case "cimd":app.Tags=[]string{"cimd"}
 case "cross_org":app.Organization="other-fixture"
 case "builtin_regular":app.Organization="built-in"
 case "builtin_dcr":app.Organization="built-in";app.Tags=[]string{"dcr"}
 }
 object.Apps[app.ClientId]=app
 object.Tokens["synthetic-at"]=&object.Token{Owner:"admin",Name:"token-fixture",Application:app.Name,Organization:"fixture",User:"alice",Scope:"openid",TokenType:"Bearer",GrantType:"authorization_code",CreatedTime:time.Now().Add(-time.Minute).Format(time.RFC3339),ExpiresIn:3600}
 object.Users["fixture/alice"]=&object.User{}
 return app
}
func runCase(c Case)Result{
 app:=setup(c.Client)
 path:="/api/update-user";if c.Operation=="read_userinfo"{path="/api/userinfo"}
 priorPolicyAllowed:=isClientSessionApiAllowed(app,"fixture/alice",path)
 seed:=newContext("/api/userinfo",nil)
 seed.Input.Queries["accessToken"]="synthetic-at"
 AutoSigninFilter(seed)
 if seed.Denied{panic("fixture conversion unexpectedly rejected")}
 values:=map[interface{}]interface{}{}
 if c.Auth=="cookie" {for k,v:=range seed.Input.CruSession.(*lazySessionStore).values{values[k]=v}}
 ctx:=newContext(path,values)
 if c.Auth=="bearer"{ctx.Request.Header.Set("Authorization","Bearer synthetic-at")}
 switch c.AppState{
 case "missing":delete(object.Apps,app.ClientId)
 case "disabled":app.DisableSignin=true
 case "lookup_error":object.AppError=errors.New("synthetic application lookup failure")
 }
 switch c.TokenState{
 case "missing":delete(object.Tokens,"synthetic-at")
 case "revoked":object.Tokens["synthetic-at"].ExpiresIn=0
 case "expired":object.Tokens["synthetic-at"].CreatedTime="2000-01-01T00:00:00Z"
 case "lookup_error":object.TokenError=errors.New("synthetic source lookup failure")
 }
 if c.Auth=="native_login"{
  // This existing setter is invoked only under the fixture's explicit fresh-login premise.
  ctl:=controllers.ApiController{Store:ctx.Input.CruSession}
  ctl.SetSessionUsername("fixture/alice")
 }
 AutoSigninFilter(ctx)
 store:=ctx.Input.CruSession.(*lazySessionStore)
 switch c.Source{
 case "missing":delete(store.values,"aud");delete(store.values,object.SessionSigninTokenId)
 case "aud_missing":delete(store.values,"aud")
 case "id_missing":delete(store.values,object.SessionSigninTokenId)
 case "scope_missing":delete(store.values,"scope")
 case "malformed_aud":store.values["aud"]=17
 }
 if c.Session=="expired"{store.values["SessionData"]=`{"ExpireTime":1}`}
 actual,reason,gate,subject:=evaluateAfterAuth(ctx,path)
 check:="OBSERVATION_ONLY_SPEC_UNRESOLVED"
 if c.Expected!="SPEC_UNRESOLVED"{check="PASS";if actual!=c.Expected{check="POLICY_MISMATCH"}}
 invariant:="NOT_APPLICABLE_OR_PRESERVED"
 if !priorPolicyAllowed&&actual=="ALLOW"&&c.Auth!="native_login"{
  invariant="VIOLATED_IN_SYNTHETIC_CONTEXT"
  if c.Source!="complete"{invariant="MALFORMED_FIXTURE_GAP_REACHABILITY_UNPROVED"}
 }
 return Result{c.ID,actual,reason,gate,subject!="",c.Expected,check,invariant}
}
func expectation(c Case)(string,[]string){
 if c.Source!="complete"{return "SPEC_UNRESOLVED",[]string{"U_SOURCE_LOSS","fixture fault injection; normal conversion writes these fields"}}
 if c.Session=="expired"{return "DENY",[]string{"R_SESSION_EXPIRY"}}
 if c.AppState=="missing"&&c.Auth=="bearer"{return "DENY",[]string{"R_BEARER_APP_LOOKUP"}}
 restricted:=c.Client=="dcr"||c.Client=="cimd"||c.Client=="cross_org"||c.Client=="builtin_dcr"
 if restricted&&c.Operation=="edit_display_name"{
  return "DENY",[]string{"R_CLIENT_BOUND","R_NO_NEW_AUTHORITY"}
 }
 if c.AppState!="present"{return "SPEC_UNRESOLVED",[]string{"U_APPLICATION_LIFECYCLE"}}
 return "ALLOW",[]string{"R_CLIENT_ALLOWLIST_OR_REGULAR_FALLTHROUGH","M_SELF_POLICY"}
}
func cases()[]Case{
 all:=[]Case{};n:=0
 for _,client:=range []string{"regular","dcr"}{for _,auth:=range []string{"bearer","cookie"}{for _,app:=range []string{"present","missing","disabled"}{for _,source:=range []string{"complete","missing"}{for _,session:=range []string{"valid","expired"}{for _,op:=range []string{"edit_display_name","read_userinfo"}{
  n++;c:=Case{ID:fmt.Sprintf("M%03d",n),Client:client,Auth:auth,AppState:app,Source:source,Session:session,Operation:op,TokenState:"live"}
  c.Expected,c.Basis=expectation(c)
  if source!="complete"{c.FixtureNote="post-authentication field loss is injected into an in-memory context; reachability unproved"}
  all=append(all,c)
 }}}}}}
 extra:=[]Case{
 {ID:"B01",Client:"cimd",Auth:"cookie",AppState:"present",Expected:"DENY",Basis:[]string{"R_CLIENT_BOUND"}},
 {ID:"B02",Client:"cimd",Auth:"cookie",AppState:"missing",Expected:"DENY",Basis:[]string{"R_CLIENT_BOUND","R_NO_NEW_AUTHORITY"}},
 {ID:"B03",Client:"cross_org",Auth:"cookie",AppState:"present",Expected:"DENY",Basis:[]string{"R_CROSS_ORG_BOUND"}},
 {ID:"B04",Client:"cross_org",Auth:"cookie",AppState:"missing",Expected:"DENY",Basis:[]string{"R_CROSS_ORG_BOUND","R_NO_NEW_AUTHORITY"}},
 {ID:"B05",Client:"builtin_regular",Auth:"cookie",AppState:"present",Expected:"ALLOW",Basis:[]string{"R_BUILTIN_EXCEPTION","M_SELF_POLICY"}},
 {ID:"B06",Client:"builtin_dcr",Auth:"cookie",AppState:"present",Expected:"DENY",Basis:[]string{"R_CLIENT_BOUND"}},
 {ID:"B07",Client:"dcr",Auth:"cookie",AppState:"lookup_error",Expected:"DENY",Basis:[]string{"R_LOOKUP_ERROR"}},
 {ID:"B08",Client:"dcr",Auth:"bearer",AppState:"lookup_error",Expected:"DENY",Basis:[]string{"R_LOOKUP_ERROR"}},
 {ID:"B09",Client:"dcr",Auth:"cookie",AppState:"missing",TokenState:"revoked",Expected:"DENY",Basis:[]string{"R_SOURCE_ENDS_SESSION"}},
 {ID:"B10",Client:"dcr",Auth:"cookie",AppState:"missing",TokenState:"expired",Expected:"DENY",Basis:[]string{"R_SOURCE_ENDS_SESSION"}},
 {ID:"B11",Client:"dcr",Auth:"cookie",AppState:"missing",TokenState:"missing",Expected:"DENY",Basis:[]string{"R_SOURCE_ENDS_SESSION"}},
 {ID:"B12",Client:"dcr",Auth:"cookie",AppState:"present",Source:"aud_missing",Expected:"SPEC_UNRESOLVED",Basis:[]string{"U_SOURCE_LOSS"}},
 {ID:"B13",Client:"dcr",Auth:"cookie",AppState:"present",Source:"id_missing",Expected:"SPEC_UNRESOLVED",Basis:[]string{"U_SOURCE_LOSS"}},
 {ID:"B14",Client:"dcr",Auth:"cookie",AppState:"present",Source:"scope_missing",Expected:"DENY",Basis:[]string{"R_CLIENT_BOUND"}},
 {ID:"B15",Client:"dcr",Auth:"cookie",AppState:"present",Source:"malformed_aud",Expected:"SPEC_UNRESOLVED",Basis:[]string{"U_SOURCE_LOSS"}},
 {ID:"B16",Client:"dcr",Auth:"native_login",AppState:"missing",Expected:"ALLOW",Basis:[]string{"R_INDEPENDENT_LOGIN","M_SELF_POLICY"},FixtureNote:"fresh independent login is a stated fixture premise; no user credential is submitted"},
 {ID:"B17",Client:"dcr",Auth:"cookie",AppState:"present",TokenState:"lookup_error",Expected:"DENY",Basis:[]string{"R_LOOKUP_ERROR"}},
 }
 for _,c:=range extra{
  if c.Source==""{c.Source="complete"};if c.Session==""{c.Session="valid"};if c.Operation==""{c.Operation="edit_display_name"};if c.TokenState==""{c.TokenState="live"};all=append(all,c)
 }
 return all
}
func writeJSON(t *testing.T,name string,v interface{}){
 dir:=os.Getenv("AUDIT_OUTPUT");if dir==""{t.Fatal("AUDIT_OUTPUT required")};if err:=os.MkdirAll(dir,0755);err!=nil{t.Fatal(err)}
 data,err:=json.MarshalIndent(v,"","  ");if err!=nil{t.Fatal(err)};if err=os.WriteFile(filepath.Join(dir,name),data,0644);err!=nil{t.Fatal(err)}
}
func TestPolicyMatrix(t *testing.T){
 inputs:=cases();outputs:=[]Result{}
 for _,c:=range inputs{c:=c;t.Run(c.ID,func(t *testing.T){
  r:=runCase(c);outputs=append(outputs,r)
  if r.ContractCheck=="POLICY_MISMATCH"{t.Errorf("source policy mismatch: expected %s, actual %s; %s",c.Expected,r.Actual,r.Reason)}
 })}
 writeJSON(t,"cases.json",inputs);writeJSON(t,"results.json",outputs)
}
func TestConversionAttributePreservation(t *testing.T){
 setup("dcr")
 seed:=newContext("/api/userinfo",nil);seed.Input.Queries["accessToken"]="synthetic-at";AutoSigninFilter(seed)
 values:=seed.Input.CruSession.(*lazySessionStore).values
 for k,want:=range map[string]string{"username":"fixture/alice","aud":"client-fixture","scope":"openid",object.SessionSigninTokenId:"admin/token-fixture"}{if values[k]!=want{t.Errorf("%s not preserved",k)}}
 if seed.Input.CruSession.(*lazySessionStore).ephemeral{t.Error("query-token fixture unexpectedly ephemeral")}
 bearer:=newContext("/api/userinfo",nil);bearer.Request.Header.Set("Authorization","Bearer synthetic-at");AutoSigninFilter(bearer)
 if !bearer.Input.CruSession.(*lazySessionStore).ephemeral{t.Error("Bearer fixture should select skipSessionPersistence")}
 if _,exists:=values["clientType"];exists{t.Error("fixture unexpectedly invents stored client type")}
}
func TestIndependentLoginClearsTokenBinding(t *testing.T){
 setup("dcr");ctx:=newContext("/api/userinfo",nil);ctx.Input.Queries["accessToken"]="synthetic-at";AutoSigninFilter(ctx)
 ctl:=controllers.ApiController{Store:ctx.Input.CruSession};ctl.SetSessionUsername("fixture/alice")
 for _,k:=range []string{"scope","aud",object.SessionSigninTokenId}{if ctx.Input.Session(k)!=nil{t.Errorf("independent login did not clear %s",k)}}
}
