// Isolated finite AST observer. Parses source data; never executes Cobra.
package main

import (
 "bytes"
 "crypto/sha256"
 "encoding/hex"
 "encoding/json"
 "fmt"
 "go/ast"
 "go/format"
 "go/parser"
 "go/token"
 "os"
 "strings"
)

type Relation struct { ID string `json:"id"`; Owner string `json:"owner"`; Value string `json:"normalized_relation"`; First int `json:"first_line"`; Last int `json:"last_line"`; Evidence string `json:"exact_ast_source"` }
func main() {
 raw,err:=os.ReadFile(os.Args[1]); if err!=nil {panic(err)}
 fs:=token.NewFileSet(); file,err:=parser.ParseFile(fs,os.Args[1],raw,parser.ParseComments|parser.AllErrors|parser.SkipObjectResolution); if err!=nil {panic(err)}
 text:=func(n ast.Node)string {var b bytes.Buffer; if err:=format.Node(&b,fs,n);err!=nil {panic(err)};return b.String()}
 functions:=map[string]*ast.FuncDecl{}; types:=map[string]*ast.TypeSpec{}
 for _,decl:=range file.Decls {switch d:=decl.(type) {case *ast.FuncDecl:if _,ok:=functions[d.Name.Name];ok {panic("duplicate owner")};functions[d.Name.Name]=d;case *ast.GenDecl:for _,spec:=range d.Specs {if t,ok:=spec.(*ast.TypeSpec);ok {types[t.Name.Name]=t}}}}
 rows:=[]Relation{}
 add:=func(id,owner,value string,n ast.Node){first,last:=fs.Position(n.Pos()).Line,fs.Position(n.End()).Line;start,end:=fs.Position(n.Pos()).Offset,fs.Position(n.End()).Offset;rows=append(rows,Relation{id,owner,value,first,last,string(raw[start:end])})}
 p:=types["PositionalArgs"];if p==nil {panic("missing type owner")};if _,ok:=p.Type.(*ast.FuncType);!ok {panic("not function type")};add("C01","PositionalArgs","type PositionalArgs "+text(p.Type),p)
 only:=functions["OnlyValidArgs"];if only==nil||only.Body==nil {panic("missing OnlyValidArgs")};guard,ok:=only.Body.List[0].(*ast.IfStmt);if !ok {panic("missing outer guard")};add("C02","OnlyValidArgs",text(guard.Cond),guard.Cond)
 // One range over cmd.ValidArgs, whose append argument is an indexed SplitN call.
 projections:=[]ast.Expr{}
 for _,stmt:=range guard.Body.List {if loop,ok:=stmt.(*ast.RangeStmt);ok&&text(loop.X)=="cmd.ValidArgs" {for _,body:=range loop.Body.List {if assign,ok:=body.(*ast.AssignStmt);ok&&len(assign.Rhs)==1 {if call,ok:=assign.Rhs[0].(*ast.CallExpr);ok&&text(call.Fun)=="append"&&len(call.Args)==2 {if index,ok:=call.Args[1].(*ast.IndexExpr);ok {if split,ok:=index.X.(*ast.CallExpr);ok&&text(split.Fun)=="strings.SplitN" {projections=append(projections,index)}}}}}}}
 if len(projections)!=1 {panic("missing/ambiguous projection")};add("C03","OnlyValidArgs",text(projections[0]),projections[0])
 exact:=functions["ExactArgs"];if exact==nil {panic("missing ExactArgs")};ret,ok:=exact.Body.List[0].(*ast.ReturnStmt);if !ok||len(ret.Results)!=1 {panic("wrong callback return")};callback,ok:=ret.Results[0].(*ast.FuncLit);if !ok {panic("not callback")};add("C04","ExactArgs","VALIDATOR_FUNCTION",ret)
 count,ok:=callback.Body.List[0].(*ast.IfStmt);if !ok {panic("missing callback guard")};add("C05","ExactArgs",text(count.Cond),count.Cond)
 match:=functions["MatchAll"];if match==nil {panic("missing MatchAll")};mret,ok:=match.Body.List[0].(*ast.ReturnStmt);if !ok||len(mret.Results)!=1 {panic("missing MatchAll callback")};mfunc,ok:=mret.Results[0].(*ast.FuncLit);if !ok {panic("not MatchAll callback")};loop,ok:=mfunc.Body.List[0].(*ast.RangeStmt);if !ok||text(loop.X)!="pargs" {panic("unadmitted iteration")};add("C06","MatchAll","SUPPLIED_SLICE_ORDER",loop)
 fail,ok:=loop.Body.List[0].(*ast.IfStmt);if !ok||fail.Init==nil||text(fail.Cond)!="err != nil" {panic("unadmitted error condition")};init,ok:=fail.Init.(*ast.AssignStmt);if !ok||len(init.Rhs)!=1||text(init.Rhs[0])!="parg(cmd, args)" {panic("unadmitted callback invocation")};early,ok:=fail.Body.List[0].(*ast.ReturnStmt);if !ok||len(early.Results)!=1||text(early.Results[0])!="err" {panic("unadmitted error return")};add("C07","MatchAll","RETURN_ERROR_IMMEDIATELY",fail)
 valid:=functions["ExactValidArgs"];if valid==nil {panic("missing ExactValidArgs")};vret,ok:=valid.Body.List[0].(*ast.ReturnStmt);if !ok||len(vret.Results)!=1 {panic("missing delegation")};add("C08","ExactValidArgs",text(vret.Results[0]),vret.Results[0])
 deprecated:=[]*ast.Comment{};if valid.Doc!=nil {for _,c:=range valid.Doc.List {if strings.HasPrefix(strings.TrimSpace(strings.TrimPrefix(c.Text,"//")),"Deprecated:") {deprecated=append(deprecated,c)}}};if len(deprecated)!=1||!strings.Contains(deprecated[0].Text,"MatchAll(ExactArgs(n), OnlyValidArgs)") {panic("unadmitted deprecation comment")};add("C09","ExactValidArgs","DEPRECATED_USE_MATCHALL_COMPOSITION",deprecated[0])
 digest:=sha256.Sum256(raw);result:=map[string]any{"source_sha256":hex.EncodeToString(digest[:]),"relations":rows,"source_executed":false,"typechecked":false,"runtime_bindings_verified":false,"profile":"finite-cobra-AST-role-v1"};encoded,err:=json.MarshalIndent(result,"","  ");if err!=nil {panic(err)};fmt.Println(string(encoded))
}
