// Stores contain synthetic fixtures only; lookup API shapes mirror native calls.
package object
import ("errors"; "strings")
const cimdTag="cimd"
type Application struct { Name,ClientId,Organization string;Tags []string;DisableSignin bool }
type Token struct { Owner,Name,CreatedTime,Application,Organization,User,Scope,TokenType,GrantType,DPoPJkt string;ExpiresIn int }
type User struct {IsForbidden,IsDeleted bool}
var Apps map[string]*Application
var Tokens map[string]*Token
var Users map[string]*User
var AppError,TokenError error
func Reset(){Apps=map[string]*Application{};Tokens=map[string]*Token{};Users=map[string]*User{};AppError=nil;TokenError=nil}
func GetApplicationByClientId(id string)(*Application,error){if AppError!=nil{return nil,AppError};return Apps[id],nil}
func GetApplicationByUserId(id string)(*Application,error){if AppError!=nil{return nil,AppError};name:=strings.TrimPrefix(id,"app/");for _,a:=range Apps{if a.Name==name{return a,nil}};return nil,nil}
func GetTokenByAccessToken(at string)(*Token,error){if TokenError!=nil{return nil,TokenError};return Tokens[at],nil}
func GetToken(id string)(*Token,error){if TokenError!=nil{return nil,TokenError};for _,t:=range Tokens{if t.GetId()==id{return t,nil}};return nil,nil}
func getUser(org,name string)(*User,error){return Users[org+"/"+name],nil}
func GetAppUserId(a *Application)string{return "app/"+a.Name}
func GetDPoPHtu(host,path string)string{return host+path}
func ValidateDPoPProof(a,b,c,d string)(string,error){return "",errors.New("DPoP outside fixture scope")}
