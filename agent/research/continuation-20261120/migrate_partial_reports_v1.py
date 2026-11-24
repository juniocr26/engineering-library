"""Preserve exact history and old archive contracts before redundant-copy removal."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=ROOT/"agent/research/documentation-intelligence-20261120"
NAMES=("CAMPAIGN_REPORT.md","FILE_INVENTORY.md","FIRST_NEURAL_FINE_TUNING_READINESS.md","PROGRESS.md","RESUME.md")


def sha(path):
    digest=hashlib.sha256()
    with path.open("rb")as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def run():
    baseline=json.loads((HERE/"baseline.json").read_text())
    incoming=json.loads((HERE/"nested-report-incoming-references-v1.json").read_text())
    consumers=json.loads((HERE/"nested-report-basename-consumers-v1.json").read_text())
    if any(row["classification"]!="HISTORICAL_CLOSED_CAMPAIGN_WRITER_OR_REPLAY"for row in consumers["references"]):
        raise ValueError("unclassified current code consumer; no deletion")
    if incoming["current_non_agent_relative_markdown_links"]:
        raise ValueError("live current document link requires migration first")
    original_manifest=ROOT/"agent/recovery/manifest.json"
    original_manifest_sha=sha(original_manifest)
    manifest=json.loads(original_manifest.read_text())
    targets={str((OLD/name).relative_to(ROOT))for name in NAMES}
    if targets&{row["path"]for row in manifest["operational_files"]}:
        raise ValueError("current operational manifest depends on a selected report")
    storage=ROOT/".local-backups/continuation-20261120/report-history-v1"
    storage.mkdir(parents=True,exist_ok=False)
    records=[]
    for name in NAMES:
        source=OLD/name;relative=str(source.relative_to(ROOT));expected=baseline["tracked_identity"][relative]
        if source.is_symlink()or sha(source)!=expected["sha256"]or source.stat().st_size!=expected["bytes"]:
            raise ValueError("owner report differs from baseline; preserve without deleting")
        archived=storage/(expected["sha256"]+".md")
        with archived.open("xb")as stream:
            stream.write(source.read_bytes())
        if sha(archived)!=expected["sha256"]:
            raise ValueError("historical preservation failed")
        records.append({"original_path":relative,"archive_path":str(archived.relative_to(ROOT)),
                        "sha256":expected["sha256"],"bytes":expected["bytes"],
                        "classification":"REDUNDANT_HUMAN_FACING_PARTIAL_CAMPAIGN_REPORT",
                        "root_destination":"AI_FINE_TUNING_READINESS.md"if name.startswith("FIRST_")else
                                           "AI_TRAINING_FILE_INVENTORY.md"if name=="FILE_INVENTORY.md"else
                                           "AI_TRAINING_RESUME.md"if name=="RESUME.md"else"AI_TRAINING_CAMPAIGN_REPORT.md"})
    prior=json.loads((OLD/"closing-receipt-v1.json").read_text())
    base=ROOT/prior["base_archive"];delta=ROOT/prior["delta_archive"]
    if sha(base)!=prior["base_archive_sha256"]or sha(delta)!=prior["delta_archive_sha256"]:
        raise ValueError("prior archive chain identity differs")
    expected=json.loads((delta.parent/"file-manifest.json").read_text())["effective"]
    restored=Path(tempfile.mkdtemp(prefix="el-report-migration-old-contract-",dir="/private/tmp"))
    for archive in (base,delta):
        with tarfile.open(archive,"r:gz")as bundle:
            for member in bundle.getmembers():
                name=Path(member.name)
                if not member.isfile()or name.is_absolute()or".."in name.parts:
                    raise ValueError("unsafe historical archive member")
            bundle.extractall(restored,filter="data")
    for relative,entry in expected.items():
        if sha(restored/relative)!=entry["sha256"]:
            raise ValueError("old recovery contract cannot be independently restored")
    for row in records:
        if sha(restored/row["original_path"])!=row["sha256"]:
            raise ValueError("old report path not reproducible from sealed chain")
    # Existing candidate knowledge verification does not depend on any of the
    # five reports. Its immutable historical/report objects remain in place.
    spec=importlib.util.spec_from_file_location("report_migration_bootstrap",ROOT/"agent/recovery/bootstrap.py")
    bootstrap=importlib.util.module_from_spec(spec);spec.loader.exec_module(bootstrap)
    candidate=json.loads((OLD/"recovery-manifest-candidate-v1.json").read_text())
    bootstrap.check_knowledge(candidate);bootstrap.model_metadata(candidate)
    before_refs=[]
    dataset_manifest=json.loads((ROOT/"agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json").read_text())
    for row in dataset_manifest["files"]:
        file=ROOT/row["path"]
        if sha(file)!=row["sha256"]:
            raise ValueError("dataset file differs before migration")
        before_refs.append({"path":row["path"],"sha256":row["sha256"]})
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with(ROOT/"AI_TRAINING_CAMPAIGN_REPORT.md").open("a")as stream:
        stream.write("\n## Consolidated previous partial campaign\n\nThe previous run lasted46min36s,not12hours. Its verified source-reference changes remain in the owner baseline:planner0.3.6 and maintenance0.1.5;old development22/24,frozen public0/8,eight abstentions. One typed-fact model response was rejected;305dataset records and77FAQpairs stayed quarantined;gold0,training0. Existing suites passed312Python,262Ruby/1787assertions and101JavaScript controls. Those dated runs are not counted as new continuation executions.\n\nFive redundant nested report copies are being migrated only after exact content-addressed preservation and independent restoration of all440old archive-chain files at their original paths. Old inventories and sealed manifests remain unchanged as dated historical identities. The immutable archives can still reconstruct the old recovery contract. Current production consumers and the1964-file candidate knowledge check do not require these five live copies. The prior campaign's root/index snapshots,raw evidence and failed experiments are retained.\n")
    with(ROOT/"AI_FINE_TUNING_READINESS.md").open("a")as stream:
        stream.write("\n## Inherited readiness — verified scope and current limits\n\nNO-GO;zero of nine gates fully satisfied in the preserved prior observation.1:model/tokenizer unverified for training;2:targets/rights unapproved;3:no certified independent split;4:memory feasibility unmeasured;5:framework absent in prior interpreter discovery;6:adapter/optimizer recovery unproved;7:pilot budget proposed only;8:trainer isolation unproved;9:training evaluation/recovery incomplete. The prior observed host was AppleM1Pro/16GiB. Current refresh is queued asI1;this paragraph does not claim a new hardware or framework execution.\n\nThe official MLX source inspection and the proposed20-step/30-minute future pilot are historical preparation,not authorization. The exact earlier readiness text,including primary links,resource assumptions and owner decisions,is preserved by content hash in the report-migration receipt. No optimizer,LoRA,QLoRA,framework installation or weight download is permitted during this continuation.\n")
    with(ROOT/"AI_TRAINING_RESUME.md").open("a")as stream:
        stream.write("\n## Report-location migration\n\nThe current four canonical reports are at the repository root. Five nested human-facing reports from the preceding partial run have exact content-addressed archives recorded in `agent/research/continuation-20261120/report-migration-v1.json`. Do not rerun the old nested report writer or an old campaign seal generator;they are historical,non-reentrant recipes. To inspect the old report text,use the archive_path and sha256 from that receipt. To reconstruct old paths,use its unchanged base+delta chain in a new isolated directory. Existing datasets,checkpoints,technical documentation and historical recovery-critical Markdown remain in place.\n")
    with(ROOT/"AI_TRAINING_FILE_INVENTORY.md").open("a")as stream:
        stream.write("\n## Verified redundant report removals\n\nThe following deletions remove live redundant report copies only. Exact bytes remain at the listed historical archive paths;necessary conclusions are consolidated into the designated root reports. Existing sealed inventories retain dated original paths and can restore them unchanged.\n\n")
        for row in records:
            stream.write("- `"+row["original_path"]+"` — redundant human-facing partial-campaign report;exact historical copy `"+row["archive_path"]+"`,SHA-256`"+row["sha256"]+"`. Destination:`"+row["root_destination"]+"`.\n")
    receipt={"at":now,"status":"PRESERVATION_AND_OLD_RECOVERY_VERIFIED_BEFORE_LIVE_REMOVAL",
             "reports":records,"old_restored_root":str(restored),"old_effective_files_verified":len(expected),
             "base_archive":prior["base_archive"],"base_sha256":prior["base_archive_sha256"],
             "delta_archive":prior["delta_archive"],"delta_sha256":prior["delta_archive_sha256"],
             "incoming_reference_classification":{"current_production_consumers":0,"current_non_agent_markdown_links":0,
                 "old_inventory_references":"Historical observation,not a current runtime reader;exact old copies remain in the sealed restoration.",
                 "sealed_manifest_references":"Immutable archive restoration at all original paths verified independently of the live report files.",
                 "code_basename_references":"Five matches in the old closed campaign inventory writer only;not rerun in current continuation."},
             "operational_manifest_sha256_before":original_manifest_sha,
             "knowledge_candidate_verified_before":len(candidate["operational_files"]),"dataset_files_pinned":before_refs,
             "blocked_report":{"path":"agent/research/continuation-20261119/agentic-architecture.md",
                               "incoming_full_path_references":1495,"reason":"Operational/dataset/sealed recovery dependencies;not safely redundant. Left intact."},
             "no_recursive_deletion":True,"model_or_dataset_deletion":False}
    # This precondition receipt is durable before any removal. Original source
    # hashes are rechecked immediately; no removal is based only on a filename.
    (HERE/"report-migration-preconditions-v1.json").write_text(json.dumps(receipt,indent=2)+"\n")
    for row in records:
        source=ROOT/row["original_path"]
        if sha(source)!=row["sha256"]or sha(ROOT/row["archive_path"])!=row["sha256"]:
            raise ValueError("report changed after preservation; no further removal")
        source.unlink()
    bootstrap.check_knowledge(candidate);bootstrap.model_metadata(candidate)
    for row in before_refs:
        if sha(ROOT/row["path"])!=row["sha256"]:
            raise ValueError("dataset changed during migration")
    if sha(original_manifest)!=original_manifest_sha:
        raise ValueError("original recovery manifest changed unexpectedly")
    if sha(base)!=prior["base_archive_sha256"]or sha(delta)!=prior["delta_archive_sha256"]:
        raise ValueError("sealed recovery chain changed")
    receipt.update(status="VERIFIED_NONDESTRUCTIVE_HISTORY_MIGRATION_LIVE_REDUNDANT_COPIES_REMOVED",
                   completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   deleted_live_report_paths=[row["original_path"]for row in records],
                   knowledge_candidate_verified_after=len(candidate["operational_files"]),
                   original_recovery_manifest_unchanged=True,old_archive_contract_preserved=True,
                   root_report_policy=True,active_documentation_modified=False)
    with(HERE/"report-migration-v1.json").open("x")as stream:
        stream.write(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"removed_redundant_live_reports":len(records),"historical_hashes_preserved":len(records),
                      "old_recovery_files_verified":len(expected),"knowledge_files_verified_after":len(candidate["operational_files"]),
                      "sealed_archives_unchanged":True}))


if __name__=="__main__":
    run()
