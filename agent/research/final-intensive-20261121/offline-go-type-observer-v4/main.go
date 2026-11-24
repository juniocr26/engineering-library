// Isolated research: typecheck supplied source graph; never execute target source.
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
	"path"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
)

type File struct {
	Path   string `json:"path"`
	Source string `json:"source"`
	SHA    string `json:"sha256"`
}
type SourcePackage struct {
	Path  string `json:"package_path"`
	Files []File `json:"files"`
}
type Export struct {
	Path string `json:"path"`
	SHA  string `json:"sha256"`
}
type Request struct {
	Packages   []SourcePackage   `json:"packages"`
	ExportRoot string            `json:"export_root"`
	Exports    map[string]Export `json:"standard_exports"`
}
type Relation struct {
	Package    string `json:"package_path"`
	File       string `json:"file"`
	Line       int    `json:"line"`
	Column     int    `json:"column"`
	Name       string `json:"name"`
	Kind       string `json:"kind"`
	Receiver   string `json:"receiver,omitempty"`
	Object     string `json:"object"`
	Type       string `json:"type"`
	ImportPath string `json:"import_path,omitempty"`
	Index      []int  `json:"index,omitempty"`
	Indirect   bool   `json:"indirect"`
}
type Declaration struct {
	Package    string `json:"package_path"`
	File       string `json:"file"`
	Line       int    `json:"line"`
	Name       string `json:"name"`
	Object     string `json:"object"`
	Type       string `json:"type"`
	Underlying string `json:"underlying"`
	Alias      bool   `json:"alias"`
}
type Response struct {
	Schema          string            `json:"schema"`
	Status          string            `json:"status"`
	GoVersion       string            `json:"go_version"`
	Language        string            `json:"language_profile"`
	GOARCH          string            `json:"goarch"`
	SourceHashes    map[string]string `json:"source_sha256"`
	GraphSHA        string            `json:"source_graph_sha256"`
	ExportsSHA      string            `json:"standard_graph_sha256"`
	UsedExports     map[string]string `json:"used_export_sha256"`
	Diagnostics     []string          `json:"diagnostics"`
	Relations       []Relation        `json:"relations"`
	Declarations    []Declaration     `json:"declarations"`
	SourceExecuted  bool              `json:"source_executed"`
	RuntimeVerified bool              `json:"runtime_bindings_verified"`
	Partial         bool              `json:"partial_type_info_admitted"`
}
type sourceImporter struct {
	load func(string) (*types.Package, error)
}

func (i sourceImporter) Import(p string) (*types.Package, error) { return i.load(p) }
func hash(b []byte) string                                       { v := sha256.Sum256(b); return hex.EncodeToString(v[:]) }

// Reject duplicate object keys at every depth, before ordinary typed decoding.
func uniqueJSON(d *json.Decoder, depth int) error {
	if depth > 64 {
		return fmt.Errorf("JSON depth exceeds64")
	}
	t, e := d.Token()
	if e != nil {
		return e
	}
	del, ok := t.(json.Delim)
	if !ok {
		return nil
	}
	switch del {
	case '{':
		seen := map[string]bool{}
		for d.More() {
			key, e := d.Token()
			if e != nil {
				return e
			}
			k, ok := key.(string)
			if !ok || seen[k] {
				return fmt.Errorf("duplicate/invalid JSON key")
			}
			seen[k] = true
			if e = uniqueJSON(d, depth+1); e != nil {
				return e
			}
		}
		end, e := d.Token()
		if e != nil || end != json.Delim('}') {
			return fmt.Errorf("object terminator")
		}
	case '[':
		for d.More() {
			if e = uniqueJSON(d, depth+1); e != nil {
				return e
			}
		}
		end, e := d.Token()
		if e != nil || end != json.Delim(']') {
			return fmt.Errorf("array terminator")
		}
	default:
		return fmt.Errorf("unexpected delimiter")
	}
	return nil
}
func cleanRelative(s string) bool {
	if s == "" || len(s) > 1024 || path.Clean(s) != s || strings.HasPrefix(s, "/") {
		return false
	}
	for _, part := range strings.Split(s, "/") {
		if part == "." || part == ".." || part == "" {
			return false
		}
	}
	for _, c := range s {
		if !((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '/' || c == '.' || c == '_' || c == '-') {
			return false
		}
	}
	return true
}
func main() {
	r := Response{Schema: "owned-go-source-graph-types-v4", Status: "REFUSED", GoVersion: runtime.Version(), Language: "go1.27", GOARCH: runtime.GOARCH, SourceHashes: map[string]string{}, UsedExports: map[string]string{}, Diagnostics: []string{}, Relations: []Relation{}, Declarations: []Declaration{}}
	defer func() {
		if e := recover(); e != nil {
			r.Status = "REFUSED"
			r.Diagnostics = append(r.Diagnostics, fmt.Sprint(e))
		}
		if r.Status != "TYPECHECKED_FROZEN_SOURCE_GRAPH" {
			r.Relations = []Relation{}
			r.Declarations = []Declaration{}
		}
		json.NewEncoder(os.Stdout).Encode(r)
	}()
	raw, e := io.ReadAll(io.LimitReader(os.Stdin, 131073))
	if e != nil || len(raw) > 131072 {
		panic("packet exceeds131072bytes")
	}
	guard := json.NewDecoder(strings.NewReader(string(raw)))
	guard.UseNumber()
	if e = uniqueJSON(guard, 0); e != nil {
		panic(e)
	}
	if _, e = guard.Token(); e != io.EOF {
		panic("trailing JSON")
	}
	var req Request
	decoder := json.NewDecoder(strings.NewReader(string(raw)))
	decoder.DisallowUnknownFields()
	if e = decoder.Decode(&req); e != nil {
		panic(e)
	}
	if len(req.Packages) < 1 || len(req.Packages) > 8 || !filepath.IsAbs(req.ExportRoot) || len(req.Exports) < 1 || len(req.Exports) > 256 {
		panic("bounded packages/frozen standard graph required")
	}
	fs := token.NewFileSet()
	packages := map[string]SourcePackage{}
	trees := map[string][]*ast.File{}
	infos := map[string]*types.Info{}
	graph := map[string]map[string]string{}
	total := 0
	for _, pkg := range req.Packages {
		first := strings.Split(pkg.Path, "/")[0]
		if !cleanRelative(pkg.Path) || !strings.Contains(first, ".") || strings.HasPrefix(first, ".") || strings.HasSuffix(first, ".") || strings.Contains(first, "..") {
			panic("source package requires explicit nonstandard clean import path")
		}
		if _, ok := req.Exports[pkg.Path]; ok {
			panic("source shadows standard export")
		}
		if _, ok := packages[pkg.Path]; ok {
			panic("duplicate source package")
		}
		packages[pkg.Path] = pkg
		if len(pkg.Files) < 1 || len(pkg.Files) > 16 {
			panic("bounded source files required")
		}
		graph[pkg.Path] = map[string]string{}
		for _, f := range pkg.Files {
			total++
			if total > 16 || len(f.Source) > 65536 || !cleanRelative(f.Path) {
				panic("file count/path/size bound")
			}
			if _, ok := graph[pkg.Path][f.Path]; ok {
				panic("duplicate source filename")
			}
			digest := hash([]byte(f.Source))
			if digest != f.SHA {
				panic("source sha256 mismatch")
			}
			graph[pkg.Path][f.Path] = digest
			r.SourceHashes[pkg.Path+"::"+f.Path] = digest
			tree, err := parser.ParseFile(fs, pkg.Path+"::"+f.Path, f.Source, parser.AllErrors|parser.ParseComments)
			if err != nil {
				r.Diagnostics = append(r.Diagnostics, err.Error())
				return
			}
			trees[pkg.Path] = append(trees[pkg.Path], tree)
		}
	}
	g, _ := json.Marshal(graph)
	r.GraphSHA = hash(g)
	g, _ = json.Marshal(req.Exports)
	r.ExportsSHA = hash(g)
	lookupFailed := false
	lookup := func(importPath string) (io.ReadCloser, error) {
		reject := func(reason string) (io.ReadCloser, error) {
			lookupFailed = true
			return nil, fmt.Errorf("frozen standard export %s: %s", importPath, reason)
		}
		x, ok := req.Exports[importPath]
		if !ok {
			return reject("not registered")
		}
		rel := filepath.Clean(x.Path)
		if filepath.IsAbs(rel) || rel == ".." || strings.HasPrefix(rel, "../") || strings.Contains(rel, "\\") {
			return reject("unsafe relative export path")
		}
		f, err := os.Open(filepath.Join(req.ExportRoot, rel))
		if err != nil {
			return reject(err.Error())
		}
		data, err := io.ReadAll(io.LimitReader(f, 33554433))
		f.Close()
		if err != nil || len(data) > 33554432 {
			return reject("read/size bound")
		}
		if hash(data) != x.SHA {
			return reject("sha256 differs")
		}
		r.UsedExports[importPath] = x.SHA
		return io.NopCloser(strings.NewReader(string(data))), nil
	}
	standard := importer.ForCompiler(fs, "gc", lookup)
	state := map[string]int{}
	checked := map[string]*types.Package{}
	var check func(string) (*types.Package, error)
	check = func(importPath string) (*types.Package, error) {
		if state[importPath] == 1 {
			return nil, fmt.Errorf("source import cycle: %s", importPath)
		}
		if pkg := checked[importPath]; pkg != nil {
			return pkg, nil
		}
		_, ok := packages[importPath]
		if !ok {
			if _, registered := req.Exports[importPath]; registered || importPath == "unsafe" {
				return standard.Import(importPath)
			}
			return nil, fmt.Errorf("import outside frozen source/standard graph: %s", importPath)
		}
		state[importPath] = 1
		info := &types.Info{Selections: map[*ast.SelectorExpr]*types.Selection{}, Types: map[ast.Expr]types.TypeAndValue{}, Defs: map[*ast.Ident]types.Object{}, Uses: map[*ast.Ident]types.Object{}}
		infos[importPath] = info
		config := types.Config{Importer: sourceImporter{check}, GoVersion: "go1.27", Sizes: types.SizesFor("gc", runtime.GOARCH), Error: func(err error) { r.Diagnostics = append(r.Diagnostics, err.Error()) }}
		pkg, err := config.Check(importPath, fs, trees[importPath], info)
		if err != nil {
			return nil, err
		}
		state[importPath] = 2
		checked[importPath] = pkg
		return pkg, nil
	}
	order := make([]string, 0, len(packages))
	for key := range packages {
		order = append(order, key)
	}
	sort.Strings(order)
	for _, key := range order {
		if _, err := check(key); err != nil {
			r.Status = "INCONCLUSIVE_TYPE_OR_IMPORT_ERRORS"
			if lookupFailed {
				r.Status = "INCONCLUSIVE_IMPORT_IDENTITY"
			}
			if len(r.Diagnostics) == 0 {
				r.Diagnostics = append(r.Diagnostics, err.Error())
			}
			return
		}
	}
	if len(r.Diagnostics) > 0 {
		r.Status = "INCONCLUSIVE_TYPE_OR_IMPORT_ERRORS"
		return
	}
	for _, key := range order {
		info := infos[key]
		for expr, s := range info.Selections {
			pos := fs.Position(expr.Pos())
			kind := map[types.SelectionKind]string{types.FieldVal: "FieldVal", types.MethodVal: "MethodVal", types.MethodExpr: "MethodExpr"}[s.Kind()]
			r.Relations = append(r.Relations, Relation{Package: key, File: pos.Filename, Line: pos.Line, Column: pos.Column, Name: expr.Sel.Name, Kind: kind, Receiver: types.TypeString(s.Recv(), nil), Object: types.ObjectString(s.Obj(), nil), Type: types.TypeString(s.Type(), nil), Index: s.Index(), Indirect: s.Indirect()})
		}
		for ident, obj := range info.Defs {
			if obj == nil || ident.Name == "_" {
				continue
			}
			if obj.Parent() != checked[key].Scope() {
				continue
			}
			pos := fs.Position(ident.Pos())
			alias := false
			if tn, ok := obj.(*types.TypeName); ok {
				alias = tn.IsAlias()
			}
			r.Declarations = append(r.Declarations, Declaration{key, pos.Filename, pos.Line, ident.Name, types.ObjectString(obj, nil), types.TypeString(obj.Type(), nil), types.TypeString(obj.Type().Underlying(), nil), alias})
		}
		for _, tree := range trees[key] {
			ast.Inspect(tree, func(node ast.Node) bool {
				expr, ok := node.(*ast.SelectorExpr)
				if !ok || info.Selections[expr] != nil {
					return true
				}
				ident, ok := expr.X.(*ast.Ident)
				if !ok {
					return true
				}
				pkg, ok := info.Uses[ident].(*types.PkgName)
				if !ok {
					return true
				}
				obj := info.Uses[expr.Sel]
				if obj == nil {
					return true
				}
				pos := fs.Position(expr.Pos())
				r.Relations = append(r.Relations, Relation{Package: key, File: pos.Filename, Line: pos.Line, Column: pos.Column, Name: expr.Sel.Name, Kind: "QualifiedUse", ImportPath: pkg.Imported().Path(), Object: types.ObjectString(obj, nil), Type: types.TypeString(obj.Type(), nil)})
				return true
			})
		}
	}
	sort.Slice(r.Relations, func(i, j int) bool {
		a, b := r.Relations[i], r.Relations[j]
		if a.File != b.File {
			return a.File < b.File
		}
		if a.Line != b.Line {
			return a.Line < b.Line
		}
		return a.Column < b.Column
	})
	sort.Slice(r.Declarations, func(i, j int) bool {
		a, b := r.Declarations[i], r.Declarations[j]
		if a.File != b.File {
			return a.File < b.File
		}
		return a.Line < b.Line
	})
	r.Status = "TYPECHECKED_FROZEN_SOURCE_GRAPH"
}
