"""Create authorized campaign controls, separate from permanent test suites."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "agent/tools"))
from documentation_candidates import packet_sha


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def run():
    lab = ROOT / ".local-backups/documentation-intelligence-20261120/reference-workspaces-v1"
    lab.mkdir(parents=True, exist_ok=False)
    definitions = [
        ("real-relocation", "old.py", "new.py", "old.py", "MODIFY", "PREPARED"),
        ("already-current", "old.py", "new.py", "new.py", "NO-OP", "NO-OP"),
        ("false-current-identity", "old.py", "ghost.py", "ghost.py", "NO-OP", "REFUSED"),
        ("false-previous-identity", "ghost-old.py", "new.py", "ghost-old.py", "MODIFY", "REFUSED"),
    ]
    cases = []
    source = b"def value():\n    return 1\n"
    for identifier, previous_path, current_path, doc_path, action, expected in definitions:
        base = lab / identifier
        for directory in ("before", "current", "docs/en", "docs/pt-br"):
            (base / directory).mkdir(parents=True, exist_ok=False)
        (base / "before/old.py").write_bytes(source)
        (base / "current/new.py").write_bytes(source)
        documents = {}
        addressed = {}
        claims = {"en": f"See {doc_path} for value.", "pt-br": f"Consulte {doc_path} para value."}
        for language, claim in claims.items():
            name = language + "/guide.md"
            body = (claim + "\n").encode()
            doc = (b"# Human preface\r\n"
                   b"<!-- documentation-agent:claim:sample.value:start -->\n" + body +
                   b"<!-- documentation-agent:claim:sample.value:end -->\n" +
                   "Human conclusion: café, ação.\n".encode())
            (base / "docs" / name).write_bytes(doc)
            documents[name] = sha(doc)
            addressed[language] = {"path": name, "expected_block_sha256": sha(body)}
        packet = {"id": identifier, "family": "source-reference-physical-identity-development", "language": "python",
                  "previous_source": source.decode(), "current_source": source.decode(), "documentation": claims,
                  "complete_scope": True, "source_available": True, "positive_retirement_evidence": None,
                  "logical_contract_id": "sample.value", "metadata": {"previous_path": previous_path,
                  "current_path": current_path, "managed_ownership": True}}
        operation = {"action": action, "claim_id": "sample.value", "previous_file": "old.py", "source_file": "new.py",
                     "source_packet": packet, "source_packet_sha256": packet_sha(packet), "documents": addressed,
                     "replacements": None if action == "NO-OP" else {
                         "en": "See new.py for value.\n", "pt-br": "Consulte new.py para value.\n"}}
        spec = {"schema_version": 1, "scope_kind": "owned-synthetic-project", "repository": "owned-source-reference-lab",
                "previous_source_root": str(base / "before"), "source_root": str(base / "current"),
                "documentation_root": str(base / "docs"), "candidate_root": str(base / "unused-candidate-root"),
                "previous_source_files": {"old.py": sha(source)}, "source_files": {"new.py": sha(source)},
                "documentation_files": documents, "operations": [operation]}
        (base / "specification.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
        cases.append({"id": identifier, "expected": expected, "specification": str(base / "specification.json"),
                      "specification_sha256": sha((base / "specification.json").read_bytes())})
    with (HERE / "reference-workspace-oracle-v1.json").open("x") as stream:
        stream.write(json.dumps({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                "cases": cases, "development_only": True,
                                "rationale": "Bind declared source-link metadata to the actual pinned operation file, not merely matching inline source bytes."}, indent=2) + "\n")
    print("Four physical-identity cases frozen before build outcomes.")


if __name__ == "__main__":
    run()
