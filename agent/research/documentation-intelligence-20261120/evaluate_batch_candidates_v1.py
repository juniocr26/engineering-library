"""Preserved multi-operation and refusal controls in owned campaign roots."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "agent/tools"))
import documentation_maintenance as maintenance
from documentation_candidates import packet_sha


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def state(base):
    return {str(f.relative_to(base)): {"sha256": sha(f.read_bytes()), "mtime_ns": f.stat().st_mtime_ns,
                                     "mode": f.stat().st_mode & 0o777}
            for folder in ("before", "current", "docs") for f in (base / folder).rglob("*") if f.is_file()}


def run():
    lab = ROOT / ".local-backups/documentation-intelligence-20261120/batch-candidates-v1"
    lab.mkdir(parents=True, exist_ok=False)
    definitions = [("independent-add-modify", "PREPARED"), ("duplicate-identity", "REFUSED"),
                   ("conflicting-operation", "REFUSED"), ("stale-source-hash", "REFUSED"),
                   ("stale-document-hash", "REFUSED"), ("human-ownership-denied", "REFUSED")]
    with (HERE / "batch-candidate-oracle-v1.json").open("x") as stream:
        stream.write(json.dumps({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                "definitions": definitions,
                                "hypothesis": "Independent ADD and MODIFY can share one bilingual document while duplicate/conflicting/stale/unowned operations fail before candidate publication.",
                                "classification": "OWNED_DEVELOPMENT_CONTROLS_NOT_HOLDOUT"}, indent=2) + "\n")
    rows = []
    for name, expected in definitions:
        base = lab / name
        for directory in ("before", "current", "docs/en", "docs/pt-br"):
            (base / directory).mkdir(parents=True)
        previous = "def first():\n    return 1\n"
        current = "def first():\n    return 2\n\ndef second():\n    return 3\n"
        (base / "before/api.py").write_text(previous)
        (base / "current/api.py").write_text(current)
        docs = {}
        claims = {"en": "first returns1.", "pt-br": "first retorna1."}
        for language, claim in claims.items():
            docs[language + "/guide.md"] = (
                "# Human title: ação\r\n".encode() +
                b"<!-- documentation-agent:claim:sample.first:start -->\n" + claim.encode() + b"\n" +
                b"<!-- documentation-agent:claim:sample.first:end -->\n" +
                b"Human middle.\n<!-- documentation-agent:anchor:sample.second -->\nHuman end.\n")
            (base / "docs" / language / "guide.md").write_bytes(docs[language + "/guide.md"])
        operations = []
        for action, symbol, old_claims, value in (("MODIFY", "first", claims, 2),
                                               ("ADD", "second", {"en": "", "pt-br": ""}, 3)):
            packet = {"id": name + "-" + symbol, "family": "owned-batch-development", "language": "python",
                      "previous_source": previous, "current_source": current, "documentation": old_claims,
                      "source_available": True, "complete_scope": True, "positive_retirement_evidence": None,
                      "logical_contract_id": "sample." + symbol, "metadata": {"managed_ownership": True}}
            operations.append({"action": action, "claim_id": "sample." + symbol,
                               "previous_file": "api.py", "source_file": "api.py", "source_packet": packet,
                               "source_packet_sha256": packet_sha(packet),
                               "documents": {lang: {"path": lang + "/guide.md", "expected_block_sha256":
                                   sha((old_claims[lang]+"\n").encode()) if action == "MODIFY" else None} for lang in claims},
                               "replacements": {"en": f"{symbol} returns{value}.\n", "pt-br": f"{symbol} retorna{value}.\n"}})
        spec = {"schema_version": 1, "scope_kind": "owned-synthetic-project", "repository": "owned-batch-candidate-lab",
                "previous_source_root": str(base / "before"), "source_root": str(base / "current"),
                "documentation_root": str(base / "docs"), "candidate_root": str(base / "candidate"),
                "previous_source_files": {"api.py": sha(previous.encode())},
                "source_files": {"api.py": sha(current.encode())},
                "documentation_files": {key: sha(raw) for key, raw in docs.items()}, "operations": operations}
        if name == "duplicate-identity":
            spec["operations"].append(copy.deepcopy(operations[0]))
        elif name == "conflicting-operation":
            conflict = copy.deepcopy(operations[0]); conflict["action"] = "REMOVE"
            spec["operations"].append(conflict)
        elif name == "stale-source-hash":
            spec["source_files"]["api.py"] = "0"*64
        elif name == "stale-document-hash":
            spec["documentation_files"]["en/guide.md"] = "0"*64
        elif name == "human-ownership-denied":
            packet = spec["operations"][0]["source_packet"]
            packet["metadata"]["human_authored"] = True
            spec["operations"][0]["source_packet_sha256"] = packet_sha(packet)
        (base / "specification.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
        before = state(base)
        try:
            result = maintenance.build(spec, prepare=True)
            observed = "PREPARED" if result["candidate_created"] else result["status"]
        except (ValueError, OSError) as error:
            observed, result = "REFUSED", {"reason": str(error), "type": type(error).__name__}
        if state(base) != before:
            raise ValueError("original bytes or metadata changed")
        human_checks = {}
        if observed == "PREPARED":
            for language in claims:
                raw = (base / "candidate/active" / language / "guide.md").read_bytes()
                human_checks[language] = all(chunk in raw for chunk in
                    ["# Human title: ação\r\n".encode(), b"Human middle.\n", b"Human end.\n"])
                if not human_checks[language]:
                    raise ValueError("human content lost")
        rows.append({"id": name, "expected": expected, "observed": observed, "matches": expected == observed,
                     "originals_preserved": True, "human_content_checks": human_checks, "result": result})
    summary = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "cases": rows,
               "correct": sum(r["matches"] for r in rows), "n": len(rows), "model_calls": 0,
               "active_documentation_modified": False, "atomic_transaction_demonstrated": False}
    with (HERE / "batch-candidate-results-v1.json").open("x") as stream:
        stream.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print([(r["id"], r["observed"]) for r in rows])


if __name__ == "__main__":
    run()
