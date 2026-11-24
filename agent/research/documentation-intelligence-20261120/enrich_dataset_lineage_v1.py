"""Resolve observation identities without inventing missing Git revisions."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_reference(ref):
    if not isinstance(ref, dict) or ref.get("immutable_snapshot") is not True:
        return None
    path = (ROOT / ref["path"]).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError("outside-root snapshot refused")
    raw = path.read_bytes()
    if sha(raw) != ref["sha256"]:
        raise ValueError("pinned snapshot changed")
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError):
        return None


def run():
    manifest = json.loads((ROOT / "agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json").read_text())
    original = {}
    for entry in manifest["files"]:
        for line in (ROOT / entry["path"]).read_text().splitlines():
            row = json.loads(line)
            original[row["id"]] = row
    dispositions = [json.loads(line) for line in (HERE / "dataset-dispositions-v2.jsonl").read_text().splitlines()]
    families = collections.Counter(r["source_repository_family"] for r in dispositions)
    rows = []
    for disposition in dispositions:
        source = original[disposition["id"]]
        identity = None
        if source.get("source_revision"):
            identity = {"kind": source.get("source_revision_kind", "declared-revision"),
                        "value": source["source_revision"], "authority": "Existing candidate metadata; not newly verified upstream Git."}
        request = source.get("request")
        if identity is None and isinstance(request, dict) and request.get("revision"):
            identity = {"kind": "operator-registry-declared-revision", "value": request["revision"],
                        "file_sha256": request.get("expected_sha256"), "physical_path": request.get("path"),
                        "authority": "Pinned request; digest length alone does not prove a Git revision."}
        input_ref = source.get("input_ref") or source.get("source_input_ref")
        evidence = read_reference(input_ref)
        if identity is None and isinstance(evidence, dict) and isinstance(evidence.get("current_source"), str):
            identity = {"kind": "content-addressed-source-pair-observation", "packet_sha256": input_ref["sha256"],
                        "previous_source_sha256": sha(evidence.get("previous_source", "").encode()),
                        "current_source_sha256": sha(evidence["current_source"].encode()),
                        "authority": "Exact synthetic or declared source packet; not an inferred repository commit."}
        if identity is None:
            ref = source.get("request_ref")
            if ref:
                identity = {"kind": "pinned-experiment-request-only", "value": ref["sha256"],
                            "authority": "Request identity is established; underlying software revision remains unresolved at this index level."}
            else:
                identity = {"kind": "UNRESOLVED", "authority": "Follow retained evidence; do not synthesize a source revision."}
        role = disposition["disposition"]
        if role == "SOURCE_REVIEWED_CANDIDATE_PENDING_OWNER":
            output = {"candidate_field": "candidate_documentation" if "candidate_documentation" in source else "answer",
                      "candidate_ref": source.get("candidate_documentation_ref") or source.get("document_ref"),
                      "proposed_action": source.get("proposed_document_action") or source.get("proposed_faq_action"),
                      "is_source_evolution_classifier_target": not source.get("not_a_source_evolution_classifier_target", False),
                      "approval": "PENDING_OWNER_NOT_GOLD"}
        elif role == "DEVELOPMENT_REFERENCE_NOT_APPROVED_TARGET":
            output = {"proposed_correct_action": source.get("proposed_correct_action"),
                      "reference_ref": source.get("reference_ref") or source.get("evaluation_ref"),
                      "scope": "Development/structural reference; no approved assistant completion."}
        else:
            output = {"positive_training_target": None, "scope": "Diagnostic or evaluation-only record; do not imitate generated output as a correct target."}
        rows.append({"id": disposition["id"], "canonical_record_id": disposition["canonical_record_id"],
                     "original_record_ref": {"path": disposition["dataset_file"], "line": disposition["physical_line"], "line_sha256": disposition["record_sha256"]},
                     "source_repository_family": disposition["source_repository_family"],
                     "source_observation_identity": identity, "lineage_group": disposition["lineage_group"],
                     "same_lineage_rows": disposition["related_group_records"],
                     "same_source_family_rows": families[disposition["source_repository_family"]],
                     "split": disposition["split"], "disposition": role,
                     "expected_output": output, "language_metadata": disposition["language"],
                     "language_metadata_limit": "For paired development/reference rows, this can name the source language rather than one completion language. Follow the pinned original task.",
                     "license_confidentiality_status": disposition["license_confidentiality_status"],
                     "license_identity_limit": "Quarantine status is not a license grant; exact upstream notices and owner clearance must be linked before training.",
                     "evidence_refs": {key: source[key] for key in ("source_evidence_ref", "input_ref", "source_input_ref", "request_ref", "evaluation_ref", "technical_review_ref") if key in source},
                     "suitable_training_now": False, "owner_approved_gold": False})
    with (HERE / "dataset-lineage-enriched-v1.jsonl").open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    summary = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "records": len(rows),
               "observation_identity_kinds": dict(collections.Counter(r["source_observation_identity"]["kind"] for r in rows)),
               "family_groups": len(families), "logical_lineage_groups": len(set(r["lineage_group"] for r in rows)),
               "split_rule": "Group by source family and shared ancestry, keeping chapter/FAQ/diagnostic descendants together; no random row split.",
               "new_gold": 0, "new_training_rows": 0,
               "limitation": "A pinned request is not a source Git commit; no metadata gap is concealed by assigning an unrelated revision."}
    with (HERE / "dataset-lineage-enriched-summary-v1.json").open("x") as stream:
        stream.write(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
