"""Execute only the reviewed public function on confined synthetic files."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def run():
    source = HERE / "public-sources/25.0.0/boltons/fileutils.py"
    raw = source.read_bytes()
    if sha(raw) != "3cf65e04eaedb63d71e5a4bfe6974194802ae203439cfd8f3f87f2807fc731fc":
        raise ValueError("reviewed source changed")
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == "rotate_file")
    expressions = {ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)}
    allowed = {"ValueError", "range", "list", "reversed", "zip", "os.path.exists", "os.path.isfile", "os.path.splitext", "kept_names.append", "os.rename", "os.remove"}
    if not expressions <= allowed:
        raise ValueError("unreviewed callable in public function")
    lab = ROOT / ".local-backups/documentation-intelligence-20261120/public-rotate-v1"
    lab.mkdir(parents=True, exist_ok=False)
    protocol = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "source_sha256": sha(raw), "selector": "rotate_file", "allowed_calls": sorted(allowed),
                "hypothesis": "The written final remove at kept_names[-1] removes the boundary backup, including the only backup when keep=1.",
                "cases": [1, 2, 5], "expected_backup_counts": [0, 1, 4],
                "safety": "Only selected AST function is compiled; full module is never imported. All filesystem calls use a confined facade over newly created synthetic directories. No external repository or user file is touched.",
                "classification": "SOURCE_INSPECTED_DEVELOPMENT_CONTROLS_NOT_INDEPENDENT_HOLDOUT"}
    (HERE / "public-rotate-protocol-v1.json").write_text(json.dumps(protocol, indent=2) + "\n")
    rows = []
    for keep in protocol["cases"]:
        directory = lab / ("keep-" + str(keep))
        directory.mkdir()
        events = []
        def confined(value):
            path = Path(value).resolve()
            if not path.is_relative_to(directory.resolve()) or path == directory.resolve():
                raise ValueError("out-of-lab path refused")
            return path
        def rename(old, new):
            old, new = confined(old), confined(new)
            events.append({"operation": "rename", "from": old.name, "to": new.name})
            os.rename(old, new)
        def remove(path):
            path = confined(path)
            events.append({"operation": "remove", "path": path.name})
            os.remove(path)
        facade = SimpleNamespace(path=SimpleNamespace(
            exists=lambda p: confined(p).exists(), isfile=lambda p: confined(p).is_file(),
            splitext=os.path.splitext), rename=rename, remove=remove)
        namespace = {"os": facade}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), namespace)
        (directory / "sample.txt").write_text("synthetic current\n")
        for i in range(1, keep+1):
            (directory / ("sample." + str(i) + ".txt")).write_text("synthetic backup " + str(i) + "\n")
        before = {p.name: sha(p.read_bytes()) for p in directory.iterdir()}
        namespace["rotate_file"](str(directory / "sample.txt"), keep=keep)
        after = {p.name: sha(p.read_bytes()) for p in directory.iterdir()}
        rows.append({"keep": keep, "before": before, "after": after, "events": events,
                     "backup_count": len(after), "current_file_absent": not (directory / "sample.txt").exists(),
                     "expected_source_trace_matches": len(after) == keep-1})
    summary = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "cases": rows,
               "source_function_executed": True, "whole_public_module_imported": False,
               "source_files_modified": False, "synthetic_files_only": True,
               "finding": "The selected revision removes backup number keep after shifting; only keep-1 backups remain in these three normal-path controls.",
               "limitations": ["No claim about all OS rename/error semantics, crash atomicity, concurrent writers or later upstream releases.",
                              "This observation does not change the frozen ADD action oracle or turn exposed source into holdout material."]}
    with (HERE / "public-rotate-observation-v1.json").open("x") as stream:
        stream.write(json.dumps(summary, indent=2) + "\n")
    print([(r["keep"], r["backup_count"]) for r in rows])


if __name__ == "__main__":
    run()
