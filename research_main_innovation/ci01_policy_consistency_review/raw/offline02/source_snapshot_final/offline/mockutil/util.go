package util
import ("encoding/json"; "net/http")
func InSlice(xs []string,x string)bool{for _,v:=range xs{if v==x{return true}};return false}
func JsonToStruct(s string,v interface{})error{return json.Unmarshal([]byte(s),v)}
func GetClientIpFromRequest(r *http.Request)string{panic("password branch outside fixture scope")}
func IsCredentialedOrigin(origin,configured,host string)bool{panic("cross-origin branch outside fixture scope")}
