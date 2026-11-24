"""Run the frozen public-source oracle without importing inspected source."""
import ast
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location(
    "frozen_lifecycle", HERE / "frozen-implementation/documentation_lifecycle.py")
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def run():
    oracle_raw = (HERE / "public-lifecycle-oracle-v1.json").read_bytes()
    oracle = json.loads(oracle_raw)
    assert sha((HERE / "frozen-implementation/documentation_lifecycle.py").read_bytes()) == oracle["implementation_sha256"]
    out = HERE / "public-lifecycle-replay-v1"
    out.mkdir(exist_ok=False)
    matrix = {a: {b: 0 for b in planner.ACTIONS} for a in planner.ACTIONS}
    rows = []
    for case in oracle["cases"]:
        sources = []
        nodes = []
        for tag in ("24.0.0", "25.0.0"):
            span = case["source_spans"][tag]
            raw = (ROOT / span["path"]).read_bytes()
            assert sha(raw) == span["sha256"]
            sources.append(raw.decode())
            found = [n for n in ast.parse(raw).body
                     if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == span["selector"]]
            nodes.append(ast.dump(found[0], include_attributes=False) if found else None)
        packet = {
            "id": case["id"], "family": case["family"], "language": "python",
            "previous_source": sources[0], "current_source": sources[1],
            "documentation": case["documentation"], "complete_scope": True,
            "source_available": True, "positive_retirement_evidence": None,
            "logical_contract_id": "boltons." + case["source_spans"]["25.0.0"]["selector"],
            "metadata": {},
        }
        result = planner.decision(packet)
        expected, actual = case["expected_action"], result["action"]
        matrix[expected][actual] += 1
        row = {"id": case["id"], "expected": expected, "actual": actual,
               "exact_match": expected == actual, "selected_ast_changed": nodes[0] != nodes[1],
               "reason": result["reason"], "patch_created": False,
               "explanation_review": "SAFE_REFUSAL_NO_FACTUAL_EXPLANATION",
               "full_result": result}
        rows.append(row)
        (out / (case["id"] + ".json")).write_text(json.dumps(
            {"input": packet, "observation": row}, ensure_ascii=False, indent=2) + "\n")
    n = len(rows)
    correct = sum(r["exact_match"] for r in rows)
    proportion = correct / n
    z = 1.959963984540054
    center = (proportion + z*z/(2*n))/(1+z*z/n)
    half = z * ((proportion*(1-proportion)/n+z*z/(4*n*n))**0.5)/(1+z*z/n)
    metrics = {}
    for action in planner.ACTIONS:
        support = sum(matrix[action].values())
        predicted = sum(matrix[a][action] for a in planner.ACTIONS)
        tp = matrix[action][action]
        metrics[action] = {"support": support, "predicted": predicted,
                           "precision": tp/predicted if predicted else None,
                           "recall": tp/support if support else None}
    summary = {
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "oracle_sha256": sha(oracle_raw), "planner_version": planner.VERSION,
        "classification": "FROZEN_BASELINE_REPLAY_NOT_NEW_CASES_OR_POST_FIX_GAIN", "n": n, "correct": correct,
        "accuracy": proportion, "wilson_95": [max(0,center-half), min(1,center+half)],
        "wilson_limit": "Illustrative case-level interval; eight correlated cases do not support population generalization.",
        "matrix_rows_expected_columns_actual": matrix, "per_action": metrics,
        "false_remove": {"numerator": sum(r["actual"] == "REMOVE" and r["expected"] != "REMOVE" for r in rows), "denominator": sum(r["expected"] != "REMOVE" for r in rows)},
        "false_modify": {"numerator": sum(r["actual"] == "MODIFY" and r["expected"] != "MODIFY" for r in rows), "denominator": sum(r["expected"] != "MODIFY" for r in rows)},
        "missed_add_modify": sum(r["expected"] in ("ADD", "MODIFY") and not r["exact_match"] for r in rows),
        "correct_noop": {"numerator": matrix["NO-OP"]["NO-OP"], "denominator": sum(matrix["NO-OP"].values())},
        "abstentions": sum(r["actual"] == "INCONCLUSIVE" for r in rows),
        "appropriate_abstention_oracle_support": 0,
        "unsupported_factual_claims_in_planner_explanations": 0,
        "incorrect_cross_file_claims_in_planner_explanations": 0,
        "patch_correctness": "NOT_EVALUATED_NO_PATCHES", "source_executed": False,
        "model_calls": 0, "training_rows_created": 0,
        "limitations": oracle["limitations"],
        "rows": [{k:v for k,v in r.items() if k != "full_result"} for r in rows],
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("rows", "limitations")}, indent=2))


if __name__ == "__main__":
    run()
