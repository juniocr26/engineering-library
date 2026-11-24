"""Isolated typed-fact maintenance proposal; never bypass the default applier."""
import ast
import datetime
import difflib
import hashlib
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_default(expression):
    value = ast.literal_eval(ast.parse(expression, mode="eval").body)
    if type(value) not in (int, float) or isinstance(value, float) and not math.isfinite(value):
        raise ValueError("timeout default is not a bounded numeric literal")
    if len(expression) > 64:
        raise ValueError("default representation bound")
    return value


def sentence(value, language):
    # No units are invented. This renderer has no permission to alter other
    # facts, infer an effective deadline or broaden the external client contract.
    if language == "en":
        return f"`BalanceAdapter` declares `timeout={value!r}` and forwards `timeout` to `self._client.get`; units and an enforced deadline are not established."
    return f"`BalanceAdapter` declara `timeout={value!r}` e encaminha `timeout` a `self._client.get`; unidades e um deadline efetivo não estão estabelecidos."


def run():
    observer = load("assemble_architecture_facts_v2.py", "default_observer")
    compiler = load("prepare_architecture_claims_v2.py", "default_compiler")
    base = {name: (observer.SOURCE / name).read_bytes() for name in observer.FILES}
    original = json.loads((HERE / "architecture-deterministic-bilingual-v2.json").read_text())
    definitions = [
        {"id": "changed-numeric-default", "expression": "3.5", "documented": 2.0, "expected": "MODIFY"},
        {"id": "format-only-default", "expression": "2.00", "documented": 2.0, "expected": "NO-OP"},
        {"id": "already-correct-default", "expression": "3.5", "documented": 3.5, "expected": "NO-OP"},
        {"id": "dynamic-default", "expression": "timeout_factory()", "documented": 2.0, "expected": "INCONCLUSIVE"},
    ]
    protocol = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "cases": definitions,
                "hypothesis": "A typed default-value delta can propose a minimal bilingual revision while preserving five unaffected architectural claims.",
                "scope": "Own source counterfactuals and manual-review proposals only, not a new default planner provider or filesystem-applier bypass.",
                "automatic_applier_supported": False, "training_use_approved": False}
    with (HERE / "architecture-default-lifecycle-protocol-v1.json").open("x") as stream:
        stream.write(json.dumps(protocol, indent=2) + "\n")
    lab = ROOT / ".local-backups/documentation-intelligence-20261120/architecture-default-lifecycle-v1"
    lab.mkdir(parents=True, exist_ok=False)
    rows = []
    for definition in definitions:
        directory = lab / definition["id"]
        for version in ("before", "current"):
            (directory / version).mkdir(parents=True)
        modified = dict(base)
        modified["adapter.py"] = base["adapter.py"].replace(b"timeout: float = 2.0", ("timeout: float = " + definition["expression"]).encode())
        for name in base:
            (directory / "before" / name).write_bytes(base[name])
            (directory / "current" / name).write_bytes(modified[name])
        try:
            before_facts = compiler.derive(observer.extract(base))
            current_facts = compiler.derive(observer.extract(modified))
            fact = next(f for f in current_facts["claims"] if f["id"] == "F2")
            value = literal_default(fact["default_expression"])
            action = "NO-OP" if value == definition["documented"] else "MODIFY"
            changed_ids = [a["id"] for a,b in zip(before_facts["claims"], current_facts["claims"]) if a != b]
            failure = None
        except (ValueError, KeyError) as error:
            action, changed_ids, failure = "INCONCLUSIVE", [], str(error)
            value = None
        evidence = {"before": {name: hashlib.sha256(raw).hexdigest() for name,raw in base.items()},
                    "current": {name: hashlib.sha256(raw).hexdigest() for name,raw in modified.items()}}
        documents = {}
        for language, key in (("en", "en"), ("pt-br", "pt-br")):
            lines = ["Human preface: café, ação.\r\n"]
            for claim in original["claims"]:
                body = sentence(definition["documented"], language) if claim["claim_id"] == "F2" else claim[key]
                lines.extend([f"<!-- owned-research-claim:{claim['claim_id']}:start -->\n", body+"\n", f"<!-- owned-research-claim:{claim['claim_id']}:end -->\n"])
            lines.append("Human conclusion.\n")
            before = "".join(lines)
            candidate = before
            if action == "MODIFY":
                old = sentence(definition["documented"], language)
                if before.count(old) != 1:
                    raise ValueError("unique owned claim body required")
                candidate = before.replace(old, sentence(value, language), 1)
            before_path = directory / (language + "-before.md")
            candidate_path = directory / (language + "-review-proposal.md")
            before_path.write_bytes(before.encode())
            candidate_path.write_bytes(candidate.encode())
            untouched = [c[key] for c in original["claims"] if c["claim_id"] != "F2"]
            if not all(candidate.count(c) == before.count(c) for c in untouched):
                raise ValueError("unaffected claim changed")
            (directory / (language + ".patch")).write_bytes("".join(difflib.unified_diff(
                before.splitlines(True), candidate.splitlines(True), fromfile=language+"-before.md", tofile=language+"-review-proposal.md")).encode())
            documents[language] = {"changed": before != candidate,
                                   "five_unaffected_claims_preserved": True,
                                   "human_prefix_and_suffix_preserved": candidate.startswith(lines[0]) and candidate.endswith(lines[-1]),
                                   "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
                                   "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest()}
        rows.append({"id": definition["id"], "expected": definition["expected"], "action": action,
                     "matches": action == definition["expected"], "changed_typed_fact_ids": changed_ids,
                     "reason_if_inconclusive": failure, "source_evidence": evidence, "documents": documents,
                     "automatic_candidate_applier_used": False, "manual_owner_review_required": True})
    report = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "cases": rows,
              "correct": sum(r["matches"] for r in rows), "n": len(rows),
              "classification": "CONTROLLED_OWNED_DEVELOPMENT_NOT_INDEPENDENT_EVALUATION",
              "model_calls": 0, "active_documentation_modified": False,
              "limits": ["Default production/research planner remains unchanged for imported class modules.",
                         "These are explicitly isolated manual-review proposals, not automatically certified maintenance candidates.",
                         "Exact numeric comparison is a bounded contract check, not arbitrary semantic comprehension."]}
    with (HERE / "architecture-default-lifecycle-results-v1.json").open("x") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print([(r["id"], r["action"]) for r in rows])


if __name__ == "__main__":
    run()
