// Research-only explicit-context MatchFile observer, not a package/type resolver.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"go/build"
	"go/parser"
	"go/token"
	"io"
	"os"
	"path"
	"regexp"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

type Context struct {
	GOOS        string   `json:"goos"`
	GOARCH      string   `json:"goarch"`
	Compiler    string   `json:"compiler"`
	Cgo         bool     `json:"cgo_enabled"`
	BuildTags   []string `json:"build_tags"`
	ToolTags    []string `json:"tool_tags"`
	ReleaseTags []string `json:"release_tags"`
}
type File struct {
	Path   string `json:"path"`
	Source string `json:"source"`
	SHA    string `json:"sha256"`
}
type Request struct {
	Context Context `json:"context"`
	Files   []File  `json:"files"`
}

func sha(raw []byte) string { sum := sha256.Sum256(raw); return hex.EncodeToString(sum[:]) }
func duplicates(raw []byte) error {
	d := json.NewDecoder(bytes.NewReader(raw))
	d.UseNumber()
	count := 0
	var value func(int) error
	value = func(depth int) error {
		count++
		if depth > 32 || count > 100000 {
			return fmt.Errorf("JSON structural bound")
		}
		t, e := d.Token()
		if e != nil {
			return e
		}
		delim, ok := t.(json.Delim)
		if !ok {
			return nil
		}
		switch delim {
		case '{':
			seen := map[string]bool{}
			for d.More() {
				k, e := d.Token()
				if e != nil {
					return e
				}
				key, ok := k.(string)
				if !ok || seen[key] {
					return fmt.Errorf("duplicate or invalid JSON key")
				}
				seen[key] = true
				if e = value(depth + 1); e != nil {
					return e
				}
			}
		case '[':
			for d.More() {
				if e = value(depth + 1); e != nil {
					return e
				}
			}
		default:
			return fmt.Errorf("unexpected JSON delimiter")
		}
		_, e = d.Token()
		return e
	}
	if e := value(0); e != nil {
		return e
	}
	if _, e := d.Token(); e != io.EOF {
		return fmt.Errorf("extra JSON content")
	}
	return nil
}
func inspect(raw []byte) (map[string]any, error) {
	if len(raw) > 12*1024*1024 || !utf8.Valid(raw) {
		return nil, fmt.Errorf("wire byte/UTF8 bound")
	}
	if e := duplicates(raw); e != nil {
		return nil, e
	}
	var top map[string]json.RawMessage
	if e := json.Unmarshal(raw, &top); e != nil {
		return nil, e
	}
	if len(top) != 2 || top["context"] == nil || top["files"] == nil {
		return nil, fmt.Errorf("closed request fields required")
	}
	var fields map[string]json.RawMessage
	if e := json.Unmarshal(top["context"], &fields); e != nil {
		return nil, e
	}
	for _, key := range []string{"goos", "goarch", "compiler", "cgo_enabled", "build_tags", "tool_tags", "release_tags"} {
		if fields[key] == nil {
			return nil, fmt.Errorf("explicit context field missing: %s", key)
		}
	}
	if len(fields) != 7 {
		return nil, fmt.Errorf("unknown context field")
	}
	var r Request
	d := json.NewDecoder(bytes.NewReader(raw))
	d.DisallowUnknownFields()
	if e := d.Decode(&r); e != nil {
		return nil, e
	}
	allowedOS := map[string]bool{"linux": true, "darwin": true, "windows": true, "freebsd": true, "plan9": true, "js": true, "wasip1": true}
	allowedArch := map[string]bool{"arm64": true, "amd64": true, "386": true, "wasm": true}
	if !allowedOS[r.Context.GOOS] || !allowedArch[r.Context.GOARCH] || r.Context.Compiler != "gc" {
		return nil, fmt.Errorf("explicit target outside research profile")
	}
	validTag := regexp.MustCompile(`^[A-Za-z0-9_.]{1,64}$`)
	for _, tags := range [][]string{r.Context.BuildTags, r.Context.ToolTags} {
		if len(tags) > 32 {
			return nil, fmt.Errorf("tag count bound")
		}
		seen := map[string]bool{}
		for _, tag := range tags {
			if !validTag.MatchString(tag) || seen[tag] {
				return nil, fmt.Errorf("invalid or duplicate context tag")
			}
			seen[tag] = true
		}
	}
	if len(r.Context.ReleaseTags) < 1 || len(r.Context.ReleaseTags) > len(build.Default.ReleaseTags) {
		return nil, fmt.Errorf("release tag bound exceeds observer toolchain")
	}
	for i, tag := range r.Context.ReleaseTags {
		if tag != "go1."+strconv.Itoa(i+1) {
			return nil, fmt.Errorf("release tags must be explicit contiguous supported versions")
		}
	}
	if len(r.Files) < 1 || len(r.Files) > 256 {
		return nil, fmt.Errorf("source file count bound")
	}
	files := map[string]File{}
	total := 0
	virtual := map[string]string{}
	for _, f := range r.Files {
		total += len(f.Source)
		if len(f.Source) > 262144 || total > 8*1024*1024 || !utf8.ValidString(f.Source) || strings.ContainsRune(f.Source, 0) {
			return nil, fmt.Errorf("source content bound")
		}
		if f.Path == "" || len(f.Path) > 300 || path.IsAbs(f.Path) || path.Clean(f.Path) != f.Path || f.Path == ".." || strings.HasPrefix(f.Path, "../") || strings.ContainsAny(f.Path, "\\\x00\r\n") || !strings.HasSuffix(f.Path, ".go") {
			return nil, fmt.Errorf("canonical relative Go source path required")
		}
		if _, exists := files[f.Path]; exists {
			return nil, fmt.Errorf("duplicate source path")
		}
		if sha([]byte(f.Source)) != f.SHA {
			return nil, fmt.Errorf("source hash mismatch")
		}
		files[f.Path] = f
		virtual[path.Join("/closed-source", f.Path)] = f.Source
	}
	ctxt := build.Context{GOOS: r.Context.GOOS, GOARCH: r.Context.GOARCH, Compiler: r.Context.Compiler, CgoEnabled: r.Context.Cgo,
		BuildTags: r.Context.BuildTags, ToolTags: r.Context.ToolTags, ReleaseTags: r.Context.ReleaseTags, UseAllFiles: false, JoinPath: path.Join}
	opens := []string{}
	ctxt.OpenFile = func(name string) (io.ReadCloser, error) {
		source, ok := virtual[name]
		if !ok {
			return nil, fmt.Errorf("unregistered virtual read denied")
		}
		opens = append(opens, name)
		return io.NopCloser(strings.NewReader(source)), nil
	}
	names := []string{}
	for name := range files {
		names = append(names, name)
	}
	sort.Strings(names)
	rows := []map[string]any{}
	matched := []string{}
	cgoPaths := []string{}
	packages := map[string]map[string]bool{}
	for _, name := range names {
		f := files[name]
		ok, e := ctxt.MatchFile(path.Join("/closed-source", path.Dir(name)), path.Base(name))
		if e != nil {
			return nil, fmt.Errorf("MatchFile %s: %w", name, e)
		}
		row := map[string]any{"path": name, "sha256": f.SHA, "constraint_match": ok, "source_executed": false}
		if ok {
			matched = append(matched, name)
			tree, e := parser.ParseFile(token.NewFileSet(), name, f.Source, parser.ImportsOnly|parser.SkipObjectResolution)
			if e != nil {
				return nil, fmt.Errorf("selected source import header %s: %w", name, e)
			}
			row["package_clause"] = tree.Name.Name
			hasC := false
			for _, item := range tree.Imports {
				if item.Path.Value == `"C"` {
					hasC = true
				}
			}
			row["import_C_requires_further_selection"] = hasC
			test := strings.HasSuffix(name, "_test.go")
			row["test_file_not_default_library"] = test
			row["library_census_input_candidate"] = !hasC && !test
			if hasC {
				cgoPaths = append(cgoPaths, name)
			}
			if !hasC && !test {
				dir := path.Dir(name)
				if packages[dir] == nil {
					packages[dir] = map[string]bool{}
				}
				packages[dir][tree.Name.Name] = true
			}
		}
		rows = append(rows, row)
	}
	ambiguous := []string{}
	for dir, names := range packages {
		if len(names) > 1 {
			ambiguous = append(ambiguous, dir)
		}
	}
	sort.Strings(ambiguous)
	return map[string]any{"status": "CONSTRAINT_MATCH_OBSERVATIONS", "go_version": runtime.Version(), "context": r.Context, "files": rows, "matched_paths": matched,
		"virtual_source_reads": opens, "matched_import_C_paths": cgoPaths, "ambiguous_library_package_directories": ambiguous,
		"source_executed": false, "source_compiled": false, "module_or_dependency_loading": false, "package_completeness_verified": false, "runtime_name_binding_verified": false,
		"limitations": []string{"MatchFile is explicit build-condition matching, not complete Go command package selection.", "Import C, test package roles, unsupplied/generated files, modules, embedding, type checking and runtime binding remain separate evidence gates."}}, nil
}
func main() {
	raw, e := io.ReadAll(io.LimitReader(os.Stdin, 12*1024*1024+1))
	var result map[string]any
	if e == nil {
		result, e = inspect(raw)
	}
	if e != nil {
		json.NewEncoder(os.Stdout).Encode(map[string]any{"status": "INCONCLUSIVE", "reason": e.Error(), "source_executed": false})
		return
	}
	json.NewEncoder(os.Stdout).Encode(result)
}
