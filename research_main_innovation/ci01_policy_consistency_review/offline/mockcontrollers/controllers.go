package controllers
import(stdcontext "context";context "policyreview.local/mockcontext")
type SessionData struct{ExpireTime int64}
type ApiController struct {Store context.Store}
func(c *ApiController)SetSession(k string,v interface{}){_ = c.Store.Set(stdcontext.Background(),k,v)}
func(c *ApiController)DelSession(k string){_ = c.Store.Delete(stdcontext.Background(),k)}
