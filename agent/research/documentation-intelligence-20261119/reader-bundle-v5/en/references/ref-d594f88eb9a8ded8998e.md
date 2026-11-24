# Evidence record: sqlx-map-argument-binding / source-excerpts.json

This is a dated raw research artifact. Findings and rejected model outputs retain their recorded status. Reading the record does not approve publication or training.

SHA-256: `d594f88eb9a8ded8998e0d32bc6c8b85e38201055c42c4fc046974cbfb770074`. Original bytes: `2019`.

Original path: `agent/research/documentation-intelligence-20261119/chapters/sqlx-map-argument-binding/source-excerpts.json`.

<!-- reading-section:reference:d594f88eb9a8ded8998e:consumers -->
## Referenced by

- [Map argument binding: presence, order and the prefix returned on error](../chapters/sqlx-map-argument-binding.md)

<!-- reading-section:reference:d594f88eb9a8ded8998e:artifact -->
## Original artifact

The fenced contents reproduce the exact UTF-8 artifact; a display-only terminal newline is added if the original lacks one.

<!-- artifact-body:d594f88eb9a8ded8998e0d32bc6c8b85e38201055c42c4fc046974cbfb770074:start -->
````json
{
  "repository": "sqlx",
  "revision": "41dac167fdad5e3fd81d66cafba0951dc6823a30",
  "path": "named.go",
  "full_file_sha256": "21d5c630ab4b4a5749ec06bada1032c25820379114624733012a8a70e04213d0",
  "first_line": 197,
  "last_line": 208,
  "quote": "func bindMapArgs(names []string, arg map[string]interface{}) ([]interface{}, error) {\n\targlist := make([]interface{}, 0, len(names))\n\n\tfor _, name := range names {\n\t\tval, ok := arg[name]\n\t\tif !ok {\n\t\t\treturn arglist, fmt.Errorf(\"could not find name %s in %#v\", name, arg)\n\t\t}\n\t\targlist = append(arglist, val)\n\t}\n\treturn arglist, nil\n}\n",
  "source_program_executed": false,
  "expanded_source_files": [
    {
      "path": "named.go",
      "full_file_sha256": "21d5c630ab4b4a5749ec06bada1032c25820379114624733012a8a70e04213d0",
      "ranges": [
        {
          "first_line": 162,
          "last_line": 167,
          "quote": "\nfunc bindAnyArgs(names []string, arg interface{}, m *reflectx.Mapper) ([]interface{}, error) {\n\tif maparg, ok := convertMapStringInterface(arg); ok {\n\t\treturn bindMapArgs(names, maparg)\n\t}\n\treturn bindArgs(names, arg, m)\n"
        },
        {
          "first_line": 210,
          "last_line": 229,
          "quote": "// bindStruct binds a named parameter query with fields from a struct argument.\n// The rules for binding field names to parameter names follow the same\n// conventions as for StructScan, including obeying the `db` struct tags.\nfunc bindStruct(bindType int, query string, arg interface{}, m *reflectx.Mapper) (string, []interface{}, error) {\n\tbound, names, err := compileNamedQuery([]byte(query), bindType)\n\tif err != nil {\n\t\treturn \"\", []interface{}{}, err\n\t}\n\n\targlist, err := bindAnyArgs(names, arg, m)\n\tif err != nil {\n\t\treturn \"\", []interface{}{}, err\n\t}\n\n\treturn bound, arglist, nil\n}\n\nvar valuesReg = regexp.MustCompile(`\\)\\s*(?i)VALUES\\s*\\(`)\n\nfunc findMatchingClosingBracketIndex(s string) int {\n"
        }
      ]
    }
  ]
}
````
<!-- artifact-body:d594f88eb9a8ded8998e0d32bc6c8b85e38201055c42c4fc046974cbfb770074:end -->
