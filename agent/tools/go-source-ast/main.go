// Stateless syntax inspection. Input source is parsed, never compiled or executed.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"io"
	"os"
	"path"
	"regexp"
	"runtime"
	"strings"
	"unicode/utf8"
)

type request struct {
	Source    string   `json:"source"`
	Path      string   `json:"path"`
	Selectors []string `json:"selectors"`
}
type unit struct {
	IfReturnChainContract  interface{} `json:"if_return_chain_contract,omitempty"`
	HandlerDeferContract   interface{} `json:"handler_defer_contract,omitempty"`
	IfReturnContract       interface{} `json:"if_return_contract,omitempty"`
	DeferredReturnContract interface{} `json:"deferred_return_contract,omitempty"`
	Selector               string      `json:"selector"`
	DeclarationKind        string      `json:"declaration_kind"`
	Symbol                 string      `json:"symbol"`
	Start                  int         `json:"start_line"`
	End                    int         `json:"end_line"`
	Quote                  string      `json:"quote"`
	Declaration            string      `json:"declaration"`
	FunctionType           string      `json:"function_type"`
	ReceiverType           string      `json:"receiver_type,omitempty"`
	Factory                interface{} `json:"factory,omitempty"`
	ReturnContract         interface{} `json:"return_contract,omitempty"`
}

func digest(s string) string { h := sha256.Sum256([]byte(s)); return hex.EncodeToString(h[:]) }
func rendered(fs *token.FileSet, n interface{}) string {
	var b bytes.Buffer
	if err := format.Node(&b, fs, n); err != nil {
		return ""
	}
	return b.String()
}
func returnContract(fs *token.FileSet, body *ast.BlockStmt, depth int) interface{} {
	if depth > 2 || body == nil || len(body.List) != 1 {
		return nil
	}
	ret, ok := body.List[0].(*ast.ReturnStmt)
	if !ok || len(ret.Results) < 1 || len(ret.Results) > 4 {
		return nil
	}
	if len(ret.Results) == 1 {
		if literal, ok := ret.Results[0].(*ast.FuncLit); ok {
			signature := rendered(fs, literal.Type)
			if len(signature) > 600 || strings.ContainsAny(signature, "`\r\n") {
				return nil
			}
			result := map[string]interface{}{"kind": "sole-return-function-literal", "literal_signature": signature, "callback_body_analyzed": false}
			if nested := returnContract(fs, literal.Body, depth+1); nested != nil {
				result["callback_contract"] = nested
				result["callback_body_analyzed"] = true
			}
			return result
		}
	}
	expressions := []string{}
	kinds := []string{}
	total := 0
	for _, expr := range ret.Results {
		switch expr.(type) {
		case *ast.BasicLit, *ast.Ident, *ast.SelectorExpr, *ast.CallExpr, *ast.ParenExpr, *ast.UnaryExpr, *ast.BinaryExpr, *ast.IndexExpr, *ast.IndexListExpr:
		default:
			return nil
		}
		text := rendered(fs, expr)
		total += len(text)
		if text == "" || strings.ContainsAny(text, "`\r\n") || total > 650 {
			return nil
		}
		expressions = append(expressions, text)
		kinds = append(kinds, fmt.Sprintf("%T", expr))
	}
	return map[string]interface{}{"kind": "sole-return-expressions", "expressions": expressions, "AST_expression_kinds": kinds, "runtime_completion_verified": false}
}

// Exactly an initializer-free guard return, followed by a return statement.
// This preserves written expressions, not type validity or helper completion.
func ifReturnContract(fs *token.FileSet, body *ast.BlockStmt) interface{} {
	if body == nil || len(body.List) != 2 {
		return nil
	}
	guard, ok := body.List[0].(*ast.IfStmt)
	if !ok || guard.Init != nil || guard.Else != nil || len(guard.Body.List) != 1 {
		return nil
	}
	fallthroughReturn, ok := body.List[1].(*ast.ReturnStmt)
	if !ok {
		return nil
	}
	condition := rendered(fs, guard.Cond)
	if condition == "" || len(condition) > 200 || strings.ContainsAny(condition, "`\r\n") {
		return nil
	}
	yes, yesOK := returnContract(fs, guard.Body, 0).(map[string]interface{})
	no, noOK := returnContract(fs, &ast.BlockStmt{List: []ast.Stmt{fallthroughReturn}}, 0).(map[string]interface{})
	if !yesOK || !noOK || yes["kind"] != "sole-return-expressions" || no["kind"] != "sole-return-expressions" {
		return nil
	}
	return map[string]interface{}{"kind": "if-return-fallthrough-expressions", "condition": condition, "true_return_contract": yes, "fallthrough_return_contract": no, "initializer_absent": true, "else_absent": true, "source_statement_order": []string{"if-return", "return"}, "runtime_completion_verified": false}
}

// Exactly two or three independent, initializer-free if-return statements and
// one final return. Expressions may have effects; bindings are never resolved.
func ifReturnChainContract(fs *token.FileSet, body *ast.BlockStmt) interface{} {
	if body == nil || len(body.List) < 3 || len(body.List) > 4 {
		return nil
	}
	last := len(body.List) - 1
	final, ok := body.List[last].(*ast.ReturnStmt)
	if !ok {
		return nil
	}
	fallthroughContract, valid := returnContract(fs, &ast.BlockStmt{List: []ast.Stmt{final}}, 0).(map[string]interface{})
	if !valid || fallthroughContract["kind"] != "sole-return-expressions" {
		return nil
	}
	guards := []interface{}{}
	order := []string{}
	for _, statement := range body.List[:last] {
		guard, ok := statement.(*ast.IfStmt)
		if !ok || guard.Init != nil || guard.Else != nil || len(guard.Body.List) != 1 {
			return nil
		}
		condition := rendered(fs, guard.Cond)
		if condition == "" || len(condition) > 200 || strings.ContainsAny(condition, "`\r\n") {
			return nil
		}
		returned, valid := returnContract(fs, guard.Body, 0).(map[string]interface{})
		if !valid || returned["kind"] != "sole-return-expressions" {
			return nil
		}
		guards = append(guards, map[string]interface{}{"condition": condition, "true_return_contract": returned,
			"line": fs.PositionFor(guard.Pos(), false).Line, "initializer_absent": true, "else_absent": true})
		order = append(order, "if-return")
	}
	order = append(order, "return")
	return map[string]interface{}{"kind": "if-return-chain-fallthrough-expressions", "guards": guards,
		"fallthrough_return_contract": fallthroughContract, "source_statement_order": order,
		"types_resolved": false, "runtime_completion_verified": false}
}

// Source syntax only. Matching method spellings do not prove mutex behavior,
// receiver identity at runtime, completion, absence of races or deferred success.
func lexicalReceiver(e ast.Expr) bool {
	switch v := e.(type) {
	case *ast.Ident:
		return true
	case *ast.SelectorExpr:
		return lexicalReceiver(v.X)
	}
	return false
}
func deferredReturnContract(fs *token.FileSet, body *ast.BlockStmt) interface{} {
	if body == nil || len(body.List) != 3 {
		return nil
	}
	stmt, ok := body.List[0].(*ast.ExprStmt)
	if !ok {
		return nil
	}
	call, ok := stmt.X.(*ast.CallExpr)
	if !ok || len(call.Args) != 0 || call.Ellipsis.IsValid() {
		return nil
	}
	first, ok := call.Fun.(*ast.SelectorExpr)
	if !ok || !lexicalReceiver(first.X) {
		return nil
	}
	expected := map[string]string{"Lock": "Unlock", "RLock": "RUnlock"}[first.Sel.Name]
	if expected == "" {
		return nil
	}
	deferred, ok := body.List[1].(*ast.DeferStmt)
	if !ok || len(deferred.Call.Args) != 0 || deferred.Call.Ellipsis.IsValid() {
		return nil
	}
	second, ok := deferred.Call.Fun.(*ast.SelectorExpr)
	if !ok || !lexicalReceiver(second.X) || second.Sel.Name != expected || rendered(fs, first.X) != rendered(fs, second.X) {
		return nil
	}
	ret, ok := body.List[2].(*ast.ReturnStmt)
	if !ok {
		return nil
	}
	nested := returnContract(fs, &ast.BlockStmt{List: []ast.Stmt{ret}}, 0)
	contract, ok := nested.(map[string]interface{})
	if !ok || contract["kind"] != "sole-return-expressions" {
		return nil
	}
	callText, deferText := rendered(fs, call), rendered(fs, deferred.Call)
	for _, text := range []string{callText, deferText} {
		if text == "" || len(text) > 300 || strings.ContainsAny(text, "`\r\n") {
			return nil
		}
	}
	return map[string]interface{}{"kind": "call-defer-return-expressions", "call": callText, "deferred_call": deferText, "return_contract": contract, "source_statement_order": []string{"call", "defer", "return"}, "defer_is_not_an_immediate_call": true, "type_or_mutex_behavior_verified": false, "runtime_completion_verified": false}
}

// Deliberately narrow wrapper shape: one local callback, then its HandlerFunc conversion.
// Records registration and lexical call order; deferred body and runtime remain unverified.
func handlerDeferContract(fs *token.FileSet, d *ast.FuncDecl) interface{} {
	if d.Recv != nil || d.Body == nil || len(d.Body.List) != 2 || rendered(fs, d.Type) != "func(next http.Handler) http.Handler" {
		return nil
	}
	binding, ok := d.Body.List[0].(*ast.AssignStmt)
	if !ok || binding.Tok != token.DEFINE || len(binding.Lhs) != 1 || len(binding.Rhs) != 1 {
		return nil
	}
	name, ok := binding.Lhs[0].(*ast.Ident)
	if !ok || name.Name == "next" || name.Name == "_" {
		return nil
	}
	callback, ok := binding.Rhs[0].(*ast.FuncLit)
	if !ok || rendered(fs, callback.Type) != "func(w http.ResponseWriter, r *http.Request)" || len(callback.Body.List) != 2 {
		return nil
	}
	deferred, ok := callback.Body.List[0].(*ast.DeferStmt)
	if !ok || len(deferred.Call.Args) != 0 || deferred.Call.Ellipsis.IsValid() {
		return nil
	}
	delayed, ok := deferred.Call.Fun.(*ast.FuncLit)
	if !ok || rendered(fs, delayed.Type) != "func()" {
		return nil
	}
	direct, ok := callback.Body.List[1].(*ast.ExprStmt)
	if !ok {
		return nil
	}
	call, ok := direct.X.(*ast.CallExpr)
	if !ok || rendered(fs, call) != "next.ServeHTTP(w, r)" {
		return nil
	}
	ret, ok := d.Body.List[1].(*ast.ReturnStmt)
	if !ok || len(ret.Results) != 1 || rendered(fs, ret.Results[0]) != "http.HandlerFunc("+name.Name+")" {
		return nil
	}
	return map[string]interface{}{
		"kind": "handler-literal-defer-then-direct-call-v1", "callback_variable": name.Name,
		"callback_function_type":   rendered(fs, callback.Type),
		"deferred_body_start_line": fs.PositionFor(delayed.Body.Pos(), false).Line,
		"deferred_body_end_line":   fs.PositionFor(delayed.Body.End(), false).Line,
		"direct_call_line":         fs.PositionFor(call.Pos(), false).Line,
		"direct_call_expression":   rendered(fs, call),
		"source_statement_order":   []string{"defer-registration", "direct-call"},
		"deferred_body_analyzed":   false, "types_resolved": false, "runtime_completion_verified": false,
	}
}

func receiver(e ast.Expr) string {
	switch x := e.(type) {
	case *ast.Ident:
		return x.Name
	case *ast.StarExpr:
		return receiver(x.X)
	case *ast.IndexExpr:
		return receiver(x.X)
	case *ast.IndexListExpr:
		return receiver(x.X)
	}
	return ""
}
func inspect(r request) (interface{}, error) {
	if !utf8.ValidString(r.Source) || strings.ContainsRune(r.Source, 0) || len(r.Source) > 2*1024*1024 || strings.Contains(strings.ReplaceAll(r.Source, "\r\n", ""), "\r") {
		return nil, errors.New("invalid source bytes or size")
	}
	if r.Path == "" || path.IsAbs(r.Path) || path.Clean(r.Path) != r.Path || r.Path == ".." || strings.HasPrefix(r.Path, "../") || strings.ContainsAny(r.Path, "\\\x00\r\n") || !strings.HasSuffix(r.Path, ".go") {
		return nil, errors.New("unsafe Go source path")
	}
	if len(r.Selectors) < 1 || len(r.Selectors) > 4 {
		return nil, errors.New("expected 1..4 selectors")
	}
	fs := token.NewFileSet()
	f, err := parser.ParseFile(fs, r.Path, r.Source, parser.AllErrors|parser.ParseComments|parser.SkipObjectResolution)
	if err != nil {
		return nil, fmt.Errorf("Go syntax refused: %w", err)
	}
	type entry struct {
		node    ast.Node
		d       *ast.FuncDecl
		name    string
		kind    string
		aliases []string
	}
	entries := []entry{}
	for _, decl := range f.Decls {
		if d, ok := decl.(*ast.FuncDecl); ok {
			name := d.Name.Name
			kind := "function"
			aliases := []string{name, f.Name.Name + "." + name}
			if d.Recv != nil {
				if len(d.Recv.List) != 1 || len(d.Recv.List[0].Names) > 1 {
					return nil, errors.New("unsupported receiver shape")
				}
				recv := receiver(d.Recv.List[0].Type)
				if recv == "" {
					return nil, errors.New("unsupported receiver type")
				}
				name = recv + "." + name
				kind = "method"
				aliases = []string{d.Name.Name, name, f.Name.Name + "." + name}
			}
			entries = append(entries, entry{node: d, d: d, name: name, kind: kind, aliases: aliases})
		} else if group, ok := decl.(*ast.GenDecl); ok && group.Tok == token.TYPE && !group.Lparen.IsValid() && len(group.Specs) == 1 {
			if spec, ok := group.Specs[0].(*ast.TypeSpec); ok {
				kind := "type"
				if spec.Assign.IsValid() {
					kind = "type-alias"
				}
				entries = append(entries, entry{node: group, name: spec.Name.Name, kind: kind, aliases: []string{spec.Name.Name, f.Name.Name + "." + spec.Name.Name}})
			}
		}
	}
	lines := strings.Split(r.Source, "\n")
	seen := map[string]bool{}
	selected := map[ast.Node]bool{}
	units := []unit{}
	valid := regexp.MustCompile(`^[A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*){0,2}$`)
	for _, sel := range r.Selectors {
		if seen[sel] || !valid.MatchString(sel) {
			return nil, errors.New("invalid or duplicate selector")
		}
		seen[sel] = true
		matches := []entry{}
		for _, e := range entries {
			for _, alias := range e.aliases {
				if sel == alias {
					matches = append(matches, e)
					break
				}
			}
		}
		if len(matches) != 1 {
			return nil, fmt.Errorf("selector %s has %d matches", sel, len(matches))
		}
		e := matches[0]
		d := e.d
		if selected[e.node] {
			return nil, errors.New("aliases select same declaration twice")
		}
		selected[e.node] = true
		if d != nil && d.Body == nil {
			return nil, errors.New("bodyless declaration")
		}
		// PositionFor(false) deliberately ignores //line directives.
		start := fs.PositionFor(e.node.Pos(), false)
		end := fs.PositionFor(e.node.End(), false)
		prefix := lines[start.Line-1][:start.Column-1]
		suffix := lines[end.Line-1][end.Column-1:]
		suffix = strings.TrimSpace(suffix)
		if strings.TrimSpace(prefix) != "" || (suffix != "" && !strings.HasPrefix(suffix, "//")) {
			return nil, errors.New("adjacent content on selected declaration lines")
		}
		quote := strings.Join(lines[start.Line-1:end.Line], "\n")
		if len(quote) > 6144 {
			return nil, errors.New("selected declaration exceeds 6144 bytes")
		}
		declaration := strings.TrimSpace(quote)
		if d != nil {
			declarationEnd := fs.PositionFor(d.Body.Lbrace, false).Offset
			declaration = strings.TrimSpace(r.Source[start.Offset:declarationEnd])
			if len(declaration) > 1900 {
				return nil, errors.New("oversized declaration")
			}
		}
		u := unit{Selector: sel, DeclarationKind: e.kind, Symbol: f.Name.Name + "." + e.name, Start: start.Line, End: end.Line, Quote: quote, Declaration: declaration}
		if d != nil {
			u.FunctionType = rendered(fs, d.Type)
			u.ReturnContract = returnContract(fs, d.Body, 0)
			u.DeferredReturnContract = deferredReturnContract(fs, d.Body)
			u.IfReturnContract = ifReturnContract(fs, d.Body)
			u.IfReturnChainContract = ifReturnChainContract(fs, d.Body)
			u.HandlerDeferContract = handlerDeferContract(fs, d)
			if d.Recv != nil {
				u.ReceiverType = rendered(fs, d.Recv.List[0].Type)
			}
			if len(d.Body.List) == 1 {
				if ret, ok := d.Body.List[0].(*ast.ReturnStmt); ok && len(ret.Results) == 1 {
					if lit, ok := ret.Results[0].(*ast.FuncLit); ok {
						u.Factory = map[string]interface{}{"profile": "returned-function-literal-signature-v1", "outer_function_type": rendered(fs, d.Type), "returned_literal_type": rendered(fs, lit.Type), "callback_body_statements": len(lit.Body.List), "claim": "The outer body solely returns this function literal. Its body is not executed by that return expression; helper behavior and types are not verified."}
					}
				}
			}
		}
		units = append(units, u)
	}
	return map[string]interface{}{"profile": "go-standard-parser-declarations-v1", "path": r.Path, "source_sha256": digest(r.Source), "go_version": runtime.Version(), "platform": runtime.GOOS + "/" + runtime.GOARCH, "parser_mode": "AllErrors|ParseComments|SkipObjectResolution", "syntax_only": true, "source_executed": false, "units": units}, nil
}

// encoding/json otherwise replaces unpaired UTF-16 surrogate escapes with U+FFFD.
func validEscapedUnicode(raw []byte) bool {
	inString := false
	hex4 := func(b []byte) (int, bool) {
		if len(b) < 4 {
			return 0, false
		}
		n := 0
		for _, c := range b[:4] {
			n *= 16
			switch {
			case c >= '0' && c <= '9':
				n += int(c - '0')
			case c >= 'a' && c <= 'f':
				n += int(c-'a') + 10
			case c >= 'A' && c <= 'F':
				n += int(c-'A') + 10
			default:
				return 0, false
			}
		}
		return n, true
	}
	for i := 0; i < len(raw); i++ {
		if raw[i] == '"' {
			inString = !inString
			continue
		}
		if !inString || raw[i] != 92 {
			continue
		}
		i++
		if i >= len(raw) {
			return false
		}
		if raw[i] != 'u' {
			continue
		}
		n, ok := hex4(raw[i+1:])
		if !ok {
			return false
		}
		i += 4
		if n >= 0xDC00 && n <= 0xDFFF {
			return false
		}
		if n >= 0xD800 && n <= 0xDBFF {
			if i+6 >= len(raw) || raw[i+1] != 92 || raw[i+2] != 'u' {
				return false
			}
			low, ok := hex4(raw[i+3:])
			if !ok || low < 0xDC00 || low > 0xDFFF {
				return false
			}
			i += 6
		}
	}
	return true
}
func decodeRequest(raw []byte) (request, error) {
	var r request
	if !utf8.Valid(raw) || !validEscapedUnicode(raw) {
		return r, errors.New("invalid Unicode request")
	}
	dec := json.NewDecoder(bytes.NewReader(raw))
	first, err := dec.Token()
	if err != nil || first != json.Delim('{') {
		return r, errors.New("request must be object")
	}
	fields := map[string]json.RawMessage{}
	for dec.More() {
		key, err := dec.Token()
		if err != nil {
			return r, err
		}
		name, ok := key.(string)
		if !ok {
			return r, errors.New("invalid field")
		}
		if _, exists := fields[name]; exists {
			return r, errors.New("duplicate field")
		}
		if name != "source" && name != "path" && name != "selectors" {
			return r, errors.New("unknown field")
		}
		var value json.RawMessage
		if err = dec.Decode(&value); err != nil {
			return r, err
		}
		if bytes.Equal(bytes.TrimSpace(value), []byte("null")) {
			return r, errors.New("null field")
		}
		fields[name] = value
	}
	if _, err = dec.Token(); err != nil {
		return r, err
	}
	var extra interface{}
	if dec.Decode(&extra) != io.EOF {
		return r, errors.New("trailing input")
	}
	if len(fields) != 3 {
		return r, errors.New("exactly source, path and selectors required")
	}
	if err = json.Unmarshal(fields["source"], &r.Source); err != nil {
		return r, err
	}
	if err = json.Unmarshal(fields["path"], &r.Path); err != nil {
		return r, err
	}
	if err = json.Unmarshal(fields["selectors"], &r.Selectors); err != nil {
		return r, err
	}
	return r, nil
}
func main() {
	raw, err := io.ReadAll(io.LimitReader(os.Stdin, 3*1024*1024+1))
	if err != nil || len(raw) > 3*1024*1024 {
		fmt.Fprintln(os.Stderr, "request too large or unreadable")
		os.Exit(2)
	}
	r, err := decodeRequest(raw)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	result, err := inspect(r)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetEscapeHTML(false)
	if err = enc.Encode(result); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
}
