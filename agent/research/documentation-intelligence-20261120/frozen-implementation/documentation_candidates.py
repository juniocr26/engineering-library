#!/usr/bin/env python3
"""Owned-block candidate construction; never writes to original documentation."""
import copy
import hashlib
import json
import re

from documentation_lifecycle import decision

VERSION = "0.1.2"
MAX_DOCUMENT = 2 * 1024 * 1024
MAX_OPERATIONS = 32
IDENTIFIER = r"[a-z][a-z0-9_.-]{0,95}"
MARKERS = re.compile(
    (r"(?m)^<!-- documentation-agent:claim:(" + IDENTIFIER
     + r"):(start|end) -->(\r?\n|\Z)").encode()
)


class CandidateRefused(ValueError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def packet_sha(packet):
    return sha(json.dumps(
        packet, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode())


def blocks(document):
    result, opened = {}, None
    for marker in MARKERS.finditer(document):
        identifier = marker[1].decode("ascii")
        if marker[2] == b"start":
            if opened is not None or identifier in result:
                raise CandidateRefused("nested or duplicate claim markers")
            opened = (identifier, marker)
        else:
            if opened is None or opened[0] != identifier:
                raise CandidateRefused("unmatched claim marker")
            result[identifier] = (opened[1], marker)
            opened = None
    if opened is not None:
        raise CandidateRefused("unclosed claim marker")
    return result


def claim_text(body):
    if not isinstance(body, bytes):
        raise CandidateRefused("claim body is not bytes")
    text = body.decode("utf-8")
    if not text.endswith("\n") or "\x00" in text:
        raise CandidateRefused("claim body must end with LF and contain no NUL")
    return text[:-2] if text.endswith("\r\n") else text[:-1]


def validate_operation(operation):
    required = {
        "action", "claim_id", "source_packet", "source_packet_sha256",
        "expected_file_sha256", "expected_block_sha256", "replacements",
    }
    if not isinstance(operation, dict) or set(operation) != required:
        raise CandidateRefused("invalid operation schema")
    identifier = operation["claim_id"]
    if not isinstance(identifier, str) or not re.fullmatch(IDENTIFIER, identifier):
        raise CandidateRefused("invalid claim identity")
    packet = operation["source_packet"]
    if not isinstance(packet, dict):
        raise CandidateRefused("invalid source packet")
    if packet_sha(packet) != operation["source_packet_sha256"]:
        raise CandidateRefused("source packet checksum changed")
    if packet.get("logical_contract_id") != identifier:
        raise CandidateRefused("source and documentation identities differ")
    recommendation = decision(packet)
    if recommendation["action"] != operation["action"]:
        raise CandidateRefused("operation contradicts current source recommendation")
    if operation["action"] in ("NO-OP", "INCONCLUSIVE"):
        if operation["replacements"] is not None:
            raise CandidateRefused("nonchanging recommendation carries replacement")
        return recommendation
    metadata = packet["metadata"]
    if metadata.get("managed_ownership") is not True or metadata.get("human_authored"):
        raise CandidateRefused("human alignment required; markers alone grant no ownership")
    replacements = operation["replacements"]
    if operation["action"] == "REMOVE":
        if replacements is not None:
            raise CandidateRefused("retirement cannot carry replacement prose")
    else:
        if not isinstance(replacements, dict) or set(replacements) != {"en", "pt-br"}:
            raise CandidateRefused("paired replacement text required")
        for body in replacements.values():
            if not isinstance(body, str) or "<!-- documentation-agent:" in body:
                raise CandidateRefused("invalid or marker-bearing replacement")
            if len(body.encode("utf-8")) > 64 * 1024:
                raise CandidateRefused("replacement exceeds byte bound")
            claim_text(body.encode("utf-8"))
        current_claim = copy.deepcopy(packet)
        current_claim["documentation"] = {
            language: claim_text(body.encode("utf-8"))
            for language, body in replacements.items()
        }
        if decision(current_claim)["action"] != "NO-OP":
            raise CandidateRefused("replacement claims are not supported in both languages")
    return recommendation


def rewrite_owned(document, language, operations):
    """Return isolated candidate bytes and preservation evidence, without I/O."""
    if (
        not isinstance(document, bytes) or len(document) > MAX_DOCUMENT
        or language not in ("en", "pt-br")
    ):
        raise CandidateRefused("invalid bounded document/language")
    document.decode("utf-8")
    if b"\x00" in document:
        raise CandidateRefused("NUL in documentation")
    if not isinstance(operations, list) or len(operations) > MAX_OPERATIONS:
        raise CandidateRefused("invalid bounded operation list")
    # Do not re-read caller-owned dictionaries after validating their source
    # packet, action and paired replacement claims. Source strings/bytes are
    # immutable; the nested operation containers must be operation-local too.
    operations = copy.deepcopy(operations)
    owned = blocks(document)
    identifiers, edits, trace = set(), [], []
    for operation in operations:
        recommendation = validate_operation(operation)
        identifier, action = operation["claim_id"], recommendation["action"]
        if identifier in identifiers:
            raise CandidateRefused("duplicate claim operation")
        identifiers.add(identifier)
        if operation["expected_file_sha256"] != sha(document):
            raise CandidateRefused("whole documentation file changed")
        if action == "INCONCLUSIVE":
            trace.append({"claim_id": identifier, "action": action, "changed": False})
            continue
        if action == "NO-OP":
            # A valid inline claim does not establish that the document already
            # contains it. Bind nonchanging certification to the same physical
            # block and checksum used for MODIFY/REMOVE, without adopting or
            # writing human content. Missing addresses require a reviewed plan.
            if identifier not in owned:
                raise CandidateRefused("NO-OP requires an addressed claim block")
            start, end = owned[identifier]
            body = document[start.end():end.start()]
            if operation["expected_block_sha256"] != sha(body):
                raise CandidateRefused("NO-OP owned claim body changed")
            if claim_text(body) != operation["source_packet"]["documentation"][language]:
                raise CandidateRefused("NO-OP source recommendation addresses different documentation")
            trace.append({"claim_id": identifier, "action": action, "changed": False})
            continue
        if action == "ADD":
            if identifier in owned or operation["expected_block_sha256"] is not None:
                raise CandidateRefused("ADD collides with an existing claim")
            anchor = re.compile(
                (r"(?m)^<!-- documentation-agent:anchor:"
                 + re.escape(identifier) + r" -->(\r?\n|\Z)").encode()
            )
            matches = list(anchor.finditer(document))
            if len(matches) != 1:
                raise CandidateRefused("ADD requires one explicit owned insertion anchor")
            marker = matches[0]
            eol = marker[1] or b"\n"
            replacement = operation["replacements"][language].encode("utf-8")
            block = (
                b"<!-- documentation-agent:claim:" + identifier.encode() + b":start -->" + eol
                + replacement
                + b"<!-- documentation-agent:claim:" + identifier.encode() + b":end -->" + eol
            )
            edits.append((marker.start(), marker.start(), block))
        else:
            if identifier not in owned:
                raise CandidateRefused("claim ownership markers missing")
            start, end = owned[identifier]
            body = document[start.end():end.start()]
            if operation["expected_block_sha256"] != sha(body):
                raise CandidateRefused("owned claim body changed")
            expected_text = operation["source_packet"]["documentation"][language]
            if claim_text(body) != expected_text:
                raise CandidateRefused("source recommendation addresses different documentation")
            if action == "REMOVE":
                edits.append((start.start(), end.end(), b""))
            elif action == "MODIFY":
                edits.append((
                    start.end(), end.start(),
                    operation["replacements"][language].encode("utf-8"),
                ))
            else:
                raise CandidateRefused("unknown mutating action")
        trace.append({
            "claim_id": identifier, "action": action, "changed": True,
            "technical_recommendation": recommendation["action"],
        })
    edits.sort(key=lambda item: (item[0], item[1]))
    previous = 0
    for start, end, _ in edits:
        if start < previous:
            raise CandidateRefused("overlapping managed edits")
        previous = end
    result, cursor, outside = [], 0, []
    for start, end, replacement in edits:
        original = document[cursor:start]
        result.extend((original, replacement))
        outside.append(original)
        cursor = end
    result.append(document[cursor:])
    outside.append(document[cursor:])
    candidate = b"".join(result)
    if len(candidate) > MAX_DOCUMENT:
        raise CandidateRefused("candidate exceeds document bound")
    blocks(candidate)
    return candidate, {
        "version": VERSION,
        "before_sha256": sha(document), "candidate_sha256": sha(candidate),
        "changed": candidate != document,
        "human_outside_managed_ranges_sha256": sha(b"".join(outside)),
        "history_required": candidate != document,
        "operations": trace, "original_files_written": 0,
        "owner_approved": False, "training_gold": False,
        "limitations": [
            "In-memory candidate construction only; no active documentation is changed.",
            "Caller must bind current source/document bytes to an approved frozen registry.",
            "Link/navigation and live-source rechecks are separate preconditions before filesystem publication.",
        ],
    }
