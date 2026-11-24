"""Bounded in-memory bilingual FAQ maintenance for operator-owned fixtures.

Deduplication uses explicit question identity, not free-form semantic matching.
No source execution, publication, original-file writes or default agent routing.
"""
import copy
import difflib
import hashlib
import re

from documentation_candidates import MAX_DOCUMENT, blocks, claim_text
from documentation_lifecycle import decision, Unsupported

VERSION = "0.1.1"
KIND = "written-integer-return"
LANGUAGES = ("en", "pt-br")
INVENTORY_KEYS = {"logical_contract_id", "question_kind", "block_id", "managed_ownership", "human_authored"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def render(symbol, value):
    if not isinstance(symbol, str) or not re.fullmatch(r"[A-Za-z_]\w*", symbol):
        raise Unsupported("unsupported FAQ symbol")
    if type(value) is not int or not -(2**31) <= value < 2**31:
        raise Unsupported("unsupported FAQ integer")
    return {
        "en": f"FAQ: Does {symbol} return{value}? Yes.",
        "pt-br": f"FAQ: {symbol} retorna{value}? Sim.",
    }


def maintain_faq(*, documents, expected_sha256, inventory, complete_inventory, packet):
    """Return isolated candidates and original history bytes, or exact originals.

    Registry completeness and ownership are trusted operator declarations within
    the synthetic fixture scope. They are not inferred from marker presence.
    """
    result = {
        "profile": "owned-faq-written-integer-return-v1", "version": VERSION, "action": "INCONCLUSIVE",
        "reason": "", "changed": False, "owner_approved": False,
        "publication_authorized": False, "training_gold": False,
        "source_executed": False, "model_calls": 0, "original_files_written": 0,
        "history_required": False, "source_evidence": {},
        "limitations": [
            "One explicit written-integer-return question kind in complete operator-declared fixture inventories.",
            "Registry identities detect registered duplicates; arbitrary prose and paraphrases are not automatically indexed.",
            "A FAQ ADD can document an existing feature and does not imply a newly introduced source feature.",
            "Changing results are memory-only candidates and require history preservation before any filesystem application.",
        ],
    }
    if isinstance(documents, dict):
        result["candidates"] = dict(documents)

    def finish(action, reason):
        result["action"], result["reason"] = action, reason
        return result

    try:
        documents = copy.deepcopy(documents)
        expected_sha256 = copy.deepcopy(expected_sha256)
        inventory = copy.deepcopy(inventory)
        packet = copy.deepcopy(packet)
        if isinstance(documents, dict):
            result["candidates"] = dict(documents)
        if not isinstance(documents, dict) or set(documents) != set(LANGUAGES):
            raise Unsupported("paired documents required")
        for language, raw in documents.items():
            if not isinstance(raw, bytes) or len(raw) > MAX_DOCUMENT or b"\0" in raw:
                raise Unsupported("invalid bounded FAQ document")
            raw.decode("utf-8")
        if not isinstance(expected_sha256, dict) or set(expected_sha256) != set(LANGUAGES) or any(
            expected_sha256[language] != sha(documents[language]) for language in LANGUAGES
        ):
            raise Unsupported("FAQ document checksum changed")
        if complete_inventory is not True or not isinstance(inventory, list) or len(inventory) > 128:
            raise Unsupported("complete bounded FAQ inventory required")
        if not isinstance(packet, dict):
            raise Unsupported("source packet required")
        metadata = packet.get("metadata", {})
        if not isinstance(metadata, dict) or metadata.get("managed_ownership") is not True or metadata.get("human_authored"):
            raise Unsupported("operator-owned source/document scope required")
        contract_id = packet.get("logical_contract_id")
        if not isinstance(contract_id, str) or not re.fullmatch(r"[a-z][a-z0-9_.-]{0,95}", contract_id):
            raise Unsupported("invalid logical contract identity")
        owned = {language: blocks(documents[language]) for language in LANGUAGES}
        registered_ids = set()
        for item in inventory:
            if not isinstance(item, dict) or set(item) != INVENTORY_KEYS:
                raise Unsupported("invalid FAQ inventory schema")
            if not all(isinstance(item[key], str) and item[key] for key in ("logical_contract_id", "question_kind", "block_id")):
                raise Unsupported("invalid inventory identity")
            if type(item["managed_ownership"]) is not bool or type(item["human_authored"]) is not bool:
                raise Unsupported("inventory ownership must be explicit booleans")
            if item["block_id"] in registered_ids:
                raise Unsupported("duplicate inventory block identity")
            registered_ids.add(item["block_id"])
        matches = [item for item in inventory if item["logical_contract_id"] == contract_id and item["question_kind"] == KIND]
        if len(matches) > 1:
            raise Unsupported("duplicate canonical FAQ identity; preserve both for review")
        selected = matches[0] if matches else None
        if selected and (selected["managed_ownership"] is not True or selected["human_authored"] is not False):
            raise Unsupported("canonical FAQ identity conflicts with human content")
        # This bounded question family uses the contract identity as its owned
        # block identity. Other identities are preserved, not silently adopted.
        if selected and selected["block_id"] != contract_id:
            raise Unsupported("FAQ block and source identities differ")
        if selected is None and any(contract_id in owned[language] for language in LANGUAGES):
            raise Unsupported("unregistered existing claim cannot be adopted as a FAQ")
        if selected:
            source_packet = copy.deepcopy(packet)
            docs = {}
            for language in LANGUAGES:
                if contract_id not in owned[language]:
                    raise Unsupported("paired owned FAQ markers missing")
                start, end = owned[language][contract_id]
                docs[language] = claim_text(documents[language][start.end():end.start()])
            if packet.get("documentation") != docs:
                raise Unsupported("source packet addresses different FAQ text")
            patterns = {"en": r"FAQ: Does ([A-Za-z_]\w*) return(-?\d+)\? Yes\.",
                        "pt-br": r"FAQ: ([A-Za-z_]\w*) retorna(-?\d+)\? Sim\."}
            parsed = [re.fullmatch(patterns[language], docs[language]) for language in LANGUAGES]
            if not all(parsed) or (parsed[0][1], int(parsed[0][2])) != (parsed[1][1], int(parsed[1][2])):
                raise Unsupported("FAQ text outside paired question profile")
            recommendation = decision(source_packet)
        else:
            if packet.get("documentation") != {"en": "", "pt-br": ""}:
                raise Unsupported("missing FAQ must have paired empty documentation")
            recommendation = decision(packet)
        result["source_evidence"] = recommendation
        if recommendation["action"] == "INCONCLUSIVE" and not (
            selected is None and recommendation["reason"] == "new documentation need not established"
        ):
            raise Unsupported("source evidence inconclusive: " + recommendation["reason"])
        current = recommendation["evidence"].get("current", {})
        selector = metadata.get("selector", contract_id.rsplit(".", 1)[-1])
        if selected and recommendation["action"] == "REMOVE":
            action, replacements = "REMOVE", None
        else:
            after = current.get("functions", {}).get(selector)
            if not after:
                raise Unsupported("current selected FAQ contract missing")
            behavior = after["fact"]["behavior"]
            if behavior.get("kind") != "literal-return" or behavior.get("literal", {}).get("type") != "int":
                raise Unsupported("current FAQ body outside integer-return profile")
            replacements = render(selector, behavior["literal"]["value"])
            if selected:
                if recommendation["action"] not in ("MODIFY", "NO-OP"):
                    raise Unsupported("FAQ source action outside admitted update profile")
                action = "NO-OP" if replacements == packet["documentation"] else "MODIFY"
            else:
                action = "ADD"
        if action == "NO-OP":
            return finish(action, "Both current source-backed FAQ answers remain valid; preserve exact bytes.")
        candidates, diffs = {}, {}
        for language in LANGUAGES:
            original = documents[language]
            if action == "ADD":
                anchor = re.compile((r"(?m)^<!-- documentation-agent:anchor:" + re.escape(contract_id) + r" -->(\r?\n|\Z)").encode())
                anchors = list(anchor.finditer(original))
                if len(anchors) != 1:
                    raise Unsupported("missing FAQ requires one explicit owned insertion anchor")
                position = anchors[0].start()
                eol = anchors[0][1] or b"\n"
                addition = b"<!-- documentation-agent:claim:"+contract_id.encode()+b":start -->"+eol+replacements[language].encode()+b"\n"+b"<!-- documentation-agent:claim:"+contract_id.encode()+b":end -->"+eol
                candidate = original[:position]+addition+original[position:]
            else:
                start, end = owned[language][contract_id]
                if action == "REMOVE":
                    candidate = original[:start.start()]+original[end.end():]
                else:
                    candidate = original[:start.end()]+replacements[language].encode()+b"\n"+original[end.start():]
            if len(candidate) > MAX_DOCUMENT:
                raise Unsupported("FAQ candidate exceeds document budget")
            blocks(candidate)
            candidates[language] = candidate
            diffs[language] = "".join(difflib.unified_diff(original.decode().splitlines(True),candidate.decode().splitlines(True),fromfile="original/"+language+".md",tofile="candidate/"+language+".md"))
        # Publish the in-memory pair only after both languages pass all checks.
        result.update(candidates=candidates, changed=True, history_required=True,
                      history=dict(documents), diffs=diffs,
                      before_sha256={language:sha(documents[language])for language in LANGUAGES},
                      candidate_sha256={language:sha(candidates[language])for language in LANGUAGES})
        return finish(action, "Source-grounded owned FAQ candidate; preserve the full original pair and request owner review.")
    except (Unsupported, ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        return finish("INCONCLUSIVE", str(error))
