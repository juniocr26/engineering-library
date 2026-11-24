// Owned syntax identity observer; parses text, never executes/typechecks Cobra.
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
)

func main() {
 raw, err := os.ReadFile(os.Args[1]); if err != nil { panic(err) }
 fs := token.NewFileSet()
 file, err := parser.ParseFile(fs, os.Args[1], raw, parser.SkipObjectResolution)
 if err != nil { panic(err) }
 owners := map[string]any{}
 for _, decl := range file.Decls {
  fn, ok := decl.(*ast.FuncDecl)
  if !ok || (fn.Name.Name != "OnlyValidArgs" && fn.Name.Name != "ExactArgs") { continue }
  if _, exists := owners[fn.Name.Name]; exists { panic("duplicate selected owner") }
  var normalized bytes.Buffer
  if err := format.Node(&normalized, fs, fn); err != nil { panic(err) }
  digest := sha256.Sum256(normalized.Bytes())
  owners[fn.Name.Name] = map[string]any{"normalized_owner_sha256":hex.EncodeToString(digest[:]),
   "normalized_owner_source": normalized.String(), "first_line":fs.Position(fn.Pos()).Line,
   "last_line":fs.Position(fn.End()).Line}
 }
 if len(owners) != 2 { panic("missing selected owner") }
 source := sha256.Sum256(raw)
 out, err := json.MarshalIndent(map[string]any{"source_sha256":hex.EncodeToString(source[:]),
  "selected_owners":owners, "comments_in_identity":false,"upstream_executed":false,
  "typechecked":false,"semantic_admission":false},"","  ")
 if err != nil { panic(err) }; fmt.Println(string(out))
}
