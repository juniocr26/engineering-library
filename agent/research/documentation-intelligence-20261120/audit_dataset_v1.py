"""Append a per-record disposition without modifying or promoting V10 data."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST = ROOT / "agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def references(value):
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            yield value
        for child in value.values():
            yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)


def run():
    raw_manifest = MANIFEST.read_bytes()
    manifest = json.loads(raw_manifest)
    records = []
    checked = {}
    failures = []
    category_counts = collections.Counter()
    family_counts = collections.Counter()
    lineage_counts = collections.Counter()
    rows_without_top_level_revision = 0
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        raw = path.read_bytes()
        if sha(raw) != entry["sha256"]:
            raise ValueError("dataset file checksum mismatch: " + entry["path"])
        lines = raw.splitlines()
        if len(lines) != entry["records"]:
            raise ValueError("record count mismatch")
        for number, line in enumerate(lines, 1):
            row = json.loads(line)
            category = row["category"]
            category_counts[category] += 1
            family_counts[row["source_family"]] += 1
            lineage_counts[row["lineage_group"]] += 1
            revision = row.get("source_revision")
            rows_without_top_level_revision += revision is None
            refs = list(references(row))
            ref_results = []
            for ref in refs:
                refpath = Path(ref["path"])
                absolute = (ROOT / refpath).resolve()
                if not absolute.is_relative_to(ROOT.resolve()):
                    failures.append({"id": row["id"], "path": ref["path"], "reason": "outside approved repository; not read"})
                    continue
                key = (str(refpath), ref["sha256"])
                if key not in checked:
                    content = absolute.read_bytes() if absolute.is_file() else None
                    checked[key] = content is not None and sha(content) == ref["sha256"]
                ref_results.append({"path": ref["path"], "sha256": ref["sha256"], "matches": checked[key]})
                if not checked[key]:
                    failures.append({"id": row["id"], "path": ref["path"], "reason": "missing or checksum mismatch"})
            if any(row.get(k) is not False for k in ("owner_approved", "training_gold", "training_use_approved")):
                raise ValueError("unexpected authority flag: " + row["id"])
            if "DIAGNOSTIC" in category:
                role = "REJECTED_OR_DIAGNOSTIC_OUTPUT_NOT_TARGET"
                target = "None: model output is evidence to review, never a positive completion."
            elif "TEST_ONLY" in category:
                role = "EVALUATION_ONLY_STRUCTURAL_NOT_NEURAL_HOLDOUT"
                target = "Structured retrieval observation; not a prose target."
            elif "DEV_REFERENCE" in category or "STRUCTURAL" in category:
                role = "DEVELOPMENT_REFERENCE_NOT_APPROVED_TARGET"
                target = "Action reference" if "DEV_REFERENCE" in category else "Structured syntax evidence"
            else:
                role = "SOURCE_REVIEWED_CANDIDATE_PENDING_OWNER"
                target = "Candidate chapter" if "CHAPTER" in category or "DOCUMENT" in category else "Candidate FAQ answer"
            records.append({
                "id": row["id"], "canonical_record_id": row.get("canonical_record_id"),
                "dataset_file": entry["path"], "physical_line": number, "record_sha256": sha(line),
                "source_repository_family": row["source_family"], "source_revision": revision,
                "revision_status": "TOP_LEVEL_PRESENT" if revision else "FOLLOW_PINNED_REFERENCES_NOT_AN_INFERRED_GIT_REVISION",
                "language": row.get("language"), "category": category,
                "input_task": "Source revision and documentation action" if "DEV_REFERENCE" in category else
                              "Source-backed bilingual chapter/FAQ" if role.startswith("SOURCE_REVIEWED") else
                              "Historical generation or structural retrieval diagnostic",
                "expected_output_role": target, "disposition": role,
                "license_confidentiality_status": row.get("license_confidentiality_status"),
                "license_training_approval": False, "review_status": row.get("original_technical_status") or row.get("reference_status") or row.get("source_review"),
                "technical_review_ref": row.get("technical_review_ref"),
                "lineage_group": row["lineage_group"], "split": row["split"],
                "related_group_records": None, "reference_checks": ref_results,
                "suitable_for_supervised_training_now": False, "owner_approved_gold": False,
                "reason_not_training_ready": "Approval and source/license validation are not established; related chapters/FAQs/diagnostics must remain grouped.",
            })
    for row in records:
        row["related_group_records"] = lineage_counts[row["lineage_group"]]
    out = HERE / "dataset-dispositions-v1.jsonl"
    with out.open("x") as stream:
        for row in records:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    summary = {
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "manifest": str(MANIFEST.relative_to(ROOT)), "manifest_sha256": sha(raw_manifest),
        "records": len(records), "original_files": len(manifest["files"]),
        "dispositions": dict(collections.Counter(r["disposition"] for r in records)),
        "categories": dict(category_counts), "families": dict(family_counts),
        "lineage_groups": dict(lineage_counts), "rows_without_top_level_revision": rows_without_top_level_revision,
        "unique_path_hash_reference_checks": len(checked), "reference_failures": failures,
        "authority_flags_checked": len(records)*3, "approved_gold": 0,
        "suitable_training_records_now": 0, "independent_neural_holdout": 0,
        "new_original_dataset_records": 0, "evaluation_family_boltons_added_to_training": False,
        "limitations": [
            "An integrity/reference audit is not an independent factual or legal review of every completion.",
            "Source-family and lineage identifiers are inherited assertions; they need ancestry review before splitting.",
            "Missing top-level revision is a curation gap, not proof of missing pinned evidence.",
            "Source reviewed candidates can still contain errors; zero automatic gold promotion.",
        ],
    }
    with (HERE / "dataset-audit-v1.json").open("x") as stream:
        stream.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("families", "lineage_groups", "categories", "limitations")}, indent=2))


if __name__ == "__main__":
    run()
