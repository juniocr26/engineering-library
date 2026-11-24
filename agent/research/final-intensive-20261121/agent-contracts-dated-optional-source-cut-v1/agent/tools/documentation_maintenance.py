#!/usr/bin/env python3
"""Explicit isolated maintenance candidates for registered synthetic workspaces.

Default mode only validates and reports. --prepare writes a NEW candidate root,
never the source or original documentation roots. This first filesystem protocol
is deliberately restricted to owned synthetic projects, not arbitrary Git repos.
"""
import argparse
import copy
from contextlib import ExitStack
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import time

from documentation_candidates import (
    CandidateRefused, packet_sha, rewrite_owned,
)
from documentation_lifecycle import decision, observe_python, observe_go
from documentation_workspace import (
    WorkspaceRefused, census, directory, directory_flags, parent, read,
    relative_path, same_root, write_new,
)

VERSION = "0.1.4"
TOP = {
    "schema_version", "scope_kind", "repository", "previous_source_root",
    "source_root", "documentation_root", "candidate_root",
    "previous_source_files", "source_files", "documentation_files", "operations",
}
OPERATION = {
    "action", "claim_id", "previous_file", "source_file", "source_packet",
    "source_packet_sha256", "documents", "replacements",
}
SHA = re.compile(r"[0-9a-f]{64}")


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise WorkspaceRefused("duplicate JSON object key")
        result[key] = value
    return result


def read_specification(path):
    """Admit stable bounded JSON from a regular file without following links."""
    path = Path(path).absolute()
    fields = lambda value: (value.st_dev, value.st_ino, value.st_size,
                            value.st_mtime_ns, value.st_ctime_ns)
    with directory(path.parent) as descriptor:
        before = os.stat(path.name, dir_fd=descriptor, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 2 * 1024 * 1024:
            raise WorkspaceRefused("specification must be a bounded regular file")
        raw, _ = read(descriptor, path.name, 2 * 1024 * 1024)
        after = os.stat(path.name, dir_fd=descriptor, follow_symlinks=False)
        if not stat.S_ISREG(after.st_mode) or fields(before) != fields(after):
            raise WorkspaceRefused("specification path changed while reading")
    specification = json.loads(raw.decode("utf-8"), object_pairs_hook=json_object,
        parse_constant=lambda _: (_ for _ in ()).throw(WorkspaceRefused("nonfinite JSON value")))
    if not isinstance(specification, dict):
        raise WorkspaceRefused("JSON specification object required")
    pending, count = [(specification, 0)], 0
    while pending:
        value, depth = pending.pop(); count += 1
        if depth > 64 or count > 65536:
            raise WorkspaceRefused("specification JSON structure bound exceeded")
        if isinstance(value, str):
            value.encode("utf-8")
        elif isinstance(value, float) and not math.isfinite(value):
            raise WorkspaceRefused("nonfinite decoded JSON number")
        elif isinstance(value, dict):
            pending.extend((item, depth + 1) for pair in value.items() for item in pair)
        elif isinstance(value, list):
            pending.extend((item, depth + 1) for item in value)
    return specification


def inventory(mapping, extensions, minimum=0):
    if not isinstance(mapping, dict) or not minimum <= len(mapping) <= 128:
        raise WorkspaceRefused("invalid bounded file inventory")
    for name, checksum in mapping.items():
        relative_path(name)
        if Path(name).suffix not in extensions or not isinstance(checksum, str) or not SHA.fullmatch(checksum):
            raise WorkspaceRefused("invalid file extension/checksum")
    return mapping


def snapshot(descriptor, expected, maximum):
    if set(census(descriptor)) != set(expected):
        raise WorkspaceRefused("unregistered or missing workspace file")
    result = {}
    for name, checksum in expected.items():
        data, metadata = read(descriptor, name, maximum)
        if metadata["sha256"] != checksum:
            raise WorkspaceRefused("workspace checksum changed: " + name)
        result[name] = (data, metadata)
    return result


def broken_local_links(documents):
    """Check declared Markdown files; fragment semantics stay explicitly unknown."""
    import posixpath
    from urllib.parse import unquote, urlsplit
    broken, fragments = set(), []
    for name, data in documents.items():
        for target in re.findall(r"\[[^\]\r\n]*\]\(([^)\s]+)\)", data.decode("utf-8")):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.fragment:
                fragments.append({"document": name, "target": target})
            path = unquote(parsed.path)
            if not path:
                continue
            if path.endswith(".md"):
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
                if resolved not in documents or resolved.startswith(("../", "/")):
                    broken.add((name, target))
    return broken, fragments


def build(specification, prepare=False):
    if type(prepare) is not bool:
        raise WorkspaceRefused("prepare must be an explicit Boolean")
    if not isinstance(specification, dict):
        raise WorkspaceRefused("explicit synthetic-workspace object required")
    # Inventory hashes, source packets, roots and replacements must all refer
    # to the same operation-local input, including the final physical recheck
    # and the persisted preconditions. A caller edit is a new request.
    specification = copy.deepcopy(specification)
    if (
        not isinstance(specification, dict) or set(specification) != TOP
        or type(specification["schema_version"]) is not int
        or specification["schema_version"] != 1
        or specification["scope_kind"] != "owned-synthetic-project"
    ):
        raise WorkspaceRefused("unsupported explicit synthetic-workspace protocol")
    repository = specification["repository"]
    if not isinstance(repository, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,95}", repository):
        raise WorkspaceRefused("invalid synthetic project identity")
    previous_files = inventory(specification["previous_source_files"], {".py", ".go"})
    source_files = inventory(specification["source_files"], {".py", ".go"}, minimum=1)
    document_files = inventory(specification["documentation_files"], {".md"}, minimum=2)
    operations = specification["operations"]
    if not isinstance(operations, list) or not 1 <= len(operations) <= 32:
        raise WorkspaceRefused("invalid bounded operations")
    roots = {
        key: Path(specification[key])
        for key in ("previous_source_root", "source_root", "documentation_root", "candidate_root")
    }
    for root in roots.values():
        if not root.is_absolute() or ".." in root.parts:
            raise WorkspaceRefused("absolute canonical workspace roots required")
    candidate = roots["candidate_root"]
    for key in ("previous_source_root", "source_root", "documentation_root"):
        root = roots[key]
        if candidate == root or candidate in root.parents or root in candidate.parents:
            raise WorkspaceRefused("candidate overlaps an original workspace")
    relative_path(candidate.name)
    if candidate.exists() or candidate.is_symlink():
        raise WorkspaceRefused("candidate root already exists")
    started = time.monotonic()
    with ExitStack() as stack:
        old_fd = stack.enter_context(directory(roots["previous_source_root"]))
        source_fd = stack.enter_context(directory(roots["source_root"]))
        docs_fd = stack.enter_context(directory(roots["documentation_root"]))
        output_parent_fd = stack.enter_context(directory(candidate.parent))
        previous = snapshot(old_fd, previous_files, 64 * 1024)
        source = snapshot(source_fd, source_files, 64 * 1024)
        documents = snapshot(docs_fd, document_files, 2 * 1024 * 1024)
        by_document, operation_results = {}, []
        identities = set()
        for operation in operations:
            if not isinstance(operation, dict) or set(operation) != OPERATION:
                raise WorkspaceRefused("invalid operation schema")
            if operation["claim_id"] in identities:
                raise WorkspaceRefused("duplicate logical claim")
            identities.add(operation["claim_id"])
            packet = operation["source_packet"]
            if not isinstance(packet, dict) or packet_sha(packet) != operation["source_packet_sha256"]:
                raise WorkspaceRefused("source packet checksum changed")
            source_name = operation["source_file"]
            previous_name = operation["previous_file"]
            if source_name not in source or previous_name is not None and previous_name not in previous:
                raise WorkspaceRefused("operation refers to unregistered source")
            expected_suffix = {"python": ".py", "go": ".go"}.get(packet.get("language"))
            if Path(source_name).suffix != expected_suffix:
                raise WorkspaceRefused("source language/path differs")
            previous_bytes = b"" if previous_name is None else previous[previous_name][0]
            if (
                packet.get("current_source") != source[source_name][0].decode("utf-8")
                or packet.get("previous_source") != previous_bytes.decode("utf-8")
            ):
                raise WorkspaceRefused("inline observation differs from pinned source bytes")
            recommendation = decision(packet)
            if recommendation["action"] != operation["action"]:
                raise WorkspaceRefused("operation contradicts admitted source facts")
            if operation["action"] == "REMOVE":
                # Positive retirement is necessary. Any remaining definition in
                # this first closed project profile can be a rename/relocation;
                # defer rather than pretend to resolve repository semantics.
                for name, (raw, _) in source.items():
                    provider = observe_python if name.endswith(".py") else observe_go
                    if provider(raw.decode("utf-8"))["functions"]:
                        raise WorkspaceRefused("retirement has unresolved current definitions")
            paths = operation["documents"]
            if not isinstance(paths, dict) or set(paths) != {"en", "pt-br"}:
                raise WorkspaceRefused("paired documentation paths required")
            if any(not isinstance(info, dict) for info in paths.values()):
                raise WorkspaceRefused("invalid documentation path record")
            if paths["en"].get("path") == paths["pt-br"].get("path"):
                raise WorkspaceRefused("both languages cannot share a document")
            for language, info in paths.items():
                if not isinstance(info, dict) or set(info) != {"path", "expected_block_sha256"}:
                    raise WorkspaceRefused("invalid documentation operation")
                name = info["path"]
                if name not in documents or not name.startswith(language + "/"):
                    raise WorkspaceRefused("unregistered or wrong-language document")
                owned = {
                    "action": operation["action"], "claim_id": operation["claim_id"],
                    "source_packet": packet, "source_packet_sha256": operation["source_packet_sha256"],
                    "expected_file_sha256": document_files[name],
                    "expected_block_sha256": info["expected_block_sha256"],
                    "replacements": operation["replacements"],
                }
                by_document.setdefault(name, []).append((language, owned))
            operation_results.append({
                "claim_id": operation["claim_id"], "action": recommendation["action"],
                "source_file": source_name,
                "source_sha256": source_files[source_name],
                "previous_file": previous_name,
                "previous_source_sha256": digest(previous_bytes),
            })
        active = {name: data for name, (data, _) in documents.items()}
        evidence = {}
        for name, grouped in by_document.items():
            languages = {language for language, _ in grouped}
            if len(languages) != 1:
                raise WorkspaceRefused("mixed language operations on one document")
            active[name], evidence[name] = rewrite_owned(
                documents[name][0], next(iter(languages)), [op for _, op in grouped],
            )
        old_broken, old_fragments = broken_local_links({name: data for name, (data, _) in documents.items()})
        new_broken, fragments = broken_local_links(active)
        introduced = new_broken - old_broken
        if introduced:
            raise WorkspaceRefused("candidate introduces broken local Markdown links")
        changed = [name for name in active if active[name] != documents[name][0]]
        inconclusive = [
            operation["claim_id"] for operation in operation_results
            if operation["action"] == "INCONCLUSIVE"
        ]
        report = {
            "status": (
                "INCONCLUSIVE_PRESERVE_ORIGINALS" if inconclusive
                else "VALIDATED_DRY_RUN" if changed else "NO-OP"
            ),
            "version": VERSION, "repository": repository,
            "scope_kind": "owned-synthetic-project", "operations": operation_results,
            "changed_documents": changed, "candidate_created": False,
            "inconclusive_claims": inconclusive,
            "original_files_written": 0, "model_calls": 0,
            "owner_approved": False, "publication_authorized": False, "training_gold": False,
            "previous_revision": {"kind": "sha256-source-inventory", "digest": digest(canonical(previous_files))},
            "current_revision": {"kind": "sha256-source-inventory", "digest": digest(canonical(source_files))},
            "documentation_inventory_sha256": digest(canonical(document_files)),
            "document_evidence": evidence,
            "existing_broken_local_links": sorted(old_broken),
            "new_broken_local_links": sorted(introduced),
            "fragment_links_not_semantically_verified": fragments,
            "limitations": [
                "Closed owned synthetic roots only; no general Git/module/build or semantic completeness claim.",
                "Original Markdown is preserved; publication and training approval remain separate.",
                "Current registered files are rehashed before and after construction; not an atomic filesystem snapshot.",
                "Heading/fragment semantics are not certified by this Markdown-path check.",
            ],
        }

        def recheck():
            for key, fd, expected, bound in (
                ("previous_source_root", old_fd, previous_files, 64 * 1024),
                ("source_root", source_fd, source_files, 64 * 1024),
                ("documentation_root", docs_fd, document_files, 2 * 1024 * 1024),
            ):
                if not same_root(roots[key], fd):
                    raise WorkspaceRefused("original root identity changed")
                snapshot(fd, expected, bound)

        recheck()
        if prepare and changed:
            if inconclusive:
                raise WorkspaceRefused("unresolved recommendations require a separate reviewed plan")
            if not same_root(candidate.parent, output_parent_fd):
                raise WorkspaceRefused("candidate parent identity changed")
            os.mkdir(candidate.name, 0o700, dir_fd=output_parent_fd)
            candidate_fd = os.open(candidate.name, directory_flags(), dir_fd=output_parent_fd)
            try:
                preconditions = canonical({
                    "specification": specification, "report_before_write": report,
                }) + b"\n"
                write_new(candidate_fd, "preconditions.json", preconditions)
                archived = set()
                for name, (data, metadata) in documents.items():
                    checksum = metadata["sha256"]
                    if checksum not in archived:
                        write_new(candidate_fd, "history/" + checksum + ".bin", data)
                        archived.add(checksum)
                    preserved_metadata = metadata if name not in changed else None
                    write_new(candidate_fd, "active/" + name, active[name], preserved_metadata)
                history_index = canonical({
                    name: {**metadata, "archive": "history/" + metadata["sha256"] + ".bin"}
                    for name, (_, metadata) in documents.items()
                }) + b"\n"
                write_new(candidate_fd, "history-index.json", history_index)

                def verify_candidate(result_bytes=None):
                    # Original-source rechecks alone cannot certify where the
                    # candidate now lives or what was actually written there.
                    # Keep all partial evidence on refusal; never repair or
                    # overwrite a replacement directory supplied by a writer.
                    if (not same_root(candidate.parent, output_parent_fd)
                            or not same_root(candidate, candidate_fd)):
                        raise WorkspaceRefused("candidate root or parent identity changed")
                    expected_top = {"active", "history", "preconditions.json", "history-index.json"}
                    records = {"preconditions.json": preconditions,
                               "history-index.json": history_index}
                    if result_bytes is not None:
                        expected_top.add("result.json")
                        records["result.json"] = result_bytes
                    if set(os.listdir(candidate_fd)) != expected_top:
                        raise WorkspaceRefused("candidate output inventory changed")
                    for name, expected in records.items():
                        actual, _ = read(candidate_fd, name, len(expected))
                        if actual != expected:
                            raise WorkspaceRefused("candidate metadata readback differs: " + name)
                    for name, expected in (
                        ("active", {key: digest(value) for key, value in active.items()}),
                        ("history", {checksum + ".bin": checksum for checksum in archived}),
                    ):
                        child_fd = os.open(name, directory_flags(), dir_fd=candidate_fd)
                        try:
                            observed = snapshot(child_fd, expected, 2 * 1024 * 1024)
                            if name == "active":
                                for key, (_, actual) in observed.items():
                                    original = documents[key][1]
                                    mode = 0o600 if key in changed else original["mode"]
                                    if actual["mode"] != mode or (
                                        key not in changed and actual["mtime_ns"] != original["mtime_ns"]
                                    ):
                                        raise WorkspaceRefused("candidate preserved metadata differs")
                            if not same_root(candidate / name, child_fd):
                                raise WorkspaceRefused("candidate output directory identity changed")
                        finally:
                            os.close(child_fd)
                    if (not same_root(candidate.parent, output_parent_fd)
                            or not same_root(candidate, candidate_fd)):
                        raise WorkspaceRefused("candidate identity changed during readback")

                recheck()
                verify_candidate()
                report.update(status="ISOLATED_CANDIDATE_PREPARED_PENDING_REVIEW", candidate_created=True,
                              candidate_output_readback_verified=True,
                              candidate_root_identity_rechecked=True)
                report["candidate_files_sha256"] = {name: digest(data) for name, data in active.items()}
                result_bytes = canonical(report) + b"\n"
                write_new(candidate_fd, "result.json", result_bytes)
                verify_candidate(result_bytes)
                recheck()
            finally:
                os.close(candidate_fd)
        report["observed_seconds"] = time.monotonic() - started
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    try:
        specification = read_specification(args.spec)
        print(json.dumps(build(specification, args.prepare), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, OSError, UnicodeError, RecursionError) as error:
        print(json.dumps({
            "status": "REFUSED_PRESERVE_ORIGINALS",
            "error_type": type(error).__name__, "reason": str(error),
            "publication_authorized": False, "owner_approved": False,
            "partial_candidate_policy": "Any owned partial new root remains preserved; no overwrite or automatic cleanup.",
        }))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
