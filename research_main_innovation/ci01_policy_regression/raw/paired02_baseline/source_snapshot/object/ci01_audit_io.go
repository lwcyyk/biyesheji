//go:build ci01audit

// Test-only isolated storage installation. All permission functions are native.
package object
import (
 "context"
 "strings"
 "fmt"
 "time"
 "github.com/casdoor/casdoor/ci01audit"
 "github.com/xorm-io/xorm/contexts"
)
type ci01SQLHook struct{}
func(ci01SQLHook)BeforeProcess(c *contexts.ContextHook)(context.Context,error){
 q:=strings.ToUpper(strings.TrimSpace(c.SQL));kind:="sql_other"
 if strings.HasPrefix(q,"SELECT"){kind="sql_select"}else if strings.HasPrefix(q,"UPDATE"){kind="sql_update"}else if strings.HasPrefix(q,"INSERT"){kind="sql_insert"}else if strings.HasPrefix(q,"DELETE"){kind="sql_delete"}
 ci01audit.Count(kind);return c.Ctx,nil
}
func(ci01SQLHook)AfterProcess(c *contexts.ContextHook)error{return nil}
func Ci01InstallStorage(path string)error{
 a,err:=NewAdapter("sqlite3",path,"");if err!=nil{return err};ormer=a
 ormer.Engine.SetMaxOpenConns(1);ormer.Engine.SetMaxIdleConns(1)
 ormer.createTable()
 initBuiltInApiModel();initBuiltInApiAdapter();initBuiltInApiEnforcer()
 ormer.Engine.AddHook(ci01SQLHook{})
 return nil
}
func Ci01ResetFixture(client string)error{
 // Reset only synthetic objects in this isolated database, leaving native policy config.
 for _,table:=range []string{"token","application","user","organization","provider","permission","session","record","role","group","syncer"}{
  if _,err:=ormer.Engine.Exec("DELETE FROM `"+table+"`");err!=nil{return err}
 }
 for _,name:=range []string{"fixture","other-fixture","built-in"}{
  org:=&Organization{Owner:"admin",Name:name,DisplayName:name,AccountItems:GetDefaultAccountItems(),PasswordType:"plain",DefaultTokenFormat:"JWT",Languages:[]string{"en"}}
  if _,err:=ormer.Engine.Insert(org);err!=nil{return err}
 }
 user:=&User{Owner:"fixture",Name:"alice",Id:"fixture-user-id",Type:"normal-user",DisplayName:"before",Properties:map[string]string{}}
 if _,err:=ormer.Engine.Insert(user);err!=nil{return err}
 app:=&Application{Owner:"admin",Name:"app-fixture",ClientId:"client-fixture",Organization:"fixture",TokenFormat:"JWT",ExpireInHours:1,GrantTypes:[]string{"authorization_code"}}
 switch client{case "dcr":app.Tags=[]string{"dcr"};case "cimd":app.Tags=[]string{"cimd"};case "cross_org":app.Organization="other-fixture";case "builtin_regular":app.Organization="built-in";case "builtin_dcr":app.Organization="built-in";app.Tags=[]string{"dcr"}}
 if _,err:=ormer.Engine.Insert(app);err!=nil{return err}
 token:=&Token{Owner:"admin",Name:"token-fixture",Application:app.Name,Organization:"fixture",User:"alice",CreatedTime:time.Now().Add(-time.Minute).Format(time.RFC3339),AccessToken:"synthetic-at",RefreshToken:"synthetic-rt",ExpiresIn:3600,Scope:"openid",GrantType:"authorization_code",TokenType:"Bearer"}
 _,err:=AddToken(token);return err
}
func Ci01SetStates(appState,tokenState string)error{
 switch appState{
 case "missing":if _,err:=ormer.Engine.Exec("DELETE FROM application WHERE name = ?","app-fixture");err!=nil{return err}
 case "disabled":if _,err:=ormer.Engine.Exec("UPDATE application SET disable_signin = ? WHERE name = ?",true,"app-fixture");err!=nil{return err}
 }
 switch tokenState{
 case "missing":_,err:=ormer.Engine.Exec("DELETE FROM token WHERE name = ?","token-fixture");return err
 case "revoked":_,err:=ormer.Engine.Exec("UPDATE token SET expires_in = 0 WHERE name = ?","token-fixture");return err
 case "expired":_,err:=ormer.Engine.Exec("UPDATE token SET created_time = ? WHERE name = ?","2000-01-01T00:00:00Z","token-fixture");return err
 }
 return nil
}
func Ci01DisplayName()(string,error){u,err:=getUser("fixture","alice");if err!=nil{return "",err};if u==nil{return "",fmt.Errorf("fixture user missing")};return u.DisplayName,nil}
// Query faults use a temporary SQLite schema rename, not a substituted predicate.
func Ci01Fault(table string,on bool)error{
 if table!="application"&&table!="token"{return fmt.Errorf("unsupported table")}
 from,to:=table,table+"_ci01_unavailable";if !on{from,to=to,from}
 _,err:=ormer.Engine.Exec("ALTER TABLE `"+from+"` RENAME TO `"+to+"`");return err
}
func Ci01SetDisplayPolicy(rule string)error{
 org,err:=GetOrganization("admin/fixture");if err!=nil{return err}
 for _,item:=range org.AccountItems{if item.Name=="Display name"{item.ModifyRule=rule}}
 _,err=ormer.Engine.Where("owner = ? AND name = ?","admin","fixture").Cols("account_items").Update(org);return err
}
