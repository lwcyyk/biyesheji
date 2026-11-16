// Extract existing Go declarations verbatim; no semantic rewriting.
package main

import (
 "crypto/sha256"
 "encoding/hex"
 "encoding/json"
 "fmt"
 "go/ast"
 "go/parser"
 "go/token"
 "os"
 "path/filepath"
 "strings"
)
type selection struct { File string; Names []string }
type target struct { Path, Header string; Parts []selection }
type record struct { Source string `json:"source"`; Name string `json:"declaration"`; Start int `json:"line_start"`; End int `json:"line_end"`; SourceHash string `json:"source_sha256"`; SegmentHash string `json:"segment_sha256"`; Output string `json:"output"`; Offset int `json:"output_byte_offset"`; Bytes int `json:"bytes"` }
func hash(b []byte) string { x:=sha256.Sum256(b);return hex.EncodeToString(x[:]) }
func main(){
 root,err:=filepath.Abs("..");if err!=nil{panic(err)}
 targets:=[]target{
 {"routers/source_generated.go",`package routers
import (stdcontext "context"; "encoding/json"; "fmt"; "strings"; "time"; "net/http"
context "policyreview.local/mockcontext"
object "policyreview.local/mockobject"
util "policyreview.local/mockutil"
mcpself "policyreview.local/mockmcp"
controllers "policyreview.local/mockcontrollers"
logs "policyreview.local/mocklogs"
conf "policyreview.local/mockconf")
`,[]selection{
 {"routers/authz_filter.go",[]string{"dynamicClientApis","crossOrgClientApis","requestCredentialUserKey","checkDynamicClientSession","isRestrictedClientSession","isClientSessionApiAllowed","isCrossOrgClient","getUsername","getSubject","isCrossOriginCookieRequest"}},
 {"routers/auto_signin_filter.go",[]string{"AutoSigninFilter"}},
 {"routers/base.go",[]string{"getSessionUser","setSessionUser","setSessionSigninToken","setSessionOidc","clearSessionOfRevokedToken","clearSessionOfToken","parseBearerToken"}},
 {"routers/session_provider.go",[]string{"skipSessionPersistence"}},
 }},
 {"mockobject/source_generated.go",`package object
import ("fmt"; "strings"; util "policyreview.local/mockutil")
`,[]selection{
 {"object/user_util.go",[]string{"IsDynamicClient","IsAppUser"}},
 {"object/token.go",[]string{"SessionSigninTokenId","GetId","IsUserActive"}},
 }},
 {"mockutil/source_generated.go",`package util
import ("fmt"; "strings"; "time"; "errors")
`,[]selection{
 {"util/time.go",[]string{"IsTokenExpired"}},
 {"util/string.go",[]string{"GetId","GetOwnerAndNameFromIdNoCheck","GetOwnerAndNameFromIdWithError"}},
 }},
 {"mockcontrollers/source_generated.go",`package controllers
import object "policyreview.local/mockobject"
`,[]selection{{"controllers/base.go",[]string{"SetSessionUsername","clearSessionOidc"}}}},
 }
 records:=[]record{}
 for _,dst:=range targets{
  output:=[]byte("// Generated verbatim declarations from Casdoor (Apache-2.0); see SOURCE_EXTRACTS.json.\n"+dst.Header+"\n")
  for _,part:=range dst.Parts{
   source:=filepath.Join(root,"sources","frozen",filepath.FromSlash(part.File));data,err:=os.ReadFile(source);if err!=nil{panic(err)}
   fs:=token.NewFileSet();file,err:=parser.ParseFile(fs,source,data,parser.ParseComments);if err!=nil{panic(err)}
   for _,name:=range part.Names{
    var found ast.Node
    for _,decl:=range file.Decls{
     if f,ok:=decl.(*ast.FuncDecl);ok&&f.Name.Name==name{found=f;break}
     if g,ok:=decl.(*ast.GenDecl);ok{for _,sp:=range g.Specs{if v,ok:=sp.(*ast.ValueSpec);ok{for _,id:=range v.Names{if id.Name==name{found=g}}}}}
    }
    if found==nil{panic("declaration missing "+part.File+" "+name)}
    start,end:=fs.Position(found.Pos()),fs.Position(found.End());segment:=data[start.Offset:end.Offset]
    records=append(records,record{part.File,name,start.Line,end.Line,hash(data),hash(segment),dst.Path,len(output),len(segment)})
    output=append(output,segment...);output=append(output,[]byte("\n\n")...)
   }
  }
  path:=filepath.Join(".",filepath.FromSlash(dst.Path));if err:=os.MkdirAll(filepath.Dir(path),0755);err!=nil{panic(err)}
  if err:=os.WriteFile(path,output,0644);err!=nil{panic(err)}
 }
 b,_:=json.MarshalIndent(records,"","  ");if err:=os.WriteFile(filepath.Join(root,"SOURCE_EXTRACTS.json"),b,0644);err!=nil{panic(err)}
 fmt.Println(strings.TrimSpace(fmt.Sprintf("extracted %d verbatim declarations",len(records))))
}
