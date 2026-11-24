// A bounded, optional source experiment. Inspected Go source is never executed.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"go/ast"
	"go/build"
	"go/parser"
	"go/token"
	"go/version"
	"io"
	"io/fs"
	"os"
	"path"
	"regexp"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"time"
	"unicode/utf8"
)

const toolVersion = "0.1.0"
const maxInput = 16 * 1024 * 1024
const maxSource = 256 * 1024
const maxQuote = 6144

type Profile struct {
	GOOS      string   `json:"goos"`
	GOARCH    string   `json:"goarch"`
	BuildTags []string `json:"build_tags"`
}
type Module struct {
	Source string `json:"source"`
	SHA256 string `json:"sha256"`
}
type SourceFile struct {
	Name   string `json:"name"`
	Source string `json:"source"`
	SHA256 string `json:"sha256"`
}
type PackageInput struct {
	ImportPath string       `json:"import_path"`
	Kind       string       `json:"kind"`
	Files      []SourceFile `json:"files"`
}
type Request struct {
	Profile           Profile        `json:"profile"`
	Module            Module         `json:"module"`
	PackageImportPath string         `json:"package_import_path"`
	File              string         `json:"file"`
	Function          string         `json:"function"`
	Builtin           string         `json:"builtin"`
	Packages          []PackageInput `json:"packages"`
}

func digest(raw []byte) string {
	sum := sha256.Sum256(raw)
	return hex.EncodeToString(sum[:])
}

// encoding/json accepts duplicate object keys by default. Reject them before
// decoding the closed request structs, including nested profile/file objects.
func uniqueJSON(raw []byte) error {
	if err := validEscapedScalars(raw); err != nil {
		return err
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	var value func(int) error
	value = func(depth int) error {
		if depth > 24 {
			return errors.New("JSON nesting exceeds bound")
		}
		item, err := decoder.Token()
		if err != nil {
			return err
		}
		if item == nil {
			return errors.New("null is outside the closed request profile")
		}
		delim, ok := item.(json.Delim)
		if !ok {
			return nil
		}
		switch delim {
		case '{':
			seen := map[string]bool{}
			for decoder.More() {
				key, err := decoder.Token()
				if err != nil {
					return err
				}
				name, ok := key.(string)
				if !ok || seen[name] {
					return errors.New("duplicate or invalid JSON object key")
				}
				seen[name] = true
				if err := value(depth + 1); err != nil {
					return err
				}
			}
		case '[':
			for decoder.More() {
				if err := value(depth + 1); err != nil {
					return err
				}
			}
		default:
			return errors.New("unexpected JSON delimiter")
		}
		_, err = decoder.Token()
		return err
	}
	if err := value(0); err != nil {
		return err
	}
	if _, err := decoder.Token(); err != io.EOF {
		return errors.New("request must contain exactly one JSON value")
	}
	return nil
}

// encoding/json replaces lone UTF-16 surrogate escapes with U+FFFD. Refuse that
// lossy spelling before hashing decoded source; literal replacement characters
// and properly paired supplementary Unicode characters remain valid.
func validEscapedScalars(raw []byte) error {
	inString := false
	for index := 0; index < len(raw); index++ {
		if raw[index] == '"' {
			inString = !inString
			continue
		}
		if !inString || raw[index] != '\\' {
			continue
		}
		index++
		if index >= len(raw) {
			return errors.New("unfinished JSON escape")
		}
		if raw[index] != 'u' {
			continue
		}
		if index+4 >= len(raw) {
			return errors.New("short Unicode escape")
		}
		value, err := strconv.ParseUint(string(raw[index+1:index+5]), 16, 16)
		if err != nil {
			return errors.New("invalid Unicode escape")
		}
		index += 4
		if value >= 0xdc00 && value <= 0xdfff {
			return errors.New("unpaired low surrogate escape")
		}
		if value >= 0xd800 && value <= 0xdbff {
			if index+6 >= len(raw) || raw[index+1] != '\\' || raw[index+2] != 'u' {
				return errors.New("unpaired high surrogate escape")
			}
			low, err := strconv.ParseUint(string(raw[index+3:index+7]), 16, 16)
			if err != nil || low < 0xdc00 || low > 0xdfff {
				return errors.New("invalid surrogate pair")
			}
			index += 6
		}
	}
	return nil
}

func decode(raw []byte) (Request, error) {
	var request Request
	if len(raw) > maxInput || !utf8.Valid(raw) {
		return request, errors.New("oversized or invalid UTF-8 request")
	}
	if err := uniqueJSON(raw); err != nil {
		return request, err
	}
	if err := strictShape(raw); err != nil {
		return request, err
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&request); err != nil {
		return request, err
	}
	return request, nil
}

func objectFields(raw json.RawMessage, names ...string) (map[string]json.RawMessage, error) {
	var object map[string]json.RawMessage
	if err := json.Unmarshal(raw, &object); err != nil || object == nil || len(object) != len(names) {
		return nil, errors.New("required closed object fields differ")
	}
	for _, name := range names {
		if _, exists := object[name]; !exists {
			return nil, errors.New("missing or incorrectly cased field: " + name)
		}
	}
	return object, nil
}

func strictShape(raw []byte) error {
	root, err := objectFields(raw, "profile", "module", "package_import_path", "file", "function", "builtin", "packages")
	if err != nil {
		return err
	}
	if _, err := objectFields(root["profile"], "goos", "goarch", "build_tags"); err != nil {
		return err
	}
	if _, err := objectFields(root["module"], "source", "sha256"); err != nil {
		return err
	}
	var packages []json.RawMessage
	if err := json.Unmarshal(root["packages"], &packages); err != nil {
		return err
	}
	for _, item := range packages {
		object, err := objectFields(item, "import_path", "kind", "files")
		if err != nil {
			return err
		}
		var files []json.RawMessage
		if err := json.Unmarshal(object["files"], &files); err != nil {
			return err
		}
		for _, file := range files {
			if _, err := objectFields(file, "name", "source", "sha256"); err != nil {
				return err
			}
		}
	}
	return nil
}

var importPattern = regexp.MustCompile(`^[A-Za-z0-9_][A-Za-z0-9_./~-]*$`)
var filePattern = regexp.MustCompile(`^[A-Za-z0-9_.-]+\.go$`)
var tagPattern = regexp.MustCompile(`^[A-Za-z0-9_.]{1,64}$`)
var releasePattern = regexp.MustCompile(`^[0-9]+\.[0-9]+(?:\.[0-9]+)?$`)
var dependencyVersion = regexp.MustCompile(`^v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9_.-]+)?$`)

func safeImport(value string) bool {
	if !importPattern.MatchString(value) || path.Clean(value) != value || strings.HasPrefix(value, "/") {
		return false
	}
	for _, component := range strings.Split(value, "/") {
		if component == "." || component == ".." || component == "" {
			return false
		}
	}
	return true
}

// This closed module-declaration profile supports ordinary require blocks, not
// a complete go.mod grammar, workspaces, replacement graphs or toolchain fetch.
func moduleIdentity(input Module) (string, string, error) {
	if len(input.Source) > 65536 || digest([]byte(input.Source)) != input.SHA256 {
		return "", "", errors.New("module source checksum or size mismatch")
	}
	modulePath, language, inRequire := "", "", false
	checkDependency := func(fields []string) bool {
		return len(fields) == 2 && safeImport(fields[0]) && dependencyVersion.MatchString(fields[1])
	}
	for _, line := range strings.Split(input.Source, "\n") {
		line = strings.TrimSpace(strings.SplitN(line, "//", 2)[0])
		if line == "" {
			continue
		}
		fields := strings.Fields(line)
		if inRequire {
			if line == ")" {
				inRequire = false
			} else if !checkDependency(fields) {
				return "", "", errors.New("unsupported require entry")
			}
			continue
		}
		switch fields[0] {
		case "module":
			if modulePath != "" || len(fields) != 2 || !safeImport(fields[1]) {
				return "", "", errors.New("invalid or duplicate module declaration")
			}
			modulePath = fields[1]
		case "go":
			if language != "" || len(fields) != 2 || !releasePattern.MatchString(fields[1]) {
				return "", "", errors.New("invalid or duplicate go language declaration")
			}
			language = fields[1]
		case "require":
			if line == "require (" {
				inRequire = true
			} else if !checkDependency(fields[1:]) {
				return "", "", errors.New("unsupported require directive")
			}
		default:
			return "", "", fmt.Errorf("module directive outside closed profile: %s", fields[0])
		}
	}
	if modulePath == "" || language == "" || inRequire {
		return "", "", errors.New("incomplete module declaration")
	}
	if !version.IsValid("go"+language) || version.Compare("go"+language, "go1.21") < 0 ||
		version.Compare("go"+language, runtime.Version()) > 0 {
		return "", "", errors.New("module language outside min/max/toolchain support")
	}
	return modulePath, language, nil
}

type virtualInfo struct {
	name  string
	size  int64
	isDir bool
}

func (info virtualInfo) Name() string       { return info.name }
func (info virtualInfo) Size() int64        { return info.size }
func (info virtualInfo) ModTime() time.Time { return time.Unix(0, 0) }
func (info virtualInfo) Sys() any           { return nil }
func (info virtualInfo) IsDir() bool        { return info.isDir }
func (info virtualInfo) Mode() fs.FileMode {
	if info.isDir {
		return fs.ModeDir | 0555
	}
	return 0444
}

type census struct {
	Directory   string   `json:"directory"`
	PackageName string   `json:"package_name"`
	ActiveFiles []string `json:"active_files"`
	IgnoredGo   []string `json:"ignored_go_files"`
	Tests       []string `json:"test_files"`
	CgoFiles    []string `json:"cgo_files"`
	SourceHash  string   `json:"source_set_sha256"`
}

type analysis struct {
	request      Request
	context      build.Context
	packages     map[string]PackageInput
	directories  map[string]string
	files        map[string]string
	packageCache map[string]*build.Package
	censuses     map[string]census
}

func prepare(request Request) (*analysis, error) {
	if request.Profile.GOARCH != "arm64" || (request.Profile.GOOS != "darwin" && request.Profile.GOOS != "linux") ||
		len(request.Profile.BuildTags) > 16 || len(request.Packages) < 1 || len(request.Packages) > 8 {
		return nil, errors.New("unsupported explicit build profile or package budget")
	}
	for _, tag := range request.Profile.BuildTags {
		if !tagPattern.MatchString(tag) {
			return nil, errors.New("invalid build tag")
		}
	}
	if request.Builtin != "max" && request.Builtin != "min" {
		return nil, errors.New("only min/max binding supported")
	}
	if !token.IsIdentifier(request.Function) || request.Function == "_" || !filePattern.MatchString(request.File) {
		return nil, errors.New("invalid selected callable/file")
	}
	modulePath, _, err := moduleIdentity(request.Module)
	if err != nil {
		return nil, err
	}
	result := &analysis{request: request, packages: map[string]PackageInput{}, directories: map[string]string{},
		files: map[string]string{}, packageCache: map[string]*build.Package{}, censuses: map[string]census{}}
	for _, item := range request.Packages {
		if !safeImport(item.ImportPath) || len(item.Files) < 1 || len(item.Files) > 512 {
			return nil, errors.New("invalid package identity or source-file budget")
		}
		if _, exists := result.packages[item.ImportPath]; exists {
			return nil, errors.New("duplicate package registration")
		}
		var directory string
		switch item.Kind {
		case "module":
			if item.ImportPath != modulePath && !strings.HasPrefix(item.ImportPath, modulePath+"/") {
				return nil, errors.New("package outside declared module")
			}
			directory = path.Join("/frozen/module", strings.TrimPrefix(strings.TrimPrefix(item.ImportPath, modulePath), "/"))
		case "stdlib":
			if strings.Contains(strings.Split(item.ImportPath, "/")[0], ".") {
				return nil, errors.New("nonstandard path labelled stdlib")
			}
			directory = path.Join("/frozen/goroot/src", item.ImportPath)
		default:
			return nil, errors.New("unknown package source kind")
		}
		seen := map[string]bool{}
		for _, file := range item.Files {
			if !filePattern.MatchString(file.Name) || seen[file.Name] || len(file.Source) > maxSource ||
				!utf8.ValidString(file.Source) || strings.ContainsRune(file.Source, 0) || digest([]byte(file.Source)) != file.SHA256 {
				return nil, errors.New("invalid, duplicate, oversized or changed package source")
			}
			seen[file.Name] = true
			result.files[path.Join(directory, file.Name)] = file.Source
		}
		result.packages[item.ImportPath] = item
		result.directories[item.ImportPath] = directory
	}
	selected, exists := result.packages[request.PackageImportPath]
	if !exists || selected.Kind != "module" {
		return nil, errors.New("selected package must belong to frozen module")
	}
	context := build.Default
	context.GOOS, context.GOARCH = request.Profile.GOOS, request.Profile.GOARCH
	context.CgoEnabled, context.UseAllFiles = false, false
	context.BuildTags = append([]string(nil), request.Profile.BuildTags...)
	context.Dir, context.GOROOT, context.GOPATH = "/frozen", "/frozen/goroot", "/frozen/gopath"
	context.JoinPath, context.IsAbsPath = path.Join, path.IsAbs
	context.SplitPathList = func(value string) []string { return strings.Split(value, ":") }
	context.HasSubdir = func(root, directory string) (string, bool) {
		root, directory = path.Clean(root), path.Clean(directory)
		if directory == root {
			return ".", true
		}
		return strings.TrimPrefix(directory, root+"/"), strings.HasPrefix(directory, root+"/")
	}
	context.IsDir = func(directory string) bool {
		for file := range result.files {
			if strings.HasPrefix(file, path.Clean(directory)+"/") {
				return true
			}
		}
		return false
	}
	context.ReadDir = func(directory string) ([]fs.FileInfo, error) {
		children := map[string]virtualInfo{}
		for file, source := range result.files {
			if !strings.HasPrefix(file, path.Clean(directory)+"/") {
				continue
			}
			relative := strings.TrimPrefix(file, path.Clean(directory)+"/")
			name, tail, hasTail := strings.Cut(relative, "/")
			_ = tail
			children[name] = virtualInfo{name, int64(len(source)), hasTail}
		}
		if len(children) == 0 {
			return nil, os.ErrNotExist
		}
		names := make([]string, 0, len(children))
		for name := range children {
			names = append(names, name)
		}
		sort.Strings(names)
		entries := make([]fs.FileInfo, 0, len(names))
		for _, name := range names {
			entries = append(entries, children[name])
		}
		return entries, nil
	}
	context.OpenFile = func(filename string) (io.ReadCloser, error) {
		source, exists := result.files[path.Clean(filename)]
		if !exists {
			return nil, os.ErrNotExist
		}
		return io.NopCloser(strings.NewReader(source)), nil
	}
	result.context = context
	return result, nil
}

func (state *analysis) packageInfo(importPath string) (*build.Package, error) {
	if info, exists := state.packageCache[importPath]; exists {
		return info, nil
	}
	directory, exists := state.directories[importPath]
	if !exists {
		return nil, fmt.Errorf("unregistered import package: %s", importPath)
	}
	// Custom filesystem callbacks and IgnoreVendor explicitly prevent the
	// go/build module fallback from invoking a go command or reading host files.
	info, err := state.context.ImportDir(directory, build.IgnoreVendor)
	if err != nil {
		return nil, fmt.Errorf("build-filtered package %s refused: %w", importPath, err)
	}
	if len(info.GoFiles) == 0 {
		return nil, errors.New("no ordinary Go files in selected build profile")
	}
	item := state.packages[importPath]
	identities := make([]string, 0, len(item.Files))
	for _, file := range item.Files {
		identities = append(identities, file.Name+":"+file.SHA256)
	}
	sort.Strings(identities)
	tests := append(append([]string(nil), info.TestGoFiles...), info.XTestGoFiles...)
	sort.Strings(tests)
	state.censuses[importPath] = census{directory, info.Name, info.GoFiles, info.IgnoredGoFiles, tests, info.CgoFiles, digest([]byte(strings.Join(identities, "\n")))}
	state.packageCache[importPath] = info
	return info, nil
}

func declaredNames(file *ast.File) map[string]int {
	names := map[string]int{}
	for _, declaration := range file.Decls {
		switch node := declaration.(type) {
		case *ast.FuncDecl:
			if node.Recv == nil {
				names[node.Name.Name]++
			}
		case *ast.GenDecl:
			for _, spec := range node.Specs {
				switch entry := spec.(type) {
				case *ast.TypeSpec:
					names[entry.Name.Name]++
				case *ast.ValueSpec:
					for _, name := range entry.Names {
						names[name.Name]++
					}
				}
			}
		}
	}
	return names
}

func localObstruction(function *ast.FuncDecl, name string) string {
	for _, list := range []*ast.FieldList{function.Recv, function.Type.TypeParams, function.Type.Params, function.Type.Results} {
		if list == nil {
			continue
		}
		for _, field := range list.List {
			for _, identifier := range field.Names {
				if identifier.Name == name {
					return "selected signature declares the builtin name"
				}
			}
		}
	}
	reason := ""
	ast.Inspect(function.Body, func(node ast.Node) bool {
		switch entry := node.(type) {
		case *ast.FuncLit:
			reason = "nested function literal outside lexical binding profile"
			return false
		case *ast.ValueSpec:
			for _, identifier := range entry.Names {
				if identifier.Name == name {
					reason = "local value declaration may shadow the builtin"
				}
			}
		case *ast.TypeSpec:
			if entry.Name.Name == name {
				reason = "local type declaration may shadow the builtin"
			}
		case *ast.AssignStmt:
			for _, expression := range entry.Lhs {
				if identifier, ok := expression.(*ast.Ident); ok && identifier.Name == name {
					reason = "local assignment/declaration may shadow the builtin"
				}
			}
		case *ast.RangeStmt:
			if entry.Tok == token.DEFINE {
				for _, expression := range []ast.Expr{entry.Key, entry.Value} {
					if identifier, ok := expression.(*ast.Ident); ok && identifier.Name == name {
						reason = "range declaration may shadow the builtin"
					}
				}
			}
		}
		return true
	})
	return reason
}

func analyze(request Request) map[string]any {
	result := map[string]any{"profile": "go-build-filtered-predeclared-binding-v1", "version": toolVersion,
		"status": "INCONCLUSIVE", "source_executed": false, "runtime_bindings_verified": false,
		"type_checked": false, "owner_approved": false, "publication_authorized": false,
		"conditional_on_supplied_complete_census": true, "build_profile": request.Profile}
	refuse := func(reason string) map[string]any { result["reason"] = reason; return result }
	state, err := prepare(request)
	if err != nil {
		return refuse(err.Error())
	}
	info, err := state.packageInfo(request.PackageImportPath)
	if err != nil {
		return refuse(err.Error())
	}
	result["package_censuses"] = state.censuses
	selected := false
	for _, name := range info.GoFiles {
		selected = selected || name == request.File
	}
	if !selected {
		return refuse("selected file is not active in ordinary non-test Go files")
	}
	fset := token.NewFileSet()
	var target *ast.FuncDecl
	var selectedFile *ast.File
	packageNames := map[string]int{}
	for _, name := range info.GoFiles {
		source := state.files[path.Join(state.directories[request.PackageImportPath], name)]
		file, err := parser.ParseFile(fset, name, source, parser.AllErrors|parser.SkipObjectResolution)
		if err != nil {
			return refuse("active package source syntax refused: " + err.Error())
		}
		for name, count := range declaredNames(file) {
			packageNames[name] += count
		}
		if name != request.File {
			continue
		}
		selectedFile = file
		for _, declaration := range file.Decls {
			if function, ok := declaration.(*ast.FuncDecl); ok && function.Recv == nil && function.Name.Name == request.Function {
				if target != nil {
					return refuse("duplicate selected function")
				}
				target = function
			}
		}
	}
	if target == nil || target.Body == nil || packageNames[request.Function] != 1 {
		return refuse("missing or ambiguous selected function ownership")
	}
	if packageNames[request.Builtin] != 0 {
		return refuse("active package declares the queried builtin name")
	}
	if reason := localObstruction(target, request.Builtin); reason != "" {
		return refuse(reason)
	}
	importNames := map[string]string{}
	for _, spec := range selectedFile.Imports {
		importPath, err := strconv.Unquote(spec.Path.Value)
		if err != nil {
			return refuse("invalid import literal")
		}
		name := ""
		if spec.Name != nil {
			name = spec.Name.Name
		}
		if name == "_" {
			continue
		}
		if name == "." {
			// Dot imports only bring exported identifiers into scope; ASCII
			// lowercase min/max cannot be an exported imported declaration.
			importNames[importPath] = ". (exported names only)"
			continue
		}
		if name == "" {
			imported, err := state.packageInfo(importPath)
			if err != nil {
				return refuse(err.Error())
			}
			name = imported.Name
		}
		importNames[importPath] = name
		if name == request.Builtin {
			return refuse("selected file import name shadows the queried builtin")
		}
	}
	calls := []map[string]any{}
	ast.Inspect(target.Body, func(node ast.Node) bool {
		call, ok := node.(*ast.CallExpr)
		if !ok {
			return true
		}
		identifier, ok := call.Fun.(*ast.Ident)
		if ok && identifier.Name == request.Builtin {
			position := fset.Position(call.Pos())
			calls = append(calls, map[string]any{"line": position.Line, "column": position.Column})
		}
		return true
	})
	if len(calls) == 0 || len(calls) > 8 {
		return refuse("no bounded bare call to queried builtin")
	}
	source := state.files[path.Join(state.directories[request.PackageImportPath], request.File)]
	file := fset.File(target.Pos())
	start, end := file.Offset(target.Pos()), file.Offset(target.End())
	quote := source[start:end]
	if len(quote) > maxQuote {
		return refuse("complete selected function exceeds quote bound")
	}
	normalized := request
	normalized.Packages = append([]PackageInput(nil), request.Packages...)
	sort.Slice(normalized.Packages, func(i, j int) bool { return normalized.Packages[i].ImportPath < normalized.Packages[j].ImportPath })
	for index := range normalized.Packages {
		normalized.Packages[index].Files = append([]SourceFile(nil), normalized.Packages[index].Files...)
		sort.Slice(normalized.Packages[index].Files, func(i, j int) bool {
			return normalized.Packages[index].Files[i].Name < normalized.Packages[index].Files[j].Name
		})
	}
	encoded, _ := json.Marshal(normalized)
	result["status"] = "LEXICALLY_UNSHADOWED_UNDER_PROFILE"
	result["reason"] = "Bare min/max name has no admitted local, package or named-import binding under the supplied build-filtered census; conditional on a valid package build."
	result["builtin"] = request.Builtin
	result["function"] = request.Function
	result["source_sha256"] = digest([]byte(source))
	result["quote"] = quote
	result["quote_sha256"] = digest([]byte(quote))
	result["quote_byte_start"], result["quote_byte_end"] = start, end
	result["first_line"], result["last_line"] = fset.Position(target.Pos()).Line, fset.Position(target.End()).Line
	result["bare_call_positions"] = calls
	result["import_names"] = importNames
	result["proof_fingerprint"] = digest(encoded)
	result["compiler_version"] = runtime.Version()
	result["tool_tags"] = state.context.ToolTags
	result["release_tags"] = state.context.ReleaseTags
	result["limitations"] = []string{
		"Supplied frozen package census and explicit standalone build profile, not an observed application build or runtime binding.",
		"Module declaration and registered import package names only; no complete dependency graph, workspace, replacement, vendor or type resolution.",
		"Conservative local-name scan can refuse calls that a full lexical/type checker could resolve.",
		"No numeric argument validity, helper semantics, operation execution, time behavior or successful completion proved.",
	}
	return result
}

func main() {
	raw, err := io.ReadAll(io.LimitReader(os.Stdin, maxInput+1))
	var result map[string]any
	if err == nil {
		var request Request
		request, err = decode(raw)
		if err == nil {
			result = analyze(request)
		}
	}
	if err != nil {
		result = map[string]any{"status": "REFUSED", "reason": err.Error(), "source_executed": false, "owner_approved": false}
	}
	result["input_sha256"] = digest(raw)
	if binary, binaryErr := os.Executable(); binaryErr == nil {
		if data, readErr := os.ReadFile(binary); readErr == nil {
			result["producer"] = map[string]any{"version": toolVersion, "go_version": runtime.Version(), "binary_sha256": digest(data)}
		}
	}
	encoded, encodeErr := json.Marshal(result)
	if encodeErr != nil || len(encoded) > 1024*1024 {
		fmt.Println(`{"status":"REFUSED","reason":"output encoding or byte budget"}`)
		os.Exit(2)
	}
	fmt.Println(string(encoded))
	if err != nil {
		os.Exit(2)
	}
}
