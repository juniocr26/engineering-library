"""Seal later research metadata and verify a base+delta local restoration."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIVATE = ROOT / ".local-backups/documentation-intelligence-20261120"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract(archive, target):
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            name = Path(member.name)
            if not member.isfile() or name.is_absolute() or ".." in name.parts:
                raise ValueError("unsafe recovery member")
        bundle.extractall(target, filter="data")


def run():
    baseline = json.loads((HERE / "baseline.json").read_text())
    base_receipt = json.loads((HERE / "local-recovery-cut-v1.json").read_text())
    base_archive = ROOT / base_receipt["archive"]
    base_manifest_path = base_archive.parent / "file-manifest.json"
    if sha(base_archive) != base_receipt["archive_sha256"] or sha(base_manifest_path) != base_receipt["manifest_sha256"]:
        raise ValueError("sealed base identity changed")
    base = json.loads(base_manifest_path.read_text())
    out = PRIVATE / "metadata-delta-v1"
    out.mkdir(parents=True, exist_ok=False)
    paths = {ROOT / relative for relative in base}
    for directory in (HERE, PRIVATE):
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError("symlink not admitted into delta")
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if out in path.parents or (PRIVATE / "recovery-cut-v1") in path.parents:
                continue
            paths.add(path)
    latest = {}
    delta = {}
    for path in sorted(paths):
        relative = str(path.relative_to(ROOT))
        if path.name == ".env" or path.name.startswith(".env.") or not path.is_file():
            raise ValueError("missing or unapproved recovery input")
        record = {"sha256": sha(path), "bytes": path.stat().st_size, "mode": path.stat().st_mode & 0o777}
        latest[relative] = record
        if relative not in base or base[relative]["sha256"] != record["sha256"]:
            delta[relative] = record
    archive = out / "later-research.tar.gz"
    with tarfile.open(archive, "x:gz") as bundle:
        for relative in delta:
            bundle.add(ROOT / relative, arcname=relative, recursive=False)
    manifest = {"base_archive_sha256": base_receipt["archive_sha256"], "delta": delta,
                "effective": latest, "later_receipt_not_self_contained": True}
    (out / "file-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    restored = Path(tempfile.mkdtemp(prefix="el-doc-intel-20261120-base-delta-", dir="/private/tmp"))
    extract(base_archive, restored)
    for relative, record in base.items():
        if sha(restored / relative) != record["sha256"]:
            raise ValueError("base restored bytes differ before overlay")
    extract(archive, restored)
    for relative, record in latest.items():
        if sha(restored / relative) != record["sha256"]:
            raise ValueError("effective restored bytes differ")
        if sha(ROOT / relative) != record["sha256"]:
            raise ValueError("live input changed during preservation")
    code = '''import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,"agent/tools")
import documentation_lifecycle as planner
import documentation_maintenance as maintenance
root=Path.cwd()
assert Path(planner.__file__).resolve().is_relative_to(root)
oracle=json.loads(Path("agent/research/documentation-intelligence-20261120/source-reference-oracle-v1.json").read_text())
rows=[{"id":c["id"],"expected":c["expected"],"actual":planner.decision(c["packet"])["action"]} for c in oracle["cases"]]
assert all(r["expected"]==r["actual"] for r in rows)
print(json.dumps({"planner_version":planner.VERSION,"maintenance_version":maintenance.VERSION,"loaded_from":planner.__file__,"source_reference_controls":rows,"n":len(rows)}))
'''
    result = subprocess.run([sys.executable, "-c", code], cwd=restored,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                            capture_output=True, timeout=120)
    (out / "restored-controls.stdout").write_bytes(result.stdout)
    (out / "restored-controls.stderr").write_bytes(result.stderr)
    if result.returncode:
        raise ValueError("restored bounded controls failed; preserve outputs")
    current_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    index_unchanged = sha(ROOT / ".git/index") == baseline["index_sha256"]
    if current_head != baseline["head"] or not index_unchanged:
        raise ValueError("owner Git metadata changed; preserve state without claiming invariance")
    end = datetime.datetime.now(datetime.timezone.utc)
    receipt = {
        "status": "PARTIAL_CAMPAIGN_PRESERVED_NOT_TWELVE_HOUR_COMPLETE",
        "start_utc": baseline["start_utc"], "end_utc": end.isoformat(),
        "end_local": end.astimezone(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
        "elapsed_seconds": (end-datetime.datetime.fromisoformat(baseline["start_utc"])).total_seconds(),
        "target_utc": baseline["target_utc"], "twelve_hour_target_achieved": False,
        "termination_observation": "This turn closes before the requested window; no host termination or observable quota warning is asserted. No background continuation was installed.",
        "base_archive": base_receipt["archive"], "base_archive_sha256": base_receipt["archive_sha256"],
        "delta_archive": str(archive.relative_to(ROOT)), "delta_archive_sha256": sha(archive),
        "delta_bytes": archive.stat().st_size, "delta_files": len(delta), "effective_files": len(latest),
        "restored_effective_hashes_verified": len(latest), "restored_root": str(restored),
        "restored_controls": json.loads(result.stdout),
        "head": current_head, "index_unchanged": index_unchanged,
        "staged_changes": subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True),
        "git_diff_check": subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True).returncode,
        "model_calls": 1, "model_server_seconds": 287.995236589,
        "optimizer_steps": 0, "training_runs": 0, "gold_targets": 0,
        "remote_recovery": False, "cold_boot": False,
        "late_created_files": [
            {"path": str(archive.relative_to(ROOT)), "purpose": "Versioned post-V1 research delta; preserve with the base capsule."},
            {"path": str((out / "file-manifest.json").relative_to(ROOT)), "purpose": "Exact delta and effective content inventory."},
            {"path": str((out / "restored-controls.stdout").relative_to(ROOT)), "purpose": "Actual restored-source runtime and12reference-control output."},
            {"path": str((out / "restored-controls.stderr").relative_to(ROOT)), "purpose": "Raw restored-control error stream, empty on success."},
            {"path": str((out / "receipt.json").relative_to(ROOT)), "purpose": "Dated base+delta restoration and closure receipt."},
            {"path": str((HERE / "closing-receipt-v1.json").relative_to(ROOT)), "purpose": "Public campaign copy of actual end, elapsed time and late individual file inventory."},
        ],
        "limits": ["Same-host local source/artifact restoration only, not remote disaster recovery or restored model serving.",
                   "The receipt cannot contain its own hash; retain it alongside both sealed archive manifests.",
                   "All case reruns are the same frozen controls, not additional independent cases."]}
    (out / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    with (HERE / "closing-receipt-v1.json").open("x") as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: receipt[key] for key in (
        "status", "end_local", "elapsed_seconds", "delta_files", "effective_files",
        "delta_bytes", "delta_archive_sha256", "index_unchanged", "git_diff_check")}))


if __name__ == "__main__":
    run()
