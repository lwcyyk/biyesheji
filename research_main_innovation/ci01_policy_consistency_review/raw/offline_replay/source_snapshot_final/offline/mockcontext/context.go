// Minimal in-memory Beego interface adapter. No listener, client, or persistence.
package context
import (stdcontext "context"; "net/http")
type Store interface {
 Get(stdcontext.Context,interface{}) interface{}
 Set(stdcontext.Context,interface{},interface{}) error
 Delete(stdcontext.Context,interface{}) error
 SessionRelease(stdcontext.Context,http.ResponseWriter)
}
type Input struct{ CruSession Store; Data map[interface{}]interface{}; Queries map[string]string; RequestBody []byte }
func(i *Input) Session(k interface{}) interface{} {return i.CruSession.Get(stdcontext.Background(),k)}
func(i *Input) SetData(k,v interface{}) {i.Data[k]=v}
func(i *Input) GetData(k interface{}) interface{} {return i.Data[k]}
func(i *Input) Query(k string) string {return i.Queries[k]}
type Context struct{ Input *Input; Request *http.Request; ResponseWriter http.ResponseWriter; Denied bool; Reason string }
