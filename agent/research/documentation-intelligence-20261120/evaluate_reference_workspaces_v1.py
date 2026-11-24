"""Execute frozen candidate preparation in distinct roots; preserve originals."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "agent/tools"))
import documentation_maintenance as maintenance


def state(base):
    return {str(p.relative_to(base)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                                     "mtime_ns": p.stat().st_mtime_ns, "mode": p.stat().st_mode}
            for name in ("before", "current", "docs") for p in (base / name).rglob("*") if p.is_file()}


def run(phase):
    if phase not in ("baseline", "candidate"):
        raise ValueError("fixed experiment phase required")
    oracle = json.loads((HERE / "reference-workspace-oracle-v1.json").read_text())
    rows = []
    for case in oracle["cases"]:
        path = Path(case["specification"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != case["specification_sha256"]:
            raise ValueError("oracle source specification drift")
        spec = json.loads(path.read_bytes())
        base = path.parent
        spec["candidate_root"] = str(base / (phase + "-candidate"))
        before = state(base)
        try:
            result = maintenance.build(spec, prepare=True)
            observed = "PREPARED" if result["candidate_created"] else result["status"]
        except (ValueError, OSError) as error:
            result = {"exception_type": type(error).__name__, "reason": str(error)}
            observed = "REFUSED"
        after = state(base)
        if before != after:
            raise ValueError("original bytes or metadata changed")
        rows.append({"id": case["id"], "expected": case["expected"], "observed": observed,
                     "matches": observed == case["expected"], "originals_preserved": True, "result": result})
    with (HERE / ("reference-workspace-" + phase + "-v1.json")).open("x") as stream:
        stream.write(json.dumps({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                "maintenance_version": maintenance.VERSION,
                                "correct": sum(r["matches"] for r in rows), "cases": rows,
                                "scope": "Owned synthetic physical-identity controls, not a general Git transaction or crash durability proof."}, indent=2) + "\n")
    print([(r["id"], r["observed"]) for r in rows])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("baseline", "candidate"))
    run(parser.parse_args().phase)
