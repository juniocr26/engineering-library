// Owned static export-data reader. Never loads or executes subject library code.
package main

import (
	"encoding/json"
	"fmt"
	"go/importer"
	"go/token"
	"go/types"
	"io"
	"os"
)

type Request struct {
	Package string            `json:"package"`
	Exports map[string]string `json:"exports"`
}

func main() {
	if len(os.Args) != 2 {
		panic("explicit trusted export-map path required")
	}
	raw, err := os.ReadFile(os.Args[1])
	if err != nil {
		panic(err)
	}
	var r Request
	if err = json.Unmarshal(raw, &r); err != nil {
		panic(err)
	}
	lookup := func(name string) (io.ReadCloser, error) {
		path, ok := r.Exports[name]
		if !ok {
			return nil, fmt.Errorf("unregistered export dependency: %s", name)
		}
		return os.Open(path)
	}
	fset := token.NewFileSet()
	imp := importer.ForCompiler(fset, "gc", lookup)
	pkg, err := imp.Import(r.Package)
	if err != nil {
		panic(err)
	}
	point := pkg.Scope().Lookup("Point")
	if point == nil {
		panic("Point type missing")
	}
	ptr := types.NewPointer(point.Type())
	set := types.NewMethodSet(ptr)
	names := []string{"setCoords", "SetCoords", "Coords", "FlatCoords", "Clone", "SetSRID", "MustSetCoords"}
	rows := []map[string]any{}
	qualifier := func(p *types.Package) string { return p.Name() }
	for _, name := range names {
		selected := set.Lookup(pkg, name)
		if selected == nil {
			panic("selected method missing: " + name)
		}
		fn, ok := selected.Obj().(*types.Func)
		if !ok {
			panic("selected object is not function")
		}
		sig, ok := fn.Type().(*types.Signature)
		if !ok || sig.Recv() == nil {
			panic("method receiver unavailable")
		}
		pos := fset.Position(fn.Pos())
		rows = append(rows, map[string]any{"name": name, "declaring_receiver": types.TypeString(sig.Recv().Type(), qualifier),
			"selection_receiver": types.TypeString(selected.Recv(), qualifier), "selection_index": selected.Index(),
			"indirect": selected.Indirect(), "signature": types.TypeString(fn.Type(), qualifier), "declared_file": pos.Filename, "declared_line": pos.Line})
	}
	functions := []map[string]any{}
	for _, name := range []string{"deriveClonePoint", "deriveDeepCopy_6", "deriveDeepCopy_11", "deflate0", "inflate0"} {
		obj := pkg.Scope().Lookup(name)
		fn, ok := obj.(*types.Func)
		if !ok {
			panic("selected helper is not a declared function: " + name)
		}
		functions = append(functions, map[string]any{"name": name, "signature": types.TypeString(fn.Type(), qualifier)})
	}
	json.NewEncoder(os.Stdout).Encode(map[string]any{"status": "STATIC_METHOD_SET_OBSERVED", "package": pkg.Path(), "package_complete_export_data": pkg.Complete(),
		"point_methods": rows, "package_functions": functions, "subject_library_executed": false, "runtime_verified": false})
}
