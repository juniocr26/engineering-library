// Owned research observer. Type checks bounded in-memory Go source; never executes it.
package main

import (
 "crypto/sha256"
 "encoding/hex"
 "encoding/json"
 "fmt"
 "go/ast"
 "go/parser"
 "go/token"
 "go/types"
 "io"
 "os"
 "runtime"
 "sort"
)

type File struct { Path string `json:"path"`; Source string `json:"source"` }
type Request struct { Package string `json:"package_path"`; Files []File `json:"files"` }
type Selection struct { File string `json:"file"`; Line int `json:"line"`; Column int `json:"column"`; Name string `json:"name"`; Kind string `json:"kind"`; Receiver string `json:"receiver"`; Object string `json:"object"`; Type string `json:"type"`; Index []int `json:"index"`; Indirect bool `json:"indirect"` }
type Response struct { Schema string `json:"schema"`; GoVersion string `json:"go_version"`; GOOS string `json:"goos"`; GOARCH string `json:"goarch"`; Status string `json:"status"`; SourceHashes map[string]string `json:"source_sha256"`; Diagnostics []string `json:"diagnostics"`; Selections []Selection `json:"selections"`; SourceExecuted bool `json:"source_executed"`; RuntimeBindingsVerified bool `json:"runtime_bindings_verified"`; ImportsSupported bool `json:"imports_supported"`; PartialInfoAdmitted bool `json:"partial_type_info_admitted"` }
func hash(s string) string { sum:=sha256.Sum256([]byte(s)); return hex.EncodeToString(sum[:]) }
func main() {
 r:=Response{Schema:"owned-go-types-observation-v1",GoVersion:runtime.Version(),GOOS:runtime.GOOS,GOARCH:runtime.GOARCH,Status:"REFUSED",SourceHashes:map[string]string{},Diagnostics:[]string{},Selections:[]Selection{}}
 defer func(){if e:=recover();e!=nil {r.Status="REFUSED";r.Selections=[]Selection{};r.Diagnostics=append(r.Diagnostics,fmt.Sprint(e))};json.NewEncoder(os.Stdout).Encode(r)}()
 raw,err:=io.ReadAll(io.LimitReader(os.Stdin,131073));if err!=nil||len(raw)>131072 {panic("packet exceeds131072bytes")}
 var req Request;dec:=json.NewDecoder(bytesReader(raw));dec.DisallowUnknownFields();if err=dec.Decode(&req);err!=nil {panic(err)}
 var extra any;if dec.Decode(&extra)!=io.EOF {panic("trailingJSON")}
 if req.Package==""||len(req.Files)<1||len(req.Files)>16 {panic("bounded package/files required")}
 fset:=token.NewFileSet();files:=[]*ast.File{};seen:=map[string]bool{}
 for _,f:=range req.Files {
  if f.Path==""||seen[f.Path]||len(f.Source)>65536 {panic("invalid file name/size")};seen[f.Path]=true;r.SourceHashes[f.Path]=hash(f.Source)
  parsed,e:=parser.ParseFile(fset,f.Path,f.Source,parser.AllErrors|parser.ParseComments);if e!=nil {r.Diagnostics=append(r.Diagnostics,e.Error());return}
  if len(parsed.Imports)>0 {r.Diagnostics=append(r.Diagnostics,"Imports are unsupported in v1 closed-package profile; no import/dependency or runtime binding claim");return}
  files=append(files,parsed)
 }
 info:=&types.Info{Selections:map[*ast.SelectorExpr]*types.Selection{},Types:map[ast.Expr]types.TypeAndValue{},Defs:map[*ast.Ident]types.Object{},Uses:map[*ast.Ident]types.Object{}}
 config:=types.Config{GoVersion:"go1.24",Sizes:types.SizesFor("gc",runtime.GOARCH),Error:func(e error){r.Diagnostics=append(r.Diagnostics,e.Error())}}
 _,err=config.Check(req.Package,fset,files,info);if err!=nil||len(r.Diagnostics)>0 {r.Status="INCONCLUSIVE_TYPE_ERRORS";return}
 for expr,s:=range info.Selections {
  pos:=fset.Position(expr.Pos());kind:=map[types.SelectionKind]string{types.FieldVal:"FieldVal",types.MethodVal:"MethodVal",types.MethodExpr:"MethodExpr"}[s.Kind()]
  r.Selections=append(r.Selections,Selection{pos.Filename,pos.Line,pos.Column,expr.Sel.Name,kind,types.TypeString(s.Recv(),nil),types.ObjectString(s.Obj(),nil),types.TypeString(s.Type(),nil),s.Index(),s.Indirect()})
 }
 sort.Slice(r.Selections,func(i,j int)bool{a,b:=r.Selections[i],r.Selections[j];if a.File!=b.File{return a.File<b.File};if a.Line!=b.Line{return a.Line<b.Line};return a.Column<b.Column})
 r.Status="TYPECHECKED_CLOSED_PACKAGE"
}
// Avoid filesystem/network import resolution, including for observer packet parsing.
type reader struct{ b []byte; at int }
func bytesReader(b []byte)*reader{return &reader{b:b}}
func(r *reader)Read(p []byte)(int,error){if r.at==len(r.b){return 0,io.EOF};n:=copy(p,r.b[r.at:]);r.at+=n;return n,nil}
