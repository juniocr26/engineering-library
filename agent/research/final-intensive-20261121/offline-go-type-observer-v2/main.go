// Owned research observer. Type checks bounded in-memory Go source; never executes it.
package main

import (
 "crypto/sha256"
 "encoding/hex"
 "encoding/json"
 "fmt"
 "go/ast"
 "go/importer"
 "go/parser"
 "go/token"
 "go/types"
 "io"
 "os"
 "runtime"
 "path/filepath"
 "strings"
 "strconv"
 "sort"
)

type File struct { Path string `json:"path"`; Source string `json:"source"` }
type Export struct { Path string `json:"path"`; SHA256 string `json:"sha256"` }
type Request struct { Package string `json:"package_path"`; Files []File `json:"files"`; ExportRoot string `json:"export_root"`; StandardExports map[string]Export `json:"standard_exports"` }
type QualifiedUse struct { File string `json:"file"`; Line int `json:"line"`; Column int `json:"column"`; Name string `json:"name"`; ImportPath string `json:"import_path"`; Object string `json:"object"`; Type string `json:"type"` }
type Selection struct { File string `json:"file"`; Line int `json:"line"`; Column int `json:"column"`; Name string `json:"name"`; Kind string `json:"kind"`; Receiver string `json:"receiver"`; Object string `json:"object"`; Type string `json:"type"`; Index []int `json:"index"`; Indirect bool `json:"indirect"` }
type Response struct { ImportGraphSHA256 string `json:"import_graph_sha256"`; ImportedExports map[string]string `json:"used_export_sha256"`; QualifiedUses []QualifiedUse `json:"qualified_uses"`; Schema string `json:"schema"`; GoVersion string `json:"go_version"`; GOOS string `json:"goos"`; GOARCH string `json:"goarch"`; Status string `json:"status"`; SourceHashes map[string]string `json:"source_sha256"`; Diagnostics []string `json:"diagnostics"`; Selections []Selection `json:"selections"`; SourceExecuted bool `json:"source_executed"`; RuntimeBindingsVerified bool `json:"runtime_bindings_verified"`; ImportsSupported bool `json:"imports_supported"`; PartialInfoAdmitted bool `json:"partial_type_info_admitted"` }
func hash(s string) string { sum:=sha256.Sum256([]byte(s)); return hex.EncodeToString(sum[:]) }
func main() {
 r:=Response{Schema:"owned-go-types-observation-v2",GoVersion:runtime.Version(),GOOS:runtime.GOOS,GOARCH:runtime.GOARCH,Status:"REFUSED",ImportsSupported:true,ImportedExports:map[string]string{},QualifiedUses:[]QualifiedUse{},SourceHashes:map[string]string{},Diagnostics:[]string{},Selections:[]Selection{}}
 defer func(){if e:=recover();e!=nil {r.Status="REFUSED";r.Selections=[]Selection{};r.QualifiedUses=[]QualifiedUse{};r.Diagnostics=append(r.Diagnostics,fmt.Sprint(e))};json.NewEncoder(os.Stdout).Encode(r)}()
 raw,err:=io.ReadAll(io.LimitReader(os.Stdin,131073));if err!=nil||len(raw)>131072 {panic("packet exceeds131072bytes")}
 var req Request;dec:=json.NewDecoder(bytesReader(raw));dec.DisallowUnknownFields();if err=dec.Decode(&req);err!=nil {panic(err)}
 var extra any;if dec.Decode(&extra)!=io.EOF {panic("trailingJSON")}
 if req.Package==""||len(req.Files)<1||len(req.Files)>16 {panic("bounded package/files required")}
 fset:=token.NewFileSet();files:=[]*ast.File{};seen:=map[string]bool{}
 if !filepath.IsAbs(req.ExportRoot)||len(req.StandardExports)<1||len(req.StandardExports)>256 {panic("Frozen standard export graph and absolute root required")}
 graphBytes,e:=json.Marshal(req.StandardExports);if e!=nil{panic(e)};r.ImportGraphSHA256=hash(string(graphBytes));lookupFailed:=false
 lookup:=func(path string)(io.ReadCloser,error){
  reject:=func(reason string)(io.ReadCloser,error){lookupFailed=true;return nil,fmt.Errorf("frozen export %s: %s",path,reason)}
  export,ok:=req.StandardExports[path];if !ok{return reject("not registered")}
  rel:=filepath.Clean(export.Path);if filepath.IsAbs(rel)||rel==".."||strings.HasPrefix(rel,"../")||strings.Contains(rel,"\\"){return reject("unsafe relative export path")}
  f,err:=os.Open(filepath.Join(req.ExportRoot,rel));if err!=nil{return reject(err.Error())}
  data,err:=io.ReadAll(io.LimitReader(f,33554433));f.Close();if err!=nil||len(data)>33554432{return reject("read/size bound")}
  if hash(string(data))!=export.SHA256{return reject("sha256 differs")};r.ImportedExports[path]=export.SHA256
  return io.NopCloser(bytesReader(data)),nil
 }
 frozenImporter:=importer.ForCompiler(fset,"gc",lookup)
 for _,f:=range req.Files {
  if f.Path==""||seen[f.Path]||len(f.Source)>65536 {panic("invalid file name/size")};seen[f.Path]=true;r.SourceHashes[f.Path]=hash(f.Source)
  parsed,e:=parser.ParseFile(fset,f.Path,f.Source,parser.AllErrors|parser.ParseComments);if e!=nil {r.Diagnostics=append(r.Diagnostics,e.Error());return}
  for _,imp:=range parsed.Imports {
   path,err:=strconv.Unquote(imp.Path.Value);if err!=nil{panic(err)}
   if _,ok:=req.StandardExports[path];!ok && path!="unsafe" {r.Diagnostics=append(r.Diagnostics,"Import is outside frozen standard export graph: "+path);return}
  }
  files=append(files,parsed)
 }
 info:=&types.Info{Selections:map[*ast.SelectorExpr]*types.Selection{},Types:map[ast.Expr]types.TypeAndValue{},Defs:map[*ast.Ident]types.Object{},Uses:map[*ast.Ident]types.Object{}}
 config:=types.Config{Importer:frozenImporter,GoVersion:"go1.24",Sizes:types.SizesFor("gc",runtime.GOARCH),Error:func(e error){r.Diagnostics=append(r.Diagnostics,e.Error())}}
 _,err=config.Check(req.Package,fset,files,info);if err!=nil||len(r.Diagnostics)>0 {r.Status="INCONCLUSIVE_TYPE_ERRORS";if lookupFailed{r.Status="INCONCLUSIVE_IMPORT_IDENTITY"};return}
 for expr,s:=range info.Selections {
  pos:=fset.Position(expr.Pos());kind:=map[types.SelectionKind]string{types.FieldVal:"FieldVal",types.MethodVal:"MethodVal",types.MethodExpr:"MethodExpr"}[s.Kind()]
  r.Selections=append(r.Selections,Selection{pos.Filename,pos.Line,pos.Column,expr.Sel.Name,kind,types.TypeString(s.Recv(),nil),types.ObjectString(s.Obj(),nil),types.TypeString(s.Type(),nil),s.Index(),s.Indirect()})
 }
 for _,file:=range files {ast.Inspect(file,func(node ast.Node)bool{
  expr,ok:=node.(*ast.SelectorExpr);if !ok||info.Selections[expr]!=nil{return true};ident,ok:=expr.X.(*ast.Ident);if !ok{return true};pkg,ok:=info.Uses[ident].(*types.PkgName);if !ok{return true};obj:=info.Uses[expr.Sel];if obj==nil{return true};pos:=fset.Position(expr.Pos());r.QualifiedUses=append(r.QualifiedUses,QualifiedUse{pos.Filename,pos.Line,pos.Column,expr.Sel.Name,pkg.Imported().Path(),types.ObjectString(obj,nil),types.TypeString(obj.Type(),nil)});return true
 })}
 sort.Slice(r.QualifiedUses,func(i,j int)bool{a,b:=r.QualifiedUses[i],r.QualifiedUses[j];if a.File!=b.File{return a.File<b.File};if a.Line!=b.Line{return a.Line<b.Line};return a.Column<b.Column})
 sort.Slice(r.Selections,func(i,j int)bool{a,b:=r.Selections[i],r.Selections[j];if a.File!=b.File{return a.File<b.File};if a.Line!=b.Line{return a.Line<b.Line};return a.Column<b.Column})
 r.Status="TYPECHECKED_FROZEN_STDLIB_PACKAGE"
}
// Avoid filesystem/network import resolution, including for observer packet parsing.
type reader struct{ b []byte; at int }
func bytesReader(b []byte)*reader{return &reader{b:b}}
func(r *reader)Read(p []byte)(int,error){if r.at==len(r.b){return 0,io.EOF};n:=copy(p,r.b[r.at:]);r.at+=n;return n,nil}
