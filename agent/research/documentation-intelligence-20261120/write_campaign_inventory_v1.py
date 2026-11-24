"""Inventory only this campaign's distinct paths and the two source changes."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def purpose(path):
    name = path.name
    text = str(path.relative_to(ROOT))
    if "/public-sources/" in text:
        return "Pinned Boltons public source/license or retrieval provenance; evaluation-only."
    if "/readiness-primary-sources/" in text:
        return "Pinned MLX LM primary source/license or provenance for readiness and checkpoint inspection; never executed."
    if "/history/previous-campaign-report.md" in text:
        return "Exact historical report recovered into research history; missing root report not recreated."
    if "/frozen-implementation/" in text:
        return "Exact pre-change implementation bytes retained for comparison and recovery."
    if "/public-lifecycle-results-v1/" in text:
        return "Frozen public evaluation input/result or summary; does not become training data."
    if "/architecture-prose-v1/" in text:
        return "One local inference protocol/request/response/measurement or source factual rejection review."
    if "/candidates/boltons-file-maintenance/" in text:
        return "Isolated evaluation-only bilingual chapter with four source-backed FAQ pairs."
    if "/recovery-cut-v1/" in text:
        return "Local recovery capsule, exact member inventory, restoration receipt or restored test log."
    if text.startswith(".local-backups/"):
        if "/history/" in text:
            return "Original candidate input retained byte-for-byte as content-addressed history."
        if "/active/" in text:
            return "Isolated candidate output; this is not the published documentation catalog."
        if "-review-proposal.md" in name or name.endswith(".patch"):
            return "Manual-review typed-fact documentation proposal; unsupported by the automatic applier."
        if name in ("preconditions.json", "history-index.json", "result.json", "specification.json"):
            return "Controlled candidate preconditions, ownership/history metadata or outcome."
        return "Preserved synthetic campaign source/document/rotation state for a named isolated control."
    if name == "FIRST_NEURAL_FINE_TUNING_READINESS.md":
        return "Nine-gate NO-GO audit and bounded future pilot proposal; no authorization to train."
    if name == "authorized-request.txt":
        return "Exact owner campaign authorization and restrictions."
    if name.startswith("dataset-dispositions-v1") or name == "dataset-audit-v1.json":
        return "Rejected first audit preserved; path-context error superseded explicitly by V2."
    if name.startswith("dataset-lineage-enriched-v1"):
        return "First lineage index preserved; prose-target and missing-source classification refined in V2."
    if name.startswith("dataset-"):
        return "Per-record disposition/lineage audit or explicit amendment; original V10 bytes unchanged."
    if name.endswith(".py"):
        return "Campaign-specific isolated research/verification program: " + name.removesuffix(".py").replace("_", " ") + "."
    if name.endswith((".stdout", ".stderr")):
        return "Raw command evidence, including empty streams or failed attempts; filename identifies the execution."
    if name.startswith("checkpoint-") or name == "PROGRESS.md":
        return "Dated recoverable progress and next-safe-action record."
    if name.startswith("recovery-manifest-"):
        return "Isolated candidate recovery inventory/validation; original recovery manifest retained."
    if name.endswith(".patch"):
        return "Reviewable isolated candidate diff; never applied to the active catalog."
    if name in ("CAMPAIGN_REPORT.md", "file-inventory-v1.json", "FILE_INVENTORY.md"):
        return "Campaign results or individual per-repository file inventory."
    return "Versioned campaign evidence: " + name + "."


def row(path, reason):
    return {"path": str(path.relative_to(ROOT)), "purpose": reason,
            "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    created = []
    for directory in (HERE, ROOT / ".local-backups/documentation-intelligence-20261120"):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                created.append(row(path, purpose(path)))
    modified = [row(ROOT / "agent/tools/documentation_lifecycle.py",
                    "v0.3.6: validate declared relative paths and preserve source links already matching current identity."),
                row(ROOT / "agent/tools/documentation_maintenance.py",
                    "v0.1.5: bind declared previous/current paths to registered operation files before NO-OP or patch certification.")]
    for name in ("file-inventory-v1.json", "FILE_INVENTORY.md"):
        created.append({"path": str((HERE / name).relative_to(ROOT)),
                        "purpose": "Individual per-repository campaign file inventory; self-hash intentionally omitted.",
                        "bytes": None, "sha256": None})
    inspected = [
        ("agent/recovery/manifest.json", "Existing historical knowledge/model/runtime metadata and recovery gaps."),
        ("agent/recovery/model-bundle.json", "Original deployment weights, parts and digest identity."),
        ("agent/recovery/bootstrap.py", "Existing read-only verification functions; candidate manifest and original store checked."),
        ("backend/test/offline/test_helper.rb", "Confirm in-memory SQLite and isolated temporary catalog roots before execution."),
        ("backend/lib/documentation/command.rb", "Actual caller version and bounded generation consumer review."),
        ("backend/lib/documentation/project_command.rb", "Current coordinator version and unchanged routing."),
        ("frontend/package.json", "Existing JavaScript dependency/test environment; no UI change."),
        ("compose.research.yaml", "Existing container purpose and non-mutating validation scope."),
        ("agent/research/documentation-intelligence-20261119/recovery-handoff-v1/en.md", "Prior recovery chain, restoration distinctions and limits."),
        ("agent/research/documentation-intelligence-20261119/training-readiness-current.json", "Dated readiness baseline, not current proof."),
        ("agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json", "Current 305-record dataset closure and inherited source files."),
        ("agent/research/documentation-intelligence-20261119/javascript-written-map-evaluation.json", "Prior opt-in explanation of the two unchanged inconclusive JS cases."),
    ]
    inspected += [(str(f.relative_to(ROOT)), "Existing suite inspected and executed without changes.")
                  for f in sorted((ROOT / "agent/test").glob("*test*")) if f.is_file()]
    inspected += [(str(f.relative_to(ROOT)), "Owned synthetic source or complete bilingual chapter used for factual review.")
                  for f in sorted((ROOT / "agent/research/documentation-intelligence-20261119/owned-adapter").rglob("*"))
                  if f.is_file() and f.suffix in (".py", ".md", ".json")]
    inventory = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 "repository": "engineering-library", "root": str(ROOT),
                 "created": created, "modified": modified, "deleted": "Nenhum",
                 "inspected_only": [{"path": path, "purpose": reason} for path, reason in inspected],
                 "preexisting_worktree_changes": "Nenhum; baseline Git status clean.",
                 "preexisting_ignored_research": "Retained; new private artifacts use a distinct campaign root. Derived __pycache__ files are excluded from the evidence inventory.",
                 "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                 "external_read_only": [{"repository": "mahmoud/boltons", "status": "sem alterações", "created": "Nenhum", "modified": "Nenhum", "deleted": "Nenhum", "inspected": "Pinned remote public fileutils.py,iterutils.py,typeutils.py,LICENSE at two revisions; copies belong to engineering-library research."},
                                        {"repository": "ml-explore/mlx-lm", "status": "sem alterações", "created": "Nenhum", "modified": "Nenhum", "deleted": "Nenhum", "inspected": "Four pinned upstream source/license files; no installation or source execution."}],
                 "self_reference_limit": "Inventory files are excluded from their own hashes; late metadata belongs to the following preservation supplement."}
    (HERE / "file-inventory-v1.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Campaign file inventory — engineering-library\n\n", "Baseline: clean Git worktree; no staging or commits. Existing ignored evidence retained.\n\n"]
    for title, rows in (("Created files", created), ("Modified files", modified), ("Inspected only", inventory["inspected_only"])):
        lines.append("## " + title + "\n\n")
        for entry in rows:
            lines.append("- `" + entry["path"] + "` — " + entry["purpose"] + "\n")
        lines.append("\n")
    lines += ["## Deleted files\n\nNenhum.\n\n", "The inventory JSON and this Markdown inventory are also campaign-created reports; they are not self-hashed. See preservation supplements for later metadata.\n\n",
              "## External sources\n\n`mahmoud/boltons` — sem alterações. `ml-explore/mlx-lm` — sem alterações. Public copies and their provenance are new research artifacts in engineering-library; original repositories were not modified.\n"]
    (HERE / "FILE_INVENTORY.md").write_text("".join(lines))
    print(json.dumps({"created": len(created), "modified": len(modified), "inspected_only": len(inspected), "deleted": "Nenhum"}))


if __name__ == "__main__":
    run()
